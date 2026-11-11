"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import type { GapRowKey } from "@/contracts/zone_gap_list_response";
import { ApiError, createApi } from "@/lib/api";
import { type GapRowMapData, joinLevels, MAP_LEVELS } from "@/lib/map/gapMap";

type Result = { row: GapRowKey; data: GapRowMapData } | { row: GapRowKey; error: ApiError };

const toApiError = (exc: unknown) => (exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)));

/**
 * One row's status in every zone of the map: municipios, and Madrid capital by its districts
 * (D-200). A level whose answer fails is left out (its zones stay «sin calcular», with a notice);
 * only when both fail is it an error.
 */
async function fetchRowMap(row: GapRowKey): Promise<GapRowMapData> {
  const api = createApi();
  const answers = await Promise.allSettled(MAP_LEVELS.map((level) => api.gapRowMap(level, row)));
  return joinLevels(answers.map((a) => (a.status === "fulfilled" ? { map: a.value.data } : { error: a.reason })));
}

/** The row map for `row` (null: none); loading while the answer is for another row. */
export function useGapRowMap(row: GapRowKey | null) {
  const [result, setResult] = useState<Result | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!row) return;
    let cancelled = false;
    fetchRowMap(row)
      .then((data) => {
        if (!cancelled) setResult({ row, data });
      })
      .catch((exc: unknown) => {
        if (!cancelled) setResult({ row, error: toApiError(exc) });
      });
    return () => {
      cancelled = true;
    };
  }, [row, attempt]);

  const retry = useCallback(() => {
    setResult(null);
    setAttempt((n) => n + 1);
  }, []);

  return useMemo(() => {
    const current = row && result?.row === row ? result : null;
    return {
      loading: row !== null && current === null,
      data: current && "data" in current ? current.data : null,
      error: current && "error" in current ? current.error : null,
      retry,
    };
  }, [row, result, retry]);
}
