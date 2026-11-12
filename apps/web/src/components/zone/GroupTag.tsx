import { Users } from "lucide-react";

import { GROUP } from "@/lib/gaps";

import styles from "./GapBadge.module.css";

/**
 * Next to the status when the API sends `comparison_group` (gap-0.3, D-217): the status is that of
 * the zone together with its nearest neighbours of the same type. The help is read by screen
 * readers and shown on hover; the row of «Qué falta» names the neighbours, so there it goes
 * without the hidden help (`described={false}`), which would repeat its first sentence.
 */
export default function GroupTag({ described = true }: { described?: boolean }) {
  return (
    <span className={`${styles.badge} ${styles.group}`} title={GROUP.help}>
      <Users size={16} aria-hidden="true" />
      {GROUP.label}
      {described && <span className="visually-hidden">. {GROUP.help}</span>}
    </span>
  );
}
