/** Choropleth and wording helpers for feature values (pure, unit tested). */

export interface FeatureInfo {
  feature_id: string;
  human_name: string;
  unit: string;
  direction: string;
  domain: string;
  public_use: boolean;
  limitations: string[];
}

export interface FeatureValueRow {
  territory_code: string;
  admin_unit_id: string | null;
  name: string | null;
  period_start: string;
  value: number | null;
  null_reason: string | null;
  confidence: number;
}

export const PALETTE = ["#fde7c8", "#f8c38a", "#ef9551", "#d4622a", "#9c3b16"] as const;
export const UNKNOWN_COLOR = "#c9c9c9";
export const LOW_CONFIDENCE = 0.75;

const NULL_REASON_TEXT: Record<string, string> = {
  SOURCE_MISSING: "La fuente no publica este dato para este municipio",
  NOT_APPLICABLE: "No aplica (sin población de referencia)",
  SOURCE_NO_COVERAGE: "Fuera de la cobertura de la fuente",
  STALE: "Dato desactualizado",
};

/** Quantile breaks over known values only, without duplicates or breaks at the minimum. */
export function quantileBreaks(values: number[], classes: number = PALETTE.length): number[] {
  const sorted = [...values].filter((v) => Number.isFinite(v)).sort((a, b) => a - b);
  if (sorted.length === 0) return [];
  const min = sorted[0] as number;
  const breaks: number[] = [];
  for (let i = 1; i < classes; i += 1) {
    const idx = Math.min(sorted.length - 1, Math.floor((i * sorted.length) / classes));
    const value = sorted[idx] as number;
    if (value > min && !breaks.includes(value)) breaks.push(value);
  }
  return breaks;
}

export function classIndex(value: number, breaks: number[]): number {
  let idx = 0;
  while (idx < breaks.length && value >= (breaks[idx] as number)) idx += 1;
  return idx;
}

/** Palette colour for class `index` out of `classes`, spread across the whole ramp. */
export function classColor(index: number, classes: number): string {
  if (classes <= 1) return PALETTE[Math.floor(PALETTE.length / 2)] as string;
  const position = Math.round((index * (PALETTE.length - 1)) / (classes - 1));
  return PALETTE[Math.min(position, PALETTE.length - 1)] as string;
}

export function colorFor(value: number | null, breaks: number[]): string {
  if (value === null || !Number.isFinite(value)) return UNKNOWN_COLOR;
  return classColor(classIndex(value, breaks), breaks.length + 1);
}

export function formatValue(value: number, unit: string): string {
  const digits = Math.abs(value) >= 1000 ? 0 : Math.abs(value) >= 10 ? 1 : 2;
  const number = value.toLocaleString("es-ES", { maximumFractionDigits: digits });
  return unit === "%" ? `${number} %` : `${number} ${unit}`;
}

export function describeValue(row: FeatureValueRow, info: FeatureInfo): string {
  if (row.value === null) {
    return NULL_REASON_TEXT[row.null_reason ?? ""] ?? "Dato desconocido";
  }
  const year = row.period_start.slice(0, 4);
  const text = `${formatValue(row.value, info.unit)} (${year})`;
  return row.confidence < LOW_CONFIDENCE ? `${text} · fiabilidad baja: municipio pequeño` : text;
}
