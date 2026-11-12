/**
 * «Qué falta» in plain words (pure, unit tested): statuses, rows, figures and walking minutes of
 * GET /api/v1/gaps, with the copy of pitch/textos_web.md (estado.*, fila.*, falta.*).
 */
import type { ComparisonGroup, GapRowKey, GapStatus, IndicatorValue, NullReason } from "@/contracts/zone_gap_list_response";
import { formatNumber } from "@/lib/format";
import type { ZoneLevel } from "@/lib/map/zones";

/** estado.* (gap-0.2, D-213: each zone against the other municipios of its type). */
export const GAP_STATUS: Record<GapStatus, { label: string; help: string }> = {
  FALTA: { label: "FALTA", help: "Tiene claramente menos que los municipios de su tipo, y no es por el tamaño de la zona." },
  JUSTO: { label: "JUSTO", help: "Tiene menos que los municipios de su tipo, pero no tanto como para decir que falta." },
  CUBIERTO: { label: "CUBIERTO", help: "Tiene lo mismo o más que los municipios de su tipo." },
  SIN_DATOS: { label: "SIN DATOS", help: "No tenemos este dato para esta zona. No quiere decir que no haya." },
};

/** fila.zona_pequena: next to the status when the API sends `reliable: false` (never FALTA, D-213). */
export const SMALL_ZONE = {
  label: "Zona pequeña para comparar",
  help: "Aquí vive tan poca gente que no podemos saber con seguridad si falta. Por eso no la marcamos como FALTA.",
};

export function isSmallZone({ reliable }: { reliable?: boolean }): boolean {
  return reliable === false;
}

/**
 * A municipio too small alone, compared together with its nearest neighbours of the same type
 * (gap-0.3, D-217): its status is the group's. Copy of pitch/textos_web.md (grupo.*).
 */
export const GROUP = {
  label: "Junto con sus vecinos",
  help: "Comparado con municipios parecidos de la zona: es demasiado pequeño para compararlo solo, así que lo juntamos con sus vecinos más cercanos del mismo tipo.",
};

export function inGroup(zone: { comparison_group?: ComparisonGroup | null }): ComparisonGroup | null {
  const group = zone.comparison_group ?? null;
  return group && group.names.length >= 2 ? group : null;
}

function listNames(names: readonly string[]): string {
  if (names.length <= 1) return names[0] ?? "";
  return `${names.slice(0, -1).join(", ")} y ${names[names.length - 1]}`;
}

/**
 * The row's group in plain words: who it is compared with and how much they have together
 * (the API's `explanation` says the same: «junto con N municipios vecinos …, tiene el N % de lo esperado»).
 */
export function groupText(zoneName: string, group: ComparisonGroup): string {
  const others = group.names.slice(1);
  // Python's round() goes to the even number on an exact half; a float ratio is never one in practice
  const share = Math.round(100 * group.ratio_to_reference);
  const who = others.length === 1 ? "su vecino" : `sus ${others.length} vecinos`;
  return (
    `Comparado con municipios parecidos de la zona. ${zoneName} es demasiado pequeño para compararlo solo en este servicio, ` +
    `así que lo juntamos con ${who} más ${others.length === 1 ? "cercano" : "cercanos"} del mismo tipo: ${listNames(others)}. ` +
    `Juntos tienen el ${formatNumber(share, 0)} % de lo que tienen de media los municipios de su tipo, y de ahí sale el estado.`
  );
}

/** Row names when the API does not send one (fila.*): the rows it has not computed yet. */
export const ROW_NAME: Record<GapRowKey, string> = {
  escuela_infantil: "Escuelas infantiles",
  colegio: "Colegios",
  centro_salud: "Centros de salud",
  mayores: "Centros de mayores",
  farmacia: "Farmacias",
  vivienda: "Vivienda para familias",
};

/**
 * What each row measures (gap-0.3, D-217): what people have within 15 min on foot, shared among
 * everyone who has it that close. Copy of pitch/textos_web.md (fila.mide.*).
 */
