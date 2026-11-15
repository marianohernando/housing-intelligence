import { CircleDashed } from "lucide-react";

import { SMALL_ZONE } from "@/lib/gaps";

import styles from "./GapBadge.module.css";

/**
 * fila.zona_pequena: «No comparable», instead of the status when the API sends `reliable: false`
 * and no group (D-213, D-230). `help` is read by screen readers after the label and says the same
 * as the visible words around the tag: the row's reason (notComparableHelp) on a row, the common
 * sentence (the default) in a legend; null where the row's reason is visible right in the row and
 * would be read twice («Qué falta»).
 */
export default function SmallZoneTag({ help = SMALL_ZONE.help }: { help?: string | null }) {
  return (
    <span className={`${styles.badge} ${styles.small}`}>
      <CircleDashed size={16} aria-hidden="true" />
      {SMALL_ZONE.label}
      {help && <span className="visually-hidden">. {help}</span>}
    </span>
  );
}
