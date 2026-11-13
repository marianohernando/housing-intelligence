import { CircleCheck, CircleExclamationPoint, CircleMinus, CircleQuestionMark, type LucideIcon } from "lucide-react";

import type { GapStatus } from "@/contracts/zone_gap_list_response";
import { GAP_STATUS } from "@/lib/gaps";

import styles from "./GapBadge.module.css";

const ICONS: Record<GapStatus, LucideIcon> = {
  FALTA: CircleExclamationPoint,
  JUSTO: CircleMinus,
  CUBIERTO: CircleCheck,
  SIN_DATOS: CircleQuestionMark,
};

/** FALTA / JUSTO / CUBIERTO / SIN DATOS with icon and text (never colour alone). */
export default function GapBadge({ status }: { status: GapStatus }) {
  const Icon = ICONS[status];
  return (
    <span className={`${styles.badge} ${styles[status]}`} title={GAP_STATUS[status].help}>
      <Icon size={16} aria-hidden="true" />
      {GAP_STATUS[status].label}
    </span>
  );
}
