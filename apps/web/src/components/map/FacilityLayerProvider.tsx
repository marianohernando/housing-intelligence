"use client";

import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { ApiError } from "@/lib/api";
import { allServicesOn, type Facility, type FacilityKey, groupFacilities, isLeisureFacility, type LeisureFacilityKey } from "@/lib/map/facilities";
import { FACILITY_CATEGORIES } from "@/lib/map/zonePlaces";

import { fetchLeisurePlaces, fetchZonePlaces } from "./fetchZones";
import { useMapZones } from "./MapProvider";

type Groups = Record<FacilityKey, Facility[]>;
type Result = { groups: Groups } | { error: ApiError };
type LeisureResult = { items: Facility[] } | { error: ApiError };

export type FacilitiesStatus = "idle" | "loading" | "ready" | "error";

interface FacilityLayerValue {
  status: FacilitiesStatus;
  groups: Groups | null;
  error: ApiError | null;
  retry: () => void;
  /** Types shown on the map, several at once (petición de Mariano, 13 nov); none is allowed */
  types: readonly FacilityKey[];
  /** The pressed types whose places are here: a leisure type is only once its own request answers */
  readyTypes: readonly FacilityKey[];
  /** Each leisure type of the zone, asked apart when pressed (D-236, R-07): absent until pressed */
  leisure: Readonly<Partial<Record<LeisureFacilityKey, FacilitiesStatus>>>;
  leisureErrors: Readonly<Partial<Record<LeisureFacilityKey, ApiError>>>;
  retryLeisure: (key: LeisureFacilityKey) => void;
  /** Press or release one type */
  toggle: (type: FacilityKey) => void;
  /** «Todos» (every service; leisure stays as it is) / «Ninguno» */
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
 * Leisure (D-236) is not in that request: each leisure type is asked when its button is pressed.
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
  // Leisure by zone and type («zone:type»); a failure stays until «Reintentar»
  const [leisureResults, setLeisureResults] = useState<ReadonlyMap<string, LeisureResult>>(new Map());

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

  useEffect(() => {
    if (!zoneId) return;
    const wanted = types.filter(isLeisureFacility).filter((key) => !leisureResults.has(`${zoneId}:${key}`));
    if (!wanted.length) return;
    let cancelled = false;
    for (const key of wanted) {
      // once() shares the request: asking again after a re-render does not send it twice
      fetchLeisurePlaces(zoneId, key)
        .then((places): LeisureResult => ({ items: groupFacilities(places)[key] }))
        .catch((exc: unknown): LeisureResult => ({ error: toApiError(exc) }))
        .then((result) => {
          if (!cancelled) setLeisureResults((all) => new Map(all).set(`${zoneId}:${key}`, result));
        });
    }
    return () => {
      cancelled = true;
    };
  }, [zoneId, types, leisureResults]);

  const retryLeisure = useCallback(
    (key: LeisureFacilityKey) => {
      if (!zoneId) return;
      setLeisureResults((all) => {
        const next = new Map(all);
        next.delete(`${zoneId}:${key}`);
        return next;
      });
    },
    [zoneId],
  );

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
    setTypes((current) => (on ? allServicesOn(current) : []));
    setPicked(null);
  }, []);
  const pick = useCallback((facility: Facility | null) => setPicked(facility && zoneId ? { zoneId, facility } : null), [zoneId]);

  const value = useMemo((): FacilityLayerValue => {
    const result = zoneId ? results.get(zoneId) : undefined;
    const status: FacilitiesStatus = !zoneId ? "idle" : !result ? "loading" : "groups" in result ? "ready" : "error";
    const base = result && "groups" in result ? result.groups : null;
    const leisure: Partial<Record<LeisureFacilityKey, FacilitiesStatus>> = {};
    const leisureErrors: Partial<Record<LeisureFacilityKey, ApiError>> = {};
    const groups = base ? { ...base } : null;
    for (const key of types.filter(isLeisureFacility)) {
      const found = zoneId ? leisureResults.get(`${zoneId}:${key}`) : undefined;
      leisure[key] = !found ? "loading" : "items" in found ? "ready" : "error";
      if (groups && found && "items" in found) groups[key] = found.items;
      if (found && "error" in found) leisureErrors[key] = found.error;
    }
    const readyTypes = types.filter((key) => !isLeisureFacility(key) || leisure[key] === "ready");
    return {
      status,
      groups,
      error: result && "error" in result ? result.error : null,
      retry,
      types,
      readyTypes,
      leisure,
      leisureErrors,
      retryLeisure,
      toggle,
      setAll,
      picked: picked && picked.zoneId === zoneId && readyTypes.includes(picked.facility.type) ? picked.facility : null,
      pick,
    };
  }, [zoneId, results, leisureResults, retry, retryLeisure, types, toggle, setAll, picked, pick]);
  return <FacilityLayerContext.Provider value={value}>{children}</FacilityLayerContext.Provider>;
}
