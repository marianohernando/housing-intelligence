"use client";

import { useEffect, useState } from "react";

import type { ZoneGapListResponse } from "@/contracts/zone_gap_list_response";
import { ApiError, createApi, type GapLevel } from "@/lib/api";

type Result = { key: string; body: ZoneGapListResponse } | { key: string; error: ApiError };

/** GET /api/v1/gaps/{level}/{code} for one zone; loading while the answer is for another zone. */
export function useZoneGaps(level: GapLevel, code: string) {
  const key = `${level}/${code}`;
  const [result, setResult] = useState<Result | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    createApi()
      .zoneGaps(level, code)
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
