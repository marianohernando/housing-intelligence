import { describe, expect, it } from "vitest";

import type { IndicatorValue } from "@/contracts/zone_gap_list_response";

import {
  GAP_STATUS,
  gapFigures,
  gapsHref,
  NULL_REASON,
  parseZoneParam,
  pendingRows,
  ROW_MEASURE,
  ROW_NAME,
  sortRows,
  topRows,
  walking,
  walkingText,
} from "../gaps";

const ROW_KEYS = ["centro_salud", "colegio", "escuela_infantil", "farmacia", "mayores", "vivienda"];

describe("gap statuses (pitch/textos_web.md, estado.*)", () => {
  it("has a text label for every status, never colour alone", () => {
    expect(Object.keys(GAP_STATUS).sort()).toEqual(["CUBIERTO", "FALTA", "JUSTO", "SIN_DATOS"]);
    expect(GAP_STATUS.SIN_DATOS.label).toBe("SIN DATOS");
    for (const meta of Object.values(GAP_STATUS)) expect(meta.help.length).toBeGreaterThan(10);
  });
});

describe("rows", () => {
  it("names and measures the six rows of /gaps", () => {
    expect(Object.keys(ROW_NAME).sort()).toEqual(ROW_KEYS);
    expect(Object.keys(ROW_MEASURE).sort()).toEqual(ROW_KEYS);
    expect(ROW_MEASURE.centro_salud).toBe("Centros de atención primaria por cada 10.000 habitantes");
  });

  it("explains every reason for a missing value in plain words (falta, null_reason)", () => {
    expect(Object.keys(NULL_REASON)).toHaveLength(9);
    expect(NULL_REASON.SOURCE_MISSING).toBe("La fuente oficial no trae este dato.");
  });
});

describe("pendingRows", () => {
  it("reads the rows /gaps has not computed at this level yet, in row order", () => {
    const warnings = [
      "INSUFFICIENT_DATA: row vivienda not computed at distrito level yet",
      "INSUFFICIENT_DATA: row escuela_infantil not computed at distrito level yet",
    ];
    expect(pendingRows(warnings)).toEqual(["escuela_infantil", "vivienda"]);
  });

  it("ignores other warnings, unknown rows and a missing list", () => {
    expect(pendingRows(["colegio: no regional reference"])).toEqual([]);
    expect(pendingRows(["INSUFFICIENT_DATA: row parques not computed at municipio level yet"])).toEqual([]);
    expect(pendingRows([])).toEqual([]);
    expect(pendingRows(undefined)).toEqual([]);
  });
});

describe("sortRows and topRows", () => {
  const rows = [
    { row: "farmacia", status: "CUBIERTO" },
    { row: "colegio", status: "FALTA" },
    { row: "mayores", status: "SIN_DATOS" },
    { row: "centro_salud", status: "JUSTO" },
    { row: "vivienda", status: "FALTA" },
  ] as const;

  it("puts what is missing first and keeps the API order within a status", () => {
    expect(sortRows([...rows]).map((r) => r.row)).toEqual(["colegio", "vivienda", "centro_salud", "farmacia", "mayores"]);
  });

  it("keeps at most three rows for the zone card", () => {
    expect(topRows([...rows]).map((r) => r.row)).toEqual(["colegio", "vivienda", "centro_salud"]);
  });
});

describe("gapFigures", () => {
  // Pairs from GET /gaps (11 nov) and the decimals of their API `explanation`
  it("formats value and reference like the API explanation", () => {
    expect(gapFigures(5.011, 4.714)).toEqual({ value: "5,0", reference: "4,7" });
    expect(gapFigures(0.469, 0.5918)).toEqual({ value: "0,47", reference: "0,59" });
    expect(gapFigures(0, 0.3895)).toEqual({ value: "0,00", reference: "0,39" });
    expect(gapFigures(142.9, 0.5918)).toEqual({ value: "142,9", reference: "0,6" });
    expect(gapFigures(10700, 177.6)).toEqual({ value: "10.700,0", reference: "177,6" });
  });

  it("never turns a missing value or reference into a number", () => {
    expect(gapFigures(null, 177.6)).toEqual({ value: null, reference: "177,6" });
    expect(gapFigures(1.2, null)).toEqual({ value: "1,2", reference: null });
  });
});

function extra(featureId: string, value: number | null, nullReason: IndicatorValue["null_reason"] = null): IndicatorValue {
  return { feature_id: featureId, label: "", unit: "min", level: "distrito", confidence: value === null ? 0 : 1, value, null_reason: nullReason };
}

describe("walking minutes (extra_indicators)", () => {
  it("picks the walking extra among the others", () => {
    const extras = [extra("plazas_residencia_por_100_mayores", 3.7), extra("min_a_pie_mayores", 10.01)];
    expect(walking(extras)?.feature_id).toBe("min_a_pie_mayores");
    expect(walking([extra("tamano_medio_hogar", 2.4)])).toBeUndefined();
    expect(walking(undefined)).toBeUndefined();
  });

  it("rounds to whole minutes and caps the text above 60", () => {
    expect(walkingText(extra("min_a_pie_colegio", 5.815))).toBe("6 min");
    expect(walkingText(extra("min_a_pie_centro_salud", 9.466))).toBe("9 min");
    expect(walkingText(extra("min_a_pie_colegio", 60))).toBe("60 min");
    expect(walkingText(extra("min_a_pie_colegio", 60.4))).toBe("más de 60 min");
    expect(walkingText(extra("min_a_pie_colegio", 207.3))).toBe("más de 60 min");
    expect(walkingText(extra("min_a_pie_farmacia", 0.3))).toBe("menos de 1 min");
  });

  it("says «sin dato» when the value is missing, never 0", () => {
    expect(walkingText(extra("min_a_pie_colegio", null, "SOURCE_NO_COVERAGE"))).toBe("sin dato");
  });
});

describe("zone links of «Qué falta»", () => {
  it("round-trips a zone through the ?zona= parameter", () => {
    expect(gapsHref("distrito", "2807905")).toBe("/que-falta?zona=distrito/2807905");
    expect(parseZoneParam("distrito/2807905")).toEqual({ level: "distrito", code: "2807905" });
    expect(parseZoneParam("municipio/28092")).toEqual({ level: "municipio", code: "28092" });
  });

  it("rejects levels without a map zone and malformed values", () => {
    expect(parseZoneParam(undefined)).toBeNull();
    expect(parseZoneParam("")).toBeNull();
    expect(parseZoneParam("seccion_censal/2807905001")).toBeNull();
    expect(parseZoneParam("distrito")).toBeNull();
    expect(parseZoneParam("distrito/28 07")).toBeNull();
    expect(parseZoneParam(["distrito/2807905", "municipio/28092"])).toBeNull();
  });
});
