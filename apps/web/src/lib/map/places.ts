/**
 * Key points of a zone for the 3D view (pure, unit tested): a few real places from
 * /api/v1/places, inside the zone, labelled in plain words (pitch/textos_web.md, mapa.3d.*).
 */
import { titleCase } from "@/lib/names";

export interface PlaceProperties {
  name: string;
  category: string;
  subcategory: string | null;
  municipio: string | null;
  /** geo_admin_unit id of the census section, e.g. ES.28.SEC.2807905001 */
  seccion: string | null;
}

export type PlaceFeature = GeoJSON.Feature<GeoJSON.Point, PlaceProperties>;

export type KeyPointKind = "transporte" | "salud" | "colegio";

export interface KeyPoint {
  id: string;
  kind: KeyPointKind;
  /** Short type in plain words («Estación», «Centro de salud») */
  label: string;
  /** Readable proper name, or null when the source only gives a generic one */
  name: string | null;
  lon: number;
  lat: number;
}

/** The section code starts with the district code (5 municipio + 2 district + 3 section digits). */
function sectionCode(seccion: string | null): string {
  return seccion?.split(".").at(-1) ?? "";
}

export function placesInZone(places: PlaceFeature[], zone: { level: string; code: string }): PlaceFeature[] {
  if (zone.level === "municipio") return places.filter((p) => p.properties.municipio === zone.code);
  return places.filter((p) => sectionCode(p.properties.seccion).startsWith(zone.code));
}

interface Rule {
  kind: KeyPointKind;
  limit: number;
  /** Subcategories in order of preference, each with its label */
  classes: { subcategory: string; label: string }[];
}

const RULES: Rule[] = [
  {
    kind: "transporte",
    limit: 2,
    classes: [
      { subcategory: "cercanias", label: "Estación" },
      { subcategory: "metro", label: "Metro" },
      { subcategory: "metro_ligero", label: "Metro Ligero" },
    ],
  },
  {
    kind: "salud",
    limit: 1,
    classes: [
      { subcategory: "Centro de salud", label: "Centro de salud" },
      { subcategory: "Hospital general", label: "Hospital" },
      { subcategory: "Consultorio de atención primaria", label: "Consultorio" },
    ],
  },
  {
    kind: "colegio",
    limit: 1,
    classes: [{ subcategory: "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", label: "Colegio" }],
  },
];

/** «Centro de salud (Madrid)» only repeats the type: the source has no proper name for it. */
function properName(place: PlaceFeature): string | null {
  const { name, subcategory } = place.properties;
  if (subcategory && name.startsWith(`${subcategory} (`)) return null;
  return titleCase(name);
}

function distance(a: [number, number], b: [number, number]): number {
  const kx = Math.cos((((a[1] + b[1]) / 2) * Math.PI) / 180);
  return Math.hypot((a[0] - b[0]) * kx, a[1] - b[1]);
}

interface Candidate extends KeyPoint {
  rank: number;
}

function candidates(places: PlaceFeature[], rule: Rule): Candidate[] {
  const seen = new Set<string>();
  return places.flatMap((place) => {
    const rank = rule.classes.findIndex((c) => c.subcategory === place.properties.subcategory);
    const cls = rule.classes[rank];
    if (!cls) return [];
    const name = properName(place);
    const key = `${cls.label}|${name ?? place.id}`;
    if (seen.has(key)) return [];
    seen.add(key);
    const [lon = 0, lat = 0] = place.geometry.coordinates;
    return [{ id: String(place.id ?? key), kind: rule.kind, label: cls.label, name, lon, lat, rank }];
  });
}

function bestClass(pool: Candidate[]): Candidate[] {
  const best = Math.min(...pool.map((c) => c.rank));
  return pool.filter((c) => c.rank === best);
}

/** The candidate that maximises `score`; ties go to the better class, then to the first. */
function argmax(options: Candidate[], score: (c: Candidate) => number): Candidate {
  return options.reduce((a, b) => {
    const diff = score(b) - score(a);
    return diff > 1e-12 || (Math.abs(diff) <= 1e-12 && b.rank < a.rank) ? b : a;
  });
}

/**
 * Up to two stations, one health centre and one public school. The first point is the best
 * station nearest the zone centre; every later point is the one farthest from those already
 * shown, so labels spread over the zone instead of piling up. Each kind starts with its best
 * class (commuter rail before metro, health centre before hospital).
 */
export function pickKeyPoints(places: PlaceFeature[], center: [number, number]): KeyPoint[] {
  const picked: Candidate[] = [];
  const at = (c: Candidate): [number, number] => [c.lon, c.lat];
  for (const rule of RULES) {
    const pool = candidates(places, rule);
    for (let n = 0; n < rule.limit && pool.length > 0; n += 1) {
      const options = n === 0 ? bestClass(pool) : pool;
      const choice =
        picked.length === 0
          ? argmax(options, (c) => -distance(at(c), center))
          : argmax(options, (c) => Math.min(...picked.map((p) => distance(at(c), at(p)))));
      picked.push(choice);
      pool.splice(pool.indexOf(choice), 1);
    }
  }
  return picked.map(({ id, kind, label, name, lon, lat }) => ({ id, kind, label, name, lon, lat }));
}
