/**
 * Vida Fácil base map (pure, unit tested): OpenFreeMap vector tiles (OpenMapTiles schema, no key)
 * with our own quiet style: lavender land, white roads, soft parks and water, a few quiet labels to
 * find your way (places, big roads, stations and water) and 3D buildings from zone zoom. Colours
 * come from tokens.css (--map-*), read at runtime by the map.
 */
import type { ExpressionSpecification, LayerSpecification, StyleSpecification, VectorSourceSpecification } from "maplibre-gl";

import { FIT_RAMP } from "@/lib/fit";

import { PATTERN_IMAGE } from "./gapMap";

/** TileJSON of OpenFreeMap's public instance; it carries the © OpenMapTiles / OSM attribution. */
export const OPENFREEMAP_TILEJSON = "https://tiles.openfreemap.org/planet";

/** OpenMapTiles carries every layer up to zoom 14 (buildings with their heights included). */
const OPENMAPTILES_MAXZOOM = 14;

/**
 * Where the base map comes from (OpenMapTiles schema): NEXT_PUBLIC_MAP_TILES_URL at build time,
 * as a TileJSON URL or a {z}/{x}/{y} template, local or not (the offline package serves an extract
 * of Madrid, e.g. with `pmtiles serve`); a path («/tiles/…») is made absolute with `origin`.
 * Unset or not http(s): OpenFreeMap, as always.
 */
