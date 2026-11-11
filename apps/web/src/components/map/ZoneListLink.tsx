import PillLink from "@/components/ui/PillLink";

/** pitch/textos_web.md, mapa.alternativa: always in view, for whoever does not use the map. */
export const ZONE_LIST_TEXT = "Ver las zonas en una lista";

export default function ZoneListLink() {
  return <PillLink href="/zonas">{ZONE_LIST_TEXT}</PillLink>;
}
