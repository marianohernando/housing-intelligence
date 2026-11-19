/**
 * Header tabs of Vida Fácil (brief: «Mapa» · «Qué falta» · «Cómo lo calculamos»; D-251, asked by
 * Mariano on 19 nov: «Inversores», so the investor version is one tap away from the map too).
 */
import { gapsHref, parseZoneParam } from "@/lib/gaps";

export interface Tab {
  href: string;
  label: string;
  /** Extra path prefixes that belong to the tab (the zone screen lives under «Mapa»). */
  alsoUnder?: string[];
}

export const TABS: readonly Tab[] = [
  { href: "/", label: "Mapa", alsoUnder: ["/zona"] },
  { href: "/que-falta", label: "Qué falta" },
  { href: "/como-lo-calculamos", label: "Cómo lo calculamos" },
  // Its barrio sheets (/inversores/28079164) and parcel sheets (/inversores/parcela/…) are under it
  { href: "/inversores", label: "Inversores" },
];

function isUnder(pathname: string, prefix: string): boolean {
  return pathname === prefix || pathname.startsWith(`${prefix}/`);
}

function owns(tab: Tab, pathname: string): boolean {
  const own = tab.href === "/" ? pathname === "/" : isUnder(pathname, tab.href);
  return own || (tab.alsoUnder ?? []).some((prefix) => isUnder(pathname, prefix));
}

/** The href of the tab that owns `pathname`, or null outside the product pages. */
export function activeTab(pathname: string): string | null {
  return TABS.find((tab) => owns(tab, pathname))?.href ?? null;
}

const GAPS_TAB = "/que-falta";
const ZONE_PATH = /^\/zona\/(\w+\/\d+)$/;

/** Where a tab leads from `pathname`: from a zone screen, «Qué falta» opens that zone's list. */
export function tabHref(tab: Tab, pathname: string): string {
  const zone = tab.href === GAPS_TAB ? parseZoneParam(ZONE_PATH.exec(pathname)?.[1]) : null;
  return zone ? gapsHref(zone.level, zone.code) : tab.href;
}

/**
 * The zone picked on the overview, in its address (second delivery of the UX mobile audit): «Volver
 * a la lista» and the phone's back button go from the card back to the list, and the link opens the
 * zone. Its value is the map's `zone_key`: «/?zona=distrito/2807913».
 */
export const OVERVIEW_ZONE_PARAM = "zona";
const OVERVIEW_ZONE_KEY = /^(municipio|distrito|barrio)\/\w+$/;

/** The zone of `?zona=`, or null when there is none or it is not a zone of the map. */
export function overviewZoneKey(param: string | null | undefined): string | null {
  return param && OVERVIEW_ZONE_KEY.test(param) ? param : null;
}

/** The overview's address with this zone picked, or the list with none. */
export function overviewHref(zoneKey: string | null): string {
  return zoneKey ? `/?${OVERVIEW_ZONE_PARAM}=${zoneKey}` : "/";
}
