/**
 * Zone camera (pure, unit tested): tilt and zoom of the 3D view of a zone. The camera lands on
 * the «island» (the whole zone in view, tilted, with its raised edge) and then, for district-sized
 * zones, comes slowly closer to the zoom where buildings stand up.
 */
import { BUILDINGS_3D_ZOOM } from "./style";

export const ZONE_PITCH = { desktop: 55, mobile: 45 } as const;
export const ZONE_BEARING = -20;

/**
 * Districts up to this size (diagonal of their box) are compact city, and the camera comes closer
 * to their buildings. Larger ones (Fuencarral-El Pardo: 31 km, mostly Monte de El Pardo) would
 * land on fields, so they stay on the island, like the municipios.
 */
export const APPROACH_MAX_KM = 10;
/** Pixels kept clear between the outline and the cards, for its glow and raised edge. */
export const ISLAND_MARGIN = 12;

/** MapLibre's camera (Transform defaults): 36.87° of vertical field of view, 512 px tiles. */
const FOV = 0.6435011087932844;
const TILE = 512;

export interface ZoneCamera {
  center: [number, number];
  zoom: number;
  pitch: number;
  bearing: number;
  padding: Padding;
  width: number;
  height: number;
}

/** Web Mercator at zoom 0, in pixels (y grows southwards). */
function mercator([lon, lat]: [number, number]): [number, number] {
  const sin = Math.sin((lat * Math.PI) / 180);
  return [(TILE * (lon + 180)) / 360, TILE * (0.5 - Math.log((1 + sin) / (1 - sin)) / (4 * Math.PI))];
}

/**
 * Where a ground point lands on screen with this camera, as MapLibre draws it: the camera centre
 * goes to the middle of the padded area, and with tilt the near side looks bigger than the far
 * one. null when the point is behind the camera.
 */
export function projectAt(camera: ZoneCamera, point: [number, number]): { x: number; y: number } | null {
  const [cx, cy] = mercator(camera.center);
  const [px, py] = mercator(point);
  const scale = 2 ** camera.zoom;
  const turn = (-camera.bearing * Math.PI) / 180;
  const dx = (px - cx) * scale;
  const dy = (py - cy) * scale;
  const x = dx * Math.cos(turn) - dy * Math.sin(turn);
  const y = dx * Math.sin(turn) + dy * Math.cos(turn);
  const pitch = (camera.pitch * Math.PI) / 180;
  const distance = (0.5 / Math.tan(FOV / 2)) * camera.height;
  const depth = distance - y * Math.sin(pitch);
  if (depth <= 0) return null;
  const { padding: pad, width, height } = camera;
  const perspective = distance / depth;
  return {
    x: pad.left + (width - pad.left - pad.right) / 2 + x * perspective,
    y: pad.top + (height - pad.top - pad.bottom) / 2 + y * Math.cos(pitch) * perspective,
  };
}

/**
 * Closest zoom at which the whole outline is seen inside `clear` (the screen minus the cards),
 * tilted. MapLibre's cameraForBounds ignores the tilt, which makes the near side overflow.
 */
export function islandZoom(ring: [number, number][], camera: Omit<ZoneCamera, "zoom">, clear: Padding = camera.padding): number {
  const { width, height } = camera;
  const pad = clear;
  const fits = (zoom: number) =>
    ring.every((point) => {
      const at = projectAt({ ...camera, zoom }, point);
      return (
        at !== null &&
        at.x >= pad.left + ISLAND_MARGIN &&
        at.x <= width - pad.right - ISLAND_MARGIN &&
        at.y >= pad.top + ISLAND_MARGIN &&
        at.y <= height - pad.bottom - ISLAND_MARGIN
      );
    });
  let [low, high] = [0, 22];
  for (let i = 0; i < 30; i += 1) {
    const mid = (low + high) / 2;
    if (fits(mid)) low = mid;
    else high = mid;
  }
  return low;
}

/** Where the camera ends: compact districts (and their barrios) come closer, to where buildings stand up. */
export function approachZoom(island: number, area: { district: boolean; extentKm: number }): number {
  const compact = area.district && area.extentKm <= APPROACH_MAX_KM;
  return compact && island < BUILDINGS_3D_ZOOM ? BUILDINGS_3D_ZOOM : island;
}

