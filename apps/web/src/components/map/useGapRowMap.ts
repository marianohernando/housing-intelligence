"use client";

import { useEffect, useState } from "react";

import type { GapRowMap, ZoneGapStatus } from "@/contracts/gap_row_map_response";
import type { GapRowKey } from "@/contracts/zone_gap_list_response";
import { ApiError, createApi } from "@/lib/api";
import { gapByZone } from "@/lib/map/gapMap";

export interface GapRowMapData {
  /** The row as the API describes it (label, what it counts, reference), from the municipios. */
  info: GapRowMap;
  byZone: Map<string, ZoneGapStatus>;
}

type Result = { row: GapRowKey; data: GapRowMapData } | { row: GapRowKey; error: ApiError };

/** One row's status in every zone of the map: municipios, and Madrid capital by its districts (D-200). */
async function fetchRowMap(row: GapRowKey): Promise<GapRowMapData> {
  const api = createApi();
  const [municipios, distritos] = await Promise.all([api.gapRowMap("municipio", row), api.gapRowMap("distrito", row)]);
  return { info: municipios.data, byZone: gapByZone([municipios.data, distritos.data]) };
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
        if (!cancelled) setResult({ row, error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)) });
      });
    return () => {
      cancelled = true;
    };
  }, [row, attempt]);

  const current = row && result?.row === row ? result : null;
  return {
    loading: row !== null && current === null,
    data: current && "data" in current ? current.data : null,
    error: current && "error" in current ? current.error : null,
    retry: () => {
      setResult(null);
      setAttempt((n) => n + 1);
    },
  };
}
