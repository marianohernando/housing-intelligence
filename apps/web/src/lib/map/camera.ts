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
