"use client";

import { createContext, type ReactNode, useCallback, useContext, useMemo, useState } from "react";

import type { ScenarioState } from "@/contracts/scenario_state";
import type { SearchResult } from "@/contracts/search_response";
import { ApiError, createApi } from "@/lib/api";
import { runSearch, SEARCH_ENABLED } from "@/lib/capabilities";
import { defaultScenario } from "@/lib/scenario";

export type SearchStatus = "idle" | "loading" | "done" | "error";

interface ScenarioContextValue {
  scenario: ScenarioState;
  update: (change: (s: ScenarioState) => ScenarioState) => void;
  search: () => Promise<void>;
  /** False while POST /search is not published: the search shows as «Muy pronto». */
  available: boolean;
  status: SearchStatus;
  result: SearchResult | null;
  error: ApiError | null;
}

const ScenarioContext = createContext<ScenarioContextValue | null>(null);

export function useScenario(): ScenarioContextValue {
  const value = useContext(ScenarioContext);
  if (!value) throw new Error("useScenario must be used inside <ScenarioProvider>");
  return value;
}

/** The single ScenarioState that chips, filters and map share (CLAUDE.md §13), and its search. */
export default function ScenarioProvider({ children }: { children: ReactNode }) {
  const [scenario, setScenario] = useState<ScenarioState>(defaultScenario);
  const [status, setStatus] = useState<SearchStatus>("idle");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  const update = useCallback((change: (s: ScenarioState) => ScenarioState) => setScenario(change), []);

  const search = useCallback(async () => {
    if (!SEARCH_ENABLED) return;
    setStatus("loading");
    setError(null);
    try {
      const body = await runSearch(createApi(), scenario);
      if (!body) return;
      setResult(body.data);
      setStatus("done");
    } catch (exc) {
      setError(exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)));
      setStatus("error");
    }
  }, [scenario]);

  const value = useMemo(
    () => ({ scenario, update, search, available: SEARCH_ENABLED, status, result, error }),
    [scenario, update, search, status, result, error],
  );
  return <ScenarioContext.Provider value={value}>{children}</ScenarioContext.Provider>;
}
