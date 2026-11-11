"use client";

import PillLink from "@/components/ui/PillLink";

import { useGapLayer } from "./GapLayerProvider";

/** pitch/textos_web.md, mapa.alternativa: always in view, for whoever does not use the map. */
export const ZONE_LIST_TEXT = "Ver las zonas en una lista";

/** The list of zones; with a row of «Qué falta» on the map, the list shows that row too. */
export default function ZoneListLink() {
  const { row } = useGapLayer();
  return <PillLink href={row ? `/zonas?fila=${row}` : "/zonas"}>{ZONE_LIST_TEXT}</PillLink>;
}
