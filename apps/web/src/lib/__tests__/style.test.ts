import { readFileSync } from "node:fs";

import { createExpression, validateStyleMin } from "@maplibre/maplibre-gl-style-spec";
import type { StyleSpecification } from "maplibre-gl";
import { describe, expect, it } from "vitest";

import { PATTERN_IMAGE } from "../map/gapMap";
import {
  baseStyle,
  BUILDING_LAYER,
  BUILDINGS_3D_ZOOM,
  clusterImageId,
  clusterImageOf,
  clusterRadius,
  FACILITY_CLUSTER_PROPERTIES,
  FACILITY_SOURCE,
  facilityLayers,
  FIRST_LABEL_LAYER,
  LABEL_AREA,
  labelLayers,
  MAP_FONTS,
  mapGlyphsUrl,
  mapTilesSource,
  MAP_PALETTE_TOKENS,
  type MapPalette,
  OPENFREEMAP_GLYPHS,
  OPENFREEMAP_TILEJSON,
  PARKS_VIVID_LAYER,
  PLAIN_ZONE_OPACITY,
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
  const { below, withLabels, above } = zoneLayers(palette);
  return {
    ...style,
    sources: {
      ...style.sources,
      zones: { type: "geojson", data: empty },
      "zone-selected": { type: "geojson", data: empty },
      "zone-mask": { type: "geojson", data: empty },
      "zone-base": { type: "geojson", data: empty },
      "zone-barrio": { type: "geojson", data: empty },
      [FACILITY_SOURCE]: { type: "geojson", data: empty, cluster: true, clusterProperties: FACILITY_CLUSTER_PROPERTIES },
    },
    layers: [...style.layers, ...below, ...withLabels, ...above, ...facilityLayers(palette)],
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

  it("uses open tiles and glyphs without a key", () => {
    const style = baseStyle(palette);
    expect(style.sources.openmaptiles).toEqual({ type: "vector", url: OPENFREEMAP_TILEJSON });
    expect(style.glyphs).toBe(OPENFREEMAP_GLYPHS);
    for (const url of [OPENFREEMAP_TILEJSON, OPENFREEMAP_GLYPHS]) expect(url).not.toMatch(/key=|token=/i);
  });

  it("takes its fonts from NEXT_PUBLIC_MAP_GLYPHS_URL when set (offline package), OpenFreeMap otherwise", () => {
    expect(mapGlyphsUrl(undefined)).toBe(OPENFREEMAP_GLYPHS);
    expect(mapGlyphsUrl("")).toBe(OPENFREEMAP_GLYPHS);
    // A path on the same site, made absolute with the page's origin: MapLibre wants an absolute URL
    expect(mapGlyphsUrl("/tiles/fonts/{fontstack}/{range}.pbf", "http://localhost:3012")).toBe(
      "http://localhost:3012/tiles/fonts/{fontstack}/{range}.pbf",
    );
    expect(mapGlyphsUrl("http://localhost:8080/fonts/{fontstack}/{range}.pbf")).toBe("http://localhost:8080/fonts/{fontstack}/{range}.pbf");
    // Not a glyph template (no tokens, a path without origin, another scheme): the default stays
    expect(mapGlyphsUrl("http://localhost:8080/fonts/Noto Sans Regular/0-255.pbf")).toBe(OPENFREEMAP_GLYPHS);
    expect(mapGlyphsUrl("/tiles/fonts/{fontstack}/{range}.pbf")).toBe(OPENFREEMAP_GLYPHS);
    expect(mapGlyphsUrl("ftp://fonts/{fontstack}/{range}.pbf")).toBe(OPENFREEMAP_GLYPHS);
    const local = baseStyle(palette, mapTilesSource(undefined), mapGlyphsUrl("/tiles/fonts/{fontstack}/{range}.pbf", "http://localhost:3012"));
    expect(local.glyphs).toBe("http://localhost:3012/tiles/fonts/{fontstack}/{range}.pbf");
    expect(validateStyleMin(local)).toEqual([]);
  });

  it("writes every label in one font the glyph servers have, alone (a stack of two is a 404)", () => {
    const fonts = [...labelLayers(palette), ...zoneLayers(palette).withLabels].flatMap((l) => (l.type === "symbol" && l.layout?.["text-font"] ? [l.layout["text-font"]] : []));
    expect(fonts.length).toBeGreaterThan(0);
    for (const font of fonts) {
      expect(Array.isArray(font) && font.length).toBe(1);
      expect(["Noto Sans Regular", "Noto Sans Bold", "Noto Sans Italic"]).toContain((font as string[])[0]);
    }
    expect(Object.values(MAP_FONTS).every((stack) => stack.length === 1)).toBe(true);
  });

  it("labels places by zoom, the big roads by their ref, stations and water, from the tiles alone", () => {
    const layers = labelLayers(palette);
    const bySourceLayer = (name: string) => layers.filter((l) => "source-layer" in l && l["source-layer"] === name);
    expect(layers.every((l) => "source" in l && l.source === "openmaptiles")).toBe(true);
    // Municipios from the overview, barrios at zone zoom; Madrid's districts after the zones' names
    const place = Object.fromEntries(bySourceLayer("place").map((l) => [l.id, l.minzoom ?? 0]));
    expect(place["label-city"]).toBe(0);
    expect(place["label-barrio"]).toBeGreaterThan(place["label-town"] ?? 0);
    const zoneNames = zoneLayers(palette).withLabels.find((l) => l.id === "zone-names");
    expect(zoneNames).toMatchObject({ type: "symbol", source: "zones", filter: ["==", ["get", "level"], "distrito"] });
    expect(place["label-district"]).toBe(zoneNames?.maxzoom);
    // The ref of motorways and trunk roads, only on their lines (exits are points in the same layer)
    const road = JSON.stringify(bySourceLayer("transportation_name")[0]);
    for (const part of ['"motorway","trunk"', '["geometry-type"],"LineString"', '"text-field":["get","ref"]']) expect(road).toContain(part);
    // Stations, not their entrances; the name of the offline extract (tilemaker) when there is no `name`
    const stations = JSON.stringify(bySourceLayer("poi"));
    expect(stations).toContain('"railway"');
    expect(stations).not.toContain("subway_entrance");
    expect(JSON.stringify(layers)).toContain('["coalesce",["get","name"],["get","name:latin"]]');
    expect(bySourceLayer("water_name")).toHaveLength(1);
    // Municipios on top: MapLibre places the top layers first, so they win a clash
    expect(layers.at(-1)?.id).toBe("label-city");
    // Only around the region: far tiles on a tilted view would ask for glyphs of other scripts
    for (const layer of layers) expect(JSON.stringify("filter" in layer && layer.filter)).toContain('["within",');
    const [west, south, east, north] = LABEL_AREA;
    expect(west < -4.58 && east > -3.06 && south < 39.88 && north > 41.16).toBe(true); // the Comunidad's box
  });

  it("draws the labels above the buildings and the zones' fill and edges, and below the mask, the outline and the centres", () => {
    // As VidaMap adds them: the fill under the buildings, the edges under the labels, the rest on top
    const ids = baseStyle(palette).layers.map((l) => l.id);
    const { below, withLabels, above } = zoneLayers(palette);
    ids.splice(ids.indexOf(BUILDING_LAYER), 0, ...below.map((l) => l.id));
    ids.splice(ids.indexOf(FIRST_LABEL_LAYER), 0, ...withLabels.map((l) => l.id));
    ids.push(...above.map((l) => l.id), ...facilityLayers(palette).map((l) => l.id));
    const first = ids.indexOf(FIRST_LABEL_LAYER);
    const last = ids.indexOf("label-city");
    expect(labelLayers(palette)[0]?.id).toBe(FIRST_LABEL_LAYER);
    expect(first).toBeGreaterThan(ids.indexOf(BUILDING_LAYER));
    // No white edge crosses a name, and the districts' names are the first to give way
    for (const under of ["zones-fill", "zones-pattern", "zones-line", "zones-nodata", "zone-names"]) expect(ids.indexOf(under)).toBeLessThan(first);
    for (const over of ["zone-mask", "zone-outline", "zones-hover", "facilities-point", "facilities-cluster"]) expect(ids.indexOf(over)).toBeGreaterThan(last);
  });

  it("keeps the labels quiet: soft ink with a white halo, never a status or centre colour", () => {
    const quiet = [palette.label, palette.labelStrong, palette.labelWater];
    const loud = [palette.gapFalta, palette.gapJusto, palette.gapCubierto, palette.violet, palette.facColegio, palette.facHospital];
    for (const layer of [...labelLayers(palette), ...zoneLayers(palette).withLabels]) {
      if (layer.type !== "symbol") continue;
      expect(quiet).toContain(layer.paint?.["text-color"]);
      expect(loud).not.toContain(layer.paint?.["text-color"]);
      expect(layer.paint?.["text-halo-color"]).toBe("#ffffff");
    }
  });

  it("takes its base map from NEXT_PUBLIC_MAP_TILES_URL when set (offline package), OpenFreeMap otherwise", () => {
    expect(mapTilesSource(undefined)).toEqual({ type: "vector", url: OPENFREEMAP_TILEJSON });
    expect(mapTilesSource("")).toEqual({ type: "vector", url: OPENFREEMAP_TILEJSON });
    // A TileJSON, local or not (pmtiles serve, martin, tileserver-gl)
    expect(mapTilesSource("http://localhost:8080/madrid.json")).toEqual({ type: "vector", url: "http://localhost:8080/madrid.json" });
    // A tile template, with the OpenMapTiles zooms
    expect(mapTilesSource("http://localhost:8080/madrid/{z}/{x}/{y}.pbf")).toEqual({
      type: "vector",
      tiles: ["http://localhost:8080/madrid/{z}/{x}/{y}.pbf"],
      maxzoom: 14,
    });
    // A path on the same site, made absolute with the page's origin (the map's worker needs it)
    expect(mapTilesSource("/tiles/madrid.json", "http://localhost:3012")).toEqual({ type: "vector", url: "http://localhost:3012/tiles/madrid.json" });
    // Anything else is not a tile URL: the default stays
    expect(mapTilesSource("ftp://tiles/madrid")).toEqual({ type: "vector", url: OPENFREEMAP_TILEJSON });
    const local = baseStyle(palette, mapTilesSource("http://localhost:8080/madrid.json"));
    expect(local.sources.openmaptiles).toEqual({ type: "vector", url: "http://localhost:8080/madrid.json" });
    expect(validateStyleMin(local)).toEqual([]);
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
    const noData = zoneLayers(palette).withLabels.find((l) => l.id === "zones-nodata");
    expect(JSON.stringify(noData?.type === "line" && noData.filter)).toContain('"fit"');
  });

  it("lets the streets show under the zones not painted yet, and keeps the painted ones solid (MAP-004)", () => {
    const fill = zoneLayers(palette).below.find((l) => l.id === "zones-fill");
    const opacity = JSON.stringify(fill?.type === "fill" && fill.paint?.["fill-opacity"]);
    expect(opacity).toContain(`["case",["any",["!=",["get","gap"],null],["!=",["get","fit"],null]],0.9,${PLAIN_ZONE_OPACITY}]`);
    expect(PLAIN_ZONE_OPACITY).toBeLessThanOrEqual(0.6);
    // Camera expressions go outermost: every zone still fades out at zone zoom
    expect(opacity.startsWith('["interpolate",["linear"],["zoom"]')).toBe(true);
  });

  it("treats a zone with gap: null as plain, not as painted (MAP-004)", () => {
    const fill = zoneLayers(palette).below.find((l) => l.id === "zones-fill");
    const opacity = fill?.type === "fill" ? fill.paint?.["fill-opacity"] : undefined;
    const caseExpr = JSON.stringify(opacity).match(/\["case".*?,0\.9,[\d.]+\]/)?.[0];
    const compiled = createExpression(JSON.parse(caseExpr ?? "null"), "fill-opacity", {
      type: "number",
      "property-type": "data-driven",
      expression: { interpolated: false, parameters: ["feature"] },
    } as never);
    if (compiled.result !== "success") throw new Error("the opacity expression does not compile");
    const opacityOf = (properties: Record<string, unknown>) =>
      compiled.value.evaluate({ zoom: 5 }, { type: 3, properties } as never);
    expect(opacityOf({ gap: "FALTA" })).toBe(0.9);
    expect(opacityOf({ gap: null })).toBe(PLAIN_ZONE_OPACITY);
    expect(opacityOf({})).toBe(PLAIN_ZONE_OPACITY);
    expect(opacityOf({ fit: "ENCAJA" })).toBe(0.9);
    expect(opacityOf({ fit: null })).toBe(PLAIN_ZONE_OPACITY);
  });

  it("colours by a row only when gap is not null, so a zone with gap: null is not painted as no data (MAP-004)", () => {
    const fill = zoneLayers(palette).below.find((l) => l.id === "zones-fill");
    const color = JSON.stringify(fill?.type === "fill" && fill.paint?.["fill-color"]);
    expect(color.startsWith('["case",["!=",["get","gap"],null],["match"')).toBe(true);
    expect(color).not.toContain('["has","gap"]');
  });

  it("crosses out the zones that fail a condition with a pattern, not only a lighter tone (R-06)", () => {
    const pattern = zoneLayers(palette).below.find((l) => l.id === "zones-pattern");
    const json = JSON.stringify(pattern?.type === "fill" && { filter: pattern.filter, paint: pattern.paint });
    expect(json).toContain('["==",["get","fit"],"NO_CUMPLE"]');
    expect(json).toContain(PATTERN_IMAGE.NO_CUMPLE);
    for (const image of [PATTERN_IMAGE.FALTA, PATTERN_IMAGE.JUSTO, PATTERN_IMAGE.ZONA_PEQUENA]) expect(json).toContain(image);
  });

  it("groups the zone's facilities without text layers: each group is an image with its count", () => {
    const layers = facilityLayers(palette);
    expect(layers.every((l) => "source" in l && l.source === FACILITY_SOURCE)).toBe(true);
    expect(layers.some((l) => l.type === "symbol" && l.layout && "text-field" in l.layout)).toBe(false);
    const cluster = layers.find((l) => l.id === "facilities-cluster");
    expect(JSON.stringify(cluster)).toContain('"point_count"');
    const point = layers.find((l) => l.id === "facilities-point");
    expect(point).toMatchObject({ type: "circle", filter: ["!", ["has", "point_count"]] });
  });

  it("paints the four leisure groups in one colour, so the map does not fill with colours (D-236)", () => {
    const point = facilityLayers(palette).find((l) => l.id === "facilities-point");
    expect(JSON.stringify(point?.type === "circle" && point.paint)).toContain(`["bares","restaurantes","gimnasios","cultura"],"${palette.facOcio}"`);
  });

  it("names each group image by its count and colour, and sizes it by how many it holds", () => {
    expect(clusterImageId(23)).toBe("facility-cluster-23");
    expect(clusterImageOf("facility-cluster-23")).toEqual({ count: 23, tone: "violet" });
    expect(clusterImageId(7, "park")).toBe("facility-cluster-park-7");
    expect(clusterImageOf(clusterImageId(7, "park"))).toEqual({ count: 7, tone: "park" });
    expect(clusterImageOf("gap-falta")).toBeNull();
    expect(clusterImageOf("facility-cluster-x")).toBeNull();
    expect(clusterImageOf("facility-cluster-park-")).toBeNull();
    expect(clusterRadius(2)).toBeLessThan(clusterRadius(20));
    expect(clusterRadius(20)).toBeLessThan(clusterRadius(200));
    // Big enough for three digits and a pointer target
    expect(clusterRadius(999)).toBeGreaterThanOrEqual(22);
  });

  it("paints parks in green: their dots and groups, and the base map's parks while «Parques» is on (DATA-018)", () => {
    const point = facilityLayers(palette).find((l) => l.id === "facilities-point");
    expect(JSON.stringify(point?.type === "circle" && point.paint)).toContain(`["match",["get","type"],"parque","${palette.parkStrong}"`);
    const cluster = facilityLayers(palette).find((l) => l.id === "facilities-cluster");
    // Green only when every place of the group is a park
    expect(JSON.stringify(cluster)).toContain('["==",["get","parks"],["get","point_count"]]');
    const vivid = baseStyle(palette).layers.find((l) => l.id === PARKS_VIVID_LAYER);
    expect(vivid).toMatchObject({ type: "fill", "source-layer": "landcover", filter: ["==", ["get", "subclass"], "park"], layout: { visibility: "none" } });
    // Above the soft green of the base map, under the buildings
    const ids = baseStyle(palette).layers.map((l) => l.id);
    expect(ids.indexOf(PARKS_VIVID_LAYER)).toBeGreaterThan(ids.indexOf("green"));
    expect(ids.indexOf(PARKS_VIVID_LAYER)).toBeLessThan(ids.indexOf(BUILDING_LAYER));
  });

  it("outlines the barrio in focus above the buildings, dashed so it reads apart from the district", () => {
    const barrio = zoneLayers(palette).above.find((l) => l.id === "zone-barrio-line");
    expect(barrio).toMatchObject({ type: "line", source: "zone-barrio" });
    expect(barrio?.type === "line" && barrio.paint?.["line-dasharray"]).toBeTruthy();
  });
});
