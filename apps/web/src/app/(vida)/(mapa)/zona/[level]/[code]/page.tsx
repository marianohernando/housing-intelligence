import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { preload } from "react-dom";

import { zoneGapsUrl } from "@/lib/api";

import ZoneIntro from "./ZoneIntro";

/** Zone levels of the map (D-200): municipios, and Madrid capital by its districts. */
const LEVELS = ["municipio", "distrito"] as const;
const isLevel = (level: string): level is (typeof LEVELS)[number] => (LEVELS as readonly string[]).includes(level);

function decoded(code: string): string | null {
  try {
    return decodeURIComponent(code);
  } catch {
    return null;
  }
}

export const metadata: Metadata = { title: "Zona" };

export default async function ZonaPage({ params }: { params: Promise<{ level: string; code: string }> }) {
  const { level, code } = await params;
  if (!isLevel(level)) notFound();
  // The zone's «Qué falta» answer names it: the browser asks for it with the HTML, not after the
  // scripts, so the screen shows the zone as soon as it starts (the same request, reused by fetch).
  const zoneCode = decoded(code);
  if (zoneCode) preload(zoneGapsUrl(level, zoneCode), { as: "fetch", crossOrigin: "anonymous" });
  return <ZoneIntro />;
}
