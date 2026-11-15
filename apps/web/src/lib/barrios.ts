/**
 * The barrios of a district that fit the search (pure, unit tested): POST /api/v1/search/barrios
 * (D-232, fit-0.7), the same engine as POST /search with barrios as zones. The web never recomputes
 * the fit: it picks what the district screen shows, with the copy of pitch/textos_web.md.
 */
import type { BarrioSearchResult, RankedZone, RealityCheck } from "@/contracts/barrio_search_response";
import { constraintLabels, factText, floorAreaOf, hasWalkingFact, type ZonePrice, zonePrice } from "@/lib/fit";
import { type MatchText, matchText } from "@/lib/match";
import { nearMissText, type Spoken } from "@/lib/shortfall";

/** Facts under each barrio: the API orders them, most important to the person first. */
export const FACTS_PER_BARRIO = 2;

/** Barrios in view before «Ver los {n} barrios». */
export const FIRST_BARRIOS = 3;

export interface BarrioRow {
  /** geo_admin_unit id, the same as its outline in /geo/admin-units?level=barrio (null: none to show) */
  id: string | null;
  code: string;
  name: string;
  /** A barrio that fits: «Encaja muy bien» and «94 %» (F5 of fit-0.9); null for a near miss, which shows what it lacks */
  fit: MatchText | null;
  /** Its approximate price for the household (D-234), or null without one */
  price: ZonePrice | null;
  facts: string[];
  /** Whether one of the facts is a walk (minutes on foot), to say once what those minutes are */
  walking: boolean;
  /** Near misses only: what it lacks, as in «Casi encajan» of the list (resultados.casi.*) */
  lacks: Spoken | null;
}

function barrioRow(zone: RankedZone, lacks: Spoken | null, buying: boolean, m2: number | null): BarrioRow {
  const facts = zone.facts.slice(0, FACTS_PER_BARRIO);
  return {
    id: zone.zone.admin_unit_id ?? null,
    code: zone.zone.code,
    name: zone.zone.name,
    fit: lacks ? null : matchText(zone),
    price: zonePrice(zone, buying, m2),
    facts: facts.map((fact) => factText(fact, buying)),
    walking: hasWalkingFact(facts),
    lacks,
  };
}

/** The barrios that fit, best first, and those that fail one condition, with what they lack. */
export function barrioRows(
  result: Pick<BarrioSearchResult, "results" | "near_misses"> & Partial<Pick<BarrioSearchResult, "scenario">>,
): { fits: BarrioRow[]; near: BarrioRow[] } {
  const labels = constraintLabels(result);
  const buying = result.scenario?.budget?.kind === "buy";
  const m2 = floorAreaOf(result);
  return {
    fits: result.results.map((zone) => barrioRow(zone, null, buying, m2)),
    near: (result.near_misses ?? []).map((zone) => barrioRow(zone, nearMissText(zone, labels, result.scenario), buying, m2)),
  };
}

/** «7 de sus 8 barrios encajan con tu búsqueda.» (barrios.encajan.resumen, B's draft for line D) */
export function barriosText(rc: Pick<RealityCheck, "zones_passing" | "zones_evaluated">): string {
  const { zones_passing: n, zones_evaluated: total } = rc;
  if (n === 0) return `Ninguno de sus ${total} barrios cumple todo lo que pides.`;
  if (n === total) return n === 1 ? "Su barrio encaja con tu búsqueda." : `Sus ${total} barrios encajan con tu búsqueda.`;
  return `${n} de sus ${total} barrios ${n === 1 ? "encaja" : "encajan"} con tu búsqueda.`;
}
