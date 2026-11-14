import { describe, expect, it } from "vitest";

import type { FeatureValueRow } from "../features";
import { lineageDataset, regionBedsLine } from "../regionBeds";

// The answers of GET /api/v1/features/{id}/values?level=ccaa on 12 nov (D-231), as test fixtures
function region(value: number | null, period = "2023-01-01"): FeatureValueRow {
  return { territory_code: "28", admin_unit_id: null, name: null, period_start: period, value, null_reason: null, confidence: 1 };
}

describe("regionBedsLine (D-231)", () => {
  it("says the region's hospitals and beds per 1,000 people, each with its dataset", () => {
    const line = regionBedsLine(
      { row: region(85), datasetId: "cm_hospitales_datos_asistenciales" },
      { row: region(3), datasetId: "cm_dotacion_camas" },
    );
    expect(line).toEqual({
      hospitals: { text: "85 hospitales", datasetId: "cm_hospitales_datos_asistenciales" },
      beds: { text: "3,0 camas instaladas por cada 1.000 habitantes", datasetId: "cm_dotacion_camas" },
      year: "2023",
    });
  });

  it("names both years when the two tables differ, and says nothing when a figure is missing", () => {
    expect(regionBedsLine({ row: region(85, "2024-01-01"), datasetId: null }, { row: region(3), datasetId: null })?.year).toBe("2023 y 2024");
    expect(regionBedsLine({ row: region(null), datasetId: null }, { row: region(3), datasetId: null })).toBeNull();
    expect(regionBedsLine({ row: undefined, datasetId: null }, { row: region(3), datasetId: null })).toBeNull();
  });

  it("takes the dataset from the feature's lineage only when it is one", () => {
    expect(lineageDataset({ cm_dotacion_camas: "2026-11-12-db9e8751577e" })).toBe("cm_dotacion_camas");
    expect(lineageDataset({ a: "1", b: "2" })).toBeNull();
    expect(lineageDataset(undefined)).toBeNull();
  });
});
