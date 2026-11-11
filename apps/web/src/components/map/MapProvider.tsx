"use client";

import { useParams } from "next/navigation";
import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { ApiError, createApi } from "@/lib/api";
import { buildZoneCollection, findZone, type ZoneCollection, type ZoneFeature } from "@/lib/map/zones";

/** Simplification of the outlines: municipios are seen from far, districts up close. */
const SIMPLIFY_M = { municipio: 50, distrito: 25 } as const;

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

  useEffect(() => {
    const api = createApi();
    let cancelled = false;
    Promise.all([api.adminUnits("municipio", SIMPLIFY_M.municipio), api.adminUnits("distrito", SIMPLIFY_M.distrito)])
      .then(([municipios, distritos]) => {
        if (!cancelled) setZones(buildZoneCollection(municipios.data.features, distritos.data.features));
      })
      .catch((exc: unknown) => {
        if (!cancelled) setError(exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)));
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  const retry = useCallback(() => {
    setError(null);
    setAttempt((n) => n + 1);
  }, []);

  const value = useMemo<MapContextValue>(() => {
    const code = params.code ? decodeURIComponent(params.code) : undefined;
    const activeZone = zones && params.level && code ? (findZone(zones, params.level, code) ?? null) : null;
    const status: ZonesStatus = error ? "error" : zones ? "ready" : "loading";
    const [level = "", selectedCode = ""] = selectedKey?.split("/") ?? [];
    const selectedZone = zones && selectedKey ? (findZone(zones, level, selectedCode) ?? null) : null;
    return { zones, status, error, retry, activeZone, selectedZone, select: setSelectedKey };
  }, [zones, error, retry, params.level, params.code, selectedKey]);

  return <MapContext.Provider value={value}>{children}</MapContext.Provider>;
}
