/**
 * «Qué falta» in plain words (pure, unit tested): statuses, rows, figures and walking minutes of
 * GET /api/v1/gaps, with the copy of pitch/textos_web.md (estado.*, fila.*, falta.*).
 */
import type { ComparisonGroup, GapRowKey, GapStatus, IndicatorValue, NullReason } from "@/contracts/zone_gap_list_response";
import { formatNumber } from "@/lib/format";
import type { ZoneLevel } from "@/lib/map/zones";

/**
 * estado.* (gap-0.2, D-213: each zone against the other municipios of its type). `short` is the
 * zone card's line under its rows (estado.*.corto): the card had the meaning only in a tooltip,
 * which a phone never shows (UX mobile audit, A5).
 */
export const GAP_STATUS: Record<GapStatus, { label: string; help: string; short: string }> = {
  FALTA: {
    label: "FALTA",
    help: "Tiene claramente menos que los municipios de su tipo, y no es por el tamaño de la zona.",
    short: "hay claramente menos que en zonas parecidas.",
  },
  JUSTO: {
    label: "JUSTO",
    help: "Tiene menos que los municipios de su tipo, pero no tanto como para decir que falta.",
    short: "hay algo menos que en zonas parecidas.",
  },
  CUBIERTO: { label: "CUBIERTO", help: "Tiene lo mismo o más que los municipios de su tipo.", short: "hay lo mismo o más que en zonas parecidas." },
  SIN_DATOS: {
    label: "SIN DATOS",
    help: "No tenemos este dato para esta zona. No quiere decir que no haya.",
    short: "no tenemos el dato; no quiere decir que no haya.",
  },
};

/**
 * fila.zona_pequena: a row with `reliable: false` and no group of neighbours shows «No comparable»
 * instead of its status (D-230). What it means (D-213, `min_expected` of hi_domain/gaps.py): for
 * the people who live there, the zone would have fewer than 4 centres (3,69 expected at 95 %; the
 * test counts centre-equivalents, also for the classrooms and the places, hi_features/fca.py), and
 * with numbers that small not even none at all could be told from chance. It is not that few people
 * live there: Barajas, with some 50.000, has too few health centres to compare. In the housing row,
 * whose denominator counts households, few households of 4 or more is the reason. `help` is the
 * legend's, for every row; notComparableText says it of one row.
 */
export const SMALL_ZONE = {
  label: "No comparable",
  help: "Para la gente que vive aquí le corresponden muy pocos centros (menos de 4), o en la vivienda viven muy pocos hogares de 4 o más personas, y con números tan pequeños no se puede saber si falta, ni siquiera junto con sus vecinos. Por eso no la comparamos.",
};

/**
 * Why one row is «No comparable», in its own unit (review R-07 of PR #81): the same words as the
 * API's explanation (not_comparable_text of hi_domain/gap_impact.py), without its figures.
 */
export function notComparableText(row: GapRowKey): string {
  if (row === "vivienda") return "aquí viven muy pocos hogares de 4 o más personas para saber si falta.";
  return `para la gente que vive aquí le corresponden menos de 4 ${ROW_IN_LIST[row]} y, con números tan pequeños, no se puede saber si faltan.`;
}

/**
 * The reason of a «No comparable» row of «Qué falta»: the API's explanation as it is, which says
 * the row's real reason and its figures since D-245 (the web cut its first sentence when it said
 * «aquí viven muy pocas personas (50.375)» of Barajas; API and web are deployed together). Any other
 * explanation: SMALL_ZONE.help.
 */
export function notComparableReason(explanation: string): string {
  return explanation.startsWith("No comparable:") ? explanation : SMALL_ZONE.help;
}

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
  short: "es un pueblo pequeño: lo comparamos junto con los de al lado.",
};

export function inGroup(zone: { comparison_group?: ComparisonGroup | null }): ComparisonGroup | null {
  const group = zone.comparison_group ?? null;
  return group && group.names.length >= 2 ? group : null;
}

