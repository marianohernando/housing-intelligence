"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import {
  type GeoJSONSource,
  type LngLatBoundsLike,
  Map as MapLibreMap,
  type MapLayerMouseEvent,
  Marker,
  NavigationControl,
  setWorkerUrl,
} from "maplibre-gl";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { createApi } from "@/lib/api";
import { type KeyPoint, keyPointQueries, type KeyPointOptions, type PlaceFeature, pickKeyPoints } from "@/lib/map/places";
import {
  approachZoom,
  cameraPadding,
  extentKm,
  islandZoom,
  MOBILE_QUERY,
  projectAt,
  ZONE_BEARING,
  ZONE_PITCH,
  type ZoneCamera,
} from "@/lib/map/camera";
import { baseStyle, BUILDING_LAYER, MAP_PALETTE_TOKENS, type MapPalette, ZONE_BASE, zoneLayers } from "@/lib/map/style";
import {
  type AdminFeature,
  boundsOf,
  boundsOfAll,
  edgeWall,
  maskAround,
  outlinePoints,
  regionOf,
  type ZoneCollection,
  type ZoneFeature,
  type ZoneGeometry,
  zoneHref,
  type ZoneProperties,
} from "@/lib/map/zones";

import KeyPointLabel from "./KeyPointLabel";
import { useMapZones } from "./MapProvider";
import styles from "./VidaMap.module.css";

const WORKER_URL = "/maplibre/maplibre-gl-worker.mjs"; // copied by scripts/copy-maplibre-worker.mjs
const MOBILE = MOBILE_QUERY;
const REDUCED_MOTION = "(prefers-reduced-motion: reduce)";
const ATTRIBUTION =
  'Comunidad de Madrid · <a href="https://www.crtm.es" target="_blank" rel="noopener noreferrer">Powered by CRTM</a>';
const FLIGHT_MS = 2800;
/** The island stays still a moment before the camera comes closer to the buildings. */
const ISLAND_HOLD_MS = 700;
const APPROACH_MS = 4000;
const EMPTY: GeoJSON.FeatureCollection = { type: "FeatureCollection", features: [] };
const NO_POINTS: KeyPoint[] = [];
/** Room a label needs around its pin (it is centred above it), beyond the cards' padding. */
const LABEL_ROOM = { desktop: { x: 140, top: 70 }, mobile: { x: 70, top: 60 } };
/** Two labels collide when their pins are closer than one label (max-width 15rem, two lines). */
const LABEL_SIZE = { desktop: { width: 260, height: 64 }, mobile: { width: 150, height: 52 } };

const TEXT = {
  aria: "Mapa de la Comunidad de Madrid por municipios, con Madrid capital dividida en sus 21 distritos.",
  noWebgl: "Tu navegador no puede mostrar el mapa. Puedes ver las zonas en una lista.",
  noTiles: "No se ha podido cargar el mapa. Puedes seguir con la lista de zonas.",
};

type Failure = "webgl" | "tiles";

function matches(query: string): boolean {
  return window.matchMedia(query).matches;
}

function readPalette(): MapPalette {
  const css = getComputedStyle(document.documentElement);
  const entries = Object.entries(MAP_PALETTE_TOKENS).map(([key, token]) => [key, css.getPropertyValue(`--${token}`).trim()]);
  return Object.fromEntries(entries) as MapPalette;
}

function padding(mode: "overview" | "zone" | "island") {
  return cameraPadding(mode, { mobile: matches(MOBILE), height: window.innerHeight });
}

/**
 * Key points are labelled only where the label is seen whole: between the cards and apart from
 * each other, with the camera where it ends (`end`), so they stay in view while it comes closer.
 */
