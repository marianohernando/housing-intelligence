import { Building2, Landmark } from "lucide-react";

import { type Dependency, DEPENDENCY_PILL } from "@/lib/map/facilities";

import styles from "./DependencyPill.module.css";

/**
 * «Público» (filled) or «Privado» (outlined) before a hospital's name, in «Todos los centros» and on
 * its map label (centros.hospital.pastilla, D-239). The word says it; the icon and the fill only help.
 */
export default function DependencyPill({ dependency }: { dependency: Dependency }) {
  const Icon = dependency === "publica" ? Landmark : Building2;
  return (
    <span className={dependency === "publica" ? styles.public : styles.private}>
      <Icon size={13} strokeWidth={2.25} aria-hidden="true" />
      {DEPENDENCY_PILL[dependency]}
    </span>
  );
}
