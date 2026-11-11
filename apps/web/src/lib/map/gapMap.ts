/**
 * The overview map coloured by one row of «Qué falta» (pure, unit tested): GET /api/v1/gaps?level=&row=
 * for municipios and for Madrid's districts, joined to the zones of the map by admin_unit_id.
 * Status is told by colour, by pattern (FALTA stripes, JUSTO dots, small zone lines, SIN DATOS
 * dashed edge) and by the legend's text, never by colour alone.
 */
import type { GapRowMap, ZoneGapStatus } from "@/contracts/gap_row_map_response";
import type { GapRowKey } from "@/contracts/zone_gap_list_response";
import type { GapStatus } from "@/contracts/zone_gap_list_response";
import { isSmallZone, ROW_NAME } from "@/lib/gaps";

import type { ZoneCollection, ZoneProperties } from "./zones";

/** Rows a person can paint the map with, in the API order (GapRowKey). */
export const MAP_ROWS = Object.keys(ROW_NAME) as GapRowKey[];

export function isGapRow(value: unknown): value is GapRowKey {
  return typeof value === "string" && (MAP_ROWS as string[]).includes(value);
}

/** Each zone's status in the row, from the maps of every level. */
export function gapByZone(maps: readonly Pick<GapRowMap, "zones">[]): Map<string, ZoneGapStatus> {
  return new Map(maps.flatMap((m) => m.zones.map((z) => [z.admin_unit_id, z] as const)));
}

/**
 * How a zone is painted: its status, or ZONA_PEQUENA when it is too small to compare (D-213,
 * `reliable: false`): one fill per zone, so the small zone gets its own class on the map.
 */
export type MapCategory = GapStatus | "ZONA_PEQUENA";

export function mapCategory(zone: { status: GapStatus; reliable?: boolean }): MapCategory {
  return isSmallZone(zone) ? "ZONA_PEQUENA" : zone.status;
}

export type PaintedProperties = ZoneProperties & { gap?: MapCategory };
export type PaintedCollection = GeoJSON.FeatureCollection<ZoneCollection["features"][number]["geometry"], PaintedProperties>;

/**
 * The zones of the map with their status in `gap`, read by the map's paint. A zone the row does
 * not carry (not computed at its level yet) gets none and keeps the plain fill: it is not SIN DATOS.
 */
export function paintZones(zones: ZoneCollection, byZone: ReadonlyMap<string, ZoneGapStatus>): PaintedCollection {
  return {
    ...zones,
    features: zones.features.map((f) => {
      const status = byZone.get(f.properties.admin_unit_id);
      return status ? { ...f, properties: { ...f.properties, gap: mapCategory(status) } } : f;
    }),
  };
}

export type StatusCounts = Record<MapCategory, number> & { pending: number };

/** How many zones of the map fall in each status (Madrid counts as its 21 districts). */
export function countByStatus(painted: PaintedCollection): StatusCounts {
  const counts: StatusCounts = { FALTA: 0, JUSTO: 0, CUBIERTO: 0, ZONA_PEQUENA: 0, SIN_DATOS: 0, pending: 0 };
  for (const f of painted.features) counts[f.properties.gap ?? "pending"] += 1;
  return counts;
}

/**
 * Pattern tiles in CSS px: FALTA diagonal stripes, JUSTO dots and small-zone horizontal lines
 * (the legend draws the same in CSS).
 */
export const GAP_PATTERN = { size: 12, period: 6, stripe: 1.5, dot: 2 } as const;
export const PATTERN_IMAGE = { FALTA: "gap-falta", JUSTO: "gap-justo", ZONA_PEQUENA: "gap-zona-pequena" } as const;

export type PatternKind = "stripes" | "dots" | "lines";
export type Rgba8 = [r: number, g: number, b: number, a: number];

/** RGBA pixels of a seamless pattern tile at `scale` device pixels per CSS pixel. */
export function patternPixels(kind: PatternKind, ink: Rgba8, scale: number): { width: number; height: number; data: Uint8Array } {
  const size = GAP_PATTERN.size * scale;
  const period = GAP_PATTERN.period * scale;
  const mark = Math.max(1, Math.round((kind === "dots" ? GAP_PATTERN.dot : GAP_PATTERN.stripe) * scale));
  const data = new Uint8Array(size * size * 4);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const on =
        kind === "stripes" ? (x + y) % period < mark : kind === "lines" ? y % period < mark : x % period < mark && y % period < mark;
      if (on) data.set(ink, (y * size + x) * 4);
    }
  }
  return { width: size, height: size, data };
}
