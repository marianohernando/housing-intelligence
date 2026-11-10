import { describe, expect, it } from "vitest";

import { classIndex, colorFor, describeValue, formatValue, PALETTE, quantileBreaks, UNKNOWN_COLOR } from "../features";

const INFO = { feature_id: "x", human_name: "X", unit: "EUR/m2/mes", direction: "lower_is_better", domain: "housing", public_use: true, limitations: [] };

describe("choropleth helpers", () => {
  it("computes monotonic quantile breaks over known values", () => {
    const breaks = quantileBreaks([5, 1, 3, 2, 4, 6, 7, 8, 9, 10]);
    expect(breaks).toHaveLength(PALETTE.length - 1);
    expect([...breaks].sort((a, b) => a - b)).toEqual(breaks);
  });

  it("assigns classes and never paints unknown as a value", () => {
    const breaks = [2, 4, 6, 8];
    expect(classIndex(1, breaks)).toBe(0);
    expect(classIndex(9, breaks)).toBe(4);
    expect(colorFor(null, breaks)).toBe(UNKNOWN_COLOR);
    expect(colorFor(0, breaks)).toBe(PALETTE[0]);
    expect(colorFor(9, breaks)).toBe(PALETTE[PALETTE.length - 1]);
  });

  it("drops duplicated breaks and breaks at the minimum (many zeros)", () => {
    const breaks = quantileBreaks([0, 0, 0, 0, 0, 0, 1, 2, 3, 4]);
    expect(breaks).not.toContain(0);
    expect(new Set(breaks).size).toBe(breaks.length);
    expect(colorFor(0, breaks)).toBe(PALETTE[0]);
    expect(colorFor(4, breaks)).toBe(PALETTE[PALETTE.length - 1]);
  });

  it("returns no breaks without data", () => {
    expect(quantileBreaks([])).toEqual([]);
  });
});

describe("wording", () => {
  it("formats values with units in Spanish", () => {
    expect(formatValue(15.1, "EUR/m2/mes")).toBe("15,1 EUR/m2/mes");
    expect(formatValue(20.19, "%")).toBe("20,2 %");
  });

  it("explains unknown and low-confidence values in plain language", () => {
    const base = { territory_code: "28001", admin_unit_id: null, name: "La Acebeda", period_start: "2024-01-01", confidence: 1 };
    expect(describeValue({ ...base, value: null, null_reason: "SOURCE_MISSING" }, INFO)).toContain("no publica");
    expect(describeValue({ ...base, value: 3, null_reason: null, confidence: 0.5 }, INFO)).toContain("fiabilidad baja");
    expect(describeValue({ ...base, value: 3, null_reason: null }, INFO)).toBe("3 EUR/m2/mes (2024)");
  });
});
