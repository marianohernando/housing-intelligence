import { describe, expect, it } from "vitest";

import {
  APPROACH_MAX_KM,
  approachZoom,
  cameraPadding,
  extentKm,
  FIRST_VIEW,
  firstViewBounds,
  ISLAND_MARGIN,
  islandZoom,
  type Padding,
  projectAt,
  SHEET_PEEK,
  THREE_COLUMNS_MIN,
  type ZoneCamera,
} from "../map/camera";
import { BUILDINGS_3D_ZOOM } from "../map/style";

const PAD: Padding = { top: 90, right: 380, bottom: 200, left: 440 };
const DESKTOP = { width: 1440, height: 900, padding: PAD };
// Centre of the padded area: where the camera centre lands on screen
const OX = 440 + (1440 - 440 - 380) / 2;
const OY = 90 + (900 - 90 - 200) / 2;
const CENTER: [number, number] = [-3.68, 40.46];

function camera(over: Partial<ZoneCamera> = {}): ZoneCamera {
  return { center: CENTER, zoom: 14, pitch: 0, bearing: 0, ...DESKTOP, ...over };
}

describe("projectAt", () => {
  it("puts the camera centre in the middle of the padded area", () => {
    const at = projectAt(camera({ pitch: 55, bearing: -20 }), CENTER);
    expect(at?.x).toBeCloseTo(OX);
    expect(at?.y).toBeCloseTo(OY);
  });

  it("seen from above, scales linearly: 512 px per 360° of longitude at zoom 0", () => {
    const at = projectAt(camera({ zoom: 10 }), [CENTER[0] + 0.01, CENTER[1]]);
    expect(at?.x).toBeCloseTo(OX + (512 * 2 ** 10 * 0.01) / 360);
    expect(at?.y).toBeCloseTo(OY);
  });

  it("tilted, the near side (south) looks bigger than the far side", () => {
    const tilted = camera({ pitch: 55 });
    const south = projectAt(tilted, [CENTER[0], CENTER[1] - 0.005]);
    const north = projectAt(tilted, [CENTER[0], CENTER[1] + 0.005]);
    expect(south && north).toBeTruthy();
    expect((south?.y ?? 0) - OY).toBeGreaterThan(OY - (north?.y ?? 0));
  });

  it("turns with the bearing: looking east, a point to the east is above the centre", () => {
    const at = projectAt(camera({ bearing: 90 }), [CENTER[0] + 0.005, CENTER[1]]);
    expect(at?.x).toBeCloseTo(OX);
    expect(at?.y).toBeLessThan(OY);
  });

  it("returns null for a point behind the camera", () => {
    expect(projectAt(camera({ pitch: 70, zoom: 16 }), [CENTER[0], CENTER[1] - 1])).toBeNull();
  });
});

describe("islandZoom", () => {
  // A district-sized square, about 3 km a side
  const ring: [number, number][] = [
    [-3.7, 40.445],
    [-3.665, 40.445],
    [-3.665, 40.472],
    [-3.7, 40.472],
    [-3.7, 40.445],
  ];
  const inside = (cam: ZoneCamera) =>
    ring.every((point) => {
      const at = projectAt(cam, point);
      return (
        at !== null &&
        at.x >= PAD.left + ISLAND_MARGIN &&
        at.x <= 1440 - PAD.right - ISLAND_MARGIN &&
        at.y >= PAD.top + ISLAND_MARGIN &&
        at.y <= 900 - PAD.bottom - ISLAND_MARGIN
      );
    });

  for (const view of [
    { pitch: 0, bearing: 0 },
    { pitch: 55, bearing: -20 },
  ]) {
    it(`is the closest zoom that keeps the whole outline in view (pitch ${view.pitch})`, () => {
      const base = { center: CENTER, ...view, ...DESKTOP };
      const zoom = islandZoom(ring, base);
      expect(inside({ ...base, zoom })).toBe(true);
      expect(inside({ ...base, zoom: zoom + 0.05 })).toBe(false);
    });
  }

  it("keeps the island clear of the cards, centred where the zone camera centres it", () => {
    const island = cameraPadding("island", { mobile: false, width: 1440, height: 900 });
    const base = { center: CENTER, pitch: 55, bearing: -20, ...DESKTOP };
    const zoom = islandZoom(ring, base, island);
    expect(zoom).toBeLessThan(islandZoom(ring, base));
    for (const point of ring) {
      const at = projectAt({ ...base, zoom }, point);
      expect(at?.x).toBeGreaterThanOrEqual(island.left);
      expect(at?.x).toBeLessThanOrEqual(1440 - island.right);
    }
    // Same centre as the zone padding, so coming closer does not pan
    expect(island.left + (1440 - island.left - island.right) / 2).toBe(OX);
  });

  it("stays below the zoom of 3D buildings for a district-sized zone", () => {
    expect(islandZoom(ring, { center: CENTER, pitch: 55, bearing: -20, ...DESKTOP })).toBeLessThan(BUILDINGS_3D_ZOOM);
  });
});

