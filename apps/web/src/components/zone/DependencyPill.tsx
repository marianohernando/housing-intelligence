import { Building2, ShieldPlus } from "lucide-react";

import { type Dependency, DEPENDENCY_PILL } from "@/lib/map/facilities";

import styles from "./DependencyPill.module.css";

/**
 * «Público» (filled) or «Privado» (outlined) before a hospital's name, in «Todos los centros» and on
 * its map label (centros.hospital.pastilla, D-239). The word says it; the icon and the fill only help.
 */
export default function DependencyPill({ dependency }: { dependency: Dependency }) {
  // Not Landmark: «Cultura» uses it in the same panel (D-236)
  const Icon = dependency === "publica" ? ShieldPlus : Building2;
  return (
    <span className={dependency === "publica" ? styles.public : styles.private}>
      <Icon size={13} strokeWidth={2.25} aria-hidden="true" />
      {DEPENDENCY_PILL[dependency]}
    </span>
  );
}
