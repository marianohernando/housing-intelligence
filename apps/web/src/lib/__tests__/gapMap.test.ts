import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { GapRowMap, ZoneGapStatus } from "@/contracts/gap_row_map_response";

import { countByStatus, gapByZone, GAP_PATTERN, isGapRow, joinLevels, MAP_ROWS, paintZones, patternPixels } from "../map/gapMap";
import type { ZoneCollection, ZoneFeature, ZoneLevel } from "../map/zones";

// Test fixture published by line A with the contract (data/fixtures/contracts), not demo data.
const FIXTURE = new URL("../../../../../data/fixtures/contracts/gap_row_map.centro_salud_distrito.fixture.json", import.meta.url);
const distritos = JSON.parse(readFileSync(FIXTURE, "utf8")) as GapRowMap;

function zone(level: ZoneLevel, code: string, adminUnitId: string): ZoneFeature {
  return {
    type: "Feature",
    id: adminUnitId,
    geometry: { type: "Polygon", coordinates: [] },
    properties: { admin_unit_id: adminUnitId, level, code, name: code, municipio_name: "", zone_key: `${level}/${code}` },
  };
}

function status(adminUnitId: string, value: ZoneGapStatus["status"], reliable = true): ZoneGapStatus {
  return { admin_unit_id: adminUnitId, code: adminUnitId.slice(-5), name: "", status: value, value: null, confidence: 1, reliable };
}

const municipios = {
  zones: [status("ES.28.MUN.28092", "FALTA"), status("ES.28.MUN.28079", "JUSTO"), status("ES.28.MUN.28001", "CUBIERTO", false)],
} as GapRowMap;

describe("rows on the map", () => {
  it("offers the six rows of /gaps in the API order", () => {
    expect(MAP_ROWS).toEqual(["escuela_infantil", "colegio", "centro_salud", "mayores", "farmacia", "vivienda"]);
    expect(isGapRow("centro_salud")).toBe(true);
    expect(isGapRow("parques")).toBe(false);
    expect(isGapRow(undefined)).toBe(false);
  });
});

describe("gapByZone and paintZones", () => {
  const map: ZoneCollection = {
    type: "FeatureCollection",
    features: [
      zone("municipio", "28092", "ES.28.MUN.28092"),
      zone("distrito", "2807901", "ES.28.DIS.2807901"),
      zone("municipio", "28006", "ES.28.MUN.28006"),
      zone("municipio", "28001", "ES.28.MUN.28001"),
    ],
  };
  const byZone = gapByZone([municipios, distritos]);

  it("joins both levels by admin_unit_id, Madrid's districts included", () => {
    expect(byZone.get("ES.28.MUN.28092")?.status).toBe("FALTA");
    expect(byZone.get("ES.28.DIS.2807901")?.status).toBe("JUSTO");
    expect(byZone.size).toBe(3 + distritos.zones.length);
  });

  it("paints each zone with its status, its own class when too small, and leaves out zones the row does not carry", () => {
    const painted = paintZones(map, byZone);
    expect(painted.features.map((f) => f.properties.gap)).toEqual(["FALTA", "JUSTO", undefined, "ZONA_PEQUENA"]);
    // the map's own zones, untouched
    expect(map.features[0]?.properties).not.toHaveProperty("gap");
  });

  it("counts the zones of the map by status; a zone not carried is not SIN DATOS", () => {
    const counts = countByStatus(paintZones(map, byZone));
    expect(counts).toEqual({ FALTA: 1, JUSTO: 1, CUBIERTO: 0, ZONA_PEQUENA: 1, SIN_DATOS: 0, pending: 1 });
  });
});

describe("joinLevels", () => {
  it("joins municipios and districts when both answer", () => {
    const data = joinLevels([{ map: municipios }, { map: distritos }]);
    expect(data.failed).toEqual([]);
    expect(data.info).toBe(municipios);
    expect(data.byZone.size).toBe(3 + distritos.zones.length);
  });

  it("keeps the level that answered when the other fails: its zones stay pending, never SIN DATOS", () => {
    const data = joinLevels([{ error: new Error("down") }, { map: distritos }]);
    expect(data.failed).toEqual(["municipio"]);
    expect(data.info).toBe(distritos);
    expect(data.byZone.has("ES.28.MUN.28092")).toBe(false);
    expect(joinLevels([{ map: municipios }, { error: new Error("down") }]).failed).toEqual(["distrito"]);
  });

  it("fails with the first error only when no level answers", () => {
    const first = new Error("municipios down");
    expect(() => joinLevels([{ error: first }, { error: new Error("distritos down") }])).toThrow(first);
  });
});

describe("patternPixels", () => {
  const ink: [number, number, number, number] = [166, 30, 51, 200];

  it("draws the FALTA stripes and the JUSTO dots on a transparent tile", () => {
    for (const kind of ["stripes", "dots", "lines"] as const) {
      const { width, height, data } = patternPixels(kind, ink, 2);
      expect(width).toBe(GAP_PATTERN.size * 2);
      expect(height).toBe(width);
      expect(data).toHaveLength(width * height * 4);
      const painted = data.filter((_, i) => i % 4 === 3 && data[i] === 200).length;
      expect(painted).toBeGreaterThan(0);
      expect(painted).toBeLessThan(width * height / 2);
    }
  });

  it("tiles seamlessly: the stripes meet across the right and bottom edges", () => {
    const { width, data } = patternPixels("stripes", ink, 1);
    const alpha = (x: number, y: number) => data[(y * width + x) * 4 + 3];
    for (let y = 0; y < width; y++) expect(alpha(0, y)).toBe(alpha(width - 1, (y + 1) % width));
  });
});
