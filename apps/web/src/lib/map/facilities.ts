/**
 * Every facility of a zone (pure, unit tested), not only its key points (FASE_PRUEBAS, T3): the
 * places of /api/v1/places asked by zone and subcategory, grouped in the types a person looks for
 * and named in plain words. Each type counts the same subcategories as its row of «Qué falta»
 * (data/catalog/features), so the figures agree; hospitals have no row yet.
 */
import type { PlaceCategory } from "@/lib/api";
import { formatNumber } from "@/lib/format";
import { titleCase } from "@/lib/names";

import type { PlaceFeature } from "./places";

export type FacilityKey = "colegio" | "escuela_infantil" | "centro_salud" | "hospital" | "farmacia" | "mayores";

export interface FacilityType {
  key: FacilityKey;
  category: PlaceCategory;
  /** Where an API older than the category still has these places (pharmacies were health until D-216) */
  fallback?: PlaceCategory;
  /** Name of the type on its button */
  chip: string;
  /** How many there are: «{n} {many}», «1 {one}», «{none}» */
  one: string;
  many: string;
  none: string;
  /** Subcategories of /places that count, each with the label of one place */
  classes: { subcategory: string; label: string }[];
}

const PUBLIC_SCHOOL = "Colegio público";
const PRIVATE_SCHOOL = "Colegio privado o concertado";
const HOME = "Residencia";

export const FACILITY_TYPES: readonly FacilityType[] = [
  {
    key: "colegio",
    category: "education",
    chip: "Colegios",
    one: "colegio con primaria",
    many: "colegios con primaria",
    none: "Ningún colegio con primaria",
    classes: [
      { subcategory: "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", label: PUBLIC_SCHOOL },
      { subcategory: "COLEGIO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA", label: PUBLIC_SCHOOL },
      { subcategory: "COLEGIO DE EDUCACIÓN PRIMARIA", label: PUBLIC_SCHOOL },
      { subcategory: "CENTRO PRIVADO DE EDUCACIÓN INFANTIL Y PRIMARIA", label: PRIVATE_SCHOOL },
      { subcategory: "CENTRO PRIVADO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA", label: PRIVATE_SCHOOL },
      { subcategory: "CENTRO PRIVADO DE EDUCACIÓN PRIMARIA", label: PRIVATE_SCHOOL },
      { subcategory: "CENTRO PRIVADO DE EDUCACIÓN PRIMARIA Y SECUNDARIA", label: PRIVATE_SCHOOL },
    ],
  },
  {
    key: "escuela_infantil",
    category: "education",
    chip: "Escuelas infantiles",
    one: "escuela infantil",
    many: "escuelas infantiles",
    none: "Ninguna escuela infantil",
    classes: [
      { subcategory: "ESCUELA INFANTIL", label: "Escuela infantil pública" },
      { subcategory: "ESCUELA  INFANTIL-CASA DE NIÑOS", label: "Casa de niños" },
      { subcategory: "ESCUELA INFANTIL PRIVADA", label: "Escuela infantil privada" },
      { subcategory: "CENTRO PRIVADO DE EDUCACIÓN INFANTIL", label: "Escuela infantil privada" },
    ],
  },
  {
    key: "centro_salud",
    category: "health",
    chip: "Centros de salud",
    one: "centro de salud",
    many: "centros de salud",
    none: "Ningún centro de salud",
    classes: [
      { subcategory: "Centro de salud", label: "Centro de salud" },
      { subcategory: "Consultorio de atención primaria", label: "Consultorio" },
    ],
  },
  {
    key: "hospital",
    category: "health",
    chip: "Hospitales",
    one: "hospital",
    many: "hospitales",
    none: "Ningún hospital",
    classes: [
      { subcategory: "Hospital general", label: "Hospital" },
      { subcategory: "Hospital especializado", label: "Hospital especializado" },
      { subcategory: "Hospital de media y larga estancia", label: "Hospital de media y larga estancia" },
      { subcategory: "Hospital de salud mental y tratamiento de toxicomanías", label: "Hospital de salud mental" },
    ],
  },
  {
    key: "farmacia",
    category: "pharmacy",
    fallback: "health",
    chip: "Farmacias",
    one: "farmacia",
    many: "farmacias",
    none: "Ninguna farmacia",
    classes: [{ subcategory: "Farmacia", label: "Farmacia" }],
  },
  {
    key: "mayores",
    category: "social",
    chip: "Mayores",
    one: "residencia o centro de mayores",
    many: "residencias y centros de mayores",
    none: "Ninguna residencia ni centro de mayores",
    classes: [
      { subcategory: "RESIDENCIAS DE PERSONAS MAYORES MIXTA", label: HOME },
      { subcategory: "RESIDENCIAS DE PERSONAS MAYORES DEPENDIENTES", label: HOME },
      { subcategory: "RESIDENCIAS DE PERSONAS MAYORES AUTONOMAS", label: HOME },
      { subcategory: "CENTROS DE DÍA: OTROS", label: "Centro de día" },
      { subcategory: "HOGARES Y CLUBES", label: "Hogar o club de mayores" },
    ],
  },
];

