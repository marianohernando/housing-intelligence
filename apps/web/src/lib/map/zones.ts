/**
 * Zones of the map (pure, unit tested): the region by municipio with Madrid capital split into
 * its 21 districts (D-200), built from /api/v1/geo/admin-units.
 */
import type { AdminUnitProperties } from "@/lib/geo";
import { displayName } from "@/lib/names";

/** Municipios shown by district instead of as one block (D-200: Madrid capital, 3.3 M people). */
export const MUNICIPIOS_BY_DISTRITO: readonly string[] = ["28079"];

export type ZoneLevel = "municipio" | "distrito";
export type ZoneGeometry = GeoJSON.Polygon | GeoJSON.MultiPolygon;

/** A feature as /api/v1/geo/admin-units returns it (`level` stays a plain string here). */
export type AdminFeature = GeoJSON.Feature<ZoneGeometry, Omit<AdminUnitProperties, "level"> & { level: string }>;

export interface ZoneProperties {
  admin_unit_id: string;
  level: ZoneLevel;
  code: string;
  name: string;
  /** Readable municipio name for the breadcrumbs («Madrid › Chamartín»). */
  municipio_name: string;
  zone_key: string;
}

export type ZoneFeature = GeoJSON.Feature<ZoneGeometry, ZoneProperties>;
export type ZoneCollection = GeoJSON.FeatureCollection<ZoneGeometry, ZoneProperties>;

function toZone(feature: AdminFeature, level: ZoneLevel, municipioName: string): ZoneFeature {
  const { admin_unit_id, code, name } = feature.properties;
  return {
    type: "Feature",
    id: admin_unit_id,
    geometry: feature.geometry,
    properties: {
      admin_unit_id,
      level,
      code,
      name: displayName(name ?? code),
      municipio_name: municipioName,
      zone_key: `${level}/${code}`,
    },
  };
}

export function buildZoneCollection(
  municipios: AdminFeature[],
  distritos: AdminFeature[],
  splitCodes: readonly string[] = MUNICIPIOS_BY_DISTRITO,
): ZoneCollection {
  const split = municipios.filter((m) => splitCodes.includes(m.properties.code));
  const splitNames = new Map(split.map((m) => [m.properties.admin_unit_id, displayName(m.properties.name ?? "")]));
  const whole = municipios
    .filter((m) => !splitCodes.includes(m.properties.code))
    .map((m) => toZone(m, "municipio", displayName(m.properties.name ?? m.properties.code)));
  const districts = distritos.flatMap((d) => {
    const municipioName = d.properties.parent ? splitNames.get(d.properties.parent) : undefined;
    return municipioName === undefined ? [] : [toZone(d, "distrito", municipioName)];
  });
  return { type: "FeatureCollection", features: [...whole, ...districts] };
}

export function findZone(zones: ZoneCollection, level: string, code: string): ZoneFeature | undefined {
  return zones.features.find((f) => f.properties.level === level && f.properties.code === code);
}

export function zoneHref(zone: { level: string; code: string }): string {
  return `/zona/${zone.level}/${encodeURIComponent(zone.code)}`;
}

export type Bounds = [west: number, south: number, east: number, north: number];

function polygons(geometry: ZoneGeometry): GeoJSON.Position[][][] {
  return geometry.type === "Polygon" ? [geometry.coordinates] : geometry.coordinates;
}

export function boundsOf(geometry: ZoneGeometry): Bounds {
  const bounds: Bounds = [Infinity, Infinity, -Infinity, -Infinity];
  for (const polygon of polygons(geometry)) {
    for (const [lon = 0, lat = 0] of polygon[0] ?? []) {
      bounds[0] = Math.min(bounds[0], lon);
      bounds[1] = Math.min(bounds[1], lat);
      bounds[2] = Math.max(bounds[2], lon);
      bounds[3] = Math.max(bounds[3], lat);
    }
  }
  return bounds;
}

export function boundsOfAll(zones: ZoneCollection): Bounds {
  return zones.features.map((f) => boundsOf(f.geometry)).reduce<Bounds>(
    (acc, b) => [Math.min(acc[0], b[0]), Math.min(acc[1], b[1]), Math.max(acc[2], b[2]), Math.max(acc[3], b[3])],
    [Infinity, Infinity, -Infinity, -Infinity],
  );
}

/** All zones as one multipolygon: the region, whose outside the overview fades. */
export function regionOf(zones: ZoneCollection): GeoJSON.MultiPolygon {
  return { type: "MultiPolygon", coordinates: zones.features.flatMap((f) => polygons(f.geometry)) };
}

/** Signed area of a ring (shoelace); the sign tells its winding. */
export function ringArea(ring: GeoJSON.Position[]): number {
  let sum = 0;
  for (let i = 0; i < ring.length - 1; i += 1) {
    const [x1 = 0, y1 = 0] = ring[i] ?? [];
    const [x2 = 0, y2 = 0] = ring[i + 1] ?? [];
    sum += x1 * y2 - x2 * y1;
  }
  return sum / 2;
}

const WORLD: GeoJSON.Position[] = [
  [-180, -85],
  [180, -85],
  [180, 85],
  [-180, 85],
  [-180, -85],
];

/** Everything except the zone, to fade the surroundings: the zone's outer rings become holes. */
export function maskAround(geometry: ZoneGeometry): GeoJSON.Polygon {
  const outerSign = Math.sign(ringArea(WORLD));
  const holes = polygons(geometry).flatMap((polygon) => {
    const ring = polygon[0];
    if (!ring) return [];
    return [Math.sign(ringArea(ring)) === outerSign ? [...ring].reverse() : ring];
  });
  return { type: "Polygon", coordinates: [WORLD, ...holes] };
}
