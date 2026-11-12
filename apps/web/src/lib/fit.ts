/**
 * The search result in plain words (pure, unit tested): POST /api/v1/search (CORE-003, method
 * fit-0.1, D-215). The web never recomputes the fit: it joins the API's figures to the map, the
 * list and the zone card, with the copy of pitch/textos_web.md (zona.*, rc.*, leyenda.*).
 */
import type { RankedZone, RealityCheck, Relaxation, SearchResult, ZoneMatch, ZoneRef } from "@/contracts/search_response";

import type { ZoneCollection, ZoneGeometry, ZoneProperties } from "./map/zones";

/** How a zone is painted after a search: by its % when it meets everything, otherwise apart. */
export type FitClass = "ENCAJA" | "NO_CUMPLE" | "SIN_DATOS";

/**
 * `match_pct: null` is unknown, never 0 (some condition could not be checked). A zone that fails
 * a condition keeps its % to compare, but it is not one of the zones that fit.
 */
export function fitClass(zone: Pick<ZoneMatch, "match_pct" | "passes_all">): FitClass {
  if (zone.match_pct == null) return "SIN_DATOS";
  return zone.passes_all ? "ENCAJA" : "NO_CUMPLE";
}

/** The map's key for a zone of the API (`zone_key` of lib/map/zones.ts). */
export function zoneKeyOf(zone: Pick<ZoneRef, "level" | "code">): string {
  return `${zone.level}/${zone.code}`;
}

/** Ends of the violet ramp of the map and its legend, in % of fit (lower values take the low end). */
export const FIT_RAMP = { low: 60, high: 100 } as const;

export type FitProperties = ZoneProperties & { fit?: FitClass; fit_pct?: number };
export type FitCollection = GeoJSON.FeatureCollection<ZoneGeometry, FitProperties>;

/** The zones of the map with their class in `fit` and, when known, their % in `fit_pct`. */
export function paintFit(zones: ZoneCollection, allZones: readonly ZoneMatch[]): FitCollection {
  const byKey = new Map(allZones.map((z) => [zoneKeyOf(z.zone), z]));
  return {
    ...zones,
    features: zones.features.map((f) => {
      const match = byKey.get(f.properties.zone_key);
      if (!match) return f;
      const pct = match.match_pct;
      return { ...f, properties: { ...f.properties, fit: fitClass(match), ...(pct == null ? {} : { fit_pct: pct }) } };
    }),
  };
}

export type FitCounts = Record<FitClass, number> & { pending: number };

/** How many zones of the map fall in each class; a zone the search did not carry is `pending`. */
export function countFit(painted: FitCollection): FitCounts {
  const counts: FitCounts = { ENCAJA: 0, NO_CUMPLE: 0, SIN_DATOS: 0, pending: 0 };
  for (const f of painted.features) counts[f.properties.fit ?? "pending"] += 1;
  return counts;
}

/** What the result says about one zone of the map: its match and, when listed, its ranked entry. */
export interface ZoneFit {
  match: ZoneMatch | null;
  ranked: RankedZone | null;
}

export function zoneFit(result: SearchResult, zoneKey: string): ZoneFit {
  const same = (z: { zone: ZoneRef }) => zoneKeyOf(z.zone) === zoneKey;
  return {
    match: result.all_zones.find(same) ?? null,
    ranked: result.results.find(same) ?? result.near_misses?.find(same) ?? null,
  };
}

/** Plain-language name of each condition of the search («Colegio con primaria a 10 min andando como mucho»). */
export function constraintLabels(result: SearchResult): Map<string, string> {
  const ranked = [...result.results, ...(result.near_misses ?? [])];
  return new Map(ranked.flatMap((z) => z.constraints.map((c) => [c.constraint_id, c.label] as const)));
}

/** The conditions a zone fails, by name; unnamed ones are left out. */
export function failedLabels(failed: readonly string[] | undefined, labels: ReadonlyMap<string, string>): string[] {
  return (failed ?? []).flatMap((id) => {
    const label = labels.get(id);
    return label ? [label] : [];
  });
}

/** Options of «¿Y si cambias algo?» that add zones, in the API order (most zones first). */
export function relaxOptions(rc: RealityCheck): Relaxation[] {
  return rc.relaxations.filter((r) => r.added_zones > 0);
}

/** With this many zones or fewer, «¿Y si cambias algo?» opens unfolded (the brief: «pocas o ninguna»). */
export const FEW_ZONES = 5;

export function fewZones(rc: Pick<RealityCheck, "zones_passing">): boolean {
  return rc.zones_passing <= FEW_ZONES;
}

export function zonesText(n: number): string {
  return n === 1 ? "1 zona" : `${n} zonas`;
}

/**
 * rc.ninguna, rc.una, rc.varias; after applying an option of «¿Y si cambias algo?» it is no longer
 * the search «tal cual»: «Con este cambio…» (rc.cambio).
 */
export function passingText(n: number, changed = false): string {
  const start = changed ? "Con este cambio" : "Con tu búsqueda tal cual";
  if (n === 0) return `${start} no sale ninguna zona.`;
  if (n === 1) return `${start} sale 1 zona.`;
  return `${start} salen ${n} zonas.`;
}

/** rc.sin_dato: zones with some condition that could not be checked are never counted as good. */
export function unknownText(n: number): string {
  const them = n === 1 ? "No la contamos como buena." : "No las contamos como buenas.";
  return `En ${zonesText(n)} no podemos comprobarlo todo por falta de datos. ${them}`;
}

/** One option of «¿Y si cambias algo?» (rc.opcion.cuenta): what it changes, how many zones there would be and how many more. */
export function optionText(r: Pick<Relaxation, "label" | "zones_if_relaxed" | "added_zones">): { label: string; count: string } {
  const would = r.zones_if_relaxed === 1 ? "saldría" : "saldrían";
  return { label: r.label, count: `${would} ${zonesText(r.zones_if_relaxed)}, ${r.added_zones} más` };
}

/** zona.puesto */
export function rankText(rank: number): string {
  return `La ${rank}.ª que más encaja`;
}

/**
 * a_pie.mediana: the walking minutes of the facts («Colegio con primaria a unos 9 min andando»)
 * are the median of the zone, said once under them, when one of them is a walk.
 */
export const WALK_MEDIAN = "Los minutos andando son los de la mitad de la zona: unos vecinos lo tienen más cerca y otros más lejos.";

export function hasWalkingFact(facts: readonly { text: string }[]): boolean {
  return facts.some((fact) => fact.text.includes("andando"));
}
