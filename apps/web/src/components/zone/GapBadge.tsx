import { CircleCheck, CircleExclamationPoint, CircleMinus, CircleQuestionMark, Info, type LucideIcon } from "lucide-react";

import type { GapStatus } from "@/contracts/zone_gap_list_response";
import { GAP_STATUS } from "@/lib/gaps";

import styles from "./GapBadge.module.css";

const ICONS: Record<GapStatus, LucideIcon> = {
  FALTA: CircleExclamationPoint,
  JUSTO: CircleMinus,
  CUBIERTO: CircleCheck,
  SIN_DATOS: CircleQuestionMark,
  CONTEXTO: Info,
};

/**
 * FALTA / JUSTO / CUBIERTO / SIN DATOS / CONTEXTO with icon and text (never colour alone). What each means is
 * visible where the badges show (the card's key, the legend of «Qué falta», «¿Qué quiere decir cada
 * estado?» of the lists): a tooltip never showed on a phone (UX mobile audit, A5).
 */
export default function GapBadge({ status }: { status: GapStatus }) {
  const Icon = ICONS[status];
  return (
    <span className={`${styles.badge} ${styles[status]}`}>
      <Icon size={16} aria-hidden="true" />
      {GAP_STATUS[status].label}
    </span>
  );
}
