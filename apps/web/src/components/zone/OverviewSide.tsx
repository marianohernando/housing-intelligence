"use client";

import type { ReactNode } from "react";

import { useMapZones } from "@/components/map/MapProvider";

import ZoneCard from "./ZoneCard";

/** Right column of the overview: the card of the zone picked on the map, or `children` until then. */
export default function OverviewSide({ children, className }: { children: ReactNode; className?: string }) {
  const { selectedZone, select } = useMapZones();
  return (
    <div className={className}>
      {selectedZone ? <ZoneCard zone={selectedZone} mode="overview" onClose={() => select(null)} /> : children}
    </div>
  );
}
