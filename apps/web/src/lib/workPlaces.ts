/**
 * Places for «Trabajo en» (pure, unit tested): CRTM stations (metro, Cercanías, Metro Ligero)
 * from /api/v1/places and the zones of the map, found by name without an external geocoder.
 */
import { titleCase } from "@/lib/names";
import type { PlaceFeature } from "@/lib/map/places";
import { type ZoneCollection, type ZoneGeometry, ringArea, searchable } from "@/lib/map/zones";

/** Station subcategories of /api/v1/places, with the word that goes after their name. */
export const STATION_KINDS: Record<string, string> = { metro: "metro", cercanias: "Cercanías", metro_ligero: "Metro Ligero" };

export interface WorkPlace {
  id: string;
  /** What the search and the zone card call it («Nuevos Ministerios (metro)»). */
  label: string;
  /** Kind of place, shown next to the name in the list («Metro», «Municipio»). */
  kind: string;
  lat: number;
  lon: number;
}

const capitalize = (text: string) => text.charAt(0).toUpperCase() + text.slice(1);

/** One entry per station name and kind: the source repeats a station once per platform or line. */
export function stationPlaces(features: readonly PlaceFeature[]): WorkPlace[] {
  const seen = new Map<string, WorkPlace>();
  for (const f of features) {
    const word = STATION_KINDS[f.properties.subcategory ?? ""];
    const [lon, lat] = f.geometry.coordinates;
    if (!word || lon === undefined || lat === undefined) continue;
    const name = titleCase(f.properties.name);
    const label = `${name} (${word})`;
    if (!seen.has(label)) seen.set(label, { id: `estacion:${label}`, label, kind: capitalize(word), lat, lon });
  }
  return [...seen.values()];
}

/** Centre of mass of the largest polygon: a point inside ordinary zones, for the distance in a straight line. */
export function centroidOf(geometry: ZoneGeometry): [lon: number, lat: number] | null {
  const rings = (geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates).map((p) => p[0] ?? []);
  const ring = rings.reduce<GeoJSON.Position[]>((best, r) => (Math.abs(ringArea(r)) > Math.abs(ringArea(best)) ? r : best), []);
  const area = ringArea(ring);
  if (area === 0) return null;
  let cx = 0;
  let cy = 0;
  for (let i = 0; i < ring.length - 1; i += 1) {
    const [x1 = 0, y1 = 0] = ring[i] ?? [];
    const [x2 = 0, y2 = 0] = ring[i + 1] ?? [];
    const cross = x1 * y2 - x2 * y1;
    cx += (x1 + x2) * cross;
    cy += (y1 + y2) * cross;
  }
  return [cx / (6 * area), cy / (6 * area)];
}

/** The zones of the map as places: municipios, and Madrid's districts with the city in brackets. */
export function zonePlaces(zones: ZoneCollection): WorkPlace[] {
  return zones.features.flatMap((f) => {
    const centre = centroidOf(f.geometry);
    if (!centre) return [];
    const { level, name, municipio_name, zone_key } = f.properties;
    const district = level === "distrito";
    return [
      {
        id: `zona:${zone_key}`,
        label: district ? `${name} (${municipio_name})` : name,
        kind: district ? `Distrito de ${municipio_name}` : "Municipio",
        lon: centre[0],
        lat: centre[1],
      },
    ];
  });
}

/** Places whose name contains what was typed (no accents, any case): names that start with it first. */
export function findPlaces(places: readonly WorkPlace[], query: string, limit = 8): WorkPlace[] {
  const wanted = searchable(query);
  if (wanted.length < 2) return [];
  const scored = places.flatMap((p) => {
    const text = searchable(p.label);
    const at = text.indexOf(wanted);
    return at < 0 ? [] : [{ p, score: at === 0 ? 0 : 1 }];
  });
  scored.sort((a, b) => a.score - b.score || a.p.label.localeCompare(b.p.label, "es"));
  return scored.slice(0, limit).map((s) => s.p);
}

/**
 * The option the arrows move to in a list of `length` (ARIA combobox): -1 is none, down from none
 * goes to the first, up from none to the last, and both wrap around.
 */
export function stepActive(current: number, step: 1 | -1, length: number): number {
  if (length === 0) return -1;
  if (current < 0) return step === 1 ? 0 : length - 1;
  return (current + step + length) % length;
}
