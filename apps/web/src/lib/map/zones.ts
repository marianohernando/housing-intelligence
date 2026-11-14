/**
 * Zones of the map (pure, unit tested): the region by municipio with Madrid capital split into
 * its 21 districts (D-200), built from /api/v1/geo/admin-units, which already gives readable names.
 */
import type { AdminUnitProperties } from "@/lib/geo";

/**
 * Municipios shown by district instead of as one block (D-200: Madrid capital, 3.3 M people), by
 * admin_unit_id: the map asks /geo/admin-units?parent= for the districts of each one.
 */
export const MUNICIPIOS_BY_DISTRITO: readonly string[] = ["ES.28.MUN.28079"];

export type ZoneLevel = "municipio" | "distrito";

/**
 * Levels a zone of the map can have: a search over Madrid capital (`scope: madrid`, D-238) paints
 * its barrios instead of its districts. A barrio has no screen nor «Qué falta» of its own: both
 * are its district's (D-232).
 */
export type MapLevel = ZoneLevel | "barrio";

/** A barrio's code starts with its district's (2807906, Tetuán; 28079061, Bellas Vistas). */
export const DISTRICT_CODE_LENGTH = 7;

/** A municipio the map shows by its districts (Madrid capital): it has a «Qué falta» list, not a zone screen. */
export function isWholeCity(adminUnitId: string | null | undefined): boolean {
  return adminUnitId != null && MUNICIPIOS_BY_DISTRITO.includes(adminUnitId);
}

/**
 * The whole cities behind the districts of the map (MUNICIPIOS_BY_DISTRITO), named after their
 * districts: the municipio code (INE) is the last part of its id and starts every district code.
 */
export function wholeCities(zones: ZoneCollection): { admin_unit_id: string; code: string; name: string }[] {
  return MUNICIPIOS_BY_DISTRITO.flatMap((id) => {
    const code = id.split(".").at(-1) ?? "";
    const district = zones.features.find((f) => f.properties.level === "distrito" && f.properties.code.startsWith(code));
    return district ? [{ admin_unit_id: id, code, name: district.properties.municipio_name }] : [];
  });
}
export type ZoneGeometry = GeoJSON.Polygon | GeoJSON.MultiPolygon;

/** A feature as /api/v1/geo/admin-units returns it (`level` stays a plain string here). */
export type AdminFeature = GeoJSON.Feature<ZoneGeometry, Omit<AdminUnitProperties, "level"> & { level: string }>;

export interface ZoneProperties {
  admin_unit_id: string;
  level: MapLevel;
  code: string;
  name: string;
  /** Readable municipio name for the breadcrumbs («Madrid › Chamartín»). */
  municipio_name: string;
  zone_key: string;
  /** Barrios only: their district, by the start of their code (flat, as map features need). */
  district_code?: string;
  district_name?: string;
}

export type ZoneFeature = GeoJSON.Feature<ZoneGeometry, ZoneProperties>;
export type ZoneCollection = GeoJSON.FeatureCollection<ZoneGeometry, ZoneProperties>;

function toZone(feature: AdminFeature, level: MapLevel, municipioName: string): ZoneFeature {
  const { admin_unit_id, code, name } = feature.properties;
  return {
    type: "Feature",
    id: admin_unit_id,
    geometry: feature.geometry,
    properties: {
      admin_unit_id,
      level,
      code,
      name: name ?? code,
      municipio_name: municipioName,
      zone_key: `${level}/${code}`,
    },
  };
}

export function buildZoneCollection(
  municipios: AdminFeature[],
  distritos: AdminFeature[],
  splitIds: readonly string[] = MUNICIPIOS_BY_DISTRITO,
): ZoneCollection {
  const isSplit = (m: AdminFeature) => splitIds.includes(m.properties.admin_unit_id);
  const nameOf = (m: AdminFeature) => m.properties.name ?? m.properties.code;
  const splitNames = new Map(municipios.filter(isSplit).map((m) => [m.properties.admin_unit_id, nameOf(m)]));
  const whole = municipios.filter((m) => !isSplit(m)).map((m) => toZone(m, "municipio", nameOf(m)));
  const districts = distritos.flatMap((d) => {
    const municipioName = d.properties.parent ? splitNames.get(d.properties.parent) : undefined;
    return municipioName === undefined ? [] : [toZone(d, "distrito", municipioName)];
  });
  return { type: "FeatureCollection", features: [...whole, ...districts] };
}

/** The district of a barrio of the map, by the start of the barrio's code. */
export function districtOf(zones: ZoneCollection, barrioCode: string): ZoneProperties | undefined {
  const code = barrioCode.slice(0, DISTRICT_CODE_LENGTH);
  return zones.features.find((f) => f.properties.level === "distrito" && f.properties.code === code)?.properties;
}

/** «Berruguete · Tetuán»: a barrio with its district, when known; any other zone by its name. */
export function zoneTitle(zone: Pick<ZoneProperties, "name" | "district_name">): string {
  return zone.district_name ? `${zone.name} · ${zone.district_name}` : zone.name;
}

