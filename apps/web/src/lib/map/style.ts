/**
 * Vida Fácil base map (pure, unit tested): OpenFreeMap vector tiles (OpenMapTiles schema, no key)
 * with our own quiet style: lavender land, white roads, soft parks and water, no labels, and 3D
 * buildings from zone zoom. Colours come from tokens.css (--map-*), read at runtime by the map.
 */
import type { ExpressionSpecification, LayerSpecification, StyleSpecification } from "maplibre-gl";

/** TileJSON of OpenFreeMap's public instance; it carries the © OpenMapTiles / OSM attribution. */
export const OPENFREEMAP_TILEJSON = "https://tiles.openfreemap.org/planet";

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
  violetSoft: "violet-soft",
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

export function baseStyle(p: MapPalette): StyleSpecification {
  return {
    version: 8,
    sources: { [SRC]: { type: "vector", url: OPENFREEMAP_TILEJSON } },
    light: { anchor: "viewport", color: "#ffffff", intensity: 0.45, position: [1.2, 210, 35] },
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
        paint: { "fill-color": p.park, "fill-opacity": 0.75 },
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
 * Zone overlays (sources `zones`, `zone-mask` and `zone-selected` are added by the map).
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
          "fill-color": ["case", ["boolean", ["feature-state", "hover"], false], p.violetSoft, p.zone],
          "fill-opacity": fadeOut(0.9),
        },
      },
    ],
    above: [
      {
        id: "zone-mask",
        type: "fill",
        source: "zone-mask",
        paint: { "fill-color": "#ffffff", "fill-opacity": 0.62 },
      },
      {
        id: "zones-line",
        type: "line",
        source: "zones",
        paint: { "line-color": "#ffffff", "line-width": ["interpolate", ["linear"], ["zoom"], 8, 0.8, 12, 1.6], "line-opacity": fadeOut(1) },
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
    ],
  };
}
