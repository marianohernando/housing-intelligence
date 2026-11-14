/**
 * The single ScenarioState of the search (CLAUDE.md §13: chips, filters and map share one
 * state). Pure helpers, unit tested; the shape is the generated contract type.
 */
import type { Anchor, BudgetKind, NearbyNeed, NeedKey, PriorityKey, ScenarioState } from "@/contracts/scenario_state";

/** Slider ranges, inside the contract ranges (RENT_RANGE_EUR, BUY_RANGE_EUR). */
export const BUDGET_RANGE: Record<BudgetKind, { min: number; max: number; step: number; initial: number }> = {
  rent: { min: 300, max: 5_000, step: 50, initial: 1_200 },
  buy: { min: 50_000, max: 2_000_000, step: 10_000, initial: 300_000 },
};

const LIMITS = { minors: 8, seniors: 4 } as const;
const PRIORITY_KEYS: readonly PriorityKey[] = ["transporte", "salud", "colegios", "zonas_verdes", "seguridad", "sin_escaleras"];

export function defaultScenario(): ScenarioState {
  return {
    schema_version: 2,
    budget: { kind: "rent", amount_eur: BUDGET_RANGE.rent.initial },
    household: { adults: 1, minors: 0, minor_ages: [], seniors_in_care: 0 },
    anchors: [],
    nearby: [],
    priorities: [],
  };
}

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

function household(s: ScenarioState) {
  return { adults: 1, minors: 0, minor_ages: [], seniors_in_care: 0, ...s.household };
}

export function peopleAtHome(s: ScenarioState): number {
  const h = household(s);
  return h.adults + h.minors + h.seniors_in_care;
}

export function setAdults(s: ScenarioState, adults: 1 | 2): ScenarioState {
  return { ...s, household: { ...household(s), adults } };
}

export function setMinors(s: ScenarioState, minors: number): ScenarioState {
  // Ages must list every child or be empty: a new count forgets the old ages.
  return { ...s, household: { ...household(s), minors: clamp(Math.round(minors), 0, LIMITS.minors), minor_ages: [] } };
}

export function setSeniors(s: ScenarioState, seniors: number): ScenarioState {
  return { ...s, household: { ...household(s), seniors_in_care: clamp(Math.round(seniors), 0, LIMITS.seniors) } };
}

/** Marks or unmarks a priority; the order of marking is the order of importance. */
export function togglePriority(s: ScenarioState, key: PriorityKey): ScenarioState {
  const current = s.priorities ?? [];
  const priorities = current.includes(key) ? current.filter((p) => p !== key) : [...current, key];
  return { ...s, priorities };
}

export function setBudgetKind(s: ScenarioState, kind: BudgetKind): ScenarioState {
  if (s.budget?.kind === kind) return s;
  return { ...s, budget: { kind, amount_eur: BUDGET_RANGE[kind].initial } };
}

export function setBudgetAmount(s: ScenarioState, amount: number): ScenarioState {
  const kind = s.budget?.kind ?? "rent";
  const { min, max, step } = BUDGET_RANGE[kind];
  return { ...s, budget: { kind, amount_eur: clamp(Math.round(amount / step) * step, min, max) } };
}

/** presupuesto.sin_limite (`budget: null`); turned off, the budget starts again as renting. */
export function setNoBudgetLimit(s: ScenarioState, noLimit: boolean): ScenarioState {
  if (noLimit) return { ...s, budget: null };
  return s.budget ? s : { ...s, budget: { kind: "rent", amount_eur: BUDGET_RANGE.rent.initial } };
}

/** «Lo quiero a un paseo» (cerca.*): services the household wants within walking minutes. */
export const NEED_KEYS: readonly NeedKey[] = ["escuela_infantil", "colegio", "centro_salud", "farmacia", "mayores", "transporte"];
const WALK_LIMITS = { min: 1, max: 60, initial: 10 } as const;
/** Contract range of a work commute (Anchor.max_minutes). */
const COMMUTE_LIMITS = { min: 5, max: 120 } as const;
/** Minutes offered in the selector; a value from the API outside them is offered too. */
export const WALK_MINUTES: readonly number[] = [5, 10, 15, 20, 30];

