import { CircleDashed } from "lucide-react";

import { SMALL_ZONE } from "@/lib/gaps";

import styles from "./GapBadge.module.css";

/**
 * fila.zona_pequena: «Zona pequeña para comparar», next to the status when the API sends
 * `reliable: false` (D-213). The help is read by screen readers and shown on hover; the legend
 * of «Qué falta» shows it in full.
 */
export default function SmallZoneTag() {
  return (
    <span className={`${styles.badge} ${styles.small}`} title={SMALL_ZONE.help}>
      <CircleDashed size={16} aria-hidden="true" />
      {SMALL_ZONE.label}
      <span className="visually-hidden">. {SMALL_ZONE.help}</span>
    </span>
  );
}
