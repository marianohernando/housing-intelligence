"use client";

import { type ReactNode, useEffect, useRef } from "react";

import { useMapZones } from "@/components/map/MapProvider";
import { MOBILE_QUERY } from "@/lib/map/camera";

import ZoneCard from "./ZoneCard";

/** Right column of the overview: the card of the zone picked on the map, or `children` until then. */
export default function OverviewSide({ children, className }: { children: ReactNode; className?: string }) {
  const { selectedZone, select } = useMapZones();
  const ref = useRef<HTMLDivElement>(null);
  const picked = selectedZone?.properties.zone_key;

  // Mobile: the card is down in the bottom sheet, so bring it into view when a zone is picked.
  useEffect(() => {
    if (!picked || !window.matchMedia(MOBILE_QUERY).matches) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    ref.current?.scrollIntoView({ block: "start", behavior: reduced ? "auto" : "smooth" });
  }, [picked]);

  return (
    <div ref={ref} className={className}>
      {selectedZone ? <ZoneCard zone={selectedZone} mode="overview" onClose={() => select(null)} /> : children}
    </div>
  );
}