/** The zone whose screen and «Qué falta» a zone of the map has: itself, or a barrio's district (D-232). */
export function screenZone(zone: Pick<ZoneProperties, "level" | "code" | "district_code">): { level: ZoneLevel; code: string } {
  if (zone.level === "barrio") return { level: "distrito", code: zone.district_code ?? zone.code.slice(0, DISTRICT_CODE_LENGTH) };
  return { level: zone.level, code: zone.code };
}

/**
 * The zone picked (its `zone_key`), once the map changes between Madrid's districts and its
 * barrios (D-238): a barrio becomes its district; a district has no single barrio, so it is let go.
 */
export function selectionAfter(key: string | null, barrios: boolean): string | null {
  const [level = "", code = ""] = key?.split("/") ?? [];
  if (!barrios && level === "barrio") {
    const district = screenZone({ level: "barrio", code });
    return `${district.level}/${district.code}`;
  }
  return barrios && level === "distrito" ? null : key;
}

/**
 * The barrios of the districts of the map, as zones (D-238): each with its district's name and
 * municipio. A barrio whose district is not on the map is left out.
 */
export function barrioZones(barrios: AdminFeature[], zones: ZoneCollection): ZoneCollection {
  const features = barrios.flatMap((b) => {
    const district = districtOf(zones, b.properties.code);
    if (!district) return [];
    const zone = toZone(b, "barrio", district.municipio_name);
    return [{ ...zone, properties: { ...zone.properties, district_code: district.code, district_name: district.name } }];
  });
  return { type: "FeatureCollection", features };
}

/** The map of a search over Madrid capital (D-238): the other municipios and, instead of its districts, its barrios. */
export function withBarrios(zones: ZoneCollection, barrios: ZoneCollection): ZoneCollection {
  const others = zones.features.filter((f) => f.properties.level !== "distrito");
  return { type: "FeatureCollection", features: [...others, ...barrios.features] };
}

/**
 * A zone of the map from a zone reference of the API (the `zone` of GET /gaps), so the zone screen
 * can name it before the outlines arrive. Null when it is not a zone of the map's levels.
 */
export function zonePropertiesOf(ref: {
  level: string;
  code: string;
  name: string;
  admin_unit_id?: string | null;
  municipio_name?: string | null;
}): ZoneProperties | null {
  const { level, code, name, admin_unit_id } = ref;
  if ((level !== "municipio" && level !== "distrito") || !admin_unit_id) return null;
  const municipioName = level === "municipio" ? name : ref.municipio_name;
  if (!municipioName) return null;
  return { admin_unit_id, level, code, name, municipio_name: municipioName, zone_key: `${level}/${code}` };
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

/** Points of the outer rings: what the camera must keep in view to show the whole zone. */
export function outlinePoints(geometry: ZoneGeometry): [number, number][] {
  return polygons(geometry).flatMap((polygon) => (polygon[0] ?? []).map(([lon = 0, lat = 0]) => [lon, lat] as [number, number]));
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

const METRES_PER_DEGREE = 111320;

/**
 * Thin quads just outside the zone outline, one per side. Extruded, they read as the edge of a
 * raised model (mockup 2) without covering the streets and parks inside the zone.
 */
export function edgeWall(geometry: ZoneGeometry, widthM: number): GeoJSON.FeatureCollection<GeoJSON.Polygon> {
  const features = polygons(geometry).flatMap((polygon) => {
    const ring = polygon[0] ?? [];
    // Outward is to the right of a counter-clockwise ring and to the left of a clockwise one.
    const side = ringArea(ring) > 0 ? 1 : -1;
    return ring.slice(0, -1).map((start, i): GeoJSON.Feature<GeoJSON.Polygon> => {
      const [x1 = 0, y1 = 0] = start;
      const [x2 = 0, y2 = 0] = ring[i + 1] ?? [];
      const kx = Math.cos((((y1 + y2) / 2) * Math.PI) / 180) * METRES_PER_DEGREE;
      const dx = (x2 - x1) * kx;
      const dy = (y2 - y1) * METRES_PER_DEGREE;
      const length = Math.hypot(dx, dy) || 1;
      const ox = ((side * dy) / length) * (widthM / kx);
      const oy = ((side * -dx) / length) * (widthM / METRES_PER_DEGREE);
      const quad = [[x1, y1], [x2, y2], [x2 + ox, y2 + oy], [x1 + ox, y1 + oy], [x1, y1]];
      return { type: "Feature", geometry: { type: "Polygon", coordinates: [quad] }, properties: {} };
    });
  });
  return { type: "FeatureCollection", features };
}

/** Lower case without accents, to find «Chamartín» by typing «chamartin». */
/** Text as the zone filter compares it: lower case, without accents. */
export function searchable(text: string): string {
  return text.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase().trim();
}

/** The zones as a list (the map's alternative): Madrid's districts and the other municipios, by name. */
export function zoneDirectory(zones: ZoneCollection, query: string): { distritos: ZoneProperties[]; municipios: ZoneProperties[] } {
  const wanted = searchable(query);
  const listed = zones.features
    .map((f) => f.properties)
    .filter((z) => searchable(z.name).includes(wanted))
    .sort((a, b) => a.name.localeCompare(b.name, "es"));
  return { distritos: listed.filter((z) => z.level === "distrito"), municipios: listed.filter((z) => z.level === "municipio") };
}
