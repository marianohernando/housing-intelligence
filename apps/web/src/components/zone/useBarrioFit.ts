"use client";

import { useEffect, useState } from "react";

import type { BarrioSearchResponse } from "@/contracts/barrio_search_response";
import type { ScenarioState } from "@/contracts/scenario_state";
import { ApiError, createApi } from "@/lib/api";
import { once } from "@/lib/once";

type Result = { key: string; body: BarrioSearchResponse } | { key: string; error: ApiError };

// One request per district and search for the whole visit: coming back to the district reuses it.
// A failed request is forgotten, so «Reintentar» asks again.
const requests = new Map<string, Promise<BarrioSearchResponse>>();

/** The district's barrios are a small search (about 40 KB); a cold start of the API adds a few seconds. */
const TIMEOUT_MS = 20_000;

/**
 * POST /api/v1/search/barrios for the district on screen with the scenario behind the search result
 * (D-232): asked only when a district opens after a search; loading while the answer is for another.
 */
export function useBarrioFit(distrito: string, scenario: ScenarioState) {
  const key = `${distrito}#${JSON.stringify(scenario)}`;
  const [result, setResult] = useState<Result | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    once(requests, key, () => createApi().searchBarrios(distrito, scenario, { timeoutMs: TIMEOUT_MS }))
      .then((body) => {
        if (!cancelled) setResult({ key, body });
      })
      .catch((exc: unknown) => {
        if (!cancelled) setResult({ key, error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)) });
      });
    return () => {
      cancelled = true;
    };
  }, [key, distrito, scenario, attempt]);

  const current = result?.key === key ? result : null;
  return {
    loading: current === null,
    data: current && "body" in current ? current.body.data : null,
    error: current && "error" in current ? current.error : null,
    retry: () => {
      setResult(null);
      setAttempt((n) => n + 1);
    },
  };
}
