"use client";

import { MapPin } from "lucide-react";
import { useId } from "react";

import { useMapZones } from "@/components/map/MapProvider";
import Chip from "@/components/ui/Chip";
import GlassCard from "@/components/ui/GlassCard";

import styles from "./BarriosBar.module.css";

// Copy from pitch/textos_web.md (barrios.titulo, barrios.todo, barrios.ayuda)
const TEXT = {
  title: "Ir a un barrio",
  all: (zone: string) => `Todo ${zone}`,
  help: "Mueve el mapa a ese barrio. Las cifras de «Qué falta» son del distrito entero.",
};

/**
 * Bottom bar of mockup 2: the barrios of a district, to move the camera between them. The demo
 * has no figures by barrio, so it only navigates; zones without barrios do not show it.
 */
export default function BarriosBar() {
  const { routeZone, barrios, barrio, focusBarrio } = useMapZones();
  const titleId = useId();
  if (!routeZone || !barrios?.length) return null;
  const focused = barrio?.properties.admin_unit_id ?? null;
  return (
    <GlassCard as="section" aria-labelledby={titleId} aria-describedby={`${titleId}-ayuda`} className={styles.bar}>
      <p id={`${titleId}-ayuda`} className="visually-hidden">
        {TEXT.help}
      </p>
      <h2 id={titleId} className={styles.title}>
        {TEXT.title}
      </h2>
      <ul className={styles.list}>
        <li>
          <Chip label={TEXT.all(routeZone.name)} pressed={focused === null} onToggle={() => focusBarrio(null)} />
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