const BY_KEY = new Map(FACILITY_TYPES.map((t) => [t.key, t]));

export function facilityType(key: FacilityKey): FacilityType {
  const type = BY_KEY.get(key);
  if (!type) throw new Error(`Unknown facility type ${key}`);
  return type;
}

export interface FacilityQuery {
  category: PlaceCategory;
  subcategories: string[];
}

/**
 * What to ask /api/v1/places for a zone: one query per category with the subcategories that count.
 * A type whose category is newer than the API (pharmacy, D-216) is asked where the API had it.
 */
export function facilityQueries(): FacilityQuery[] {
  const byCategory = new Map<PlaceCategory, FacilityQuery>();
  for (const type of FACILITY_TYPES) {
    const category = type.fallback ?? type.category;
    const query = byCategory.get(category) ?? { category, subcategories: [] };
    query.subcategories.push(...type.classes.map((c) => c.subcategory));
    byCategory.set(category, query);
  }
  return [...byCategory.values()];
}

/**
 * Queries to add when /places answers with a contract version: places-1 brings the pharmacy
 * category (D-216), so pharmacies are no longer in health. Asking an older API for it would fail.
 */
export const CONTRACT_QUERIES: Readonly<Record<string, readonly FacilityQuery[]>> = {
  "places-1": [{ category: "pharmacy", subcategories: ["Farmacia"] }],
};

/**
 * One facility on the map and in the list. `detail` is its capacity («1.300 camas») when /places
 * carries it (places-1, line A); until then it is null and nothing is shown.
 */
export interface Facility {
  id: string;
  type: FacilityKey;
  label: string;
  name: string | null;
  detail: string | null;
  lon: number;
  lat: number;
}

/** Street types of the pharmacy addresses in the source («AVDA de Alberto Alcocer 22»). */
const STREET: Record<string, string> = {
  AVDA: "Avenida",
  CTRA: "Carretera",
  CMNO: "Camino",
  TRVA: "Travesía",
  GTA: "Glorieta",
  SECT: "Sector",
  URB: "Urbanización",
  BULEV: "Bulevar",
  PSAJE: "Pasaje",
  CLLON: "Callejón",
  CUSTA: "Cuesta",
};

/** «Farmacia · AVDA de Alberto Alcocer 22» -> «Avenida de Alberto Alcocer 22»: the source names a pharmacy by its address. */
function pharmacyAddress(name: string): string {
  const address = name.includes(" · ") ? name.slice(name.indexOf(" · ") + 3) : name;
  const [street = "", ...rest] = address.trim().split(/\s+/);
  const kind = STREET[street] ?? titleCase(street);
  return [kind, titleCase(rest.join(" "))].filter(Boolean).join(" ");
}

