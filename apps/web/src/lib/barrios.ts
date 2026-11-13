/**
 * The barrios of a district that fit the search (pure, unit tested): POST /api/v1/search/barrios
 * (D-232, fit-0.7), the same engine as POST /search with barrios as zones. The web never recomputes
 * the fit: it picks what the district screen shows, with the copy of pitch/textos_web.md.
 */
import type { BarrioSearchResult, RankedZone, RealityCheck } from "@/contracts/barrio_search_response";
import { constraintLabels, failedLabels, hasWalkingFact } from "@/lib/fit";

/** Facts under each barrio: the API orders them, most important to the person first. */
export const FACTS_PER_BARRIO = 2;

/** Barrios in view before «Ver los {n} barrios». */
export const FIRST_BARRIOS = 3;

export interface BarrioRow {
  /** geo_admin_unit id, the same as its outline in /geo/admin-units?level=barrio (null: none to show) */
  id: string | null;
  code: string;
  name: string;
  pct: number;
  facts: string[];
  /** Whether one of the facts is a walk (minutes on foot), to say once what those minutes are */
  walking: boolean;
  /** Near misses only: the conditions it fails, by name (zona.cerca_de_encajar.motivo) */
  fails: string[] | null;
}

function barrioRow(zone: RankedZone, fails: string[] | null): BarrioRow {
  const facts = zone.facts.slice(0, FACTS_PER_BARRIO);
  return {
    id: zone.zone.admin_unit_id ?? null,
    code: zone.zone.code,
    name: zone.zone.name,
    pct: zone.match_pct,
    facts: facts.map((fact) => fact.text),
    walking: hasWalkingFact(facts),
    fails,
  };
}

/** The barrios that fit, best first, and those that fail one condition, with it by name. */
export function barrioRows(result: Pick<BarrioSearchResult, "results" | "near_misses">): { fits: BarrioRow[]; near: BarrioRow[] } {
  const labels = constraintLabels(result);
  return {
    fits: result.results.map((zone) => barrioRow(zone, null)),
    near: (result.near_misses ?? []).map((zone) => barrioRow(zone, failedLabels(zone.failed_constraints, labels))),
  };
}

/** «7 de sus 8 barrios encajan con tu búsqueda.» (barrios.encajan.resumen, B's draft for line D) */
export function barriosText(rc: Pick<RealityCheck, "zones_passing" | "zones_evaluated">): string {
  const { zones_passing: n, zones_evaluated: total } = rc;
  if (n === 0) return `Ninguno de sus ${total} barrios cumple todo lo que pides.`;
  if (n === total) return n === 1 ? "Su barrio encaja con tu búsqueda." : `Sus ${total} barrios encajan con tu búsqueda.`;
  return `${n} de sus ${total} barrios ${n === 1 ? "encaja" : "encajan"} con tu búsqueda.`;
}