export const ROW_MEASURE: Record<GapRowKey, string> = {
  escuela_infantil: "Escuelas infantiles a 15 min andando por cada 1.000 niños de 0 a 4 años, repartidas entre todos los que las tienen cerca",
  colegio: "Aulas de primaria, públicas y concertadas, a 15 min andando por cada 1.000 niños de 5 a 14 años, repartidas entre todos los que las tienen cerca",
  centro_salud: "Centros de salud del SERMAS a 15 min andando por cada 10.000 habitantes, repartidos entre todos los que los tienen cerca",
  mayores: "Plazas en hogares, clubes y centros de día a 15 min andando por cada 100 personas de 65 años o más, repartidas entre todos los que las tienen cerca",
  farmacia: "Farmacias a 15 min andando por cada 10.000 habitantes, repartidas entre todos los que las tienen cerca",
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

type Classified = { status: GapStatus; reliable?: boolean };

/** What is missing first, a small zone after a comparable one; otherwise the API order. */
export function sortRows<T extends Classified>(rows: readonly T[]): T[] {
  const rank = (r: T) => STATUS_ORDER[r.status] * 2 + (isSmallZone(r) ? 1 : 0);
  return [...rows].sort((a, b) => rank(a) - rank(b));
}

/** The zone card shows three rows: what is missing first. */
export function topRows<T extends Classified>(rows: readonly T[], limit = 3): T[] {
  return sortRows(rows).slice(0, limit);
}

/**
 * A zone that fits everything asked can still be short of something (Mariano, jurado simulado):
 * «Encaja con lo que pides; aun así, en la zona van justos de: escuelas infantiles, colegios.»
 * From the rows the card shows, FALTA first; null when none is FALTA or JUSTO. Draft text until
 * line D writes it in textos_web.md.
 */
export function fitsButShortText(rows: readonly { label: string; status: GapStatus }[]): string | null {
  const names = (status: GapStatus) => rows.filter((r) => r.status === status).map((r) => r.label.charAt(0).toLowerCase() + r.label.slice(1));
  const [missing, tight] = [names("FALTA"), names("JUSTO")];
  if (!missing.length && !tight.length) return null;
  const parts = [missing.length ? `faltan: ${missing.join(", ")}` : null, tight.length ? `van justos de: ${tight.join(", ")}` : null];
  return `Encaja con lo que pides; aun así, en la zona ${parts.filter(Boolean).join("; y ")}.`;
}

/**
 * Value, reference (zones of the same type) and the whole region, with the decimals of the API
 * `explanation` (hi_domain.gaps): set by the value and its reference.
 */
export function gapFigures(
  value: number | null,
  reference: number | null,
  regional: number | null = null,
): { value: string | null; reference: string | null; regional: string | null } {
  const decimals = Math.max(Math.abs(value ?? 0), Math.abs(reference ?? 0)) < 1 ? 2 : 1;
  const format = (n: number | null) => (n === null ? null : formatNumber(n, decimals));
  return { value: format(value), reference: format(reference), regional: format(regional) };
}

const WALKING_PREFIX = "min_a_pie_";
const WALKING_CAP_MIN = 60;

const HOSPITAL = `${WALKING_PREFIX}hospital`;

/**
 * The walking minutes to the row's own service among its extra indicators (CORE-005, median of
 * the zone's streets): `min_a_pie_<row>`, or the first walking extra that is not the hospital.
 */
export function walking(extras: readonly IndicatorValue[] | undefined, row?: GapRowKey): IndicatorValue | undefined {
  const own = row ? extras?.find((e) => e.feature_id === `${WALKING_PREFIX}${row}`) : undefined;
  return own ?? extras?.find((e) => e.feature_id.startsWith(WALKING_PREFIX) && e.feature_id !== HOSPITAL);
}

/** Walking minutes to the nearest general hospital, an extra of the health row (D-217). */
export function hospitalWalking(extras: readonly IndicatorValue[] | undefined): IndicatorValue | undefined {
  return extras?.find((e) => e.feature_id === HOSPITAL);
}

/**
 * The hospital extra in plain words, declared as a proxy (D-217: no open source says which hospital
 * has a 24 h emergency department), and it does not count for the row's status (D-217 §5).
 * Copy of pitch/textos_web.md (falta.fila.a_pie.hospital, hospital.nota).
 */
export const HOSPITAL_WALK = {
  to: "el hospital general más cercano",
  note: "Es una pista de dónde pueden quedar las urgencias, no un dato de urgencias: ninguna fuente abierta dice qué hospitales las tienen abiertas las 24 horas. Andando, no en coche ni en ambulancia, y no cuenta para el estado de la fila.",
};

/** a_pie.min */
export function walkingText({ value }: Pick<IndicatorValue, "value">): string {
  if (value === null) return "Sin datos";
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
