import { CircleDashed } from "lucide-react";

import { SMALL_ZONE } from "@/lib/gaps";

import styles from "./GapBadge.module.css";

/**
 * fila.zona_pequena: «No comparable», instead of the status when the API sends `reliable: false`
 * and no group (D-213, D-230). The help is read by screen readers and visible where the tag shows:
 * the row's reason in «Qué falta», its legend, the card's key and «¿Qué quiere decir cada estado?».
 */
export default function SmallZoneTag() {
  return (
    <span className={`${styles.badge} ${styles.small}`}>
      <CircleDashed size={16} aria-hidden="true" />
      {SMALL_ZONE.label}
      <span className="visually-hidden">. {SMALL_ZONE.help}</span>
    </span>
  );
}