/** Diagonal of a box, in km: the size of a zone, whatever the screen. */
export function extentKm([west, south, east, north]: [number, number, number, number]): number {
  const kx = Math.cos((((south + north) / 2) * Math.PI) / 180) * 111.32;
  return Math.hypot((east - west) * kx, (north - south) * 111.32);
}

/** Mobile layout (bottom sheet, compact labels); the same breakpoint as the CSS. */
export const MOBILE_QUERY = "(max-width: 760px)";

/** Share of the screen height the mobile bottom sheet takes when folded. */
export const SHEET_PEEK = 0.45;
/** Mobile header (brand and tabs) above the map. */
const MOBILE_HEADER = 130;
/** Height of the compact legend over the mobile overview map (select and one or two lines of statuses). */
const MOBILE_LEGEND = 100;

export interface Padding {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

/**
 * From this width the map screens have three columns (cards, map, cards); below it, one column of
 * cards on the left and the map on the right. The same breakpoint as the CSS (min-width: 1260px).
 */
export const THREE_COLUMNS_MIN = 1260;
/** Root font size (tokens.css: 106.25 %) and the CSS page gutter, clamp(1rem, 0.5rem + 2.5vw, 3rem). */
const REM = 17;
const gutter = (width: number) => Math.min(3 * REM, Math.max(REM, 0.5 * REM + 0.025 * width));
/** Share of the canvas the map always keeps, so the region is never a dot. */
const MIN_MAP_SHARE = 0.25;

/** Scales the padding of one axis down when it would leave the map less than its share of the canvas. */
function fitAxis(a: number, b: number, size: number): [number, number] {
  const room = size * (1 - MIN_MAP_SHARE);
  if (a + b <= room) return [a, b];
  const scale = room / (a + b);
  return [Math.floor(a * scale), Math.floor(b * scale)];
}

function fitPadding(pad: Padding, width: number, height: number): Padding {
  const [left, right] = fitAxis(pad.left, pad.right, width);
  const [top, bottom] = fitAxis(pad.top, pad.bottom, height);
  return { top, right, bottom, left };
}

/** One column of cards (28rem in the zone, 27rem in the overview) on the left, the map on the right. */
function oneColumnPadding(mode: "overview" | "zone" | "island", width: number): Padding {
  const left = Math.round(gutter(width) + (mode === "overview" ? 27 : 28) * REM + 2 * REM);
  if (mode === "zone") return { top: 90, right: 24, bottom: 60, left };
  if (mode === "island") return { top: 90, right: 104, bottom: 60, left: left + 80 };
  // The legend sits at the bottom right, over the map
  return { top: 100, right: 24, bottom: 250, left };
}

/**
 * Room for the glass cards around the map: search on the left and zone card on the right on
 * desktop; one column of cards on the left below THREE_COLUMNS_MIN (a projector at 125 %); on
 * mobile, the header above and the bottom sheet below. In the zone view a district at building
 * zoom is wider than the gap and the glass lets the map show through, so the desktop side
 * padding is smaller there. The island (the whole zone, before coming closer) must be clear of
 * the cards and of the barrios bar: it keeps the zone's centre, with wider margins. Whatever the
 * screen, the padding leaves the map a share of the canvas.
 */
export function cameraPadding(
  mode: "overview" | "zone" | "island",
  screen: { mobile: boolean; width: number; height: number },
): Padding {
  if (screen.mobile) {
    const bottom = Math.round(screen.height * SHEET_PEEK) + 16;
    // Overview: the legend («¿Qué quieres ver?» and the statuses) floats just above the sheet
    return mode === "overview"
      ? { top: MOBILE_HEADER, right: 16, bottom: bottom + MOBILE_LEGEND, left: 16 }
      : { top: MOBILE_HEADER, right: 0, bottom, left: 0 };
  }
  if (screen.width < THREE_COLUMNS_MIN) return fitPadding(oneColumnPadding(mode, screen.width), screen.width, screen.height);
  const pad =
    mode === "zone"
      ? { top: 90, right: 380, bottom: 200, left: 440 }
      : mode === "island"
        ? { top: 90, right: 460, bottom: 200, left: 520 }
        : // The bottom keeps the region above the legend («¿Qué quieres ver?» and its statuses)
          { top: 100, right: 460, bottom: 250, left: 500 };
  return fitPadding(pad, screen.width, screen.height);
}
