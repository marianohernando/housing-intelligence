"use client";

import { useEffect, useState } from "react";

import type { ZoneGapListResponse } from "@/contracts/zone_gap_list_response";
import { ApiError, createApi, type GapLevel } from "@/lib/api";

type Result = { key: string; body: ZoneGapListResponse } | { key: string; error: ApiError };

// One request per zone for the whole page: the zone screen asks for its name as soon as it opens,
// and its card for the rows, with the same answer. A failed request is forgotten, so retry asks again.
const requests = new Map<string, Promise<ZoneGapListResponse>>();

/**
 * The zone screen and its map wait for this answer: if the API hangs, it fails after this long, so
 * the map loads anyway and the card offers «Reintentar» (review of PR #16). A cold start of the API
 * takes a few seconds. Counted from when it is sent, not while it waits its turn (lib/api.ts).
 */
const ZONE_GAPS_TIMEOUT_MS = 10_000;

export function fetchZoneGaps(level: GapLevel, code: string): Promise<ZoneGapListResponse> {
  const key = `${level}/${code}`;
  let request = requests.get(key);
  if (!request) {
    request = createApi().zoneGaps(level, code, { timeoutMs: ZONE_GAPS_TIMEOUT_MS });
    requests.set(key, request);
    request.catch(() => requests.delete(key));
  }
  return request;
}

/** GET /api/v1/gaps/{level}/{code} for one zone; loading while the answer is for another zone. */
export function useZoneGaps(level: GapLevel, code: string) {
  const key = `${level}/${code}`;
  const [result, setResult] = useState<Result | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    fetchZoneGaps(level, code)
      .then((body) => {
        if (!cancelled) setResult({ key, body });
      })
      .catch((exc: unknown) => {
        if (!cancelled) setResult({ key, error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)) });
      });
    return () => {
      cancelled = true;
    };
  }, [key, level, code, attempt]);

  const current = result?.key === key ? result : null;
  return {
    loading: current === null,
    data: current && "body" in current ? current.body : null,
    error: current && "error" in current ? current.error : null,
    retry: () => {
      setResult(null);
      setAttempt((n) => n + 1);
    },
  };
}
