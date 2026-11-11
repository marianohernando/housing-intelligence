import { describe, expect, it } from "vitest";

import type { ScenarioState } from "@/contracts/scenario_state";
import type { SearchResult } from "@/contracts/search_response";

import { defaultScenario, setAdults, setBudgetAmount, togglePriority } from "../scenario";
import {
  initialSearchState,
  isStale,
  plainAttempt,
  relaxAttempt,
  retryAttempt,
  searchReducer,
  type SearchState,
  undoAttempt,
} from "../searchState";

type State = SearchState<string>;

const result = (passing: number) => ({ reality_check: { zones_passing: passing } }) as unknown as SearchResult;
const mine = setBudgetAmount(defaultScenario(), 1500);
const relaxed: ScenarioState = setBudgetAmount(mine, 1650);

function searched(): State {
  let s = initialSearchState<string>(mine);
  s = searchReducer(s, { type: "start", attempt: plainAttempt(s, 1) });
  return searchReducer(s, { type: "done", id: 1, result: result(32) });
}

describe("searchReducer: only the latest search counts", () => {
  it("ignores the answer to an older search that arrives late", () => {
    let s = initialSearchState<string>(mine);
    s = searchReducer(s, { type: "start", attempt: plainAttempt(s, 1) });
    s = searchReducer(s, { type: "start", attempt: plainAttempt(s, 2, relaxed) });
    s = searchReducer(s, { type: "done", id: 1, result: result(1) });
    expect(s.status).toBe("loading");
    s = searchReducer(s, { type: "done", id: 2, result: result(2) });
    expect(s.result?.reality_check.zones_passing).toBe(2);
    expect(s.searched).toBe(relaxed);
    expect(searchReducer(s, { type: "fail", id: 1, error: "late" })).toBe(s);
  });
});

describe("«¿Y si cambias algo?»: apply and undo", () => {
  it("confirms the option only when its answer arrives, and goes back to the search before it", () => {
    let s = searched();
    const attempt = relaxAttempt(s, 2, "+150 €/mes", relaxed);
    s = searchReducer(s, { type: "start", attempt });
    expect(s.applied).toBeNull();
    expect(s.scenario).toBe(relaxed);
    s = searchReducer(s, { type: "done", id: 2, result: result(33) });
    expect(s.applied).toEqual({ label: "+150 €/mes", previous: mine });
    // A second option still goes back to the search before any option
    expect(relaxAttempt(s, 3, "+5 min", relaxed).applied?.previous).toBe(mine);
    const undo = undoAttempt(s, 4);
    expect(undo?.scenario).toBe(mine);
    s = searchReducer(s, { type: "start", attempt: undo! });
    s = searchReducer(s, { type: "done", id: 4, result: result(32) });
    expect(s.applied).toBeNull();
    expect(undoAttempt(s, 5)).toBeNull();
  });

  it("on failure keeps the last result and its scenario, and retries the option as it was", () => {
    let s = searched();
    s = searchReducer(s, { type: "start", attempt: relaxAttempt(s, 2, "+150 €/mes", relaxed) });
    s = searchReducer(s, { type: "fail", id: 2, error: "NETWORK" });
    expect(s).toMatchObject({ status: "error", error: "NETWORK", applied: null, scenario: mine });
    expect(s.result?.reality_check.zones_passing).toBe(32);
    expect(isStale(s)).toBe(false);
    const again = retryAttempt(s, 3);
    expect(again).toMatchObject({ id: 3, scenario: relaxed, applied: { label: "+150 €/mes", previous: mine } });
    s = searchReducer(s, { type: "start", attempt: again! });
    s = searchReducer(s, { type: "done", id: 3, result: result(33) });
    expect(s.applied?.label).toBe("+150 €/mes");
  });

  it("has nothing to retry unless the last search failed", () => {
    expect(retryAttempt(searched(), 9)).toBeNull();
  });
});

describe("isStale", () => {
  it("is true only when the scenario on screen differs in content from the one searched", () => {
    let s = searched();
    expect(isStale(s)).toBe(false);
    s = searchReducer(s, { type: "edit", change: (x) => setAdults(x, 2) });
    expect(isStale(s)).toBe(true);
    s = searchReducer(s, { type: "edit", change: (x) => setAdults(x, 1) });
    expect(isStale(s)).toBe(false);
    s = searchReducer(s, { type: "edit", change: (x) => togglePriority(togglePriority(x, "salud"), "salud") });
    expect(isStale(s)).toBe(false);
    expect(isStale(initialSearchState(mine))).toBe(false);
  });
});
