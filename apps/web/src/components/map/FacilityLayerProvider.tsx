"use client";

import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { ApiError, createApi } from "@/lib/api";
import { CONTRACT_QUERIES, type Facility, type FacilityKey, facilityQueries, groupFacilities } from "@/lib/map/facilities";

import { useMapZones } from "./MapProvider";

type Groups = Record<FacilityKey, Facility[]>;
type Result = { groups: Groups } | { error: ApiError };

export type FacilitiesStatus = "idle" | "loading" | "ready" | "error";

interface FacilityLayerValue {
  status: FacilitiesStatus;
  groups: Groups | null;
  error: ApiError | null;
  retry: () => void;
  /** Type shown on the map (null: none) */
  type: FacilityKey | null;
  setType: (type: FacilityKey | null) => void;
  /** The facility whose label is open on the map */
  picked: Facility | null;
  pick: (facility: Facility | null) => void;
}

const FacilityLayerContext = createContext<FacilityLayerValue | null>(null);

export function useFacilityLayer(): FacilityLayerValue {
  const value = useContext(FacilityLayerContext);
  if (!value) throw new Error("useFacilityLayer must be used inside <FacilityLayerProvider>");
  return value;
}

const toApiError = (exc: unknown) => (exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)));

/**
 * A zone's facilities: one /places query per category, by zone and subcategory (a few KB each),
 * plus the categories the answering contract adds (never asked to an API that would reject them).
 */
async function fetchFacilities(adminUnitId: string): Promise<Groups> {
  const api = createApi();
  const answers = await Promise.all(facilityQueries().map((query) => api.placesCollection({ ...query, adminUnitId })));
  const version = answers.find((a) => a.contractVersion)?.contractVersion;
  const extra = version ? (CONTRACT_QUERIES[version] ?? []) : [];
  const more = await Promise.all(extra.map((query) => api.places({ ...query, adminUnitId })));
  return groupFacilities([...answers.flatMap((a) => a.features), ...more.flat()]);
}

/**
 * Every facility of the zone on screen (FASE_PRUEBAS, T3), shared by the map (clustered layer)
 * and the «Todos los centros» card (counts and list). Loaded when a zone opens and kept per zone;
 * schools are shown first, the first thing families look for and what looked scarce before.
 */
export default function FacilityLayerProvider({ children }: { children: ReactNode }) {
  const { activeZone } = useMapZones();
  const zoneId = activeZone?.properties.admin_unit_id ?? null;
  const [results, setResults] = useState<ReadonlyMap<string, Result>>(new Map());
  const [attempt, setAttempt] = useState(0);
  const [type, setTypeState] = useState<FacilityKey | null>("colegio");
  const [picked, setPicked] = useState<{ zoneId: string; facility: Facility } | null>(null);
  // A zone with an answer is not asked again (a failure waits for «Reintentar»)
  const answered = zoneId !== null && results.has(zoneId);

  useEffect(() => {
    if (!zoneId || answered) return;
    let cancelled = false;
    const save = (result: Result) => {
      if (!cancelled) setResults((all) => new Map(all).set(zoneId, result));
    };
    fetchFacilities(zoneId)
      .then((groups) => save({ groups }))
      .catch((exc: unknown) => save({ error: toApiError(exc) }));
    return () => {
      cancelled = true;
    };
  }, [zoneId, answered, attempt]);

  const retry = useCallback(() => {
    if (!zoneId) return;
    setResults((all) => {
      const next = new Map(all);
      next.delete(zoneId);
      return next;
    });
    setAttempt((n) => n + 1);
  }, [zoneId]);

  const setType = useCallback((next: FacilityKey | null) => {
    setTypeState(next);
    setPicked(null);
  }, []);
  const pick = useCallback((facility: Facility | null) => setPicked(facility && zoneId ? { zoneId, facility } : null), [zoneId]);

  const value = useMemo((): FacilityLayerValue => {
    const result = zoneId ? results.get(zoneId) : undefined;
    const status: FacilitiesStatus = !zoneId ? "idle" : !result ? "loading" : "groups" in result ? "ready" : "error";
    return {
      status,
      groups: result && "groups" in result ? result.groups : null,
      error: result && "error" in result ? result.error : null,
      retry,
      type,
      setType,
      picked: picked && picked.zoneId === zoneId && picked.facility.type === type ? picked.facility : null,
      pick,
    };
  }, [zoneId, results, retry, type, setType, picked, pick]);
  return <FacilityLayerContext.Provider value={value}>{children}</FacilityLayerContext.Provider>;
}
