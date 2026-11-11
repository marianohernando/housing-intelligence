import { GraduationCap, type LucideIcon, Stethoscope, TrainFront } from "lucide-react";

import type { KeyPoint, KeyPointKind } from "@/lib/map/places";

import styles from "./VidaMap.module.css";

const ICONS: Record<KeyPointKind, LucideIcon> = {
  transporte: TrainFront,
  salud: Stethoscope,
  colegio: GraduationCap,
};

/** Glass label of a key point in the 3D zone view (mockup 2). */
export default function KeyPointLabel({ point }: { point: KeyPoint }) {
  const Icon = ICONS[point.kind];
  return (
    <div className={styles.label}>
      <span className={styles.labelIcon} aria-hidden="true">
        <Icon size={18} strokeWidth={2.2} />
      </span>
      <span className={styles.labelText}>
        <span className={styles.labelKind}>{point.label}</span>
        {point.name && <span className={styles.labelName}>{point.name}</span>}
      </span>
      <span className={styles.labelPin} aria-hidden="true" />
    </div>
  );
}
