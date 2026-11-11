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

import { createApi, type PlaceCategory } from "@/lib/api";
import { type KeyPoint, type KeyPointOptions, type PlaceFeature, pickKeyPoints, placesInZone } from "@/lib/map/places";
import { ZONE_BEARING, ZONE_PITCH, zoneZoom } from "@/lib/map/camera";
import { baseStyle, BUILDING_LAYER, MAP_PALETTE_TOKENS, type MapPalette, ZONE_BASE, zoneLayers } from "@/lib/map/style";
import {
  boundsOf,
  boundsOfAll,
  edgeWall,
  maskAround,
  regionOf,
  type ZoneCollection,
  type ZoneFeature,
  zoneHref,
  type ZoneProperties,
} from "@/lib/map/zones";

import KeyPointLabel from "./KeyPointLabel";
import { useMapZones } from "./MapProvider";
import styles from "./VidaMap.module.css";

const WORKER_URL = "/maplibre/maplibre-gl-worker.mjs"; // copied by scripts/copy-maplibre-worker.mjs
const MOBILE = "(max-width: 760px)";
const REDUCED_MOTION = "(prefers-reduced-motion: reduce)";
const FLIGHT_MS = 2800;
const KEY_POINT_CATEGORIES: PlaceCategory[] = ["transport", "health", "education"];
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

/** Room for the glass cards: search on the left, zone on the right, bottom sheet on mobile. */
function padding(mode: "overview" | "zone") {
  if (matches(MOBILE)) return mode === "zone" ? { top: 380, right: 0, bottom: 40, left: 0 } : { top: 150, right: 16, bottom: 200, left: 16 };
  // Zone view: a district at building zoom is wider than the gap, and the glass cards let the
  // map show through, so the side padding is smaller there.
  if (mode === "zone") return { top: 90, right: 380, bottom: 200, left: 440 };
  return { top: 100, right: 460, bottom: 40, left: 500 };
}

/** Key points are labelled only where the label is seen whole: between the cards and apart from each other. */
function labelOptions(map: MapLibreMap): KeyPointOptions {
  const pad = padding("zone");
  const mobile = matches(MOBILE);
  const room = mobile ? LABEL_ROOM.mobile : LABEL_ROOM.desktop;
  const size = mobile ? LABEL_SIZE.mobile : LABEL_SIZE.desktop;
  const { clientWidth: width, clientHeight: height } = map.getContainer();
  const screen = (p: { lon: number; lat: number }) => map.project([p.lon, p.lat]);
  return {
    inView: (lon, lat) => {
      const { x, y } = screen({ lon, lat });
      return x >= pad.left + room.x && x <= width - pad.right - room.x && y >= pad.top + room.top && y <= height - pad.bottom;
    },
    apart: (a, b) => {
      const [pa, pb] = [screen(a), screen(b)];
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
  source(map, "zone-mask").setData({ type: "Feature", geometry: maskAround(regionOf(zones)), properties: {} });
  map.fitBounds(boundsOfAll(zones) as LngLatBoundsLike, {
    padding: padding("overview"),
    pitch: 0,
    bearing: 0,
    duration: animate ? 1600 : 0,
  });
}

/** Camera flight to the zone, tilted ~60° (45° on mobile), then a slow turn. `onLanded` fires when the flight ends. */
function showZone(map: MapLibreMap, zone: ZoneFeature, onLanded: () => void): () => void {
  source(map, "zone-selected").setData(zone);
  source(map, "zone-mask").setData({ type: "Feature", geometry: maskAround(zone.geometry), properties: {} });
  source(map, "zone-base").setData(edgeWall(zone.geometry, ZONE_BASE.widthM));
  const mobile = matches(MOBILE);
  const bounds = boundsOf(zone.geometry);
  const fit = map.cameraForBounds(bounds as LngLatBoundsLike, { padding: padding("zone"), bearing: ZONE_BEARING });
  // Centre the zone in the free area between the cards (padding), at the zone zoom.
  map.flyTo({
    center: [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2],
    zoom: fit?.zoom === undefined ? undefined : zoneZoom(fit.zoom, mobile),
    pitch: mobile ? ZONE_PITCH.mobile : ZONE_PITCH.desktop,
    bearing: ZONE_BEARING,
    padding: padding("zone"),
    duration: FLIGHT_MS,
    essential: false, // with prefers-reduced-motion MapLibre jumps instead of flying
  });
  const turn = () => {
    onLanded();
    if (!matches(REDUCED_MOTION)) map.easeTo({ bearing: ZONE_BEARING + 15, duration: 18000, easing: (t) => t });
  };
  // With prefers-reduced-motion flyTo jumps at once, so the flight has already ended here.
  if (map.isMoving()) map.once("moveend", turn);
  else turn();
  return () => {
    map.off("moveend", turn);
    map.stop();
  };
}

function loadPlaces(cache: Map<PlaceCategory, Promise<PlaceFeature[]>>): Promise<PlaceFeature[]> {
  const api = createApi();
  const lists = KEY_POINT_CATEGORIES.map((category) => {
    let request = cache.get(category);
    if (!request) {
      request = api.places(category).then((body) => body.data.features);
      cache.set(category, request);
      request.catch(() => cache.delete(category));
    }
    return request;
  });
  return Promise.all(lists).then((all) => all.flat());
}

export default function VidaMap() {
  const { zones, activeZone, selectedZone, select } = useMapZones();
  const router = useRouter();
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const placesCache = useRef(new Map<PlaceCategory, Promise<PlaceFeature[]>>());
  const shownOverview = useRef(false);
  const [ready, setReady] = useState(false);
  const [failure, setFailure] = useState<Failure | null>(null);
  const [keyPoints, setKeyPoints] = useState<{ key: string; points: KeyPoint[] } | null>(null);
  // Zone whose camera flight has ended: its key points are picked from what is then in view.
  const [landed, setLanded] = useState<string | null>(null);

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
        attributionControl: { compact: matches(MOBILE), customAttribution: "Comunidad de Madrid · Powered by CRTM" },
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
    if (activeZone) {
      const stop = showZone(map, activeZone, () => setLanded(activeZone.properties.zone_key));
      return () => {
        stop();
        setLanded(null);
      };
    }
    showOverview(map, zones, shownOverview.current);
    shownOverview.current = true;
  }, [ready, zones, activeZone]);

  // Overview: outline the zone picked on the map (its card shows on the right).
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready || activeZone) return;
    source(map, "zone-selected").setData(selectedZone ?? EMPTY);
  }, [ready, activeZone, selectedZone]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !activeZone || landed !== activeZone.properties.zone_key) return;
    let cancelled = false;
    const [west, south, east, north] = boundsOf(activeZone.geometry);
    loadPlaces(placesCache.current)
      .then((places) => {
        if (cancelled) return;
        const center: [number, number] = [(west + east) / 2, (south + north) / 2];
        const points = pickKeyPoints(placesInZone(places, activeZone.properties), center, labelOptions(map));
        setKeyPoints({ key: activeZone.properties.zone_key, points });
      })
      .catch(() => {
        // Key points are a complement: without them the zone, its outline and buildings still show.
        if (!cancelled) setKeyPoints({ key: activeZone.properties.zone_key, points: NO_POINTS });
      });
    return () => {
      cancelled = true;
    };
  }, [activeZone, landed]);

  const points = activeZone && keyPoints?.key === activeZone.properties.zone_key ? keyPoints.points : NO_POINTS;
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
