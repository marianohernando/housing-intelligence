import { describe, expect, it } from "vitest";

import { confidenceText } from "../confidence";

describe("confidence in words (pitch/textos_web.md, section 6)", () => {
  it("uses D's cut-offs, with 0,5 counted as approximate", () => {
    expect(confidenceText(1).label).toBe("Dato fiable");
    expect(confidenceText(0.8).label).toBe("Dato fiable");
    expect(confidenceText(0.79).label).toBe("Dato aproximado");
    expect(confidenceText(0.5).label).toBe("Dato aproximado");
    expect(confidenceText(0.49).label).toBe("Dato poco seguro");
    expect(confidenceText(0.01).label).toBe("Dato poco seguro");
    expect(confidenceText(0).label).toBe("Sin datos");
  });

  it("has a help line for every level", () => {
    for (const c of [1, 0.6, 0.2, 0]) expect(confidenceText(c).help.length).toBeGreaterThan(10);
  });
});