export function walkMinutesOptions(current: number | undefined): number[] {
  const all = new Set([...WALK_MINUTES, ...(current === undefined ? [] : [current])]);
  return [...all].sort((a, b) => a - b);
}

/** A new service starts at 10 min and as a must («Imprescindible»), the contract defaults. */
export function addNearby(s: ScenarioState, need: NeedKey): ScenarioState {
  const nearby = s.nearby ?? [];
  if (nearby.some((n) => n.need === need)) return s;
  return { ...s, nearby: [...nearby, { need, max_walk_minutes: WALK_LIMITS.initial, required: true }] };
}

export function removeNearby(s: ScenarioState, need: NeedKey): ScenarioState {
  return { ...s, nearby: (s.nearby ?? []).filter((n) => n.need !== need) };
}

function changeNearby(s: ScenarioState, need: NeedKey, change: (n: NearbyNeed) => NearbyNeed): ScenarioState {
  return { ...s, nearby: (s.nearby ?? []).map((n) => (n.need === need ? change(n) : n)) };
}

export function setNearbyMinutes(s: ScenarioState, need: NeedKey, minutes: number): ScenarioState {
  const max_walk_minutes = clamp(Math.round(minutes), WALK_LIMITS.min, WALK_LIMITS.max);
  return changeNearby(s, need, (n) => ({ ...n, max_walk_minutes }));
}

export function setNearbyRequired(s: ScenarioState, need: NeedKey, required: boolean): ScenarioState {
  return changeNearby(s, need, (n) => ({ ...n, required }));
}

/** A place picked for «Trabajo en» or «Cerca de mi familia o amigos»: a name and a point. */
export interface Place {
  label: string;
  lat: number;
  lon: number;
}

/** The places the search asks for: where the person works and, optionally, where family or friends live. */
export type PlaceKind = "work" | "family";

/** Their order in `anchors`: the earlier a place, the more its trip weighs in the fit (the work place first). */
const PLACE_KINDS: readonly PlaceKind[] = ["work", "family"];
const kindOf = (a: Anchor) => a.kind ?? "work";
/** Position of a place in `anchors`; kinds the web does not edit (from a shared link) go last. */
const placeOrder = (a: Anchor) => (PLACE_KINDS as readonly string[]).indexOf(kindOf(a)) + 1 || PLACE_KINDS.length + 1;
const LABEL_MAX = 80;

/** The place of a kind, if the search has one. */
export function placeOf(s: ScenarioState, kind: PlaceKind): Anchor | null {
  return (s.anchors ?? []).find((a) => kindOf(a) === kind) ?? null;
}

function changePlace(s: ScenarioState, kind: PlaceKind, change: (a: Anchor) => Anchor): ScenarioState {
  return { ...s, anchors: (s.anchors ?? []).map((a) => (kindOf(a) === kind ? change(a) : a)) };
}

/**
 * Sets (or with null, removes) the place of a kind. It goes without a minutes limit (`max_minutes:
 * null`, «Sin límite») until the person picks one in «Tardar como mucho». The zone card says how far
 * each zone is either way, except for a work place with «Teletrabajo total» and no limit: that trip
 * neither scores nor limits, so it is not shown (D-240).
 */
export function setPlace(s: ScenarioState, kind: PlaceKind, place: Place | null): ScenarioState {
  const kept = (s.anchors ?? []).filter((a) => kindOf(a) !== kind);
  const picked: Anchor[] = place ? [{ kind, label: place.label.slice(0, LABEL_MAX), lat: place.lat, lon: place.lon, max_minutes: null }] : [];
  return { ...s, anchors: [...picked, ...kept].sort((a, b) => placeOrder(a) - placeOrder(b)) };
}

/** Minutes offered in «Tardar como mucho» (trabajo.max_min); a value from a shared link outside them is offered too. */
export const COMMUTE_MINUTES: readonly number[] = [30, 45, 60, 90];

export function commuteMinutesOptions(current: number | null | undefined): number[] {
  const all = new Set([...COMMUTE_MINUTES, ...(current == null ? [] : [current])]);
  return [...all].sort((a, b) => a - b);
}

