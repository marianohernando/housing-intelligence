/**
 * What a near miss lacks, in plain words (pure, unit tested): «Casi valen» no longer shows a %
 * (F5 of fit-0.9): it says how far the zone is from what the person asks, from the API's own
 * figures for the condition it fails (`ConstraintCheck.value` against `threshold`). Without them,
 * the condition by name, as before: a figure is never made up. «unos», not «≈» (UX mobile audit, §4).
 * `many`: a household of more than one (speaksToMany), told «vuestro presupuesto», «lo que pedís».
 */
import type { ConstraintCheck, RankedZone, ScenarioState } from "@/contracts/search_response";

import { type Voice, voice } from "./fit";
import { formatEuros } from "./format";

type Check = Pick<ConstraintCheck, "constraint_id" | "label" | "status" | "value" | "threshold" | "unit">;

/** One line, as seen and as read aloud (the same words since «≈» became «unos»). */
export interface Spoken {
  text: string;
  aria: string;
  /** Said by its name only («No cumple: {condición}»): the API gave no figures to tell what is missing */
  label?: string;
}

/** Above this many minutes the API says «más de 2 h» (MAX_COMMUTE_SHOWN of hi_domain/fit.py). */
const MAX_COMMUTE_SHOWN = 120;

/** Above this many minutes on foot the API gives no minutes, it is not a walk (MAX_WALK_SHOWN of hi_domain/fit.py). */
const MAX_WALK_SHOWN = 60;

/** «unos 11.000 €» buying and «unos 120 € al mes» renting: the excess rounded so the «unos» is honest. */
const EURO_STEP = { "€": 1_000, "€/mes": 10 } as const;

function excess(check: Check): number | null {
  const { value, threshold } = check;
  if (check.status !== "FAIL" || typeof value !== "number" || !Number.isFinite(value) || threshold == null || value <= threshold) return null;
  return value - threshold;
}

function roundTo(amount: number, step: number): number {
  return amount >= step ? Math.round(amount / step) * step : Math.max(1, Math.round(amount));
}

/** resultados.casi.presupuesto: «Se pasa unos 11.000 € de tu presupuesto» or «… unos 120 € al mes …». */
function overBudget(check: Check, v: Voice): Spoken | null {
  const over = excess(check);
  const unit = check.unit === "€" || check.unit === "€/mes" ? check.unit : null;
  if (over === null || unit === null) return null;
  const amount = formatEuros(roundTo(over, EURO_STEP[unit]));
  const text = `Se pasa unos ${amount}${unit === "€/mes" ? " al mes" : ""} de ${v.presupuesto}`;
  return { text, aria: text };
}

/**
 * «unos 12 min», «1 min» (one minute is no estimate to round: never «unos 1 min», as walkMinutesText
 * of lib/gaps.ts), or «menos de 1 min» for a few seconds over (45,2 against 45 is not 0 min).
 */
function minutesOver(over: number): { text: string; aria: string } {
  const minutes = Math.round(over);
  const text = minutes < 1 ? "menos de 1 min" : minutes === 1 ? "1 min" : `unos ${minutes} min`;
  return { text, aria: text };
}

/**
 * resultados.casi.trayecto: «Tarda unos 12 min más de lo que pides», and the place when the search
 * has more than one with a limit («… hasta Getafe Central (Cercanías)»). Above 2 h the API gives
 * no minutes: «Tarda más de 2 h; pides 45 min como mucho».
 */
function tooLong(check: Check, scenario: Pick<ScenarioState, "anchors"> | undefined, v: Voice): Spoken | null {
  const over = excess(check);
  if (over === null) return null;
  const anchors = scenario?.anchors ?? [];
  const place = anchors[Number(check.constraint_id.slice("commute:".length))];
  const limited = anchors.filter((a) => a.max_minutes != null).length;
  const where = limited > 1 && place ? ` hasta ${place.label}` : "";
  if ((check.value as number) > MAX_COMMUTE_SHOWN) {
    const text = `Tarda más de 2 h${where}; ${v.pides} ${check.threshold} min como mucho`;
    return { text, aria: text };
  }
  const more = minutesOver(over);
  return { text: `Tarda ${more.text} más de lo que ${v.pides}${where}`, aria: `Tarda ${more.aria} más de lo que ${v.pides}${where}` };
}

