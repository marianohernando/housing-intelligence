"use client";

import { useEffect, useState } from "react";

import type { InvestorZoneListResponse } from "@/contracts/investor_zone_list_response";
import type { InvestorZoneResponse } from "@/contracts/investor_zone_response";
import type { ParcelSheetResponse } from "@/contracts/parcel_sheet_response";
import { ApiError, createApi } from "@/lib/api";

/** A cold API container takes a few seconds; after this, «Reintentar» (as useZoneGaps). */
const TIMEOUT_MS = 15_000;

type Result<T> = { key: string; body: T } | { key: string; error: ApiError };

/** One GET per key, with loading, error and retry; the answer of another key never shows. */
function useGet<T>(key: string, get: () => Promise<T>) {
  const [result, setResult] = useState<Result<T> | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    get()
      .then((body) => {
        if (!cancelled) setResult({ key, body });
      })
      .catch((exc: unknown) => {
        if (!cancelled) setResult({ key, error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)) });
      });
    return () => {
      cancelled = true;
    };
    // `get` is rebuilt on every render; the key says what it fetches
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, attempt]);

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

export function useInvestorZones() {
  return useGet<InvestorZoneListResponse>("zones", () => createApi().investorZones({ timeoutMs: TIMEOUT_MS }));
}

export function useInvestorZone(adminUnitId: string) {
  return useGet<InvestorZoneResponse>(adminUnitId, () => createApi().investorZone(adminUnitId, { timeoutMs: TIMEOUT_MS }));
}

/** A cold API container plus a cold Catastro or Ayuntamiento (6–9 s on their first call) */
const PARCEL_TIMEOUT_MS = 30_000;

/** GET /api/v1/investors/parcels?rc= (D-250): a parcel's sheet, by its reference. */
export function useParcel(rc14: string) {
  return useGet<ParcelSheetResponse>(`parcel:${rc14}`, () => createApi().parcel({ rc: rc14 }, { timeoutMs: PARCEL_TIMEOUT_MS }));
}
