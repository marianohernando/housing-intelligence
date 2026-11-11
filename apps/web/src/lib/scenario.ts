/**
 * The single ScenarioState of the search (CLAUDE.md §13: chips, filters and map share one
 * state). Pure helpers, unit tested; the shape is the generated contract type.
 */
import type { BudgetKind, PriorityKey, ScenarioState } from "@/contracts/scenario_state";

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
