import { describe, expect, it } from "vitest";

import { zoneZoom } from "../map/camera";
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
