import { describe, expect, it } from "vitest";

import { compositeOver, contrastRatio, parseColor, relativeLuminance } from "../color";

describe("parseColor", () => {
  it("reads 6-digit hex", () => {
    expect(parseColor("#6A5AE0")).toEqual({ r: 106, g: 90, b: 224, a: 1 });
  });

  it("reads 3-digit hex", () => {
    expect(parseColor("#fff")).toEqual({ r: 255, g: 255, b: 255, a: 1 });
  });

  it("reads rgba with a leading-dot alpha", () => {
    expect(parseColor("rgba(255, 255, 255, .82)")).toEqual({ r: 255, g: 255, b: 255, a: 0.82 });
  });

  it("rejects anything else", () => {
    expect(() => parseColor("violet")).toThrow();
  });
});

describe("contrastRatio (WCAG 2.2)", () => {
  it("is 21 for black on white and 1 for a colour on itself", () => {
    expect(contrastRatio("#000000", "#ffffff")).toBeCloseTo(21, 5);
    expect(contrastRatio("#6A5AE0", "#6A5AE0")).toBeCloseTo(1, 5);
  });

  it("is symmetric", () => {
    expect(contrastRatio("#141B3D", "#F6F5FC")).toBeCloseTo(contrastRatio("#F6F5FC", "#141B3D"), 10);
  });

  it("matches the known value for #767676 on white (4.54)", () => {
    expect(contrastRatio("#767676", "#ffffff")).toBeCloseTo(4.54, 2);
  });

  it("refuses translucent colours: composite them first", () => {
    expect(() => contrastRatio("rgba(0,0,0,.5)", "#ffffff")).toThrow();
  });
});

describe("compositeOver", () => {
  it("returns the backdrop for a fully transparent colour", () => {
    expect(compositeOver("rgba(255,255,255,0)", "#6A5AE0")).toBe("#6a5ae0");
  });

  it("mixes channel by channel", () => {
    expect(compositeOver("rgba(255,255,255,.5)", "#000000")).toBe("#808080");
  });

  it("keeps luminance between both colours", () => {
    const mixed = compositeOver("rgba(255,255,255,.82)", "#6A5AE0");
    expect(relativeLuminance(mixed)).toBeGreaterThan(relativeLuminance("#6A5AE0"));
    expect(relativeLuminance(mixed)).toBeLessThan(1);
  });
});
