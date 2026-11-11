import { describe, expect, it } from "vitest";

import { formatEuros, formatNumber } from "../format";

describe("formatEuros", () => {
  it("groups thousands with a dot, also for 4-digit amounts", () => {
    expect(formatEuros(1200)).toBe("1.200 €");
    expect(formatEuros(300000)).toBe("300.000 €");
    expect(formatEuros(950)).toBe("950 €");
  });
});

describe("formatNumber", () => {
  it("keeps the decimals asked for and groups thousands like the API", () => {
    expect(formatNumber(10700, 1)).toBe("10.700,0");
    expect(formatNumber(0.469, 2)).toBe("0,47");
    expect(formatNumber(0, 2)).toBe("0,00");
    expect(formatNumber(1500, 0)).toBe("1.500");
  });
});
