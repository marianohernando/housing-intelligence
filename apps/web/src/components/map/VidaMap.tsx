"use client";

import "maplibre-gl/dist/maplibre-gl.css";

// MapLibre itself loads after the page (import() below): it is the largest script of the site, and
// a zone screen or the search can be read before it arrives. Only its types are imported here.
import type { GeoJSONSource, IControl, LngLatBoundsLike, Map as MapLibreMap, MapLayerMouseEvent } from "maplibre-gl";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { type CSSProperties, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { useDatasets } from "@/components/provenance/useDatasets";
import { useScenario } from "@/components/search/ScenarioProvider";
import Button from "@/components/ui/Button";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { parseColor } from "@/lib/color";
import { errorMessage } from "@/lib/errors";
import { paintFit } from "@/lib/fit";
import { facilitiesGeoJSON, selectedCountText, selectedFacilities } from "@/lib/map/facilities";
import { paintZones, PATTERN_IMAGE, patternPixels, type Rgba8 } from "@/lib/map/gapMap";
import { type KeyPoint, type KeyPointOptions, type PlaceFeature, pickKeyPoints } from "@/lib/map/places";
import { KEY_POINT_CATEGORIES } from "@/lib/map/zonePlaces";
import {
  approachZoom,
  cameraPadding,
  extentKm,
  firstViewBounds,
  islandZoom,
  MOBILE_QUERY,
  projectAt,
  SHEET_PEEK,
  ZONE_BEARING,
  ZONE_PITCH,
  type ZoneCamera,
} from "@/lib/map/camera";
import {
  baseStyle,
  BUILDING_LAYER,
  clusterImageOf,
  clusterRadius,
  type ClusterTone,
  FACILITY_CLUSTER,
  FACILITY_CLUSTER_PROPERTIES,
  FACILITY_SOURCE,
  facilityLayers,
  FIRST_LABEL_LAYER,
  MAP_PALETTE_TOKENS,
  mapGlyphsUrl,
  mapTilesSource,
  type MapPalette,
  PARKS_VIVID_LAYER,
  ZONE_BASE,
  zoneLayers,
} from "@/lib/map/style";
import {
  type AdminFeature,
  boundsOf,
  edgeWall,
  maskAround,
  outlinePoints,
  type ZoneFeature,
  type ZoneGeometry,
  zoneHref,
  type ZoneProperties,
} from "@/lib/map/zones";
import { MAP_CREDITS, mapAttribution } from "@/lib/provenance";

import { useFacilityLayer } from "./FacilityLayerProvider";
import { fetchZonePlaces } from "./fetchZones";
import FacilityLabel from "./FacilityLabel";
import { useGapLayer } from "./GapLayerProvider";
import KeyPointLabel from "./KeyPointLabel";
import { ZONE_LIST_TEXT } from "./ZoneListLink";
import { useMapZones } from "./MapProvider";
import styles from "./VidaMap.module.css";

const WORKER_URL = "/maplibre/maplibre-gl-worker.mjs"; // copied by scripts/copy-maplibre-worker.mjs
/** Base map tiles: OpenFreeMap unless the build sets NEXT_PUBLIC_MAP_TILES_URL (offline package). */
const MAP_TILES_URL = process.env.NEXT_PUBLIC_MAP_TILES_URL;
/** Fonts of the map labels: OpenFreeMap unless the build sets NEXT_PUBLIC_MAP_GLYPHS_URL (offline package). */
const MAP_GLYPHS_URL = process.env.NEXT_PUBLIC_MAP_GLYPHS_URL;
const MOBILE = MOBILE_QUERY;
const REDUCED_MOTION = "(prefers-reduced-motion: reduce)";
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
  // Only the street background failed: the zones are there (mapa.sin_calles)
  noStreets: "Mapa sin fondo de calles.",
  loading: "Cargando el mapa…",
  retry: "Reintentar",
  // mapa.aria.fila of pitch/textos_web.md (D-213), with the neighbours of gap-0.3
  ariaRow: (label: string) =>
    `Cada zona tiene el color de su estado en ${label.toLowerCase()} frente a los municipios de su tipo (los pueblos muy pequeños, junto con sus vecinos); la leyenda lo explica.`,
  ariaFit: "Cada zona tiene el color de su encaje con tu búsqueda; la leyenda lo explica y la lista de zonas que encajan está junto al mapa.",
  // mapa.aria.centros of pitch/textos_web.md (T3)
  ariaFacilities: (count: string) => `En el mapa salen, agrupados, ${count.charAt(0).toLowerCase()}${count.slice(1)}; su lista está en «Todos los centros».`,
};
/** MapLibre's UI strings this map shows, in Spanish (its `locale` option patches the English defaults): mapa.fuentes. */
const MAP_LOCALE = { "AttributionControl.ToggleAttribution": "Fuentes y licencias de los datos" };
const NEW_TAB = " (se abre en una pestaña nueva)";
const FACILITY_LAYERS: string[] = ["facilities-point", "facilities-cluster"];

