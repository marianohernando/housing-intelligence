"use client";

import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { ApiError } from "@/lib/api";
import { type Facility, type FacilityKey, FACILITY_TYPES, groupFacilities } from "@/lib/map/facilities";
import { FACILITY_CATEGORIES } from "@/lib/map/zonePlaces";

import { fetchZonePlaces } from "./fetchZones";
import { useMapZones } from "./MapProvider";

type Groups = Record<FacilityKey, Facility[]>;
type Result = { groups: Groups } | { error: ApiError };

export type FacilitiesStatus = "idle" | "loading" | "ready" | "error";

interface FacilityLayerValue {
  status: FacilitiesStatus;
  groups: Groups | null;
  error: ApiError | null;
  retry: () => void;
  /** Types shown on the map, several at once (petición de Mariano, 13 nov); none is allowed */
  types: readonly FacilityKey[];
  /** Press or release one type */
  toggle: (type: FacilityKey) => void;
  /** «Todos» / «Ninguno» */
  setAll: (on: boolean) => void;
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

/** A zone's facilities: one /places query per category, by zone and subcategory (a few KB each). */
async function fetchFacilities(adminUnitId: string): Promise<Groups> {
  return groupFacilities(await fetchZonePlaces(adminUnitId, FACILITY_CATEGORIES));
}

/**
 * Every facility of the zone on screen (FASE_PRUEBAS, T3), shared by the map (clustered layer)
 * and the «Todos los centros» card (counts and list). Loaded when a zone opens and kept per zone;
 * schools are shown first, the first thing families look for and what looked scarce before.
 */
export default function FacilityLayerProvider({ children }: { children: ReactNode }) {
  const { routeZone } = useMapZones();
  const zoneId = routeZone?.admin_unit_id ?? null;
  const [results, setResults] = useState<ReadonlyMap<string, Result>>(new Map());
  const [attempt, setAttempt] = useState(0);
  const [types, setTypes] = useState<readonly FacilityKey[]>(["colegio"]);
  const [picked, setPicked] = useState<{ zoneId: string; facility: Facility } | null>(null);
  // A zone already loaded is not asked again; a failure is asked again on «Reintentar» or on coming back
  const cached = zoneId ? results.get(zoneId) : undefined;
  const answered = cached !== undefined && "groups" in cached;

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

  // Filtered on the client: /places already brought every type of the zone in one request
  const toggle = useCallback((key: FacilityKey) => {
    setTypes((current) => (current.includes(key) ? current.filter((k) => k !== key) : [...current, key]));
    setPicked(null);
  }, []);
  const setAll = useCallback((on: boolean) => {
    setTypes(on ? FACILITY_TYPES.map((t) => t.key) : []);
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
      types,
      toggle,
      setAll,
      picked: picked && picked.zoneId === zoneId && types.includes(picked.facility.type) ? picked.facility : null,
      pick,
    };
  }, [zoneId, results, retry, types, toggle, setAll, picked, pick]);
  return <FacilityLayerContext.Provider value={value}>{children}</FacilityLayerContext.Provider>;
}
