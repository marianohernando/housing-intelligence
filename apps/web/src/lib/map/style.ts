/**
 * Vida Fácil base map (pure, unit tested): OpenFreeMap vector tiles (OpenMapTiles schema, no key)
 * with our own quiet style: lavender land, white roads, soft parks and water, no labels, and 3D
 * buildings from zone zoom. Colours come from tokens.css (--map-*), read at runtime by the map.
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
 * of Madrid, e.g. with `pmtiles serve`). Unset or not http(s): OpenFreeMap, as always.
 */
export function mapTilesSource(url: string | undefined): VectorSourceSpecification {
  if (!url || !/^https?:\/\//.test(url)) return { type: "vector", url: OPENFREEMAP_TILEJSON };
  if (url.includes("{z}")) return { type: "vector", tiles: [url], maxzoom: OPENMAPTILES_MAXZOOM };
  return { type: "vector", url };
}

export const MAP_PALETTE_TOKENS = {
  land: "map-land",
  water: "map-water",
  park: "map-park",
  road: "map-road",
  rail: "map-rail",
  zone: "map-zone",
  building: "map-building",
  buildingTall: "map-building-tall",
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
} as const;

export type MapPalette = Record<keyof typeof MAP_PALETTE_TOKENS, string>;

export const BUILDING_LAYER = "buildings";
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

export function baseStyle(p: MapPalette, tiles: VectorSourceSpecification = mapTilesSource(undefined)): StyleSpecification {
  return {
    version: 8,
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
 * `below` goes under the buildings; `above` on top of them: MapLibre composites the extrusions
 * first, so the white mask drawn above fades the surroundings, buildings included.
 */
export function zoneLayers(p: MapPalette): { below: LayerSpecification[]; above: LayerSpecification[] } {
  const fadeOut = (from: number): ExpressionSpecification => ["interpolate", ["linear"], ["zoom"], 11.5, from, 13, 0];
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
          "fill-opacity": fadeOut(0.9),
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
const CLUSTER_IMAGE = "facility-cluster-";

/** Each group is drawn as an image with its count (the map has no glyph server): its id says the count. */
export function clusterImageId(count: number): string {
  return `${CLUSTER_IMAGE}${count}`;
}

export function clusterImageCount(id: string): number | null {
  if (!id.startsWith(CLUSTER_IMAGE)) return null;
  const count = Number(id.slice(CLUSTER_IMAGE.length));
  return Number.isInteger(count) && count > 0 ? count : null;
}

/** Radius in CSS px of a group's circle: bigger groups, bigger circles; always a 44 px target or close. */
export function clusterRadius(count: number): number {
  return count < 10 ? 17 : count < 50 ? 20 : 23;
}

/**
 * The zone's facilities of one type (FASE_PRUEBAS, T3): groups as violet circles with their count
 * and single places as violet dots, above the buildings so none hides behind a block.
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
        "circle-color": p.violetStrong,
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
        "icon-image": ["concat", CLUSTER_IMAGE, ["to-string", ["get", "point_count"]]],
        "icon-allow-overlap": true,
        "icon-ignore-placement": true,
      },
    },
  ];
}
