"use client";

import { useParams } from "next/navigation";
import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { ApiError, createApi } from "@/lib/api";
import {
  type AdminFeature,
  buildZoneCollection,
  findZone,
  MUNICIPIOS_BY_DISTRITO,
  type ZoneCollection,
  type ZoneFeature,
} from "@/lib/map/zones";

/** Simplification of the outlines: municipios are seen from far, districts and barrios up close. */
const SIMPLIFY_M = { municipio: 50, distrito: 25, barrio: 10 } as const;

export type ZonesStatus = "loading" | "ready" | "error";

interface MapContextValue {
  zones: ZoneCollection | null;
  status: ZonesStatus;
  error: ApiError | null;
  retry: () => void;
  /** Zone of the current route (/zona/[level]/[code]), once the outlines are loaded. */
  activeZone: ZoneFeature | null;
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

  useEffect(() => {
    const api = createApi();
    let cancelled = false;
    Promise.all([
      api.adminUnits("municipio", SIMPLIFY_M.municipio),
      ...MUNICIPIOS_BY_DISTRITO.map((parent) => api.adminUnits("distrito", SIMPLIFY_M.distrito, parent)),
    ])
      .then(([municipios, ...distritos]) => {
        const features = distritos.flatMap((d) => d.data.features);
        if (!cancelled) setZones(buildZoneCollection(municipios.data.features, features));
      })
      .catch((exc: unknown) => {
        if (!cancelled) setError(exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)));
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  const code = params.code ? decodeURIComponent(params.code) : undefined;
  const activeZone = useMemo(
    () => (zones && params.level && code ? (findZone(zones, params.level, code) ?? null) : null),
    [zones, params.level, code],
  );
  const districtId = activeZone?.properties.level === "distrito" ? activeZone.properties.admin_unit_id : null;

  // Entering another district (or coming back to one) starts from the whole district.
  const [focusDistrict, setFocusDistrict] = useState(districtId);
  if (focusDistrict !== districtId) {
    setFocusDistrict(districtId);
    setFocus(null);
  }

  useEffect(() => {
    if (!districtId || barrioList?.parent === districtId) return;
    let cancelled = false;
    createApi()
      .adminUnits("barrio", SIMPLIFY_M.barrio, districtId)
      .then((body) => {
        if (!cancelled) setBarrioList({ parent: districtId, features: body.data.features });
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
    return { zones, status, error, retry, activeZone, selectedZone, select: setSelectedKey, barrios, barrio, focusBarrio };
  }, [zones, error, retry, activeZone, selectedKey, districtId, barrioList, focus, focusBarrio]);

  return <MapContext.Provider value={value}>{children}</MapContext.Provider>;
}