/** The trip limit of a place; null is «Sin límite». Without the place there is nothing to limit. */
export function setPlaceMaxMinutes(s: ScenarioState, kind: PlaceKind, minutes: number | null): ScenarioState {
  const max_minutes = minutes === null ? null : clamp(Math.round(minutes), COMMUTE_LIMITS.min, COMMUTE_LIMITS.max);
  return changePlace(s, kind, (a) => ({ ...a, max_minutes }));
}

/** «Trabajo en», if the search has one. */
export const workPlace = (s: ScenarioState) => placeOf(s, "work");
export const setWorkPlace = (s: ScenarioState, place: Place | null) => setPlace(s, "work", place);
export const setWorkMaxMinutes = (s: ScenarioState, minutes: number | null) => setPlaceMaxMinutes(s, "work", minutes);

/** Days offered in «¿Cuántos días vas a la oficina?» (trabajo.dias); 0 is «Teletrabajo total». */
export const OFFICE_DAYS: readonly number[] = [5, 4, 3, 2, 1, 0];
/** Up to this many days a week the trip to work weighs half in the fit (FEW_DAYS_PER_WEEK of hi_domain/fit.py, D-240). */
export const FEW_OFFICE_DAYS = 2;
const DAYS_LIMITS = { min: 0, max: 7, usual: 5 } as const;

/** Days a week the person goes to the work place; the contract default (5) until they say otherwise. */
export function officeDays(anchor: Anchor): number {
  return anchor.days_per_week ?? DAYS_LIMITS.usual;
}

/** The days offered, most first; a value from a shared link outside them (6 or 7) is offered too. */
export function officeDaysOptions(current: number): number[] {
  return [...new Set([...OFFICE_DAYS, current])].sort((a, b) => b - a);
}

/**
 * Days a week at the work place (`days_per_week`, D-240). The limit stays as it was: with 0
 * («Teletrabajo total») the trip is not scored, but a limit the person set still applies.
 */
export function setWorkDays(s: ScenarioState, days: number): ScenarioState {
  const days_per_week = clamp(Math.round(days), DAYS_LIMITS.min, DAYS_LIMITS.max);
  return changePlace(s, "work", (a) => ({ ...a, days_per_week }));
}

/**
 * The demo case (portada.ejemplo.boton): a couple with 2 children who work on the Castellana.
 * Same as line A's golden profile (data/fixtures/contracts/scenario_state.familia_castellana.fixture.json),
 * checked by a test, with the work place without a limit (`max_minutes: null`): its figures are the pitch's.
 */
export function exampleScenario(): ScenarioState {
  return {
    schema_version: 2,
    budget: { kind: "rent", amount_eur: 1500 },
    min_floor_area_m2: null,
    household: { adults: 2, minors: 2, minor_ages: [4, 8], seniors_in_care: 0 },
    anchors: [{ kind: "work", label: "Paseo de la Castellana (Azca)", lon: -3.693, lat: 40.45, days_per_week: 4, max_minutes: null }],
    nearby: [{ need: "colegio", max_walk_minutes: 10, required: true }],
    priorities: ["colegios", "transporte", "salud"],
  };
}

function toBase64Url(text: string): string {
  let binary = "";
  for (const byte of new TextEncoder().encode(text)) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(text: string): string {
  const binary = atob(text.replace(/-/g, "+").replace(/_/g, "/"));
  return new TextDecoder().decode(Uint8Array.from(binary, (c) => c.charCodeAt(0)));
}

export function encodeScenario(s: ScenarioState): string {
  return toBase64Url(JSON.stringify(s));
}

function isScenario(value: unknown): value is ScenarioState {
  if (typeof value !== "object" || value === null) return false;
  const s = value as ScenarioState;
  const h = s.household;
  return (
    s.schema_version === 2 &&
    (h === undefined || (Number.isInteger(h.adults) && Number.isInteger(h.minors ?? 0))) &&
    (s.priorities ?? []).every((p) => PRIORITY_KEYS.includes(p)) &&
    (s.budget == null || ((s.budget.kind === "rent" || s.budget.kind === "buy") && Number.isFinite(s.budget.amount_eur)))
  );
}

/** The scenario in a shared link, or null if the text is not a valid one (the API validates again). */
export function decodeScenario(text: string): ScenarioState | null {
  try {
    const value: unknown = JSON.parse(fromBase64Url(text));
    return isScenario(value) ? value : null;
  } catch {
    return null;
  }
}