type Failure = "webgl" | "tiles" | "script";
type MapLibre = typeof import("maplibre-gl");

function matches(query: string): boolean {
  return window.matchMedia(query).matches;
}

function readPalette(): MapPalette {
  const css = getComputedStyle(document.documentElement);
  const entries = Object.entries(MAP_PALETTE_TOKENS).map(([key, token]) => [key, css.getPropertyValue(`--${token}`).trim()]);
  return Object.fromEntries(entries) as MapPalette;
}

function padding(mode: "overview" | "zone" | "island") {
  return cameraPadding(mode, { mobile: matches(MOBILE), width: window.innerWidth, height: window.innerHeight });
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

/**
 * The sources whose licences ask to be cited where their data shows (mapAttribution). Spelled out,
 * the cards would cover them (desktop) or they would show through the sheet and be the page's
 * largest paint (mobile, LCP). So on every screen MapLibre's compact control is folded behind its
 * (i) button (MapLibre opens it until the map is first dragged), at the top left of the map's free
 * area (VidaMap.module.css places it for each screen, also after turning the phone). One tap or
 * click opens it, and the pages with a footer list every citation. Beside it, always in view, the
 * two citations that cannot start folded (MAP_CREDITS). Returns its controls, to change the citations.
 */
function addAttribution(lib: MapLibre, map: MapLibreMap, citations: string): IControl[] {
  const control = new lib.AttributionControl({ compact: true, customAttribution: citations });
  map.addControl(control, "top-left");
  const folded = map.getContainer().querySelector(".maplibregl-ctrl-attrib");
  folded?.classList.remove("maplibregl-compact-show");
  folded?.removeAttribute("open");
  // Right after it, so the CSS hides it while the full list (which has both) is open
  const credits = creditsControl();
  map.addControl(credits, "top-left");
  return [control, credits];
}

/** MAP_CREDITS as a MapLibre control: a short line of links with the (i)'s white background (AA contrast). */
function creditsControl(): IControl {
  const line = document.createElement("p");
  line.className = `maplibregl-ctrl ${styles.credits}`;
  MAP_CREDITS.forEach(({ text, href }, i) => {
    if (i > 0) line.append(" · ");
    const link = document.createElement("a");
    link.href = href;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = text;
    const hint = document.createElement("span");
    hint.className = "visually-hidden";
    hint.textContent = NEW_TAB;
    link.append(hint);
    line.append(link);
  });
  return { onAdd: () => line, onRemove: () => line.remove() };
}

/**
 * The FALTA stripes, JUSTO dots and small-zone lines the zones are filled with when the map shows
 * a row of «Qué falta», and the crossed diagonals of the zones that fail a condition after a search.
 */
function addPatterns(map: MapLibreMap, palette: MapPalette): void {
  const scale = Math.min(2, Math.ceil(window.devicePixelRatio || 1));
  const ink = (color: string, alpha: number): Rgba8 => {
    const { r, g, b } = parseColor(color);
    return [r, g, b, alpha];
  };
  map.addImage(PATTERN_IMAGE.FALTA, patternPixels("stripes", ink(palette.gapFaltaInk, 170), scale), { pixelRatio: scale });
  map.addImage(PATTERN_IMAGE.JUSTO, patternPixels("dots", ink(palette.gapJustoInk, 200), scale), { pixelRatio: scale });
  map.addImage(PATTERN_IMAGE.ZONA_PEQUENA, patternPixels("lines", ink(palette.gapZonaPequenaInk, 120), scale), { pixelRatio: scale });
  map.addImage(PATTERN_IMAGE.NO_CUMPLE, patternPixels("cross", ink(palette.fitNoCumpleInk, 80), scale), { pixelRatio: scale });
}

function addZoneLayers(map: MapLibreMap, palette: MapPalette, onPick: (zone: ZoneProperties) => void): void {
  map.addSource("zones", { type: "geojson", data: EMPTY, promoteId: "admin_unit_id" });
  map.addSource("zone-selected", { type: "geojson", data: EMPTY });
  map.addSource("zone-mask", { type: "geojson", data: EMPTY });
  map.addSource("zone-base", { type: "geojson", data: EMPTY });
  map.addSource("zone-barrio", { type: "geojson", data: EMPTY });
  const { below, withLabels, above } = zoneLayers(palette);
  for (const layer of below) map.addLayer(layer, BUILDING_LAYER);
  for (const layer of withLabels) map.addLayer(layer, FIRST_LABEL_LAYER);
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
    // A tap on a facility of the zone is not a tap on the zone under it
    if (map.getLayer("facilities-point") && map.queryRenderedFeatures(e.point, { layers: FACILITY_LAYERS }).length > 0) return;
    const zone = e.features?.[0]?.properties as ZoneProperties | undefined;
    if (zone) onPick(zone);
  });
}

