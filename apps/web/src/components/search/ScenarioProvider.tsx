"use client";

import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useReducer, useRef } from "react";

import type { ScenarioState } from "@/contracts/scenario_state";
import type { Relaxation, SearchResult } from "@/contracts/search_response";
import { ApiError, createApi } from "@/lib/api";
import { runSearch, SEARCH_ENABLED } from "@/lib/capabilities";
import { defaultScenario, exampleScenario, scopeOf, setScope } from "@/lib/scenario";
import {
  type Attempt,
  initialSearchState,
  isStale,
  plainAttempt,
  relaxAttempt,
  retryAttempt,
  searchReducer,
  type SearchState,
  type SearchStatus,
  undoAttempt,
} from "@/lib/searchState";

export type { SearchStatus };

interface ScenarioContextValue {
  scenario: ScenarioState;
  update: (change: (s: ScenarioState) => ScenarioState) => void;
  /** «Ver zonas que encajan»: searches the scenario on screen. */
  search: () => void;
  /** «Reintentar»: the failed search again, as it was. */
  retry: () => void;
  /** False while the search capability is off: it shows as «Muy pronto». */
  available: boolean;
  status: SearchStatus;
  result: SearchResult | null;
  error: ApiError | null;
  /** The scenario on screen changed after the search that `result` answers. */
  stale: boolean;
  /** Label of the «¿Y si cambias algo?» option behind `result`, if one was applied. */
  applied: string | null;
  applyRelaxation: (relaxation: Relaxation) => void;
  undoRelaxation: () => void;
  /** The demo case from the portada (portada.ejemplo.boton): fills the search and runs it. */
  loadExample: () => void;
}

const ScenarioContext = createContext<ScenarioContextValue | null>(null);

export function useScenario(): ScenarioContextValue {
  const value = useContext(ScenarioContext);
  if (!value) throw new Error("useScenario must be used inside <ScenarioProvider>");
  return value;
}

type State = SearchState<ApiError>;

/** The single ScenarioState that chips, filters and map share (CLAUDE.md §13), and its search. */
export default function ScenarioProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(searchReducer<ApiError>, defaultScenario(), initialSearchState<ApiError>);
  // Actions build their attempt from the latest committed state
  const stateRef = useRef(state);
  useEffect(() => {
    stateRef.current = state;
  }, [state]);
  const nextId = useRef(0);
  // The search in flight: a newer one cancels it, and so does leaving the page.
  const inFlight = useRef<AbortController | null>(null);
  useEffect(() => () => inFlight.current?.abort(), []);

  const update = useCallback((change: (s: ScenarioState) => ScenarioState) => dispatch({ type: "edit", change }), []);

  /** Sends an attempt built from the current state; only the answer to the latest one counts. */
  const send = useCallback(async (build: (s: State, id: number) => Attempt | null) => {
    if (!SEARCH_ENABLED) return;
    const attempt = build(stateRef.current, ++nextId.current);
    if (!attempt) return;
    inFlight.current?.abort();
    const controller = new AbortController();
    inFlight.current = controller;
    dispatch({ type: "start", attempt });
    try {
      const body = await runSearch(createApi(), attempt.scenario, SEARCH_ENABLED, controller.signal);
      if (body) dispatch({ type: "done", id: attempt.id, result: body.data });
    } catch (exc) {
      // Cancelled by a newer search (whose answer is the one that counts) or by leaving the page
      if (controller.signal.aborted) return;
      dispatch({ type: "fail", id: attempt.id, error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)) });
    } finally {
      if (inFlight.current === controller) inFlight.current = null;
    }
  }, []);

  const search = useCallback(() => void send((s, id) => plainAttempt(s, id)), [send]);
  const retry = useCallback(() => void send(retryAttempt), [send]);
  const applyRelaxation = useCallback(
    // The API echoes `scope: "all"`; the web leaves it out, as «Toda la Comunidad» does (D-238)
    (r: Relaxation) => void send((s, id) => relaxAttempt(s, id, r.label, setScope(r.relaxed_scenario, scopeOf(r.relaxed_scenario)))),
    [send],
  );
  const undoRelaxation = useCallback(() => void send(undoAttempt), [send]);
  const loadExample = useCallback(() => void send((s, id) => plainAttempt(s, id, exampleScenario())), [send]);

  const value = useMemo(
    () => ({
      scenario: state.scenario,
      update,
      search,
      retry,
      available: SEARCH_ENABLED,
      status: state.status,
      result: state.result,
      error: state.error,
      stale: isStale(state),
      applied: state.applied?.label ?? null,
      applyRelaxation,
      undoRelaxation,
      loadExample,
    }),
    [state, update, search, retry, applyRelaxation, undoRelaxation, loadExample],
  );
  return <ScenarioContext.Provider value={value}>{children}</ScenarioContext.Provider>;
}
