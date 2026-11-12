/**
 * Key points of a zone for the 3D view (pure, unit tested): a few real places from
 * /api/v1/places, which filters them by zone, labelled in plain words (pitch/textos_web.md, mapa.3d.*).
 */
import type { PlaceProperties } from "@/contracts/places_response";
import type { PlaceCategory } from "@/lib/api";
import { titleCase } from "@/lib/names";

export type { PlaceProperties };

/** A place of /api/v1/places (places-1): its properties from the contract, its point as GeoJSON. */
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

interface Rule {
  kind: KeyPointKind;
  category: PlaceCategory;
  limit: number;
  /** Subcategories in order of preference, each with its label */
  classes: { subcategory: string; label: string }[];
}

const RULES: Rule[] = [
  {
    kind: "transporte",
    category: "transport",
    limit: 2,
    classes: [
      { subcategory: "cercanias", label: "Estación" },
      { subcategory: "metro", label: "Metro" },
      { subcategory: "metro_ligero", label: "Metro Ligero" },
    ],
  },
  {
    kind: "salud",
    category: "health",
    limit: 1,
    classes: [
      { subcategory: "Centro de salud", label: "Centro de salud" },
      { subcategory: "Hospital general", label: "Hospital" },
      { subcategory: "Consultorio de atención primaria", label: "Consultorio" },
    ],
  },
  {
    kind: "colegio",
    category: "education",
    limit: 1,
    classes: [{ subcategory: "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", label: "Colegio" }],
  },
];

/** What to ask /api/v1/places for: only the classes that can become key points, per category. */
export function keyPointQueries(): { category: PlaceCategory; subcategories: string[] }[] {
  return RULES.map((rule) => ({ category: rule.category, subcategories: rule.classes.map((c) => c.subcategory) }));
}

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

/** Whether a place's label would be seen on screen (not under a card, not off the map). */
export type InView = (lon: number, lat: number) => boolean;

export interface KeyPointOptions {
  inView?: InView;
  /** Whether two labels can both show without one covering the other. */
  apart?: (a: KeyPoint, b: KeyPoint) => boolean;
}

/**
 * Up to two stations, one health centre and one public school. The first point is the best
 * station nearest the zone centre; every later point is the one farthest from those already
 * shown, so labels spread over the zone instead of piling up. Each kind starts with its best
 * class (commuter rail before metro, health centre before hospital). Only places `inView` and
 * `apart` from the points already picked count: a kind without one is left out rather than
 * labelled under a card or on top of another label.
 */
export function pickKeyPoints(
  places: PlaceFeature[],
  center: [number, number],
  { inView = () => true, apart = () => true }: KeyPointOptions = {},
): KeyPoint[] {
  const picked: Candidate[] = [];
  const at = (c: Candidate): [number, number] => [c.lon, c.lat];
  for (const rule of RULES) {
    const pool = candidates(places, rule).filter((c) => inView(c.lon, c.lat));
    for (let n = 0; n < rule.limit; n += 1) {
      const free = pool.filter((c) => picked.every((p) => apart(c, p)));
      if (free.length === 0) break;
      const options = n === 0 ? bestClass(free) : free;
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
