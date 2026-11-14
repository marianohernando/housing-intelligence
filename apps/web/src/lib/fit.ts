/**
 * The search result in plain words (pure, unit tested): POST /api/v1/search (CORE-003, method
 * fit-0.1, D-215). The web never recomputes the fit: it joins the API's figures to the map, the
 * list and the zone card, with the copy of pitch/textos_web.md (zona.*, rc.*, leyenda.*).
 */
import type { ConstraintCheck, RankedZone, RealityCheck, Relaxation, SearchResult, ZoneMatch, ZoneRef } from "@/contracts/search_response";

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

/**
 * Plain-language name of each condition of the search («Colegio con primaria a 10 min andando como
 * mucho»), from POST /search or POST /search/barrios.
 */
export function constraintLabels(result: Pick<SearchResult, "results" | "near_misses">): Map<string, string> {
  const ranked = [...result.results, ...(result.near_misses ?? [])];
  return new Map(ranked.flatMap((z) => z.constraints.map((c) => [c.constraint_id, c.label] as const)));
}

/** The API stops giving minutes above this (MAX_COMMUTE_SHOWN of hi_domain/fit.py). */
const MAX_COMMUTE_SHOWN = 120;

/**
 * How long a failing commute takes, as the API's own fact says it (rounded to the nearest minute,
 * «más de 2 h» above 120), except that it never reads as the limit itself: 45,2 against 45 is 46.
 */
export function commuteTakes(minutes: number, limit: number | null | undefined): string {
  if (minutes > MAX_COMMUTE_SHOWN) return "más de 2 h";
  const rounded = Math.round(minutes);
  return `${limit == null ? rounded : Math.max(rounded, limit + 1)} min`;
}

/**
 * The conditions a zone fails, by name; unnamed ones are left out. With the zone's own
 * `constraints`, a commute that is too long says how long it is (trabajo.tarda): «… de 45 min como
 * mucho (tardarías 52 min)».
 */
export function failedLabels(
  failed: readonly string[] | undefined,
  labels: ReadonlyMap<string, string>,
  constraints: readonly Pick<ConstraintCheck, "constraint_id" | "status" | "value" | "threshold">[] = [],
): string[] {
  return (failed ?? []).flatMap((id) => {
    const label = labels.get(id);
    if (!label) return [];
    const own = constraints.find((c) => c.constraint_id === id);
    const isCommute = id.startsWith("commute:") && own?.status === "FAIL" && typeof own.value === "number";
    return [isCommute ? `${label} (tardarías ${commuteTakes(own.value as number, own.threshold)})` : label];
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

/** More zones than this with the best % of the ranking and the web says so (resultados.empate, D-239). */
export const MANY_TIED = 10;

/** Zones that meet everything with the same shown % as the first of the ranking. */
export function tiedAtTop(result: Pick<SearchResult, "results" | "all_zones">): number {
  const best = result.results[0]?.match_pct;
  if (best === undefined) return 0;
  return result.all_zones.filter((z) => z.passes_all && z.match_pct === best).length;
}

/**
 * resultados.empate: with many zones tied at the top the order says little (the API breaks the
 * tie by the services at a walk, D-239), so the person is told how to tell them apart; null otherwise.
 */
export function tiedText(result: Pick<SearchResult, "results" | "all_zones">): string | null {
  const n = tiedAtTop(result);
  return n > MANY_TIED ? `Encajan ${n} zonas igual de bien: marca qué te importa o dónde trabajas para afinar el orden.` : null;
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

/** feature_id prefix of the indicators that are minutes on foot (min_a_pie_colegio, min_a_pie_transporte…) */
export const WALK_MINUTES_FEATURE_PREFIX = "min_a_pie_";

export function hasWalkingFact(facts: readonly { indicator?: { feature_id: string } | null }[]): boolean {
  return facts.some((fact) => fact.indicator?.feature_id.startsWith(WALK_MINUTES_FEATURE_PREFIX) === true);
}