/** A group of facilities as an image: a violet (or, for parks, green) circle with its count, for the screen's pixel ratio. */
function clusterImage(count: number, tone: ClusterTone, palette: MapPalette): { image: ImageData; pixelRatio: number } | null {
  const scale = Math.min(2, Math.ceil(window.devicePixelRatio || 1));
  const radius = clusterRadius(count);
  const size = (radius + 3) * 2 * scale;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");
  if (!ctx) return null;
  ctx.scale(scale, scale);
  const centre = radius + 3;
  ctx.beginPath();
  ctx.arc(centre, centre, radius, 0, Math.PI * 2);
  ctx.fillStyle = tone === "park" ? palette.parkStrong : palette.violetStrong;
  ctx.fill();
  ctx.lineWidth = 3;
  ctx.strokeStyle = "#ffffff";
  ctx.stroke();
  ctx.fillStyle = "#ffffff";
  ctx.font = `600 ${count < 100 ? 15 : 13}px ${getComputedStyle(document.body).fontFamily}`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(String(count), centre, centre + 1);
  return { image: ctx.getImageData(0, 0, size, size), pixelRatio: scale };
}

/** Clicks on the facilities layer: a group zooms in, a single place opens its label, the rest closes it. */
interface FacilityHandlers {
  onPlace: (id: string) => void;
  onNothing: () => void;
}