describe("approachZoom", () => {
  const chamartin = { district: true, extentKm: 4.6 };

  it("takes a compact district from its island to the zoom where buildings stand up (zoom-14 tiles)", () => {
    expect(BUILDINGS_3D_ZOOM).toBe(14);
    expect(approachZoom(12.9, chamartin)).toBe(14);
    expect(approachZoom(11.3, chamartin)).toBe(14); // mobile: the whole district fits from farther away
  });

  it("leaves a large district on its island instead of landing on fields", () => {
    expect(APPROACH_MAX_KM).toBe(10);
    expect(approachZoom(11, { district: true, extentKm: 31.1 })).toBe(11); // Fuencarral-El Pardo
  });

  it("does not crop a municipio to force 3D buildings, and never zooms out", () => {
    expect(approachZoom(11.4, { district: false, extentKm: 11.7 })).toBe(11.4);
    expect(approachZoom(14.6, chamartin)).toBe(14.6);
  });

  it("measures a zone by the diagonal of its box, in km", () => {
    // 0.01° of latitude is 1.11 km; of longitude, at 40.45°, 0.85 km
    expect(extentKm([-3.7, 40.44, -3.69, 40.45])).toBeCloseTo(Math.hypot(0.847, 1.113), 2);
  });
});

describe("cameraPadding", () => {
  it("keeps the desktop cards clear: search on the left, zone card on the right, legend below", () => {
    expect(cameraPadding("overview", { mobile: false, width: 1440, height: 900 })).toEqual({ top: 100, right: 460, bottom: 250, left: 500 });
    expect(cameraPadding("zone", { mobile: false, width: 1440, height: 900 })).toEqual({ top: 90, right: 380, bottom: 200, left: 440 });
  });

  it("with one column of cards (projector at 125 %: 1024 px), frames the map on the right of it", () => {
    for (const [width, height] of [[1024, 768], [1024, 576], [1180, 700]] as const) {
      expect(width).toBeLessThan(THREE_COLUMNS_MIN);
      for (const mode of ["overview", "zone", "island"] as const) {
        const pad = cameraPadding(mode, { mobile: false, width, height });
        // Clear of the 27-28rem column of cards (17 px rem) on the left…
        expect(pad.left).toBeGreaterThanOrEqual(27 * 17);
        // …and a real share of the canvas left for the map, never a dot
        expect(width - pad.left - pad.right).toBeGreaterThanOrEqual(width * 0.25);
        expect(height - pad.top - pad.bottom).toBeGreaterThanOrEqual(height * 0.25);
      }
    }
  });

  it("never asks for more padding than the canvas has", () => {
    for (const [width, height] of [[1260, 600], [1280, 720], [1366, 768], [800, 500]] as const) {
      const pad = cameraPadding("overview", { mobile: false, width, height });
      expect(width - pad.left - pad.right).toBeGreaterThanOrEqual(width * 0.25 - 1);
      expect(height - pad.top - pad.bottom).toBeGreaterThanOrEqual(height * 0.25 - 1);
    }
  });

  it("on mobile frames the map between the header and the bottom sheet", () => {
    const height = 844;
    const sheet = Math.round(height * SHEET_PEEK);
    for (const mode of ["overview", "zone"] as const) {
      const pad = cameraPadding(mode, { mobile: true, width: 390, height });
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

describe("first view of the map (MAP-004)", () => {
  const SOL: [number, number] = [-3.7038, 40.4168];
  const inside = ([lon, lat]: [number, number], [w, s, e, n]: [number, number, number, number]) => lon > w && lon < e && lat > s && lat < n;

  it("opens on Madrid and its first ring, not on the whole region", () => {
    const [west, south, east, north] = firstViewBounds(false);
    expect(inside(SOL, firstViewBounds(false))).toBe(true);
    // First ring: Pozuelo, Alcorcón, Getafe, Rivas and Alcobendas fit; the whole region (about 1.5° by 1.3°) does not
    for (const town of [[-3.81, 40.43], [-3.83, 40.35], [-3.73, 40.31], [-3.53, 40.36], [-3.64, 40.54]] as [number, number][]) {
      expect(inside(town, firstViewBounds(false))).toBe(true);
    }
    expect(east - west).toBeLessThan(0.5);
    expect(north - south).toBeLessThan(0.4);
  });

  it("on a phone, Madrid inside the M-40: the map shows between the header and the legend", () => {
    const [west, south, east, north] = firstViewBounds(true);
    const [ww, ws, we, wn] = FIRST_VIEW.wide;
    expect(inside(SOL, firstViewBounds(true))).toBe(true);
    expect(west > ww && south > ws && east < we && north < wn).toBe(true);
  });
});
