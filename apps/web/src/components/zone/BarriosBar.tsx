"use client";

import { MapPin } from "lucide-react";
import { useId } from "react";

import { useMapZones } from "@/components/map/MapProvider";
import Chip from "@/components/ui/Chip";
import GlassCard from "@/components/ui/GlassCard";

import styles from "./BarriosBar.module.css";

// Copy: barrios.titulo from pitch/textos_web.md; «Todo {zona}» is provisional, pending line D.
const TEXT = {
  title: "Barrios de la zona",
  all: (zone: string) => `Todo ${zone}`,
};

/**
 * Bottom bar of mockup 2: the barrios of a district, to move the camera between them. The demo
 * has no figures by barrio, so it only navigates; zones without barrios do not show it.
 */
export default function BarriosBar() {
  const { activeZone, barrios, barrio, focusBarrio } = useMapZones();
  const titleId = useId();
  if (!activeZone || !barrios?.length) return null;
  const focused = barrio?.properties.admin_unit_id ?? null;
  return (
    <GlassCard as="section" aria-labelledby={titleId} className={styles.bar}>
      <h2 id={titleId} className={styles.title}>
        {TEXT.title}
      </h2>
      <ul className={styles.list}>
        <li>
          <Chip label={TEXT.all(activeZone.properties.name)} pressed={focused === null} onToggle={() => focusBarrio(null)} />
        </li>
        {barrios.map(({ properties: { admin_unit_id: id, name, code } }) => (
          <li key={id}>
            <Chip icon={MapPin} label={name ?? code} pressed={focused === id} onToggle={() => focusBarrio(id)} />
          </li>
        ))}
      </ul>
    </GlassCard>
  );
}