/** «Colegio con primaria a 10 min andando como mucho» -> «Colegio con primaria» (the API's label of `near:*`). */
const WALK_LABEL = /^(.+) a \d+ min andando como mucho$/;

/**
 * resultados.casi.a_pie: «Escuela infantil: unos 5 min más andando de lo que pides». Beyond an hour on
 * foot, which is no walk, the minutes are not said: «Colegio con primaria a más de 1 h andando;
 * pides 10 min como mucho».
 */
function tooFar(check: Check, v: Voice): Spoken | null {
  const over = excess(check);
  const service = WALK_LABEL.exec(check.label)?.[1];
  if (over === null || check.unit !== "min" || !service) return null;
  if ((check.value as number) > MAX_WALK_SHOWN) {
    const text = `${service} a más de 1 h andando; ${v.pides} ${check.threshold} min como mucho`;
    return { text, aria: text };
  }
  const more = minutesOver(over);
  return { text: `${service}: ${more.text} más andando de lo que ${v.pides}`, aria: `${service}: ${more.aria} más andando de lo que ${v.pides}` };
}

/** As before (zona.cerca_de_encajar.motivo): «No cumple: {condición}». */
function byName(label: string): Spoken {
  return { text: `No cumple: ${label}`, aria: `No cumple: ${label}`, label };
}

/** One failed condition in plain words; by its name when the API gives no figures to tell it. */
export function shortfallOf(check: Check, scenario?: Pick<ScenarioState, "anchors">, many = false): Spoken {
  const id = check.constraint_id;
  const v = voice(many);
  const said = id === "budget" ? overBudget(check, v) : id.startsWith("commute:") ? tooLong(check, scenario, v) : tooFar(check, v);
  return said ?? byName(check.label);
}

/** zona.no_cumple, when the API names no condition: «No cumple todo lo que pides.» / «… pedís.» */
export function failsUnnamedText(many = false): string {
  return `No cumple todo lo que ${voice(many).pides}.`;
}

/** A zone's failed conditions, with its own checks when it has them (a near miss, not every zone of the map). */
type Failing = Pick<RankedZone, "failed_constraints"> & { constraints?: readonly Check[] };

/**
 * Every condition a zone fails, in the API order, in plain words. A zone without its own checks
 * (one of the map that is not a near miss) says them by name, from the labels of the search
 * (`constraintLabels`); one the search does not name is left out. Empty: failsUnnamedText.
 */
export function shortfalls(
  zone: Failing,
  labels: ReadonlyMap<string, string> = new Map(),
  scenario?: Pick<ScenarioState, "anchors">,
  many = false,
): Spoken[] {
  return (zone.failed_constraints ?? []).flatMap((id) => {
    const own = zone.constraints?.find((c) => c.constraint_id === id);
    if (own) return [shortfallOf(own, scenario, many)];
    const label = labels.get(id);
    return label ? [byName(label)] : [];
  });
}

/**
 * Every condition of the zone card in one line, separated by « · »: those with figures first, then
 * those said by name under a single «No cumple:» («No cumple: A · B»). Null without any.
 */
export function joinShortfalls(list: readonly Spoken[]): Spoken | null {
  if (list.length === 0) return null;
  const told = list.filter((s) => s.label === undefined);
  const named = list.flatMap((s) => (s.label === undefined ? [] : [s.label]));
  const tail = named.length > 0 ? [`No cumple: ${named.join(" · ")}`] : [];
  return {
    text: [...told.map((s) => s.text), ...tail].join(" · "),
    aria: [...told.map((s) => s.aria), ...tail].join(". "),
  };
}

/**
 * The line of a near miss in «Casi valen»: what it lacks in the first condition it fails (the
 * API's order: budget, services, trips) and, if it fails more, «y otra condición» or «y 2
 * condiciones más» (resultados.casi.varias).
 */
export function nearMissText(zone: Failing, labels?: ReadonlyMap<string, string>, scenario?: Pick<ScenarioState, "anchors">, many = false): Spoken {
  const [first, ...rest] = shortfalls(zone, labels, scenario, many);
  if (!first) {
    const unnamed = failsUnnamedText(many);
    return { text: unnamed, aria: unnamed };
  }
  const more = rest.length === 0 ? "" : rest.length === 1 ? " y otra condición" : ` y ${rest.length} condiciones más`;
  return { text: `${first.text}${more}`, aria: `${first.aria}${more}` };
}
