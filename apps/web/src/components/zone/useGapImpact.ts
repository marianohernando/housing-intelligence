"use client";

import { useEffect, useState } from "react";

import type { GapImpactResponse } from "@/contracts/gap_impact_response";
import { ApiError, createApi } from "@/lib/api";

// One request per visit (about 20 KB), only from the screen that shows it; a failed one is forgotten.
let request: Promise<GapImpactResponse> | null = null;

function load(): Promise<GapImpactResponse> {
  if (!request) {
    request = createApi().gapImpact();
    request.catch(() => {
      request = null;
    });
  }
  return request;
}

type Result = { body: GapImpactResponse } | { error: ApiError };

/** GET /api/v1/gaps/impact: where to invest first (D-229). */
export function useGapImpact() {
  const [result, setResult] = useState<Result | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    load()
      .then((body) => {
        if (!cancelled) setResult({ body });
      })
      .catch((exc: unknown) => {
        if (!cancelled) setResult({ error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)) });
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  return {
    loading: result === null,
    data: result && "body" in result ? result.body.data : null,
    error: result && "error" in result ? result.error : null,
    retry: () => {
      setResult(null);
      setAttempt((n) => n + 1);
    },
  };
}
