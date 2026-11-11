/**
 * «Qué falta» in plain words (pure, unit tested): statuses, rows, figures and walking minutes of
 * GET /api/v1/gaps, with the copy of pitch/textos_web.md (estado.*, fila.*, falta.*).
 */
import type { GapRowKey, GapStatus, IndicatorValue, NullReason } from "@/contracts/zone_gap_list_response";
import { formatNumber } from "@/lib/format";
import type { ZoneLevel } from "@/lib/map/zones";

export const GAP_STATUS: Record<GapStatus, { label: string; help: string }> = {
  FALTA: { label: "FALTA", help: "Esta zona está claramente peor que el conjunto de la Comunidad de Madrid." },
  JUSTO: { label: "JUSTO", help: "Esta zona está algo peor que el conjunto de la Comunidad de Madrid." },
  CUBIERTO: { label: "CUBIERTO", help: "Esta zona está igual o mejor que el conjunto de la Comunidad de Madrid." },
  SIN_DATOS: { label: "SIN DATOS", help: "No tenemos este dato para esta zona. No quiere decir que no haya." },
};

/** Row names when the API does not send one (fila.*): the rows it has not computed yet. */
export const ROW_NAME: Record<GapRowKey, string> = {
  escuela_infantil: "Escuelas infantiles",
  colegio: "Colegios",
  centro_salud: "Centros de salud",
  mayores: "Mayores",
  farmacia: "Farmacias",
  vivienda: "Vivienda",
};

/** What each row counts, per population, against the whole region (line A's /gaps, 11 nov). */
export const ROW_MEASURE: Record<GapRowKey, string> = {
  escuela_infantil: "Escuelas infantiles por cada 1.000 niños de 0 a 4 años",
  colegio: "Colegios con primaria, públicos o concertados, por cada 1.000 menores de 15 años",
  centro_salud: "Centros de atención primaria por cada 10.000 habitantes",
  mayores: "Hogares, clubes y centros de día por cada 1.000 personas de 65 años o más",
  farmacia: "Farmacias por cada 10.000 habitantes",
  vivienda: "Viviendas de más de 90 m² por cada 100 hogares de 4 o más personas",
};

/** Why a value is missing (falta, «Por qué falta un dato»). */
export const NULL_REASON: Record<NullReason, string> = {
  SOURCE_NO_COVERAGE: "La fuente oficial no publica este dato para esta zona.",
  SOURCE_MISSING: "La fuente oficial no trae este dato.",
  NOT_APPLICABLE: "Este dato no tiene sentido en esta zona.",
  TEMPORARILY_UNAVAILABLE: "Este dato no está disponible ahora mismo. Vuelve a intentarlo más tarde.",
  STALE: "El último dato publicado es demasiado antiguo para usarlo.",
  PARSE_ERROR: "El dato publicado venía con errores y no lo usamos.",
  ENTITY_NOT_RESOLVED: "No hemos podido situar este dato en el mapa.",
  ESTIMATION_NOT_ALLOWED: "No hay dato oficial y preferimos no inventarlo.",
  UNKNOWN: "No sabemos este dato.",
};

const ROW_ORDER = Object.keys(ROW_NAME) as GapRowKey[];
const PENDING = /^INSUFFICIENT_DATA: row (\w+) not computed at \w+ level yet$/;

/**
 * Rows the API has not computed at this level yet: one warning each (services/gaps.py,
 * missing_row_warnings). They are absent from the list and never shown as SIN DATOS.
 */
export function pendingRows(warnings: readonly string[] | undefined): GapRowKey[] {
  const keys = new Set((warnings ?? []).map((w) => PENDING.exec(w)?.[1]));
  return ROW_ORDER.filter((key) => keys.has(key));
}

const STATUS_ORDER: Record<GapStatus, number> = { FALTA: 0, JUSTO: 1, CUBIERTO: 2, SIN_DATOS: 3 };

/** What is missing first; rows with the same status keep the API order. */
export function sortRows<T extends { status: GapStatus }>(rows: readonly T[]): T[] {
  return [...rows].sort((a, b) => STATUS_ORDER[a.status] - STATUS_ORDER[b.status]);
}

/** The zone card shows three rows: what is missing first. */
export function topRows<T extends { status: GapStatus }>(rows: readonly T[], limit = 3): T[] {
  return sortRows(rows).slice(0, limit);
}

/** Value and regional reference with the decimals of the API `explanation` (hi_domain.gaps). */
export function gapFigures(value: number | null, reference: number | null): { value: string | null; reference: string | null } {
  const decimals = Math.max(Math.abs(value ?? 0), Math.abs(reference ?? 0)) < 1 ? 2 : 1;
  return {
    value: value === null ? null : formatNumber(value, decimals),
    reference: reference === null ? null : formatNumber(reference, decimals),
  };
}

const WALKING_PREFIX = "min_a_pie_";
const WALKING_CAP_MIN = 60;

/** The walking minutes among a row's extra indicators (CORE-005, median of the zone's streets). */
export function walking(extras: readonly IndicatorValue[] | undefined): IndicatorValue | undefined {
  return extras?.find((e) => e.feature_id.startsWith(WALKING_PREFIX));
}

export function walkingText({ value }: Pick<IndicatorValue, "value">): string {
  if (value === null) return "sin dato";
  if (value > WALKING_CAP_MIN) return `más de ${WALKING_CAP_MIN} min`;
  if (value < 1) return "menos de 1 min";
  return `${Math.round(value)} min`;
}

/** Where the walking minutes go to, by row (falta.fila.a_pie); vivienda has none. */
export const WALK_TO: Partial<Record<GapRowKey, string>> = {
  escuela_infantil: "la escuela infantil más cercana",
  colegio: "el colegio más cercano",
  centro_salud: "el centro de salud más cercano",
  mayores: "el centro de mayores más cercano",
  farmacia: "la farmacia más cercana",
};

const ZONE_LEVELS: readonly ZoneLevel[] = ["municipio", "distrito"];

/** The «Qué falta» tab for one zone of the map. */
export function gapsHref(level: ZoneLevel, code: string): string {
  return `/que-falta?zona=${level}/${encodeURIComponent(code)}`;
}

/** `?zona=distrito/2807905` back to a zone of the map, or null when it is not one. */
export function parseZoneParam(param: string | string[] | undefined): { level: ZoneLevel; code: string } | null {
  if (typeof param !== "string") return null;
  const [, level, code] = /^(\w+)\/(\d+)$/.exec(param) ?? [];
  if (!level || !code || !ZONE_LEVELS.includes(level as ZoneLevel)) return null;
  return { level: level as ZoneLevel, code };
}