/** «a», «a y b», «a, b y c» (fila.lista.*). */
export function listNames(names: readonly string[]): string {
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
    `Juntos tienen el ${formatNumber(share, 0)}\u00a0% de lo que tienen de media los municipios de su tipo, y de ahí sale el estado.`
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

/** Row names inside a sentence (fila.lista.*): «Aquí falta: escuelas infantiles». */
export const ROW_IN_LIST: Record<GapRowKey, string> = {
  escuela_infantil: "escuelas infantiles",
  colegio: "colegios",
  centro_salud: "centros de salud",
  mayores: "centros de mayores",
  farmacia: "farmacias",
  vivienda: "viviendas grandes para familias",
};

/**
 * falta.fila.comparacion (D-229 §6): n = round(100 × ratio to the zones of its type), or the
 * group's ratio when the zone is compared together with its neighbours. It can pass 100.
 */
export function comparisonText(ratio: number, grouped: boolean): string {
  const n = formatNumber(Math.round(100 * ratio), 0);
  return `${grouped ? "Junto con sus vecinos, hay" : "Aquí hay"} ${n} por cada 100 que hay en municipios parecidos.`;
}

/**
 * The comparison of one row of /gaps, or null when it has no ratio (SIN DATOS) or the zone is too
 * small to compare even with its neighbours: that ratio is noise, the figure stays behind «Ver la cifra».
 */
export function rowComparison(row: {
  status: GapStatus;
  reliable?: boolean;
  ratio_to_reference?: number | null;
  comparison_group?: ComparisonGroup | null;
}): string | null {
  if (row.status === "SIN_DATOS" || notComparable(row)) return null;
  const group = inGroup(row);
  const ratio = group ? group.ratio_to_reference : row.ratio_to_reference;
  return ratio == null ? null : comparisonText(ratio, group !== null);
}

/** «Afecta a 9.433 niños de 0 a 4 años.»: the people a FALTA row leaves short (D-229, `people` of /gaps). */
export function peopleAffectedText(row: { status: GapStatus; people?: { count: number; label: string } | null }): string | null {
  if (row.status !== "FALTA" || !row.people) return null;
  return `Afecta a ${formatNumber(row.people.count, 0)} ${row.people.label}.`;
}

/**
 * What each row measures (gap-0.3, D-217): what people have within 15 min on foot, shared among
 * everyone who has it that close. Copy of pitch/textos_web.md (fila.mide.*).
 */
export const ROW_MEASURE: Record<GapRowKey, string> = {
  escuela_infantil: "Escuelas infantiles a 15 min andando por cada 1.000 niños de 0 a 4 años, repartidas entre todos los que las tienen cerca",
  colegio: "Aulas de primaria, públicas y concertadas, a 15 min andando por cada 1.000 niños de 5 a 14 años, repartidas entre todos los que las tienen cerca",
  centro_salud: "Centros de salud de la red pública de salud de la Comunidad (SERMAS) a 15 min andando por cada 10.000 habitantes, repartidos entre todos los que los tienen cerca",
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

type Classified = { status: GapStatus; reliable?: boolean; comparison_group?: ComparisonGroup | null };

/** Where a row goes by its status: «No comparable» after CUBIERTO and before SIN DATOS, as the small zones went before (D-230). */
function statusRank(r: Classified): number {
  return notComparable(r) ? 5 : STATUS_ORDER[r.status] * 2;
}

/** What is missing first, a small zone after a comparable one; otherwise the API order. */
export function sortRows<T extends Classified>(rows: readonly T[]): T[] {
  return [...rows].sort((a, b) => statusRank(a) - statusRank(b));
}

/** Who lives in the home, as far as «Qué falta» cares (ScenarioState.household). */
export interface HouseholdLike {
  minors?: number;
  minor_ages?: readonly number[];
  seniors_in_care?: number;
  seniors?: boolean;
}

/** Up to this age a child goes to an escuela infantil (INFANT_MAX_AGE of hi_domain/search.py). */
const INFANT_MAX_AGE = 2;
/** The rows about children: they never stand in for another row in a home without children. */
const CHILD_ROWS: readonly GapRowKey[] = ["escuela_infantil", "colegio"];

/**
 * The rows of «Qué falta» that matter to this household, in the card's order (D-244 and review of
 * PR #79: «lo que le falta que le afecte»): the same rule as highlight_rows of hi_domain/search.py,
 * which feeds `gap_highlights`, without the housing row. Escuela infantil with a child of 0 to 2
 * (or ages not given), colegio with any child, the health centre and the pharmacy always, and the
 * centres for older people with «Somos mayores» or someone older looked after.
 */
export function householdRows(household: HouseholdLike | null | undefined): GapRowKey[] {
  const minors = household?.minors ?? 0;
  const ages = household?.minor_ages ?? [];
  const rows: GapRowKey[] = [];
  if (minors > 0 && (ages.length === 0 || Math.min(...ages) <= INFANT_MAX_AGE)) rows.push("escuela_infantil");
  if (minors > 0) rows.push("colegio");
  rows.push("centro_salud", "farmacia");
  if (household?.seniors === true || (household?.seniors_in_care ?? 0) > 0) rows.push("mayores");
  return rows;
}

/**
 * The three rows of the zone card. Without a household, by status (what is missing first, then
 * the API order). With one, what matters to it first (householdRows), whatever its status, a «No
 * comparable» one included: among them, what is short (FALTA, then JUSTO) and then the household's
 * order. Other rows only fill in when fewer than three of the household's have data, by status;
 * those about children never do in a home without children. The household's rows without data go last.
 */
export function topRows<T extends Classified & { row?: GapRowKey }>(
  rows: readonly T[],
  limit = 3,
  household?: HouseholdLike | null,
  marked: readonly GapRowKey[] = [],
): T[] {
  if (!household) return sortRows(rows).slice(0, limit);
  // The household's rows and then what the person marks (review R-02 of PR #81), as the essentials
  const mine = [...new Set([...householdRows(household), ...marked])];
  const children = (household.minors ?? 0) > 0;
  const ownRank = (r: T) => (r.row === undefined ? -1 : mine.indexOf(r.row));
  const fills = (r: T) => children || r.row === undefined || !CHILD_ROWS.includes(r.row);
  const known = (r: T) => r.status !== "SIN_DATOS";
  // 0: the household's with data · 1: others with data · 2: the household's without · 3: others without
  const group = (r: T) => (ownRank(r) >= 0 ? (known(r) ? 0 : 2) : known(r) ? 1 : 3);
  const short = (r: T) => (notComparable(r) ? 2 : r.status === "FALTA" ? 0 : r.status === "JUSTO" ? 1 : 2);
  const order = (a: T, b: T) => {
    const g = group(a) - group(b);
    if (g !== 0) return g;
    if (group(a) === 0) return short(a) - short(b) || ownRank(a) - ownRank(b);
    if (group(a) === 2) return ownRank(a) - ownRank(b);
    return statusRank(a) - statusRank(b);
  };
  // A stable sort: other rows of the same status keep the API order
  return rows.filter((r) => ownRank(r) >= 0 || fills(r)).sort(order).slice(0, limit);
}

type SummaryRow = Classified & { row: GapRowKey };

/**
 * Too small to compare even with its neighbours (D-230): shown as «No comparable», never as JUSTO
 * or CUBIERTO, and it never counts as short or tight (falta.resumen.pequena). A presentation rule:
 * GapStatus keeps its values.
 */
export function notComparable(row: { status: GapStatus; reliable?: boolean; comparison_group?: ComparisonGroup | null }): boolean {
  return row.status !== "SIN_DATOS" && isSmallZone(row) && inGroup(row) === null;
}

const cannotCompare = notComparable;

/** Comparable rows of each status, and the rest, as names inside a sentence (fila.lista.*). */
function rowsByStatus(rows: readonly SummaryRow[]) {
  const names = (pick: (r: SummaryRow) => boolean) => rows.filter(pick).map((r) => ROW_IN_LIST[r.row]);
  const comparable = (status: GapStatus) => (r: SummaryRow) => r.status === status && !cannotCompare(r);
  return {
    falta: names(comparable("FALTA")),
    justo: names(comparable("JUSTO")),
    cubierto: names(comparable("CUBIERTO")),
    small: names((r) => r.status !== "SIN_DATOS" && cannotCompare(r)),
    none: names((r) => r.status === "SIN_DATOS"),
  };
}

/**
 * The first lines of «Qué falta» (falta.resumen.*): the verdict in bold («Aquí falta: escuelas
 * infantiles.»; null when no row can be compared), then what is tight, too small to compare or
 * without data.
 */
export function gapSummary(rows: readonly SummaryRow[]): { lead: string | null; rest: string[] } {
  const { falta, justo, cubierto, small, none } = rowsByStatus(rows);
  let lead: string | null = null;
  if (falta.length) lead = `Aquí falta: ${listNames(falta)}.`;
  else if (justo.length) lead = "Aquí no falta nada claro.";
  else if (cubierto.length) lead = "Aquí no falta nada, comparado con municipios parecidos.";
  const rest: string[] = [];
  if (justo.length) rest.push(`Van justos: ${listNames(justo)}.`);
  if (small.length) rest.push(`Zona muy pequeña para comparar: ${listNames(small)}.`);
  if (none.length) rest.push(`Sin datos: ${listNames(none)}.`);
  return { lead, rest };
}

/**
 * A zone that fits everything asked can still be short of something (encaje.aviso_*): from every
 * row of its «Qué falta», not only the three the card shows. Rows too small to compare do not
 * count; null when no row is FALTA or JUSTO.
 */
export function fitsButShortText(rows: readonly SummaryRow[]): string | null {
  const { falta, justo } = rowsByStatus(rows);
  const parts = [falta.length ? `faltan ${listNames(falta)}` : null, justo.length ? `van justos de ${listNames(justo)}` : null].filter(Boolean);
  if (!parts.length) return null;
  return `Tiene lo que pides. Aun así, comparado con municipios parecidos, aquí ${parts.join(" y ")}.`;
}

/**
 * zona.falta.ayuda: «Qué falta» measures something else than «Me importa» and «Lo quiero a un paseo»
 * (minutes on foot): whether what is within 15 min on foot is enough for everyone who shares it,
 * against similar zones (2SFCA, D-217). In plain words since the UX mobile audit (§4 n.º 31).
 */
export const GAPS_HELP = "Un servicio puede estar cerca y aun así ir lleno: aquí miramos si hay bastante para toda la gente de la zona.";

/**
 * zona.cerca_pocas: what each row counts, said as «too few for so many» (FALTA) or «tight» (JUSTO).
 * The words follow fila.mide.*: schools and pharmacies count one each, colegios count classrooms,
 * mayores count places (nobody publishes the places of an escuela infantil, D-217).
 */
export const NEAR_BUT_SHORT: Partial<Record<GapRowKey, { service: string; FALTA: string; JUSTO: string }>> = {
  escuela_infantil: { service: "Escuela infantil", FALTA: "hay pocas para tantos niños", JUSTO: "van justas para tantos niños" },
  colegio: { service: "Colegio con primaria", FALTA: "hay pocas aulas para tantos niños", JUSTO: "las aulas van justas para tantos niños" },
  centro_salud: { service: "Centro de salud", FALTA: "hay pocos para tanta gente", JUSTO: "van justos para tanta gente" },
  mayores: { service: "Centro de mayores", FALTA: "hay pocas plazas para tantas personas mayores", JUSTO: "las plazas van justas para tantas personas mayores" },
  farmacia: { service: "Farmacia", FALTA: "hay pocas para tanta gente", JUSTO: "van justas para tanta gente" },
};

/** «a unos 6 min andando», «a 1 min andando» or «a menos de 1 min andando». */
export function walkMinutesText(minutes: number): string {
  const n = Math.round(minutes);
  if (n < 1) return "a menos de 1 min andando";
  return n === 1 ? "a 1 min andando" : `a unos ${formatNumber(n, 0)} min andando`;
}

type NearRow = Classified & { row: GapRowKey };

/** The walk each row of services measures (fila.mide.*, 2SFCA): what is within 15 min on foot. */
export const ROW_WALK_MIN = 15;

/** One line of zona.cerca_pocas and the row of «Qué falta» it explains. */
export interface NearButShort {
  row: GapRowKey;
  text: string;
}

/**
 * zona.cerca_pocas: a service the search found within the row's own walk (`walks`, minutes by row,
 * up to ROW_WALK_MIN) that «Qué falta» marks FALTA or JUSTO, in one line that says both are true:
 * «Escuela infantil a unos 6 min andando, pero hay pocas para tantos niños: por eso sale FALTA.»
 * Further than that, the row does not count it and there is nothing to reconcile.
 * `place` is the district when the card is a barrio's (its rows are the district's). Rows compared
 * together with neighbours or too small to compare are left out: their status is not the zone's own.
 */
export function nearButShort(rows: readonly NearRow[], walks: Partial<Record<GapRowKey, number>>, place: string | null = null): NearButShort[] {
  return sortRows(rows).flatMap((row) => {
    const words = NEAR_BUT_SHORT[row.row];
    const minutes = walks[row.row];
    if (!words || minutes === undefined || minutes > ROW_WALK_MIN || (row.status !== "FALTA" && row.status !== "JUSTO")) return [];
    if (notComparable(row) || inGroup(row)) return [];
    const where = place ? `en ${place} ` : "";
    return [{ row: row.row, text: `${words.service} ${walkMinutesText(minutes)}, pero ${where}${words[row.status]}: por eso sale ${row.status}.` }];
  });
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

/** Who a district is compared with (falta.fila.referencia.distrito): the API leaves Madrid out of its reference. */
export const DISTRICT_REFERENCE = "Municipios urbanos de la Comunidad, sin contar Madrid (como Getafe o Alcalá de Henares)";

export function referenceLabel(apiLabel: string, level: string): string {
  return level === "distrito" ? DISTRICT_REFERENCE : apiLabel;
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
  label: "Hospital más cercano",
  note: "Es una pista de dónde pueden quedar las urgencias, no un dato de urgencias: ninguna fuente abierta dice qué hospitales las tienen abiertas las 24 horas. Andando, no en coche ni en ambulancia, y no cuenta para el estado de la fila.",
};

/** a_pie.min */
export function walkingText({ value }: Pick<IndicatorValue, "value">): string {
  if (value === null) return "Sin datos";
  if (value > WALKING_CAP_MIN) return `más de ${WALKING_CAP_MIN} min`;
  if (value < 1) return "menos de 1 min";
  return `${Math.round(value)} min`;
}

const HOSPITAL_KM_FROM_MIN = 30;

/**
 * hospital.distancia: up to 30 min, «a 12 min andando»; further, the distance at 4 km/h, «a unos
 * 3,4 km» (walking 51 minutes to a hospital is not useful, the distance is).
 */
export function hospitalText({ value }: Pick<IndicatorValue, "value">): string {
  if (value === null) return "Sin datos";
  if (value > HOSPITAL_KM_FROM_MIN) return `a unos ${formatNumber((value * 4) / 60, 1)} km`;
  return `a ${walkingText({ value })} andando`;
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
