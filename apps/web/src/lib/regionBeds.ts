/**
 * Hospital beds of the whole region (D-231, pure, unit tested). The two CM tables («Dotación de
 * camas por dependencia» and «Hospitales y datos asistenciales») only publish the regional total, so
 * they go as context under the hospital note, never into a zone's row (D-218 §7).
 */
import type { FeatureValueRow } from "@/lib/features";
import { formatNumber } from "@/lib/format";

export const REGION_BEDS_FEATURES = { hospitals: "hospitales_total", beds: "camas_instaladas_por_1000_hab" } as const;

/** One figure of the line, with the dataset it comes from (the feature's lineage) to link it. */
export interface RegionFigure {
  row: FeatureValueRow | undefined;
  datasetId: string | null;
}

export interface RegionBedsLine {
  hospitals: { text: string; datasetId: string | null };
  beds: { text: string; datasetId: string | null };
  /** «2023», or «2023 y 2024» if the two tables are of different years */
  year: string;
}

/**
 * «En toda la Comunidad hay 85 hospitales y 3,0 camas instaladas por cada 1.000 habitantes (2023)»,
 * in parts so each figure can link its dataset. null when either figure is missing: half a line
 * would read as if the other were zero.
 */
export function regionBedsLine(hospitals: RegionFigure, beds: RegionFigure): RegionBedsLine | null {
  const [h, b] = [hospitals.row, beds.row];
  if (h?.value == null || b?.value == null) return null;
  const years = [...new Set([h.period_start.slice(0, 4), b.period_start.slice(0, 4)])].sort();
  return {
    hospitals: { text: `${formatNumber(h.value, 0)} ${h.value === 1 ? "hospital" : "hospitales"}`, datasetId: hospitals.datasetId },
    beds: { text: `${formatNumber(b.value, 1)} camas instaladas por cada 1.000 habitantes`, datasetId: beds.datasetId },
    year: years.join(" y "),
  };
}

/** The dataset a feature's values come from: the only one in its lineage, or none when there are several. */
export function lineageDataset(datasetVersions: Record<string, string> | undefined): string | null {
  const ids = Object.keys(datasetVersions ?? {});
  return ids.length === 1 ? (ids[0] ?? null) : null;
}
