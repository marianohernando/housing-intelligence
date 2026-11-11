import type { Metadata } from "next";
import { notFound } from "next/navigation";

import ZoneIntro from "./ZoneIntro";

/** Zone levels of the map (D-200): municipios, and Madrid capital by its districts. */
const LEVELS: readonly string[] = ["municipio", "distrito"];

export const metadata: Metadata = { title: "Zona" };

export default async function ZonaPage({ params }: { params: Promise<{ level: string; code: string }> }) {
  const { level } = await params;
  if (!LEVELS.includes(level)) notFound();
  return <ZoneIntro />;
}
