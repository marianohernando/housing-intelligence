/** Header tabs of Vida Fácil (brief: «Mapa» · «Qué falta» · «Cómo lo calculamos»). */
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
