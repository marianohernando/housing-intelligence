import { describe, expect, it } from "vitest";

import { cameraPadding, SHEET_PEEK, zoneZoom } from "../map/camera";
import { BUILDINGS_3D_ZOOM } from "../map/style";

describe("zoneZoom", () => {
  it("takes a district-sized zone to the zoom where buildings stand up (zoom-14 tiles)", () => {
    expect(BUILDINGS_3D_ZOOM).toBe(14);
    expect(zoneZoom(12.85, false)).toBe(14);
    expect(zoneZoom(12.2, true)).toBe(14);
  });

  it("only adds the tilt boost when the zone already fits closer", () => {
    expect(zoneZoom(14.2, false)).toBeCloseTo(14.95);
    expect(zoneZoom(14.2, true)).toBeCloseTo(14.6);
  });

  it("does not crop a large municipio to force 3D buildings", () => {
    expect(zoneZoom(11, false)).toBeCloseTo(11.75);
    expect(zoneZoom(11.9, true)).toBeCloseTo(12.3);
  });
});

describe("cameraPadding", () => {
  it("keeps the desktop cards clear: search on the left, zone card on the right", () => {
    expect(cameraPadding("overview", { mobile: false, height: 900 })).toEqual({ top: 100, right: 460, bottom: 40, left: 500 });
    expect(cameraPadding("zone", { mobile: false, height: 900 })).toEqual({ top: 90, right: 380, bottom: 200, left: 440 });
  });

  it("on mobile frames the map between the header and the bottom sheet", () => {
    const height = 844;
    const sheet = Math.round(height * SHEET_PEEK);
    for (const mode of ["overview", "zone"] as const) {
      const pad = cameraPadding(mode, { mobile: true, height });
      expect(pad.bottom).toBeGreaterThanOrEqual(sheet);
      expect(pad.top).toBeGreaterThan(100); // the header (brand and tabs)
      expect(height - pad.top - pad.bottom).toBeGreaterThan(200); // still a usable map
    }
  });

  it("the sheet takes a bit under half the screen", () => {
    expect(SHEET_PEEK).toBeGreaterThan(0.35);
    expect(SHEET_PEEK).toBeLessThan(0.5);
  });
});