/** «SANITAS RESIDENCIAL EL VISO, RESIDENCIA DE PERSONAS MAYORES»: the tail repeats the type. */
const TYPE_TAIL = /^(RESIDENCIA|CENTRO DE D[IÍ]A|HOGAR|CLUB)/;

function placeName(place: PlaceFeature, type: FacilityKey): string | null {
  const { name, subcategory } = place.properties;
  // «Hospital general (Madrid)», «Centro de salud (Pinto)»: the source has no proper name for it
  if (!name || (subcategory && name.startsWith(`${subcategory} (`))) return null;
  if (type === "farmacia") return pharmacyAddress(name);
  const comma = name.lastIndexOf(", ");
  const own = comma > 0 && TYPE_TAIL.test(name.slice(comma + 2)) ? name.slice(0, comma) : name;
  return titleCase(own);
}

/** Schools by the ownership of the register, when the API gives it (places-1). */
const SCHOOL_BY_OWNERSHIP = { publica: PUBLIC_SCHOOL, concertada: "Colegio concertado", privada: "Colegio privado" } as const;

/** «1.300 camas», «120 plazas autorizadas»: only what the register publishes. */
function capacityText(place: PlaceFeature): string | null {
  const capacity = place.properties.capacity;
  return capacity ? `${formatNumber(capacity.value, 0)} ${capacity.unit}` : null;
}

function facility(place: PlaceFeature, type: FacilityType): Facility | null {
  const cls = type.classes.find((c) => c.subcategory === place.properties.subcategory);
  if (!cls) return null;
  const [lon = 0, lat = 0] = place.geometry.coordinates;
  const { ownership } = place.properties;
  const label = type.key === "colegio" && ownership ? SCHOOL_BY_OWNERSHIP[ownership] : cls.label;
  return { id: String(place.id), type: type.key, label, name: placeName(place, type.key), detail: capacityText(place), lon, lat };
}

function byName(a: Facility, b: Facility): number {
  if (a.name && b.name) return a.name.localeCompare(b.name, "es");
  return Number(a.name === null) - Number(b.name === null);
}

/** The zone's places by type, named places first in alphabetical order; the rest are left out. */
export function groupFacilities(places: readonly PlaceFeature[]): Record<FacilityKey, Facility[]> {
  const groups = Object.fromEntries(FACILITY_TYPES.map((t) => [t.key, [] as Facility[]])) as Record<FacilityKey, Facility[]>;
  for (const place of places) {
    for (const type of FACILITY_TYPES) {
      const category = place.properties.category;
      if (category !== type.category && category !== type.fallback) continue;
      const item = facility(place, type);
      if (item) groups[type.key].push(item);
    }
  }
  for (const list of Object.values(groups)) list.sort(byName);
  return groups;
}

/** «23 colegios con primaria en Chamartín», «1 hospital en …», «Ninguna farmacia en …». */
export function facilityCountText(key: FacilityKey, n: number, zone: string): string {
  const type = facilityType(key);
  if (n === 0) return `${type.none} en ${zone}`;
  return `${formatNumber(n, 0)} ${n === 1 ? type.one : type.many} en ${zone}`;
}

export type FacilityPoint = GeoJSON.Feature<GeoJSON.Point, { id: string; type: FacilityKey }>;

/** Points of the clustered layer; the map looks the facility up by `id` when one is clicked. */
export function facilitiesGeoJSON(list: readonly Facility[]): GeoJSON.FeatureCollection<GeoJSON.Point, FacilityPoint["properties"]> {
  return {
    type: "FeatureCollection",
    features: list.map((f) => ({
      type: "Feature",
      id: f.id,
      geometry: { type: "Point", coordinates: [f.lon, f.lat] },
      properties: { id: f.id, type: f.type },
    })),
  };
}