function labelOptions(end: ZoneCamera): KeyPointOptions {
  const { padding: pad, width, height } = end;
  const mobile = matches(MOBILE);
  const room = mobile ? LABEL_ROOM.mobile : LABEL_ROOM.desktop;
  const size = mobile ? LABEL_SIZE.mobile : LABEL_SIZE.desktop;
  const screen = (p: { lon: number; lat: number }) => projectAt(end, [p.lon, p.lat]);
  return {
    inView: (lon, lat) => {
      const at = screen({ lon, lat });
      if (!at) return false;
      return at.x >= pad.left + room.x && at.x <= width - pad.right - room.x && at.y >= pad.top + room.top && at.y <= height - pad.bottom;
    },
    apart: (a, b) => {
      const [pa, pb] = [screen(a), screen(b)];
      if (!pa || !pb) return false;
      return Math.abs(pa.x - pb.x) >= size.width || Math.abs(pa.y - pb.y) >= size.height;
    },
  };
}

function source(map: MapLibreMap, id: string): GeoJSONSource {
  return map.getSource(id) as GeoJSONSource;
}

function addZoneLayers(map: MapLibreMap, palette: MapPalette, onPick: (zone: ZoneProperties) => void): void {
  map.addSource("zones", { type: "geojson", data: EMPTY, promoteId: "admin_unit_id" });
  map.addSource("zone-selected", { type: "geojson", data: EMPTY });
  map.addSource("zone-mask", { type: "geojson", data: EMPTY });
  map.addSource("zone-base", { type: "geojson", data: EMPTY });
  map.addSource("zone-barrio", { type: "geojson", data: EMPTY });
  const { below, above } = zoneLayers(palette);
  for (const layer of below) map.addLayer(layer, BUILDING_LAYER);
  for (const layer of above) map.addLayer(layer);

  let hovered: string | number | undefined;
  const setHover = (id: string | number | undefined) => {
    if (hovered !== undefined) map.setFeatureState({ source: "zones", id: hovered }, { hover: false });
    hovered = id;
    if (id !== undefined) map.setFeatureState({ source: "zones", id }, { hover: true });
    map.getCanvas().style.cursor = id === undefined ? "" : "pointer";
  };
  map.on("mousemove", "zones-fill", (e: MapLayerMouseEvent) => setHover(e.features?.[0]?.id));
  map.on("mouseleave", "zones-fill", () => setHover(undefined));
  map.on("click", "zones-fill", (e: MapLayerMouseEvent) => {
    const zone = e.features?.[0]?.properties as ZoneProperties | undefined;
    if (zone) onPick(zone);
  });
}

function showOverview(map: MapLibreMap, zones: ZoneCollection, animate: boolean): void {
  source(map, "zone-selected").setData(EMPTY);
  source(map, "zone-base").setData(EMPTY);
  source(map, "zone-barrio").setData(EMPTY);
  source(map, "zone-mask").setData({ type: "Feature", geometry: maskAround(regionOf(zones)), properties: {} });
  map.fitBounds(boundsOfAll(zones) as LngLatBoundsLike, {
    padding: padding("overview"),
    pitch: 0,
    bearing: 0,
    duration: animate ? 1600 : 0,
  });
}

/** The «island» (the whole area in view, tilted, between the cards) and where the camera ends. */
function zoneCameras(map: MapLibreMap, area: ZoneGeometry, district: boolean): { island: ZoneCamera; end: ZoneCamera } {
  const bounds = boundsOf(area);
  const [west, south, east, north] = bounds;
  const { clientWidth: width, clientHeight: height } = map.getContainer();
  const base = {
    center: [(west + east) / 2, (south + north) / 2] as [number, number],
    pitch: matches(MOBILE) ? ZONE_PITCH.mobile : ZONE_PITCH.desktop,
    bearing: ZONE_BEARING,
    padding: padding("zone"),
    width,
    height,
  };
  const zoom = islandZoom(outlinePoints(area), base, padding("island"));
  return { island: { ...base, zoom }, end: { ...base, zoom: approachZoom(zoom, { district, extentKm: extentKm(bounds) }) } };
}

function easeInOut(t: number): number {
  return t < 0.5 ? 2 * t * t : 1 - (-2 * t + 2) ** 2 / 2;
}

