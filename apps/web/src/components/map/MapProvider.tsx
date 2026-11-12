"use client";

import { useParams } from "next/navigation";
import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { fetchZoneGaps } from "@/components/zone/useZoneGaps";
import { ApiError } from "@/lib/api";
import { type AdminFeature, findZone, type ZoneCollection, type ZoneFeature, type ZoneProperties, zonePropertiesOf } from "@/lib/map/zones";

import { fetchBarrios, fetchZones } from "./fetchZones";

export type ZonesStatus = "loading" | "ready" | "error";

interface MapContextValue {
  zones: ZoneCollection | null;
  status: ZonesStatus;
  error: ApiError | null;
  retry: () => void;
  /** Zone of the current route (/zona/[level]/[code]), once the outlines are loaded. */
  activeZone: ZoneFeature | null;
  /**
   * The same zone without its outline: from the outlines once loaded, before that from the zone's
   * «Qué falta» answer, which is small. The zone screen and its requests start with it.
   */
  routeZone: ZoneProperties | null;
  /**
   * False while a zone screen opened from its link waits for the zone's name: the outlines and the
   * map's script (the heaviest downloads) start right after it, so they do not slow it down.
   */
  mapMayLoad: boolean;
  /** Zone picked on the overview map (its card shows on the right). */
  selectedZone: ZoneFeature | null;
  select: (zoneKey: string | null) => void;
  /** Barrios of the active district, for the «Barrios de la zona» bar: navigation only, no figures. */
  barrios: AdminFeature[] | null;
  /** Barrio the camera shows, inside the active district (null: the whole district). */
  barrio: AdminFeature | null;
  focusBarrio: (adminUnitId: string | null) => void;
}

const MapContext = createContext<MapContextValue | null>(null);

export function useMapZones(): MapContextValue {
  const value = useContext(MapContext);
  if (!value) throw new Error("useMapZones must be used inside <MapProvider>");
  return value;
}

export default function MapProvider({ children }: { children: ReactNode }) {
  const params = useParams<{ level?: string; code?: string }>();
  const [zones, setZones] = useState<ZoneCollection | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  // The list remembers its district, so another zone never shows the wrong barrios.
  const [barrioList, setBarrioList] = useState<{ parent: string; features: AdminFeature[] } | null>(null);
  const [focus, setFocus] = useState<string | null>(null);

  const code = params.code ? decodeURIComponent(params.code) : undefined;
  const level = params.level;
  const routeKey = level && code ? `${level}/${code}` : null;
  const activeZone = useMemo(
    () => (zones && level && code ? (findZone(zones, level, code) ?? null) : null),
    [zones, level, code],
  );

  // The route's zone by name, from its small «Qué falta» answer (preloaded with the zone's HTML);
  // `settled` is the zone it was asked for, answered or failed
  const [routeRef, setRouteRef] = useState<{ settled: string; zone: ZoneProperties | null } | null>(null);
  useEffect(() => {
    if ((level !== "municipio" && level !== "distrito") || !code) return;
    let cancelled = false;
    const settled = `${level}/${code}`;
    fetchZoneGaps(level, code)
      .then((body) => {
        if (!cancelled) setRouteRef({ settled, zone: zonePropertiesOf(body.data.zone) });
      })
      .catch(() => {
        if (!cancelled) setRouteRef({ settled, zone: null });
      });
    return () => {
      cancelled = true;
    };
  }, [level, code]);
  const routeAnswer = routeKey && routeRef?.settled === routeKey ? routeRef : null;
  // Only the first load waits, and only for the zone it opened on; from then on, nothing does
  const [mapMayLoad, setMapMayLoad] = useState(false);
  if (!mapMayLoad && (!routeKey || routeAnswer !== null)) setMapMayLoad(true);

  useEffect(() => {
    if (!mapMayLoad) return;
    let cancelled = false;
    fetchZones()
      .then((collection) => {
        if (!cancelled) setZones(collection);
      })
      .catch((exc: unknown) => {
        if (!cancelled) setError(exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)));
      });
    return () => {
      cancelled = true;
    };
  }, [attempt, mapMayLoad]);

  // Once the outlines are in, only a zone of the map counts (Madrid as a whole is its districts)
  const routeZone = zones || error ? (activeZone?.properties ?? null) : (routeAnswer?.zone ?? null);
  const districtId = routeZone?.level === "distrito" ? routeZone.admin_unit_id : null;

  // Entering another district (or coming back to one) starts from the whole district.
  const [focusDistrict, setFocusDistrict] = useState(districtId);
  if (focusDistrict !== districtId) {
    setFocusDistrict(districtId);
    setFocus(null);
  }

  useEffect(() => {
    if (!districtId || barrioList?.parent === districtId) return;
    let cancelled = false;
    fetchBarrios(districtId)
      .then((features) => {
        if (!cancelled) setBarrioList({ parent: districtId, features });
      })
      // The bar only helps to move around the district: on failure it is not shown, and the
      // next visit to the district asks again.
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [districtId, barrioList?.parent]);

  const retry = useCallback(() => {
    setError(null);
    setAttempt((n) => n + 1);
  }, []);

  const focusBarrio = useCallback((id: string | null) => setFocus(id), []);

  const value = useMemo<MapContextValue>(() => {
    const status: ZonesStatus = error ? "error" : zones ? "ready" : "loading";
    const [level = "", selectedCode = ""] = selectedKey?.split("/") ?? [];
    const selectedZone = zones && selectedKey ? (findZone(zones, level, selectedCode) ?? null) : null;
    const barrios = districtId && barrioList?.parent === districtId ? barrioList.features : null;
    const barrio = focus ? (barrios?.find((b) => b.properties.admin_unit_id === focus) ?? null) : null;
    return { zones, status, error, retry, activeZone, routeZone, mapMayLoad, selectedZone, select: setSelectedKey, barrios, barrio, focusBarrio };
  }, [zones, error, retry, activeZone, routeZone, mapMayLoad, selectedKey, districtId, barrioList, focus, focusBarrio]);

  return <MapContext.Provider value={value}>{children}</MapContext.Provider>;
}
