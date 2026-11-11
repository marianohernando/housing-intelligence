/** Zone camera (pure, unit tested): tilt and zoom of the 3D view of a zone. */
import { BUILDINGS_3D_ZOOM } from "./style";

export const ZONE_PITCH = { desktop: 55, mobile: 45 } as const;
export const ZONE_BEARING = -20;

/** Tilted, the zone recedes, so the camera comes closer than the flat fit. */
const TILT_BOOST = { desktop: 0.75, mobile: 0.4 } as const;
/** Zones that already fit from this zoom are district-sized: take them to where buildings stand up. */
const SNAP_FROM = 12.5;

export function zoneZoom(fitted: number, mobile: boolean): number {
  const zoom = fitted + (mobile ? TILT_BOOST.mobile : TILT_BOOST.desktop);
  return zoom >= SNAP_FROM && zoom < BUILDINGS_3D_ZOOM ? BUILDINGS_3D_ZOOM : zoom;
}

/** Mobile layout (bottom sheet, compact labels); the same breakpoint as the CSS. */
export const MOBILE_QUERY = "(max-width: 760px)";

/** Share of the screen height the mobile bottom sheet takes when folded. */
export const SHEET_PEEK = 0.45;
/** Mobile header (brand and tabs) above the map. */
const MOBILE_HEADER = 130;

export interface Padding {
  top: number;
  right: number;
  bottom: number;
  left: number;
}

/**
 * Room for the glass cards around the map: search on the left and zone card on the right on
 * desktop; on mobile, the header above and the bottom sheet below. In the zone view a district
 * at building zoom is wider than the gap and the glass lets the map show through, so the
 * desktop side padding is smaller there.
 */
export function cameraPadding(mode: "overview" | "zone", screen: { mobile: boolean; height: number }): Padding {
  if (screen.mobile) {
    const bottom = Math.round(screen.height * SHEET_PEEK) + 16;
    return mode === "zone" ? { top: MOBILE_HEADER, right: 0, bottom, left: 0 } : { top: MOBILE_HEADER, right: 16, bottom, left: 16 };
  }
  if (mode === "zone") return { top: 90, right: 380, bottom: 200, left: 440 };
  return { top: 100, right: 460, bottom: 40, left: 500 };
}