/**
 * Camera flight to the zone (or to one of its barrios): it lands on the island, with the raised
 * edge in view, holds a moment and comes slowly closer to the 3D buildings, then turns gently.
 * With prefers-reduced-motion it goes straight to the end, without animation. `onLanded` fires
 * when the camera reaches its end, to label the key points in view (on the island they would
 * pile up: on mobile it is about six times farther).
 */
function showZone(map: MapLibreMap, zone: ZoneFeature, barrio: AdminFeature | null, onLanded: (end: ZoneCamera) => void): () => void {
  source(map, "zone-selected").setData(zone);
  source(map, "zone-mask").setData({ type: "Feature", geometry: maskAround(zone.geometry), properties: {} });
  source(map, "zone-base").setData(edgeWall(zone.geometry, ZONE_BASE.widthM));
  source(map, "zone-barrio").setData(barrio ?? EMPTY);
  const area = barrio?.geometry ?? zone.geometry;
  const { island, end } = zoneCameras(map, area, barrio !== null || zone.properties.level === "distrito");
  const camera = ({ center, zoom, pitch, bearing, padding: pad }: ZoneCamera) => ({ center, zoom, pitch, bearing, padding: pad });
  if (matches(REDUCED_MOTION)) {
    map.jumpTo(camera(end));
    onLanded(end);
    return () => map.stop();
  }
  let hold: number | undefined;
  const arrive = () => {
    onLanded(end);
    map.easeTo({ bearing: ZONE_BEARING + 15, duration: 18000, easing: (t) => t });
  };
  const approach = () => {
    if (end.zoom <= island.zoom) {
      arrive();
      return;
    }
    hold = window.setTimeout(() => {
      map.easeTo({ ...camera(end), duration: APPROACH_MS, easing: easeInOut });
      map.once("moveend", arrive);
    }, ISLAND_HOLD_MS);
  };
  map.flyTo({ ...camera(island), duration: FLIGHT_MS });
  if (map.isMoving()) map.once("moveend", approach);
  else approach();
  return () => {
    window.clearTimeout(hold);
    map.off("moveend", approach);
    map.off("moveend", arrive);
    map.stop();
  };
}

/** The zone's candidate key points, asked by zone and subcategory (a few KB, not whole layers). */
function loadPlaces(cache: Map<string, Promise<PlaceFeature[]>>, adminUnitId: string): Promise<PlaceFeature[]> {
  let request = cache.get(adminUnitId);
  if (!request) {
    const api = createApi();
    const lists = keyPointQueries().map((query) => api.places({ ...query, adminUnitId }));
    request = Promise.all(lists).then((all) => all.flat());
    cache.set(adminUnitId, request);
    request.catch(() => cache.delete(adminUnitId));
  }
  return request;
}

