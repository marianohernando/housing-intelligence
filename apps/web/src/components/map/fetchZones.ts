import { createApi } from "@/lib/api";
import { buildZoneCollection, MUNICIPIOS_BY_DISTRITO, type ZoneCollection } from "@/lib/map/zones";

/** Simplification of the outlines: municipios are seen from far, districts and barrios up close. */
export const SIMPLIFY_M = { municipio: 50, distrito: 25, barrio: 10 } as const;

/** The zones of the map (D-200): every municipio, with Madrid capital by its districts. */
export async function fetchZones(api = createApi()): Promise<ZoneCollection> {
  const [municipios, ...distritos] = await Promise.all([
    api.adminUnits("municipio", SIMPLIFY_M.municipio),
    ...MUNICIPIOS_BY_DISTRITO.map((parent) => api.adminUnits("distrito", SIMPLIFY_M.distrito, parent)),
  ]);
  return buildZoneCollection(
    municipios.data.features,
    distritos.flatMap((d) => d.data.features),
  );
}
