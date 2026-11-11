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
      "zone-barrio": { type: "geojson", data: empty },
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

  it("marks the zone under the pointer with an edge of its own, so the fill of a row or of the fit stays", () => {
    const { below, above } = zoneLayers(palette);
    const hover = above.find((l) => l.id === "zones-hover");
    expect(hover).toMatchObject({ type: "line", source: "zones" });
    expect(JSON.stringify(hover?.type === "line" && hover.paint?.["line-opacity"])).toContain('"feature-state","hover"');
    const fill = below.find((l) => l.id === "zones-fill");
    expect(JSON.stringify(fill?.type === "fill" && fill.paint?.["fill-color"])).not.toContain("feature-state");
  });

  it("paints the fit after a search: a ramp for the zones that fit, apart those that fail or are unknown", () => {
    const fill = JSON.stringify(zoneLayers(palette).below.find((l) => l.id === "zones-fill")?.paint);
    for (const c of ["ENCAJA", "NO_CUMPLE", "SIN_DATOS", "fit_pct", palette.fitLow, palette.violet, palette.fitNoCumple]) expect(fill).toContain(c);
    const noData = zoneLayers(palette).above.find((l) => l.id === "zones-nodata");
    expect(JSON.stringify(noData?.type === "line" && noData.filter)).toContain('"fit"');
  });

  it("outlines the barrio in focus above the buildings, dashed so it reads apart from the district", () => {
    const barrio = zoneLayers(palette).above.find((l) => l.id === "zone-barrio-line");
    expect(barrio).toMatchObject({ type: "line", source: "zone-barrio" });
    expect(barrio?.type === "line" && barrio.paint?.["line-dasharray"]).toBeTruthy();
  });
});
