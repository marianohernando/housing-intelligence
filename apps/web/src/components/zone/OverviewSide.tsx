"use client";

import { type ReactNode, useEffect, useRef, useState } from "react";

import { useMapZones } from "@/components/map/MapProvider";
import { MOBILE_QUERY } from "@/lib/map/camera";

import ZoneCard from "./ZoneCard";

const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/**
 * Right column of the overview: the card of the zone picked on the map or in the list, or
 * `children` until then. The list stays mounted under the card (only hidden), so «Volver a la
 * lista» finds it as it was: unfolded or not, with the focus back on the row that was opened.
 */
export default function OverviewSide({ children, className }: { children: ReactNode; className?: string }) {
  const { selectedZone, backToList } = useMapZones();
  const ref = useRef<HTMLDivElement>(null);
  const picked = selectedZone?.properties.zone_key ?? null;
  // The zone whose card was just closed (a new object each time, so closing it twice counts twice)
  const [left, setLeft] = useState<{ key: string } | null>(null);
  const [shown, setShown] = useState(picked);
  if (shown !== picked) {
    setShown(picked);
    if (shown !== null && picked === null) setLeft({ key: shown });
  }

  // Mobile: the card is down in the bottom sheet, so bring it into view when a zone is picked.
  useEffect(() => {
    if (!picked || !window.matchMedia(MOBILE_QUERY).matches) return;
    ref.current?.scrollIntoView({ block: "start", behavior: reducedMotion() ? "auto" : "smooth" });
  }, [picked]);

  // Back to the list: the focus, lost with the card, goes to the row of the zone that was open (or,
  // folded away, to the list's title) and it comes into view. Never when the person is elsewhere
  // (typing in the search when a new search closes the card)
  useEffect(() => {
    if (!left) return;
    const active = document.activeElement;
    if (active && active !== document.body && document.contains(active)) return;
    // The row, if it is in view (not folded under «Ver las 10 primeras»), else the list's title (review R-09 of PR #81)
    const shown = (el: HTMLElement | null | undefined) => (el && (el.checkVisibility?.() ?? el.getClientRects().length > 0) ? el : null);
    const row = shown(ref.current?.querySelector<HTMLElement>(`[data-zone="${left.key}"]`)) ?? ref.current?.querySelector<HTMLElement>("h2[tabindex='-1']");
    const mobile = window.matchMedia(MOBILE_QUERY).matches;
    row?.focus({ preventScroll: mobile });
    // In the bottom sheet the focus alone would leave it at an edge
    if (mobile) row?.scrollIntoView({ block: "center", behavior: "auto" });
  }, [left]);

  return (
    <div ref={ref} className={className}>
      {selectedZone && <ZoneCard key={selectedZone.properties.zone_key} zone={selectedZone.properties} mode="overview" onBack={backToList} />}
      <div hidden={selectedZone !== null}>{children}</div>
    </div>
  );
}
