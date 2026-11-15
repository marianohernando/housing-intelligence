"use client";

import { useParams, usePathname, useSearchParams } from "next/navigation";
import { createContext, type ReactNode, Suspense, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";

import { useScenario } from "@/components/search/ScenarioProvider";
import { fetchZoneGaps } from "@/components/zone/useZoneGaps";
import { ApiError } from "@/lib/api";
import { byBarrio } from "@/lib/fit";
import {
  type AdminFeature,
  barrioZones,
  findZone,
  selectionAfter,
  withBarrios,
  type ZoneCollection,
  type ZoneFeature,
  type ZoneProperties,
  zonePropertiesOf,
} from "@/lib/map/zones";
import { OVERVIEW_ZONE_PARAM, overviewHref, overviewZoneKey } from "@/lib/nav";
import { scopeOf } from "@/lib/scenario";

import { fetchBarrios, fetchCapitalBarrios, fetchZones } from "./fetchZones";

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
  /**
   * The zones the overview paints with the search: those of the map, or with a search over Madrid
   * capital its barrios instead of its districts (D-238), once their outlines are in.
   */
  resultZones: ZoneCollection | null;
  /** The barrios' outlines could not be loaded for a search over the capital: its map stays unpainted. */
  barriosError: ApiError | null;
  /** Asks for the barrios' outlines again (also done by the next search over the capital). */
  retryBarrios: () => void;
  /**
   * Zone picked on the overview map or in the list (its card shows on the right); also a barrio. It
   * lives in the address (`/?zona=…`, lib/nav.ts), so the browser's back button closes it.
   */
  selectedZone: ZoneFeature | null;
  select: (zoneKey: string | null) => void;
  /**
   * «Volver a la lista»: the same as the back button when the card was opened from the overview
   * (a step back in the history); a card opened from its link closes in place.
   */
  backToList: () => void;
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

/** The zone code of the route; a malformed one («%E0%A4%A») is no zone, as the page treats it, never a crash. */
function decodedCode(code: string | undefined): string | undefined {
  if (!code) return undefined;
  try {
    return decodeURIComponent(code);
  } catch {
    return undefined;
  }
}

/** The zone of the address, when it is the overview's. */
function overviewZoneInAddress(): string | null | undefined {
  if (window.location.pathname !== "/") return undefined;
  return overviewZoneKey(new URLSearchParams(window.location.search).get(OVERVIEW_ZONE_PARAM));
}

/**
 * Hands `?zona=` of the overview up: the only part of the map that waits for the address, so the
 * pages around it are still rendered on the server (useSearchParams needs Suspense). The address
 * itself is the truth, read when the router moves (useSearchParams) and on every step of the
 * history (popstate): a back right after a pick can reach the router after its own update of that
 * pick. On a zone screen the pick is kept: the back button returns to its card.
 */
function OverviewZoneParam({ onChange }: { onChange: (zoneKey: string | null) => void }) {
  const param = useSearchParams().get(OVERVIEW_ZONE_PARAM);
  const overview = usePathname() === "/";
  useEffect(() => {
    const follow = () => {
      const key = overviewZoneInAddress();
      if (key !== undefined) onChange(key);
    };
    follow();
    window.addEventListener("popstate", follow);
    return () => window.removeEventListener("popstate", follow);
  }, [overview, param, onChange]);
  return null;
}

export default function MapProvider({ children }: { children: ReactNode }) {
  const params = useParams<{ level?: string; code?: string }>();
  const [zones, setZones] = useState<ZoneCollection | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [attempt, setAttempt] = useState(0);
  // The zone picked on the overview, as its address says it (`?zona=`, lib/nav.ts). `live` is false
  // once the person leaves the overview: back on it, the card shows again only if its address says
  // so (the back button), never for a moment on the way to the list («Volver a la lista»)
  const [picked, setPicked] = useState<{ key: string | null; live: boolean }>({ key: null, live: true });
  const overview = usePathname() === "/";
  const [onOverview, setOnOverview] = useState(overview);
  if (onOverview !== overview) {
    setOnOverview(overview);
    if (!overview && picked.live) setPicked({ key: picked.key, live: false });
  }
  // The list remembers its district, so another zone never shows the wrong barrios.
  const [barrioList, setBarrioList] = useState<{ parent: string; features: AdminFeature[] } | null>(null);
  const [focus, setFocus] = useState<string | null>(null);
  // Madrid capital's barrios, asked as soon as the search is set to «Madrid capital» (D-238)
  const { scenario, result } = useScenario();
  const wantsBarrios = scopeOf(scenario) === "madrid" || byBarrio(result);
  const [capital, setCapital] = useState<AdminFeature[] | null>(null);
  const [capitalError, setCapitalError] = useState<ApiError | null>(null);
  // A new search over the capital asks again for outlines that failed
  const [searched, setSearched] = useState(result);
  if (searched !== result) {
    setSearched(result);
    if (capitalError && byBarrio(result)) setCapitalError(null);
  }
  // The map changes between districts and barrios with the search: the zone picked follows it
  // (a barrio becomes its district; a district, which has no single barrio, is let go), and so does
  // its address (below), so a later search never brings back a card the person did not open
  const barrioMap = byBarrio(result);
  const selectedKey = picked.live ? selectionAfter(picked.key, barrioMap) : null;
  useEffect(() => {
    const shown = overviewZoneInAddress();
    if (shown === undefined) return;
    const next = selectionAfter(shown, barrioMap);
    // The address follows; OverviewZoneParam then hands the new pick up
    if (next !== shown) window.history.replaceState(null, "", overviewHref(next));
  }, [barrioMap]);
  // Whether the card in view was opened from the overview, one step after the list in the history
  const openedFromList = useRef(false);
  const followAddress = useCallback((key: string | null) => {
    if (key === null) openedFromList.current = false;
    setPicked({ key, live: true });
  }, []);
  const select = useCallback((key: string | null) => {
    const shown = overviewZoneInAddress();
    if (shown !== undefined) {
      // From the list, a new step in the history; from one card to another, the same step
      if (key !== null && shown === null) {
        window.history.pushState(null, "", overviewHref(key));
        openedFromList.current = true;
      } else if (key !== shown) {
        window.history.replaceState(null, "", overviewHref(key));
      }
    }
    if (key === null) openedFromList.current = false;
    setPicked({ key, live: true });
  }, []);
  const backToList = useCallback(() => {
    // Once: a second tap before the history moves closes in place instead of going back twice
    const fromList = openedFromList.current;
    openedFromList.current = false;
    if (fromList) window.history.back();
    else select(null);
  }, [select]);

  const code = decodedCode(params.code);
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

  useEffect(() => {
    if (!wantsBarrios || capital || capitalError) return;
    let cancelled = false;
    fetchCapitalBarrios()
      .then((features) => {
        if (!cancelled) setCapital(features);
      })
      // The list of barrios still works and the map leaves the capital unpainted, with a notice
      // and «Reintentar» in the legend; the next search over the capital also asks again.
      .catch((exc: unknown) => {
        if (!cancelled) setCapitalError(exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)));
      });
    return () => {
      cancelled = true;
    };
  }, [wantsBarrios, capital, capitalError]);
  const barrios = useMemo(() => (zones && capital ? barrioZones(capital, zones) : null), [zones, capital]);
  const resultZones = useMemo(() => (zones && barrios && byBarrio(result) ? withBarrios(zones, barrios) : zones), [zones, barrios, result]);

  const retry = useCallback(() => {
    setError(null);
    setAttempt((n) => n + 1);
  }, []);

  const focusBarrio = useCallback((id: string | null) => setFocus(id), []);
  const retryBarrios = useCallback(() => setCapitalError(null), []);

  const value = useMemo<MapContextValue>(() => {
    const status: ZonesStatus = error ? "error" : zones ? "ready" : "loading";
    const [level = "", selectedCode = ""] = selectedKey?.split("/") ?? [];
    const pickedIn = (from: ZoneCollection | null) => (from && selectedKey ? findZone(from, level, selectedCode) : undefined);
    const selectedZone = pickedIn(zones) ?? pickedIn(barrios) ?? null;
    const districtBarrios = districtId && barrioList?.parent === districtId ? barrioList.features : null;
    const barrio = focus ? (districtBarrios?.find((b) => b.properties.admin_unit_id === focus) ?? null) : null;
    return {
      zones,
      status,
      error,
      retry,
      activeZone,
      routeZone,
      mapMayLoad,
      resultZones,
      barriosError: capitalError,
      retryBarrios,
      selectedZone,
      select,
      backToList,
      barrios: districtBarrios,
      barrio,
      focusBarrio,
    };
  }, [
    zones,
    error,
    retry,
    activeZone,
    routeZone,
    mapMayLoad,
    resultZones,
    capitalError,
    retryBarrios,
    selectedKey,
    select,
    backToList,
    barrios,
    districtId,
    barrioList,
    focus,
    focusBarrio,
  ]);

  return (
    <MapContext.Provider value={value}>
      <Suspense fallback={null}>
        <OverviewZoneParam onChange={followAddress} />
      </Suspense>
      {children}
    </MapContext.Provider>
  );
}
