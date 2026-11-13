/**
 * What the map asks the API for, once per visit: the outlines, a district's barrios and a zone's
 * places are shared by every screen and kept when leaving the map for another tab and coming back
 * (incident EMAXCONNSESSION, 12 nov: each request can hold a database connection).
 */
import { createApi, type PlaceCategory } from "@/lib/api";
import type { PlaceFeature } from "@/lib/map/places";
import { askedFor, zonePlaceQueries } from "@/lib/map/zonePlaces";
import { type AdminFeature, buildZoneCollection, MUNICIPIOS_BY_DISTRITO, type ZoneCollection } from "@/lib/map/zones";
import { once } from "@/lib/once";

/** Simplification of the outlines: municipios are seen from far, districts and barrios up close. */
export const SIMPLIFY_M = { municipio: 50, distrito: 25, barrio: 10 } as const;

/**
 * A request that hangs fails after this long: it frees its turn (lib/api.ts) and the screen offers
 * to retry or goes on without it (review of PR #19, M4). The outlines of the municipios are the
 * largest answer (about 340 KB, a few seconds on slow 4G), and a cold start of the API adds more.
 */
const TIMEOUT_MS = { outlines: 20_000, small: 15_000 } as const;

const zones = new Map<string, Promise<ZoneCollection>>();
const barrios = new Map<string, Promise<AdminFeature[]>>();
const places = new Map<string, Promise<PlaceFeature[]>>();

/** The zones of the map (D-200): every municipio, with Madrid capital by its districts. */
export function fetchZones(): Promise<ZoneCollection> {
  return once(zones, "zones", async () => {
    const api = createApi();
    const [municipios, ...distritos] = await Promise.all([
      api.adminUnits("municipio", SIMPLIFY_M.municipio, undefined, { timeoutMs: TIMEOUT_MS.outlines }),
      ...MUNICIPIOS_BY_DISTRITO.map((parent) => api.adminUnits("distrito", SIMPLIFY_M.distrito, parent, { timeoutMs: TIMEOUT_MS.outlines })),
    ]);
    return buildZoneCollection(
      municipios.data.features,
      distritos.flatMap((d) => d.data.features),
    );
  });
}

/** The barrios of a district, for the «Barrios de la zona» bar. */
export function fetchBarrios(districtId: string): Promise<AdminFeature[]> {
  return once(barrios, districtId, async () => {
    const body = await createApi().adminUnits("barrio", SIMPLIFY_M.barrio, districtId, { timeoutMs: TIMEOUT_MS.small });
    return body.data.features;
  });
}

/**
 * A zone's places of some categories, for «Todos los centros» and the key points: one request per
 * zone with every category and subcategory both need (/places takes several categories since
 * 12 nov), shared by both. Only the pairs of category and subcategory asked for are kept (askedFor),
 * and each side takes its own categories.
 */
export async function fetchZonePlaces(adminUnitId: string, categories: readonly PlaceCategory[]): Promise<PlaceFeature[]> {
  const queries = zonePlaceQueries();
  // Never a whole layer: a category the zone screen does not use has nothing to ask for
  const unknown = categories.find((category) => !queries.has(category));
  if (unknown) throw new Error(`The zone screen does not ask for ${unknown}`);
  const all = await once(places, adminUnitId, async () => {
    const query = { category: [...queries.keys()], adminUnitId, subcategories: [...queries.values()].flat() };
    const found = await createApi().places(query, { timeoutMs: TIMEOUT_MS.small });
    return found.filter((place) => askedFor(queries, place));
  });
  return all.filter((place) => categories.includes(place.properties.category));
}