export function mapTilesSource(setting: string | undefined, origin?: string): VectorSourceSpecification {
  const url = setting?.startsWith("/") && origin ? `${origin}${setting}` : setting;
  if (!url || !/^https?:\/\//.test(url)) return { type: "vector", url: OPENFREEMAP_TILEJSON };
  if (url.includes("{z}")) return { type: "vector", tiles: [url], maxzoom: OPENMAPTILES_MAXZOOM };
  return { type: "vector", url };
}

/** OpenFreeMap's glyphs (signed-distance-field fonts in PBF) for the labels. */
export const OPENFREEMAP_GLYPHS = "https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf";

/**
 * Where the labels' fonts come from: NEXT_PUBLIC_MAP_GLYPHS_URL at build time, like the tiles. The
 * offline package serves «/tiles/fonts/{fontstack}/{range}.pbf», made absolute with `origin`
 * (MapLibre wants an absolute glyphs URL). Unset, not http(s) or without both tokens: OpenFreeMap.
 */
export function mapGlyphsUrl(setting: string | undefined, origin?: string): string {
  const url = setting?.startsWith("/") && origin ? `${origin}${setting}` : setting;
  const usable = url && /^https?:\/\//.test(url) && url.includes("{fontstack}") && url.includes("{range}");
  return usable ? url : OPENFREEMAP_GLYPHS;
}

/**
 * The fonts of the labels. MapLibre joins a `text-font` list into one font stack name and asks the
 * server for it, and both glyph servers (OpenFreeMap and the offline package) only have «Noto Sans
 * Regular», «Bold» and «Italic», each alone: a list of two would be a 404.
 */
export const MAP_FONTS = { regular: ["Noto Sans Regular"], italic: ["Noto Sans Italic"] };

export const MAP_PALETTE_TOKENS = {
  land: "map-land",
  water: "map-water",
  park: "map-park",
  parkVivid: "map-park-vivid",
  parkStrong: "park",
  road: "map-road",
  rail: "map-rail",
  zone: "map-zone",
  building: "map-building",
  buildingTall: "map-building-tall",
  label: "map-label",
  labelStrong: "map-label-strong",
  labelWater: "map-label-water",
  violet: "violet",
  violetStrong: "violet-strong",
  violetSoft: "violet-soft",
  gapFalta: "map-falta",
  gapJusto: "map-justo",
  gapCubierto: "map-cubierto",
  gapSinDatos: "map-sin-datos",
  gapZonaPequena: "map-zona-pequena",
  gapZonaPequenaInk: "zona-pequena-ink",
  fitLow: "map-fit-low",
  fitNoCumple: "map-no-cumple",
  fitNoCumpleInk: "ink-soft",
  gapFaltaInk: "falta-ink",
  gapJustoInk: "justo-ink",
  sinDatos: "sin-datos",
  facColegio: "fac-colegio",
  facEscuelaInfantil: "fac-escuela-infantil",
  facCentroSalud: "fac-centro-salud",
  facHospital: "fac-hospital",
  facFarmacia: "fac-farmacia",
  facMayores: "fac-mayores",
} as const;

export type MapPalette = Record<keyof typeof MAP_PALETTE_TOKENS, string>;

export const BUILDING_LAYER = "buildings";
/** The base map's urban parks in a livelier green, hidden until «Parques» is on. */
export const PARKS_VIVID_LAYER = "parks-vivid";
/**
 * OpenMapTiles only carries building heights (render_height) in zoom-14 tiles; at 13 the
 * footprints come merged and flat. Buildings show from 13 and stand up from 14.
 */
export const BUILDINGS_MINZOOM = 13;
export const BUILDINGS_3D_ZOOM = 14;

/**
 * Stylised city view (brief: «estilo Cities: Skylines»): heights are exaggerated so a district
 * reads as 3D at zone zoom. Building heights are scenery, never shown as data.
 */
export const HEIGHT_SCALE = 2;

/**
 * Zones not painted by a row or a search (the first view): light enough for the roads, parks and
 * water under them to show, so the map reads as a map and not as a lilac stain (MAP-004).
 */
export const PLAIN_ZONE_OPACITY = 0.5;

/** Edge of the zone as a raised model (mockup 2): a thin wall just outside the outline. */
export const ZONE_BASE = { widthM: 14, heightM: 80 } as const;

const SRC = "openmaptiles";

function width(base: number): ExpressionSpecification {
  return ["interpolate", ["exponential", 1.5], ["zoom"], 9, base * 0.25, 13, base, 17, base * 5];
}

function lineLayer(
  id: string,
  classes: string[],
  color: string,
  base: number,
  minzoom: number,
  dash?: [number, number],
): LayerSpecification {
  return {
    id,
    type: "line",
    source: SRC,
    "source-layer": "transportation",
    minzoom,
    filter: ["match", ["get", "class"], classes, true, false],
    layout: { "line-cap": "round", "line-join": "round" },
    paint: { "line-color": color, "line-width": width(base), ...(dash ? { "line-dasharray": dash } : {}) },
  };
}

function buildingsLayer(p: MapPalette): LayerSpecification {
  const realHeight: ExpressionSpecification = ["coalesce", ["get", "render_height"], 0];
  return {
    id: BUILDING_LAYER,
    type: "fill-extrusion",
    source: SRC,
    "source-layer": "building",
    minzoom: BUILDINGS_MINZOOM,
    filter: ["!", ["to-boolean", ["get", "hide_3d"]]],
    paint: {
      "fill-extrusion-color": ["interpolate", ["linear"], realHeight, 0, p.building, 25, p.building, 90, p.buildingTall],
      "fill-extrusion-height": ["*", realHeight, HEIGHT_SCALE],
      "fill-extrusion-base": ["*", ["coalesce", ["get", "render_min_height"], 0], HEIGHT_SCALE],
      "fill-extrusion-opacity": 0.95,
      "fill-extrusion-vertical-gradient": true,
    },
  };
}

/** A place's name: OpenFreeMap carries `name`; the offline extract (tilemaker) only `name:latin`. */
const NAME: ExpressionSpecification = ["coalesce", ["get", "name"], ["get", "name:latin"]];
/** Railway stations of OSM in the `poi` layer: Metro, Cercanías and Metro Ligero (not their entrances). */
const STATIONS: ExpressionSpecification = [
  "all",
  ["==", ["get", "class"], "railway"],
  ["match", ["get", "subclass"], ["station", "subway", "halt", "tram_stop"], true, false],
];
export const STATION_MINZOOM = 13;

/**
 * Labels only in and around the Comunidad de Madrid (the box of the offline extract, line C): in a
 * tilted zone view the horizon brings low-zoom tiles of half of Europe and Africa, whose names in
 * other scripts would make MapLibre download their glyph ranges (about 240 KB) for nothing.
 */
export const LABEL_AREA: [number, number, number, number] = [-4.6, 39.85, -2.9, 41.2];
const [W, S, E, N] = LABEL_AREA;
const IN_AREA: ExpressionSpecification = [
  "within",
  { type: "Polygon", coordinates: [[[W, S], [E, S], [E, N], [W, N], [W, S]]] },
];

/** Every label layer keeps only its features in LABEL_AREA. */
function inArea(filter: ExpressionSpecification): ExpressionSpecification {
  return ["all", IN_AREA, filter];
}
/** The bottom label layer: the zones' edges and the districts' names go just under it (zoneLayers). */
export const FIRST_LABEL_LAYER = "label-river";
/**
 * The zones fade out from 11.5 to 13 (zoneLayers): up to there Madrid's districts are named after
 * the zones themselves (OpenMapTiles has no districts below zoom 11), and from there after the tiles.
 */
const ZONE_NAMES_MAXZOOM = 13;

function grow(from: number, to: number, zooms: [number, number] = [8, 14]): ExpressionSpecification {
  return ["interpolate", ["linear"], ["zoom"], zooms[0], from, zooms[1], to];
}

/** Quiet ink with a white halo, so a label reads over any zone colour without competing with it. */
function labelPaint(color: string) {
  return { "text-color": color, "text-halo-color": "#ffffff", "text-halo-width": 1.5, "text-halo-blur": 0.5 };
}

function placeLabel(
  id: string,
  classes: string[],
  minzoom: number,
  size: ExpressionSpecification | number,
  color: string,
  upper = false,
): LayerSpecification {
  return {
    id,
    type: "symbol",
    source: SRC,
    "source-layer": "place",
    minzoom,
    filter: inArea(["match", ["get", "class"], classes, true, false]),
    layout: {
      "text-field": NAME,
      "text-font": MAP_FONTS.regular,
      "text-size": size,
      "text-max-width": 8,
      // OSM ranks the places of a tile (lower is more important); the offline extract has no rank
      "symbol-sort-key": ["coalesce", ["get", "rank"], 99],
      ...(upper ? { "text-transform": "uppercase", "text-letter-spacing": 0.08 } : {}),
    },
    paint: labelPaint(color),
  };
}

/**
 * Labels to find your way (petición de Mariano tras probar producción, MAP-004), from the same
 * tiles, without new requests: rivers and reservoirs, the ref of motorways and trunk roads (M-30,
 * A-6), railway stations from zone zoom, barrios, districts and municipios by zoom. Listed bottom to
 * top: MapLibre places the top layers first, so municipios win a clash and stations give way.
 */
export function labelLayers(p: MapPalette): LayerSpecification[] {
  return [
    {
      id: FIRST_LABEL_LAYER,
      type: "symbol",
      source: SRC,
      "source-layer": "waterway",
      minzoom: 12,
      filter: inArea(["==", ["get", "class"], "river"]),
      layout: { "symbol-placement": "line", "text-field": NAME, "text-font": MAP_FONTS.italic, "text-size": 12, "text-letter-spacing": 0.05 },
      paint: labelPaint(p.labelWater),
    },
    {
      id: "label-water",
      type: "symbol",
      source: SRC,
      "source-layer": "water_name",
      filter: inArea(["==", ["geometry-type"], "Point"]),
      layout: { "text-field": NAME, "text-font": MAP_FONTS.italic, "text-size": grow(11, 13), "text-max-width": 8 },
      paint: labelPaint(p.labelWater),
    },
    {
      id: "label-road",
      type: "symbol",
      source: SRC,
      "source-layer": "transportation_name",
      minzoom: 9,
      // Lines with a ref (OpenMapTiles also puts motorway exits here, as points); no bus lanes
      filter: inArea([
        "all",
        ["==", ["geometry-type"], "LineString"],
        ["match", ["get", "class"], ["motorway", "trunk"], true, false],
        ["has", "ref"],
        ["!", ["in", "BUS", ["get", "ref"]]],
      ]),
      layout: {
        "symbol-placement": "line",
        "symbol-spacing": 400,
        "text-field": ["get", "ref"],
        "text-font": MAP_FONTS.regular,
        "text-size": grow(10.5, 12, [9, 14]),
        "text-letter-spacing": 0.04,
      },
      paint: labelPaint(p.label),
    },
    {
      // A small ring under each station's name, so it reads apart from a barrio's name and from the
      // centres (bigger filled dots)
      id: "station-ring",
      type: "circle",
      source: SRC,
      "source-layer": "poi",
      minzoom: STATION_MINZOOM,
      filter: inArea(STATIONS),
      paint: { "circle-radius": 3.5, "circle-color": "#ffffff", "circle-stroke-color": p.label, "circle-stroke-width": 1.5 },
    },
    {
      id: "label-station",
      type: "symbol",
      source: SRC,
      "source-layer": "poi",
      minzoom: STATION_MINZOOM,
      filter: inArea(STATIONS),
      layout: {
        "text-field": NAME,
        "text-font": MAP_FONTS.regular,
        "text-size": 11.5,
        "text-max-width": 8,
        "text-variable-anchor": ["left", "right", "top", "bottom"],
        "text-radial-offset": 0.6,
        "text-justify": "auto",
        "symbol-sort-key": ["coalesce", ["get", "rank"], 99],
      },
      paint: labelPaint(p.label),
    },
    placeLabel("label-barrio", ["quarter", "neighbourhood"], 13, grow(11.5, 13, [13, 16]), p.label),
    // Madrid's districts, and the suburbs of other towns, once the zones and their names have faded
    placeLabel("label-district", ["suburb"], ZONE_NAMES_MAXZOOM, 12.5, p.label, true),
    placeLabel("label-village", ["village"], 10, grow(11, 13, [10, 14]), p.label),
    placeLabel("label-town", ["town"], 0, grow(11.5, 15), p.labelStrong),
    placeLabel("label-city", ["city"], 0, grow(13, 18), p.labelStrong),
  ];
}

export function baseStyle(
  p: MapPalette,
  tiles: VectorSourceSpecification = mapTilesSource(undefined),
  glyphs: string = OPENFREEMAP_GLYPHS,
): StyleSpecification {
  return {
    version: 8,
    glyphs,
    sources: { [SRC]: tiles },
    // Soft lavender-tinted light: shaded walls stay lavender instead of turning grey.
    light: { anchor: "viewport", color: "#f6f4ff", intensity: 0.35, position: [1.2, 210, 35] },
    sky: {
      "sky-color": p.violetSoft,
      "horizon-color": p.land,
      "fog-color": p.land,
      "sky-horizon-blend": 0.6,
      "horizon-fog-blend": 0.7,
      "fog-ground-blend": 0.85,
      "atmosphere-blend": 0,
    },
    layers: [
      { id: "land", type: "background", paint: { "background-color": p.land } },
      {
        id: "green",
        type: "fill",
        source: SRC,
        "source-layer": "landcover",
        minzoom: 11, // regional vegetation is noise in the overview
        filter: ["match", ["get", "class"], ["grass", "wood"], true, false],
        paint: { "fill-color": p.park, "fill-opacity": 0.9 },
      },
      { id: "park", type: "fill", source: SRC, "source-layer": "park", paint: { "fill-color": p.park } },
      {
        // The urban parks of OSM (leisure=park: landcover «park» in OpenMapTiles), lit up while
        // «Parques» is on (VidaMap shows it); woods like the Casa de Campo are not in it
        id: PARKS_VIVID_LAYER,
        type: "fill",
        source: SRC,
        "source-layer": "landcover",
        minzoom: 11,
        filter: ["==", ["get", "subclass"], "park"],
        layout: { visibility: "none" },
        paint: { "fill-color": p.parkVivid },
      },
      { id: "water", type: "fill", source: SRC, "source-layer": "water", paint: { "fill-color": p.water } },
      {
        id: "waterway",
        type: "line",
        source: SRC,
        "source-layer": "waterway",
        minzoom: 11,
        paint: { "line-color": p.water, "line-width": width(1.2) },
      },
      lineLayer("rail", ["rail", "transit"], p.rail, 1, 11, [3, 2]),
      lineLayer("roads-minor", ["minor", "service"], p.road, 1.1, 12),
      lineLayer("roads-major", ["motorway", "trunk", "primary", "secondary", "tertiary"], p.road, 2, 7),
      buildingsLayer(p),
      // Above the buildings and the zones' fill; the zone overlays (mask, edges) and the centres go on top
      ...labelLayers(p),
    ],
  };
}

/**
 * Zone overlays (sources `zones`, `zone-mask`, `zone-selected`, `zone-base` and `zone-barrio` are
 * added by the map). A zone with a `gap` property (lib/map/gapMap.ts) is filled by its status in
 * the row the person picked, with the FALTA, JUSTO and small-zone patterns and a dashed edge for
 * SIN DATOS. After a search, a zone with a `fit` property (lib/fit.ts) is filled by its % when it
 * fits, almost white and crossed out when it fails a condition and grey with a dashed edge when
 * unknown. The
 * zone under the pointer gets a violet edge of its own layer, whatever its fill.
 * `below` goes under the buildings; `withLabels` just under the labels (FIRST_LABEL_LAYER): the
 * edges, so no white edge crosses a name, and the districts' names, the first to give way; `above`
 * on top of them all: MapLibre composites the extrusions first, so the white mask drawn above fades
 * the surroundings, buildings and labels included.
 */
export function zoneLayers(p: MapPalette): { below: LayerSpecification[]; withLabels: LayerSpecification[]; above: LayerSpecification[] } {
  const fadeOut = (from: number | ExpressionSpecification): ExpressionSpecification => ["interpolate", ["linear"], ["zoom"], 11.5, from, 13, 0];
  return {
    below: [
      {
        id: "zones-fill",
        type: "fill",
        source: "zones",
        paint: {
          "fill-color": [
            "case",
            ["has", "gap"],
            [
              "match",
              ["get", "gap"],
              "FALTA",
              p.gapFalta,
              "JUSTO",
              p.gapJusto,
              "CUBIERTO",
              p.gapCubierto,
              "ZONA_PEQUENA",
              p.gapZonaPequena,
              p.gapSinDatos,
            ],
            ["==", ["get", "fit"], "ENCAJA"],
            ["interpolate", ["linear"], ["to-number", ["get", "fit_pct"], 0], FIT_RAMP.low, p.fitLow, FIT_RAMP.high, p.violet],
            ["==", ["get", "fit"], "NO_CUMPLE"],
            p.fitNoCumple,
            ["==", ["get", "fit"], "SIN_DATOS"],
            p.gapSinDatos,
            p.zone,
          ],
          // A zone painted by a row or by the search hides the streets; a plain one lets them show
          "fill-opacity": fadeOut(["case", ["any", ["has", "gap"], ["has", "fit"]], 0.9, PLAIN_ZONE_OPACITY]),
        },
      },
      {
        // FALTA, JUSTO and small zones of a row; after a search, the zones that fail a condition
        // are crossed out, so they read apart from those that fit by more than their tone (R-06)
        id: "zones-pattern",
        type: "fill",
        source: "zones",
        filter: ["any", ["match", ["get", "gap"], ["FALTA", "JUSTO", "ZONA_PEQUENA"], true, false], ["==", ["get", "fit"], "NO_CUMPLE"]],
        paint: {
          "fill-pattern": [
            "case",
            ["==", ["get", "fit"], "NO_CUMPLE"],
            PATTERN_IMAGE.NO_CUMPLE,
            ["match", ["get", "gap"], "FALTA", PATTERN_IMAGE.FALTA, "JUSTO", PATTERN_IMAGE.JUSTO, PATTERN_IMAGE.ZONA_PEQUENA],
          ],
          "fill-opacity": fadeOut(1),
        },
      },
    ],
    withLabels: [
      {
        id: "zones-line",
        type: "line",
        source: "zones",
        paint: { "line-color": "#ffffff", "line-width": ["interpolate", ["linear"], ["zoom"], 8, 0.8, 12, 1.6], "line-opacity": fadeOut(1) },
      },
      {
        id: "zones-nodata",
        type: "line",
        source: "zones",
        filter: ["any", ["==", ["get", "gap"], "SIN_DATOS"], ["==", ["get", "fit"], "SIN_DATOS"]],
        paint: { "line-color": p.sinDatos, "line-width": 1.5, "line-dasharray": [2, 2], "line-opacity": fadeOut(1) },
      },
      {
        // Madrid's districts by their official names (the API's), at the zone's pole of inaccessibility
        id: "zone-names",
        type: "symbol",
        source: "zones",
        // From where Madrid is big enough for its districts to be told apart
        minzoom: 9,
        maxzoom: ZONE_NAMES_MAXZOOM,
        filter: ["==", ["get", "level"], "distrito"],
        layout: {
          "text-field": ["get", "name"],
          "text-font": MAP_FONTS.regular,
          "text-size": grow(10.5, 12.5, [10, 13]),
          "text-transform": "uppercase",
          "text-letter-spacing": 0.08,
          "text-max-width": 7,
        },
        paint: labelPaint(p.label),
      },
    ],
    above: [
      {
        id: "zone-mask",
        type: "fill",
        source: "zone-mask",
        paint: { "fill-color": "#ffffff", "fill-opacity": 0.78 },
      },
      {
        id: "zone-base",
        type: "fill-extrusion",
        source: "zone-base",
        paint: {
          "fill-extrusion-color": p.buildingTall,
          "fill-extrusion-height": ZONE_BASE.heightM,
          "fill-extrusion-opacity": 0.85,
          "fill-extrusion-vertical-gradient": true,
        },
      },
      {
        id: "zones-hover",
        type: "line",
        source: "zones",
        layout: { "line-join": "round" },
        paint: {
          "line-color": p.violet,
          "line-width": 2.5,
          // Camera expressions go outermost: the edge fades with the other zone layers at zone zoom
          "line-opacity": ["interpolate", ["linear"], ["zoom"], 11.5, ["case", ["boolean", ["feature-state", "hover"], false], 1, 0], 13, 0],
        },
      },
      {
        id: "zone-glow",
        type: "line",
        source: "zone-selected",
        layout: { "line-join": "round" },
        paint: { "line-color": p.violet, "line-width": 14, "line-blur": 10, "line-opacity": 0.45 },
      },
      {
        id: "zone-outline",
        type: "line",
        source: "zone-selected",
        layout: { "line-join": "round" },
        paint: { "line-color": p.violet, "line-width": ["interpolate", ["linear"], ["zoom"], 10, 2, 15, 3.5] },
      },
      {
        id: "zone-barrio-line",
        type: "line",
        source: "zone-barrio",
        layout: { "line-join": "round" },
        paint: { "line-color": p.violet, "line-width": 4, "line-dasharray": [2, 1] },
      },
    ],
  };
}

/** Source of every facility of the zone on screen (lib/map/facilities.ts), clustered by MapLibre. */
export const FACILITY_SOURCE = "facilities";
export const FACILITY_CLUSTER = { radius: 48, maxZoom: 16 } as const;
/** Each group counts its parks: a group made only of parks is drawn in green, any other stays violet. */
export const FACILITY_CLUSTER_PROPERTIES = { parks: ["+", ["case", ["==", ["get", "type"], "parque"], 1, 0]] } as const;
const CLUSTER_IMAGE = "facility-cluster-";
const PARK_TONE = "park-";

export type ClusterTone = "violet" | "park";

/** Each group is drawn as an image with its count, in the page's font: its id says the count and colour. */
export function clusterImageId(count: number, tone: ClusterTone = "violet"): string {
  return `${CLUSTER_IMAGE}${tone === "park" ? PARK_TONE : ""}${count}`;
}

/** The count and colour a group image stands for, or null when the id is not a group's. */
export function clusterImageOf(id: string): { count: number; tone: ClusterTone } | null {
  if (!id.startsWith(CLUSTER_IMAGE)) return null;
  const rest = id.slice(CLUSTER_IMAGE.length);
  const tone: ClusterTone = rest.startsWith(PARK_TONE) ? "park" : "violet";
  const count = Number(tone === "park" ? rest.slice(PARK_TONE.length) : rest);
  return Number.isInteger(count) && count > 0 ? { count, tone } : null;
}

/** Radius in CSS px of a group's circle: bigger groups, bigger circles; always a 44 px target or close. */
export function clusterRadius(count: number): number {
  return count < 10 ? 17 : count < 50 ? 20 : 23;
}

/**
 * The zone's facilities of one type (FASE_PRUEBAS, T3): groups as violet circles with their count
 * and single places as violet dots, above the buildings so none hides behind a block. Parks
 * (DATA-018) in green.
 */
export function facilityLayers(p: MapPalette): LayerSpecification[] {
  return [
    {
      id: "facilities-point",
      type: "circle",
      source: FACILITY_SOURCE,
      filter: ["!", ["has", "point_count"]],
      paint: {
        "circle-radius": 7,
        // One colour per type, so several types can be on at once (petición de Mariano, 13 nov)
        "circle-color": [
          "match",
          ["get", "type"],
          "parque",
          p.parkStrong,
          "colegio",
          p.facColegio,
          "escuela_infantil",
          p.facEscuelaInfantil,
          "centro_salud",
          p.facCentroSalud,
          "hospital",
          p.facHospital,
          "farmacia",
          p.facFarmacia,
          "mayores",
          p.facMayores,
          p.violetStrong,
        ],
        "circle-stroke-color": "#ffffff",
        "circle-stroke-width": 2.5,
      },
    },
    {
      id: "facilities-cluster",
      type: "symbol",
      source: FACILITY_SOURCE,
      filter: ["has", "point_count"],
      layout: {
        "icon-image": ["concat", CLUSTER_IMAGE, ["case", ["==", ["get", "parks"], ["get", "point_count"]], PARK_TONE, ""], ["to-string", ["get", "point_count"]]],
        "icon-allow-overlap": true,
        "icon-ignore-placement": true,
      },
    },
  ];
}
