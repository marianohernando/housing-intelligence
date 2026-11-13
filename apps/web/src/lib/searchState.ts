/**
 * State of the search on screen (pure, unit tested): the scenario being edited, the search behind
 * the result and the attempt in flight. Only the answer to the latest attempt counts, and what an
 * attempt brings (its scenario, the «¿Y si cambias algo?» option applied) is confirmed only when
 * its answer arrives; a failed attempt can be retried as it was.
 */
import type { ScenarioState } from "@/contracts/scenario_state";
import type { SearchResult } from "@/contracts/search_response";

export type SearchStatus = "idle" | "loading" | "done" | "error";

/** An option of «¿Y si cambias algo?» behind a result, and the search to go back to. */
export interface Applied {
  label: string;
  previous: ScenarioState;
}

/** One search sent to the API: the scenario, and the option it applies (null: none). */
export interface Attempt {
  id: number;
  scenario: ScenarioState;
  applied: Applied | null;
  /** Scenario on screen before the attempt replaced it, put back if it fails. */
  before: ScenarioState;
}

export interface SearchState<E> {
  scenario: ScenarioState;
  /** The scenario behind `result`. */
  searched: ScenarioState | null;
  status: SearchStatus;
  result: SearchResult | null;
  error: E | null;
  /** The option behind `result`, confirmed with it. */
  applied: Applied | null;
  /** The latest attempt: in flight, or failed and ready to retry. */
  attempt: Attempt | null;
}

export type SearchAction<E> =
  | { type: "edit"; change: (s: ScenarioState) => ScenarioState }
  | { type: "start"; attempt: Attempt }
  | { type: "done"; id: number; result: SearchResult }
  | { type: "fail"; id: number; error: E };

export function initialSearchState<E>(scenario: ScenarioState): SearchState<E> {
  return { scenario, searched: null, status: "idle", result: null, error: null, applied: null, attempt: null };
}

export function searchReducer<E>(state: SearchState<E>, action: SearchAction<E>): SearchState<E> {
  switch (action.type) {
    case "edit":
      return { ...state, scenario: action.change(state.scenario) };
    case "start":
      // The scenario searched goes on screen at once (the example, a relaxed search, the undo)
      return { ...state, scenario: action.attempt.scenario, status: "loading", error: null, attempt: action.attempt };
    case "done":
      if (state.attempt?.id !== action.id) return state;
      return { ...state, result: action.result, searched: state.attempt.scenario, applied: state.attempt.applied, status: "done", attempt: null };
    case "fail": {
      if (state.attempt?.id !== action.id) return state;
      // The result on screen is still the previous one, and so is its scenario, unless the user
      // edited the search while the attempt was in flight: those edits are kept.
      const untouched = state.scenario === state.attempt.scenario;
      return { ...state, scenario: untouched ? state.attempt.before : state.scenario, status: "error", error: action.error };
    }
  }
}

/** «Ver zonas que encajan»: the scenario on screen, as it is. */
export function plainAttempt(state: SearchState<unknown>, id: number, scenario: ScenarioState = state.scenario): Attempt {
  return { id, scenario, applied: null, before: state.scenario };
}

/** An option of «¿Y si cambias algo?»: back always leads to the search before any option. */
export function relaxAttempt(state: SearchState<unknown>, id: number, label: string, relaxed: ScenarioState): Attempt {
  const previous = state.applied?.previous ?? state.searched ?? state.scenario;
  return { id, scenario: relaxed, applied: { label, previous }, before: state.scenario };
}

/** «Volver a mi búsqueda», or null when no option is applied. */
export function undoAttempt(state: SearchState<unknown>, id: number): Attempt | null {
  return state.applied ? plainAttempt(state, id, state.applied.previous) : null;
}

/**
 * Canonical JSON of a value: object keys sorted and undefined members left out, as JSON does.
 * Arrays keep their order (the priorities go first to last).
 */
function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map((v) => (v === undefined ? "null" : canonical(v))).join(",")}]`;
  if (value !== null && typeof value === "object") {
    const entries = Object.entries(value)
      .filter(([, v]) => v !== undefined)
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
    return `{${entries.map(([k, v]) => `${JSON.stringify(k)}:${canonical(v)}`).join(",")}}`;
  }
  return JSON.stringify(value) ?? "null";
}

/** The scenario on screen is not the one behind the result (same content counts as the same, whatever the key order). */
export function isStale(state: Pick<SearchState<unknown>, "result" | "searched" | "scenario">): boolean {
  return state.result !== null && canonical(state.searched) !== canonical(state.scenario);
}

/**
 * «Reintentar»: the failed attempt again, as it was (with its option, if any). If the user edited
 * the search since it started, what is on screen is searched instead: it is the newer wish.
 */
export function retryAttempt(state: SearchState<unknown>, id: number): Attempt | null {
  if (state.status !== "error" || !state.attempt) return null;
  if (state.scenario !== state.attempt.before) return plainAttempt(state, id);
  return { ...state.attempt, id, before: state.scenario };
}
