import { readFileSync } from "node:fs";

import { validateStyleMin } from "@maplibre/maplibre-gl-style-spec";
import type { StyleSpecification } from "maplibre-gl";
import { describe, expect, it } from "vitest";

import {
  baseStyle,
  BUILDING_LAYER,
  BUILDINGS_3D_ZOOM,
  MAP_PALETTE_TOKENS,
  type MapPalette,
  OPENFREEMAP_TILEJSON,
  zoneLayers,
} from "../map/style";

const CSS = readFileSync(new URL("../../styles/tokens.css", import.meta.url), "utf8");

function tokenValue(name: string): string {
  const raw = new RegExp(`--${name}:\\s*([^;]+);`).exec(CSS)?.[1]?.trim();
  if (!raw) throw new Error(`missing --${name}`);
  const ref = /^var\(--([a-z0-9-]+)\)$/.exec(raw)?.[1];
  return ref ? tokenValue(ref) : raw;
}

const palette = Object.fromEntries(
  Object.entries(MAP_PALETTE_TOKENS).map(([key, token]) => [key, tokenValue(token)]),
) as MapPalette;

function withZone(style: StyleSpecification): StyleSpecification {
  const empty: GeoJSON.FeatureCollection = { type: "FeatureCollection", features: [] };
  const { below, above } = zoneLayers(palette);
  return {
    ...style,
    sources: {
      ...style.sources,
      zones: { type: "geojson", data: empty },
      "zone-selected": { type: "geojson", data: empty },
      "zone-mask": { type: "geojson", data: empty },
      "zone-base": { type: "geojson", data: empty },
    },
    layers: [...style.layers, ...below, ...above],
  };
}

describe("map style", () => {
  it("reads every map colour from tokens.css", () => {
    for (const value of Object.values(palette)) expect(value).toMatch(/^#[0-9a-f]{6}$/i);
  });

  it("is a valid MapLibre style (official style-spec validator)", () => {
    expect(validateStyleMin(baseStyle(palette))).toEqual([]);
  });

  it("stays valid with the zone layers", () => {
    expect(validateStyleMin(withZone(baseStyle(palette)))).toEqual([]);
  });

  it("uses open tiles without a key and has no text layers (no glyph server needed)", () => {
    const style = baseStyle(palette);
    expect(style.sources.openmaptiles).toEqual({ type: "vector", url: OPENFREEMAP_TILEJSON });
    expect(OPENFREEMAP_TILEJSON).not.toMatch(/key=|token=/i);
    expect(style.layers.some((l) => l.type === "symbol")).toBe(false);
    expect(style.glyphs).toBeUndefined();
  });

  it("extrudes buildings from zone zoom, honouring hide_3d", () => {
    const extrusions = baseStyle(palette).layers.filter((l) => l.type === "fill-extrusion");
    // (the zone's own raised edge, `zone-base`, is a zone overlay, not part of the base style)
    expect(extrusions.map((l) => l.id)).toEqual([BUILDING_LAYER]);
    expect(extrusions[0]?.minzoom).toBeGreaterThanOrEqual(13);
    expect(BUILDINGS_3D_ZOOM).toBe(14);
  });

  it("draws the outside mask above the buildings, so the surroundings fade", () => {
    const { below, above } = zoneLayers(palette);
    expect(above.map((l) => l.id)).toContain("zone-mask");
    expect(below.map((l) => l.id)).not.toContain("zone-mask");
  });
});
