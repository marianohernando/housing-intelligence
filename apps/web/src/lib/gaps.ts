/** «Qué falta» statuses in plain words (pitch/textos_web.md, estado.*): always text and icon. */
import type { GapStatus } from "@/contracts/zone_gap_list_response";

export const GAP_STATUS: Record<GapStatus, { label: string; help: string }> = {
  FALTA: { label: "FALTA", help: "Esta zona está claramente peor que el conjunto de la Comunidad de Madrid." },
  JUSTO: { label: "JUSTO", help: "Esta zona está algo peor que el conjunto de la Comunidad de Madrid." },
  CUBIERTO: { label: "CUBIERTO", help: "Esta zona está igual o mejor que el conjunto de la Comunidad de Madrid." },
  SIN_DATOS: { label: "SIN DATOS", help: "No tenemos este dato para esta zona. No quiere decir que no haya." },
};

/**
 * Rows the API has not computed yet at a level are absent (never SIN DATOS). Today the API only
 * warns when none is computed: «No indicators computed at this level yet» (routes/gaps.py).
 */
export function rowsPending(warnings: string[] | undefined): boolean {
  return (warnings ?? []).some((w) => /computed at this level/i.test(w));
}

const ORDER: Record<GapStatus, number> = { FALTA: 0, JUSTO: 1, CUBIERTO: 2, SIN_DATOS: 3 };

/** The zone card shows three rows: what is missing first. */
export function topRows<T extends { status: GapStatus }>(rows: T[], limit = 3): T[] {
  return [...rows].sort((a, b) => ORDER[a.status] - ORDER[b.status]).slice(0, limit);
}
