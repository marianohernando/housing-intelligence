/**
 * What the map asks the API for, once per visit: the outlines, a district's barrios and a zone's
 * places are shared by every screen and kept when leaving the map for another tab and coming back
 * (incident EMAXCONNSESSION, 12 nov: each request can hold a database connection).
 */
import { createApi, type PlaceCategory } from "@/lib/api";
import type { PlaceFeature } from "@/lib/map/places";
import { zonePlaceQueries } from "@/lib/map/zonePlaces";
import { type AdminFeature, buildZoneCollection, MUNICIPIOS_BY_DISTRITO, type ZoneCollection } from "@/lib/map/zones";
import { once } from "@/lib/once";

/** Simplification of the outlines: municipios are seen from far, districts and barrios up close. */
export const SIMPLIFY_M = { municipio: 50, distrito: 25, barrio: 10 } as const;

const zones = new Map<string, Promise<ZoneCollection>>();
const barrios = new Map<string, Promise<AdminFeature[]>>();
const places = new Map<string, Promise<PlaceFeature[]>>();

/** The zones of the map (D-200): every municipio, with Madrid capital by its districts. */
export function fetchZones(): Promise<ZoneCollection> {
  return once(zones, "zones", async () => {
    const api = createApi();
    const [municipios, ...distritos] = await Promise.all([
      api.adminUnits("municipio", SIMPLIFY_M.municipio),
      ...MUNICIPIOS_BY_DISTRITO.map((parent) => api.adminUnits("distrito", SIMPLIFY_M.distrito, parent)),
    ]);
    return buildZoneCollection(
      municipios.data.features,
      distritos.flatMap((d) => d.data.features),
    );
  });
}

/** The barrios of a district, for the «Barrios de la zona» bar. */
export function fetchBarrios(districtId: string): Promise<AdminFeature[]> {
  return once(barrios, districtId, async () => (await createApi().adminUnits("barrio", SIMPLIFY_M.barrio, districtId)).data.features);
}

/**
 * A zone's places of some categories, for «Todos los centros» and the key points: one request per
 * zone with every category and subcategory both need (/places takes several categories since
 * 12 nov), shared by both; each keeps the categories it asks for and filters out what it does not show.
 */
export async function fetchZonePlaces(adminUnitId: string, categories: readonly PlaceCategory[]): Promise<PlaceFeature[]> {
  const queries = zonePlaceQueries();
  // Never a whole layer: a category the zone screen does not use has nothing to ask for
  const unknown = categories.find((category) => !queries.has(category));
  if (unknown) throw new Error(`The zone screen does not ask for ${unknown}`);
  const all = await once(places, adminUnitId, () =>
    createApi().places({ category: [...queries.keys()], adminUnitId, subcategories: [...queries.values()].flat() }),
  );
  return all.filter((place) => categories.includes(place.properties.category));
}
