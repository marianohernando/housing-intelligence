/**
 * «Dónde invertir primero» in plain words (pure, unit tested): GET /api/v1/gaps/impact (D-229,
 * impact-0.1), the people who live where each row is missing and the zones in FALTA ranked by them.
 * Every figure comes from the API; the web only words it.
 */
import type { GapImpactRow, GapImpactZone } from "@/contracts/gap_impact_response";
import { formatNumber } from "@/lib/format";
import { comparisonText, gapsHref, inGroup, parseZoneParam, ROW_IN_LIST } from "@/lib/gaps";

/** Zones of each row shown before «Ver N zonas más». */
export const SHOWN_FIRST = 3;

/** The big figure of a row: «25.551». */
export function impactFigure(row: Pick<GapImpactRow, "people_in_falta">): string {
  return formatNumber(row.people_in_falta, 0);
}

/** What the figure counts: «niños de 0 a 4 años viven donde faltan escuelas infantiles». */
export function impactSentence(row: Pick<GapImpactRow, "people_label" | "row">): string {
  return `${row.people_label} viven donde faltan ${ROW_IN_LIST[row.row]}`;
}

/** «El 9,8 % de toda la Comunidad, en 3 zonas.» */
export function impactContext(row: Pick<GapImpactRow, "share_in_falta" | "zones_in_falta">): string {
  const zones = row.zones_in_falta === 1 ? "1 zona" : `${row.zones_in_falta} zonas`;
  return `El ${formatNumber(100 * row.share_in_falta, 1)} % de toda la Comunidad, en ${zones}.`;
}

/** Rows with people in FALTA, in the API order, apart from those with no zone clearly short. */
export function splitImpactRows<T extends Pick<GapImpactRow, "people_in_falta">>(rows: readonly T[]): { affected: T[]; clear: T[] } {
  return { affected: rows.filter((r) => r.people_in_falta > 0), clear: rows.filter((r) => r.people_in_falta === 0) };
}

export interface RankedZone {
  key: string;
  name: string;
  /** The zone's «Qué falta» list, or null for a level the web has no list of */
  href: string | null;
  people: string;
  comparison: string;
}

/** One zone of the ranking: its people and how much it has against similar municipios (the group's ratio when grouped). */
export function rankedZone(zone: GapImpactZone, peopleLabel: string): RankedZone {
  const parsed = parseZoneParam(`${zone.level}/${zone.code}`);
  return {
    key: zone.admin_unit_id,
    name: zone.name,
    href: parsed ? gapsHref(parsed.level, parsed.code) : null,
    people: `${formatNumber(zone.people, 0)} ${peopleLabel}`,
    comparison: comparisonText(zone.ratio_to_reference, inGroup(zone) !== null),
  };
}

/** «Ver 3 zonas más» / «Ver 1 zona más» */
export function moreZonesText(n: number): string {
  return n === 1 ? "Ver 1 zona más" : `Ver ${n} zonas más`;
}