export default function VidaMap() {
  const { zones, activeZone, selectedZone, select, barrio } = useMapZones();
  const router = useRouter();
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const placesCache = useRef(new Map<string, Promise<PlaceFeature[]>>());
  const shownOverview = useRef(false);
  const [ready, setReady] = useState(false);
  const [failure, setFailure] = useState<Failure | null>(null);
  const [keyPoints, setKeyPoints] = useState<{ key: string; points: KeyPoint[] } | null>(null);
  // Zone (or barrio) whose flight has landed, and where its camera ends: key points are picked from that view.
  const [landed, setLanded] = useState<{ key: string; end: ZoneCamera } | null>(null);
  const view = activeZone ? `${activeZone.properties.zone_key}#${barrio?.properties.admin_unit_id ?? ""}` : null;

  // The map's click handler is registered once: it reads the current mode and actions from a ref.
  const pickRef = useRef<(zone: ZoneProperties) => void>(() => undefined);
  useEffect(() => {
    pickRef.current = (zone) => (activeZone ? router.push(zoneHref(zone)) : select(zone.zone_key));
  }, [activeZone, router, select]);

  useEffect(() => {
    const element = container.current;
    if (!element) return;
    let map: MapLibreMap;
    try {
      setWorkerUrl(WORKER_URL);
      map = new MapLibreMap({
        container: element,
        style: baseStyle(readPalette()),
        center: [-3.7, 40.42],
        zoom: 8.3,
        maxPitch: 70,
        // CRTM asks for «Powered by CRTM» with a link (data/catalog/sources/crtm_open_data.yaml)
        attributionControl: { compact: matches(MOBILE), customAttribution: ATTRIBUTION },
      });
    } catch {
      queueMicrotask(() => setFailure("webgl"));
      return;
    }
    mapRef.current = map;
    if (!matches(MOBILE)) map.addControl(new NavigationControl({ visualizePitch: true }), "bottom-right");
    map.on("load", () => {
      addZoneLayers(map, readPalette(), (zone) => pickRef.current(zone));
      // Fewer layers on mobile: no blurred glow and no raised edge around the zone.
      if (matches(MOBILE)) {
        map.setLayoutProperty("zone-glow", "visibility", "none");
        map.setLayoutProperty("zone-base", "visibility", "none");
      }
      setReady(true);
    });
    map.on("error", (event) => {
      if ((event as { sourceId?: string }).sourceId === "openmaptiles") setFailure("tiles");
    });
    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready || !zones) return;
    source(map, "zones").setData(zones);
  }, [ready, zones]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready || !zones) return;
    if (activeZone && view) {
      // Ask for the key points during the flight; a failure is handled when they are labelled.
      loadPlaces(placesCache.current, activeZone.properties.admin_unit_id).catch(() => undefined);
      const stop = showZone(map, activeZone, barrio, (end) => setLanded({ key: view, end }));
      return () => {
        // On unmount the map is already removed (its effect cleans up first).
        if (mapRef.current) stop();
        setLanded(null);
      };
    }
    showOverview(map, zones, shownOverview.current);
    shownOverview.current = true;
  }, [ready, zones, activeZone, barrio, view]);

  // Overview: outline the zone picked on the map (its card shows on the right).
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready || activeZone) return;
    source(map, "zone-selected").setData(selectedZone ?? EMPTY);
  }, [ready, activeZone, selectedZone]);

  useEffect(() => {
    if (!activeZone || !landed || landed.key !== view) return;
    let cancelled = false;
    const { key, end } = landed;
    // The district's places: in a barrio, those of the district that end in view are labelled.
    loadPlaces(placesCache.current, activeZone.properties.admin_unit_id)
      .then((places) => {
        if (!cancelled) setKeyPoints({ key, points: pickKeyPoints(places, end.center, labelOptions(end)) });
      })
      .catch(() => {
        // Key points are a complement: without them the zone, its outline and buildings still show.
        if (!cancelled) setKeyPoints({ key, points: NO_POINTS });
      });
    return () => {
      cancelled = true;
    };
  }, [activeZone, landed, view]);

  // Only once landed: back on a view already seen, its old labels would show over the island.
  const points = view && landed?.key === view && keyPoints?.key === view ? keyPoints.points : NO_POINTS;
  const labels = useMemo(
    () => (typeof document === "undefined" ? [] : points.map((point) => ({ point, element: document.createElement("div") }))),
    [points],
  );

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const markers = labels.map(({ point, element }) =>
      new Marker({ element, anchor: "bottom" }).setLngLat([point.lon, point.lat]).addTo(map),
    );
    return () => markers.forEach((marker) => marker.remove());
  }, [labels]);

  return (
    <>
      <div ref={container} className={styles.map} role="region" aria-label={TEXT.aria} />
      {failure && (
        <p role="alert" className={`glass ${styles.failure}`}>
          {failure === "webgl" ? TEXT.noWebgl : TEXT.noTiles}
        </p>
      )}
      {labels.map(({ point, element }) => createPortal(<KeyPointLabel point={point} />, element, point.id))}
    </>
  );
}
