/**
 * How the neighbours of a Madrid district rate the safety of their own barrio (pure, unit tested):
 * DATA-020, D-226 §1. Context in the zone view only: it does not score, rank or enter «Qué falta»,
 * it is opinion and not crime, and it is never shown with status or alarm colours.
 */
import { formatNumber } from "@/lib/format";
import type { FeatureValueRow } from "@/lib/features";

/** Features of GET /api/v1/features/{id}/values: night and day, 0 to 10 (Encuesta de calidad de vida). */
export const PERCEIVED_SAFETY_FEATURES = { night: "seguridad_percibida_noche", day: "seguridad_percibida_dia" } as const;

export interface SafetyRows {
  /** level=distrito: the 21 districts */
  night: readonly FeatureValueRow[];
  day: readonly FeatureValueRow[];
  /** level=municipio: the city, the reference; the other municipios come without a value */
  nightCity: readonly FeatureValueRow[];
  dayCity: readonly FeatureValueRow[];
}

export interface PerceivedSafety {
  night: number;
  day: number;
  /** The city's, or null when the API does not give it */
  city: { night: number; day: number } | null;
  year: string;
}

/** The latest known value of a territory, with its year; null without one (never 0). */
function latest(rows: readonly FeatureValueRow[], code: string): { value: number; year: string } | null {
  const known = rows.filter((r) => r.territory_code === code && r.value !== null);
  const last = known.sort((a, b) => b.period_start.localeCompare(a.period_start))[0];
  return last && last.value !== null ? { value: last.value, year: last.period_start.slice(0, 4) } : null;
}

/**
 * A district's night and day ratings with the city's of the same year. A district's INE code is its
 * municipio's (5 digits) and two more, so «2807905» is in «28079». Null when the district has no
 * rating for both, or they are from different years.
 */
export function perceivedSafety(districtCode: string, rows: SafetyRows): PerceivedSafety | null {
  const [night, day] = [latest(rows.night, districtCode), latest(rows.day, districtCode)];
  if (!night || !day || night.year !== day.year) return null;
  const cityCode = districtCode.slice(0, 5);
  const [cityNight, cityDay] = [latest(rows.nightCity, cityCode), latest(rows.dayCity, cityCode)];
  const city = cityNight && cityDay && cityNight.year === night.year && cityDay.year === night.year ? { night: cityNight.value, day: cityDay.value } : null;
  return { night: night.value, day: day.value, city, year: night.year };
}

const score = (value: number) => formatNumber(value, 1);

/**
 * zona.seguridad_vecinos of pitch/textos_web.md: what the neighbours say, then where it comes from.
 * «Unas 400 personas por distrito» is the 2025 survey's sample (D-226 §1): line D's copy, to review
 * if a later year comes with another sample.
 */
export function perceivedSafetyText(s: PerceivedSafety): { rating: string; source: string } {
  const city = s.city ? ` (en todo Madrid, ${score(s.city.night)} y ${score(s.city.day)})` : "";
  return {
    rating: `Así valoran sus vecinos la seguridad de su barrio: ${score(s.night)} de noche y ${score(s.day)} de día, de 0 a 10${city}.`,
    source: `Encuesta de calidad de vida del Ayuntamiento de Madrid, ${s.year}, unas 400 personas por distrito.`,
  };
}