function addFacilityLayers(map: MapLibreMap, palette: MapPalette, handlers: FacilityHandlers): void {
  map.addSource(FACILITY_SOURCE, {
    type: "geojson",
    data: EMPTY,
    cluster: true,
    clusterRadius: FACILITY_CLUSTER.radius,
    clusterMaxZoom: FACILITY_CLUSTER.maxZoom,
    clusterProperties: FACILITY_CLUSTER_PROPERTIES,
  });
  for (const layer of facilityLayers(palette)) map.addLayer(layer);
  map.on("styleimagemissing", (e: { id: string }) => {
    const group = clusterImageOf(e.id);
    const drawn = group === null || map.hasImage(e.id) ? null : clusterImage(group.count, group.tone, palette);
    if (drawn) map.addImage(e.id, drawn.image, { pixelRatio: drawn.pixelRatio });
  });
  for (const layer of FACILITY_LAYERS) {
    map.on("mouseenter", layer, () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", layer, () => (map.getCanvas().style.cursor = ""));
  }
  map.on("click", "facilities-cluster", (e: MapLayerMouseEvent) => {
    const feature = e.features?.[0];
    const clusterId = feature?.properties?.cluster_id as number | undefined;
    if (!feature || clusterId === undefined || feature.geometry.type !== "Point") return;
    const [lon = 0, lat = 0] = feature.geometry.coordinates;
    source(map, FACILITY_SOURCE)
      .getClusterExpansionZoom(clusterId)
      .then((zoom) => map.easeTo({ center: [lon, lat], zoom, duration: matches(REDUCED_MOTION) ? 0 : 800 }))
      .catch(() => undefined);
  });
  map.on("click", (e) => {
    const [hit] = map.queryRenderedFeatures(e.point, { layers: ["facilities-point"] });
    const id = hit?.properties?.id as string | undefined;
    if (id) handlers.onPlace(id);
    else if (map.queryRenderedFeatures(e.point, { layers: ["facilities-cluster"] }).length === 0) handlers.onNothing();
  });
}

function showOverview(map: MapLibreMap, animate: boolean): void {
  source(map, "zone-selected").setData(EMPTY);
  source(map, "zone-base").setData(EMPTY);
  source(map, "zone-barrio").setData(EMPTY);
  // No mask in the overview: with a hole per zone (outlines simplified one by one, so neighbours
  // overlap a little) MapLibre filled white wedges across the region, over the names too. The
  // lilac zones already tell the region apart; a zone's own mask has one hole and stays.
  source(map, "zone-mask").setData(EMPTY);
  // Madrid and its first ring (lib/map/camera.ts, FIRST_VIEW), not the whole region in lilac
  map.fitBounds(firstViewBounds(matches(MOBILE)) as LngLatBoundsLike, {
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

/** The zone's candidate key points, asked by zone and subcategory with «Todos los centros» (a few KB, not whole layers). */
function loadPlaces(adminUnitId: string): Promise<PlaceFeature[]> {
  return fetchZonePlaces(adminUnitId, KEY_POINT_CATEGORIES);
}

export default function VidaMap() {
  const { zones, status, error, retry, activeZone, selectedZone, select, barrio, mapMayLoad } = useMapZones();
  const { row, data: gapData } = useGapLayer();
  const { result } = useScenario();
  const facilities = useFacilityLayer();
  const overview = usePathname() === "/";
  // Overview coloured by a row of «Qué falta» once its statuses arrive, or by the fit with the
  // search («Encaje con tu búsqueda») once there is one; plain zones otherwise
  const painted = useMemo(() => {
    if (!zones || !overview) return zones;
    if (row) return gapData ? paintZones(zones, gapData.byZone) : zones;
    return result ? paintFit(zones, result.all_zones) : zones;
  }, [zones, overview, row, gapData, result]);
  const paintedAria = !overview || painted === zones ? null : row && gapData ? TEXT.ariaRow(gapData.info.label) : TEXT.ariaFit;
  // The zone's facilities of the types pressed in «Todos los centros» (several at once), or none
  const facilityList = useMemo(
    () => (activeZone && facilities.types.length && facilities.groups ? selectedFacilities(facilities.groups, facilities.types) : null),
    [activeZone, facilities.types, facilities.groups],
  );
  const facilityCount = activeZone && facilities.groups ? selectedCountText(facilities.groups, facilities.types, activeZone.properties.name, { empty: false }) : null;
  const facilityAria = facilityCount ? TEXT.ariaFacilities(facilityCount) : null;
  const mapAria = [TEXT.aria, paintedAria, facilityAria].filter(Boolean).join(" ");
  const slow = useSlow(status === "loading");
  const router = useRouter();
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const libRef = useRef<MapLibre | null>(null);
  const shownOverview = useRef(false);
  // The map screens have no footer: the map cites every source with the attribution_text of
  // /datasets (shared request), or the fallback while it has not answered
  const { data: datasets } = useDatasets();
  const attribution = useRef(mapAttribution(null));
  // The citations the map shows and their controls, to put the API's in when they arrive
  const attributionShown = useRef<{ citations: string; controls: IControl[] } | null>(null);
  useEffect(() => {
    attribution.current = mapAttribution(datasets?.datasets ?? null);
    const [map, lib, shown] = [mapRef.current, libRef.current, attributionShown.current];
    // Created before /datasets answered: the map takes its citations, open if the person opened them
    if (!map || !lib || !shown || shown.citations === attribution.current) return;
    const wasOpen = map.getContainer().querySelector(".maplibregl-compact-show") !== null;
    for (const control of shown.controls) map.removeControl(control);
    attributionShown.current = { citations: attribution.current, controls: addAttribution(lib, map, attribution.current) };
    const details = wasOpen ? map.getContainer().querySelector(".maplibregl-ctrl-attrib") : null;
    details?.classList.add("maplibregl-compact-show");
    details?.setAttribute("open", "");
  }, [datasets]);
  const [ready, setReady] = useState(false);
  const [failure, setFailure] = useState<Failure | null>(null);
  // No WebGL, or neither the streets nor the zones: the map cannot be used, the list can
  const strongFailure = failure === "webgl" || failure === "script" || (failure === "tiles" && status === "error");
  const [keyPoints, setKeyPoints] = useState<{ key: string; points: KeyPoint[] } | null>(null);
  // Zone (or barrio) whose flight has landed, and where its camera ends: key points are picked from that view.
  const [landed, setLanded] = useState<{ key: string; end: ZoneCamera } | null>(null);
  const view = activeZone ? `${activeZone.properties.zone_key}#${barrio?.properties.admin_unit_id ?? ""}` : null;

  // The map's click handler is registered once: it reads the current mode and actions from a ref.
  const pickRef = useRef<(zone: ZoneProperties) => void>(() => undefined);
  useEffect(() => {
    pickRef.current = (zone) => (activeZone ? router.push(zoneHref(zone)) : select(zone.zone_key));
  }, [activeZone, router, select]);
  const facilityRef = useRef<FacilityHandlers>({ onPlace: () => undefined, onNothing: () => undefined });
  const { pick } = facilities;
  useEffect(() => {
    facilityRef.current = {
      onPlace: (id) => pick(facilityList?.find((f) => f.id === id) ?? null),
      onNothing: () => pick(null),
    };
  }, [facilityList, pick]);

  useEffect(() => {
    const element = container.current;
    if (!element || !mapMayLoad) return;
    let map: MapLibreMap | null = null;
    let cancelled = false;
    // The map once MapLibre is in: base style, zone and facility layers, controls and errors
    const createMap = (lib: MapLibre, element: HTMLDivElement): MapLibreMap | null => {
      let instance: MapLibreMap;
      try {
        lib.setWorkerUrl(WORKER_URL);
        instance = new lib.Map({
          container: element,
          style: baseStyle(
            readPalette(),
            mapTilesSource(MAP_TILES_URL, window.location.origin),
            mapGlyphsUrl(MAP_GLYPHS_URL, window.location.origin),
          ),
          // Where the overview starts (showOverview), so the first tiles are those of that view
          bounds: firstViewBounds(matches(MOBILE)) as LngLatBoundsLike,
          fitBoundsOptions: { padding: padding("overview") },
          maxPitch: 70,
          // Added below, where it fits each screen (addAttribution)
          attributionControl: false,
          locale: MAP_LOCALE,
        });
      } catch {
        setFailure("webgl");
        return null;
      }
      const created = instance;
      mapRef.current = created;
      attributionShown.current = { citations: attribution.current, controls: addAttribution(lib, created, attribution.current) };
      if (!matches(MOBILE)) created.addControl(new lib.NavigationControl({ visualizePitch: true }), "bottom-right");
      created.on("load", () => {
        const palette = readPalette();
        addPatterns(created, palette);
        addZoneLayers(created, palette, (zone) => pickRef.current(zone));
        addFacilityLayers(created, palette, {
          onPlace: (id) => facilityRef.current.onPlace(id),
          onNothing: () => facilityRef.current.onNothing(),
        });
        // Fewer layers on mobile: no blurred glow and no raised edge around the zone.
        if (matches(MOBILE)) {
          created.setLayoutProperty("zone-glow", "visibility", "none");
          created.setLayoutProperty("zone-base", "visibility", "none");
        }
        setReady(true);
      });
      created.on("error", (event) => {
        // The base map source failed (its TileJSON, or the network): not one tile outside a local extract
        const { sourceId, tile } = event as { sourceId?: string; tile?: unknown };
        if (sourceId === "openmaptiles" && !tile) setFailure("tiles");
      });
      return created;
    };
    import("maplibre-gl")
      .then((lib) => {
        if (cancelled) return;
        libRef.current = lib;
        map = createMap(lib, element);
      })
      .catch(() => {
        if (!cancelled) setFailure("script");
      });
    return () => {
      cancelled = true;
      map?.remove();
      mapRef.current = null;
      attributionShown.current = null;
    };
  }, [mapMayLoad]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready || !painted) return;
    source(map, "zones").setData(painted);
  }, [ready, painted]);

  // Every facility of the type picked, once the camera has landed on the zone (not during the flight)
  const facilitiesShown = Boolean(view && landed?.key === view && facilityList);
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready) return;
    source(map, FACILITY_SOURCE).setData(facilitiesShown && facilityList ? facilitiesGeoJSON(facilityList) : EMPTY);
  }, [ready, facilitiesShown, facilityList]);

  // With «Parques» on, the base map's parks light up under their green dots
  const parksLit = facilitiesShown && facilities.types.includes("parque");
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready || !map.getLayer(PARKS_VIVID_LAYER)) return;
    map.setLayoutProperty(PARKS_VIVID_LAYER, "visibility", parksLit ? "visible" : "none");
  }, [ready, parksLit]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !ready || !zones) return;
    if (activeZone && view) {
      // Ask for the key points during the flight; a failure is handled when they are labelled.
      loadPlaces(activeZone.properties.admin_unit_id).catch(() => undefined);
      const stop = showZone(map, activeZone, barrio, (end) => setLanded({ key: view, end }));
      return () => {
        // On unmount the map is already removed (its effect cleans up first).
        if (mapRef.current) stop();
        setLanded(null);
      };
    }
    showOverview(map, shownOverview.current);
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
    loadPlaces(activeZone.properties.admin_unit_id)
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
    const lib = libRef.current;
    if (!map || !lib) return;
    const markers = labels.map(({ point, element }) =>
      new lib.Marker({ element, anchor: "bottom" }).setLngLat([point.lon, point.lat]).addTo(map),
    );
    return () => markers.forEach((marker) => marker.remove());
  }, [labels]);

  // The facility tapped on the map, with its label like a key point's
  const picked = facilitiesShown ? facilities.picked : null;
  const pickedLabel = useMemo(
    () => (picked && typeof document !== "undefined" ? { facility: picked, element: document.createElement("div") } : null),
    [picked],
  );
  useEffect(() => {
    const map = mapRef.current;
    const lib = libRef.current;
    if (!map || !lib || !pickedLabel) return;
    const { facility, element } = pickedLabel;
    const marker = new lib.Marker({ element, anchor: "bottom" }).setLngLat([facility.lon, facility.lat]).addTo(map);
    return () => {
      marker.remove();
    };
  }, [pickedLabel]);

  return (
    <>
      <div
        ref={container}
        className={styles.map}
        role="region"
        aria-label={mapAria}
        style={{ "--sheet-peek": `${SHEET_PEEK * 100}dvh` } as CSSProperties}
      />
      {strongFailure && (
        <div role="alert" className={`glass ${styles.failure}`}>
          <p>{failure === "webgl" ? TEXT.noWebgl : TEXT.noTiles}</p>
          <Link href="/zonas">{ZONE_LIST_TEXT}</Link>
        </div>
      )}
      {/* Without the street background the zones still show and work: a quiet note is enough */}
      {failure === "tiles" && !strongFailure && status === "ready" && (
        <p role="status" className={`glass ${styles.note}`}>
          {TEXT.noStreets}
        </p>
      )}
      {/* The outlines of the zones; a zone screen tells its own loading and errors (ZoneIntro). */}
      {!strongFailure && overview && status === "loading" && (
        <p role="status" className={`glass ${styles.failure}`}>
          {TEXT.loading}
          {slow && ` ${SLOW_TEXT}`}
        </p>
      )}
      {!strongFailure && overview && status === "error" && error && (
        <div role="alert" className={`glass ${styles.failure}`}>
          <p>{errorMessage(error)}</p>
          <Button variant="secondary" onClick={retry}>
            {TEXT.retry}
          </Button>
        </div>
      )}
      {labels.map(({ point, element }) => createPortal(<KeyPointLabel point={point} />, element, point.id))}
      {pickedLabel && createPortal(<FacilityLabel facility={pickedLabel.facility} />, pickedLabel.element, pickedLabel.facility.id)}
    </>
  );
}
