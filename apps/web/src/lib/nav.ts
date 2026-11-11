/** Header tabs of Vida Fácil (brief: «Mapa» · «Qué falta» · «Cómo lo calculamos»). */

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
