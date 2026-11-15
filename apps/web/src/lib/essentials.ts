/**
 * What a zone card says first (pure, unit tested): the second delivery of the UX mobile audit
 * (prompts/UX_AUDITORIA_MOVIL.md §7, option 2), as Mariano decided it. Three things, from what the
 * API already sends and without changing its contract: what the zone costs (`zonePrice` of
 * lib/fit.ts), what the person asked for with its minutes (`askedLines`) and what it lacks that
 * matters to the home (`householdGaps`). The rest (the %, the place in the list, the ties, every
 * fact with its confidence, the whole «Qué falta») stays behind «Ver más».
 */
import type { ConstraintCheck, Fact, FactKind, FactTopic, NeedKey, PriorityKey, RankedZone, ScenarioState } from "@/contracts/search_response";
import type { ComparisonGroup, GapRowKey, GapStatus } from "@/contracts/zone_gap_list_response";

import { voice, WALK_MINUTES_FEATURE_PREFIX } from "./fit";
import { householdRows, NEAR_BUT_SHORT, notComparable, ROW_IN_LIST, ROW_NAME, walkMinutesText } from "./gaps";

/** «Me importa» measured by walking to a service (PRIORITY_NEED of hi_domain/fit.py). */
const PRIORITY_NEED: Partial<Record<PriorityKey, NeedKey>> = { transporte: "transporte", salud: "centro_salud", colegios: "colegio" };

/**
 * The services the API adds as context when the person asked for fewer than three things
 * (CONTEXT_NEEDS of hi_domain/fit.py): nobody asked for them, so they wait in «Ver más».
 */
const CONTEXT_NEEDS: readonly NeedKey[] = ["transporte", "centro_salud", "colegio", "farmacia"];

/**
 * The tail of a fact about the % (D-243's limits, hi_domain/fit.py: «No llegas a Getafe a las 9:00
 * en transporte público: el % se queda en la mitad», «Más de 1 h de trayecto hasta Getafe: como
 * mucho 74 %», «Faltan colegios: como mucho 89 %»). The essentials keep the sentence and drop
 * only that tail: the % is in «Ver más» (review R-04 of PR #81).
 */
const ABOUT_PCT = /:\s*(el % se queda en la mitad|como mucho \d+\s*%)\s*$/;

/** shortage_fact of hi_domain/fit.py: «Faltan colegios y farmacias en Barajas: como mucho 89 %». */
const SHORTAGE = /^Faltan /;

/** The rows of «Qué falta» of the services the person marks (NEED_ROW of hi_domain/fit.py). */
const NEED_ROW: Partial<Record<NeedKey, GapRowKey>> = {
  escuela_infantil: "escuela_infantil",
  colegio: "colegio",
  centro_salud: "centro_salud",
  farmacia: "farmacia",
  mayores: "mayores",
};

/** «Colegio con primaria a 10 min andando como mucho» -> «Colegio con primaria» (the API's label of `near:*`). */
const NEAR_LABEL = /^(.+) a \d+ min andando como mucho$/;

/** One line of what the person asked for: a fact of the API, or a condition it met without one. */
export interface AskedLine {
  kind: FactKind;
  topic: FactTopic;
  text: string;
  /** A shortage the API caps the % for («Faltan colegios»): the rows it names, said again by the home's gaps once they load */
  rows?: GapRowKey[];
}

type Asked = Pick<ScenarioState, "priorities" | "nearby" | "anchors">;

function askedNeeds(scenario: Asked): Set<string> {
  const fromPriorities = (scenario.priorities ?? []).flatMap((p) => PRIORITY_NEED[p] ?? []);
  return new Set<string>([...fromPriorities, ...(scenario.nearby ?? []).map((n) => n.need)]);
}

/** A walk to a service nobody asked for, which the API adds as context. */
function isContext(fact: Pick<Fact, "indicator">, asked: Set<string>): boolean {
  const id = fact.indicator?.feature_id ?? "";
  if (!id.startsWith(WALK_MINUTES_FEATURE_PREFIX)) return false;
  const need = id.slice(WALK_MINUTES_FEATURE_PREFIX.length) as NeedKey;
  return CONTEXT_NEEDS.includes(need) && !asked.has(need);
}

/** Leisure of «Lo quiero a un paseo» (D-236): the API says it in a single fact about «Ocio». */
const LEISURE: readonly string[] = ["bares", "restaurantes", "gimnasios", "cultura"];

type Ranked = Pick<RankedZone, "facts" | "constraints">;

/** A service of «Lo quiero a un paseo» the zone meets, said with its minutes when no fact says it. */
function nearLine(check: ConstraintCheck, ranked: Ranked): AskedLine | null {
  const need = check.constraint_id.slice("near:".length);
  const said = LEISURE.includes(need)
    ? ranked.facts.some((f) => f.topic === "ocio")
    : ranked.facts.some((f) => f.indicator?.feature_id === `${WALK_MINUTES_FEATURE_PREFIX}${need}`);
  if (said) return null;
  const service = NEAR_LABEL.exec(check.label)?.[1];
  // Without its minutes or a label of the usual form, the condition met as the API names it
  const text = service && typeof check.value === "number" ? `${service} ${walkMinutesText(check.value)}` : check.label;
  return { kind: "strength", topic: "otro", text };
}

/** A trip with a limit the zone meets, said with its minutes when no fact says it. */
function tripLine(check: ConstraintCheck, ranked: Ranked, scenario: Asked): AskedLine | null {
  const place = (scenario.anchors ?? [])[Number(check.constraint_id.slice("commute:".length))];
  const said = place !== undefined && ranked.facts.some((f) => f.topic === "trayecto" && f.text.includes(`hasta ${place.label}`));
  if (!place || said || typeof check.value !== "number") return null;
  return { kind: "strength", topic: "trayecto", text: `${Math.round(check.value)} min en transporte público hasta ${place.label}` };
}

/** A fact as the essentials say it: without the tail about the %, and with the rows of a shortage. */
function factLine({ kind, topic, text }: Pick<Fact, "kind" | "topic" | "text">): AskedLine {
  const said = text.replace(ABOUT_PCT, "");
  if (!SHORTAGE.test(said)) return { kind, topic, text: said };
  const rows = (Object.keys(ROW_IN_LIST) as GapRowKey[]).filter((row) => said.includes(ROW_IN_LIST[row]));
  return { kind, topic, text: said, rows };
}

/**
 * What the person asked for, with its minutes: the API's facts in their order (most important
 * first) without the cost (said apart) and the walks it adds as context, those about the % without
 * their tail; then the walks of «Lo quiero a un paseo» and the trips with a limit that the zone
 * meets and no fact says (the API keeps at most five facts). Nothing for a zone the search did not rank.
 */
export function askedLines(ranked: Ranked | null, scenario: Asked): AskedLine[] {
  if (!ranked) return [];
  const asked = askedNeeds(scenario);
  const facts = ranked.facts.filter((f) => f.topic !== "coste" && !isContext(f, asked));
  const met = ranked.constraints.filter((c) => c.status === "PASS");
  const nears = met.filter((c) => c.constraint_id.startsWith("near:")).map((c) => nearLine(c, ranked));
  const trips = met.filter((c) => c.constraint_id.startsWith("commute:")).map((c) => tripLine(c, ranked, scenario));
  return [...facts.map(factLine), ...[...nears, ...trips].filter((line) => line !== null)];
}

/**
 * The rows of «Qué falta» of what the person marks in «¿Qué quieres tener cerca?» or «Lo quiero a
 * un paseo» (marked_rows of hi_domain/fit.py), in their order: a couple without children who marks
 * «Colegios» cares about the colegios (review R-02 of PR #81).
 */
export function markedRows(scenario: Pick<ScenarioState, "priorities" | "nearby">): GapRowKey[] {
  const needs = [...(scenario.priorities ?? []).flatMap((p) => PRIORITY_NEED[p] ?? []), ...(scenario.nearby ?? []).map((n) => n.need)];
  return [...new Set(needs.flatMap((need) => NEED_ROW[need] ?? []))];
}

type Pertinent = Pick<ScenarioState, "household" | "priorities" | "nearby">;

/** The rows that matter to the search: the household's (householdRows, D-244) and then what the person marks. */
export function pertinentRows(scenario: Pertinent): GapRowKey[] {
  return [...new Set([...householdRows(scenario.household), ...markedRows(scenario)])];
}

type GapRowLike = { row: GapRowKey; status: GapStatus; reliable?: boolean; comparison_group?: ComparisonGroup | null };

/** One row of «Qué falta» that matters to the home and is short: «Centros de salud: van justos para tanta gente.» */
export interface HouseholdShortfall {
  row: GapRowKey;
  status: "FALTA" | "JUSTO";
  text: string;
}

export interface HouseholdGaps {
  /** The home's rows marked FALTA or JUSTO, what is missing first and then in the home's order */
  short: HouseholdShortfall[];
  /** Some of the home's rows can be compared and has enough (CUBIERTO): only then «No le falta nada…» */
  covered: boolean;
  /** The home's rows nobody can tell («No comparable» or SIN DATOS): «no lo sabemos», never «no falta» */
  unknown: GapRowKey[];
}

const isShort = (status: GapStatus): status is "FALTA" | "JUSTO" => status === "FALTA" || status === "JUSTO";

/**
 * What the zone lacks that matters: the rows of pertinentRows (the household's, D-244, and what the
 * person marks) that «Qué falta» marks FALTA or JUSTO, in plain words (zona.esencial.falta).
 * `place` is the district when the card is a barrio's: its rows are the whole district's.
 */
export function householdGaps(rows: readonly GapRowLike[], scenario: Pertinent, place: string | null = null): HouseholdGaps {
  const own = pertinentRows(scenario).flatMap((key) => rows.filter((r) => r.row === key));
  const where = place ? ` en ${place}` : "";
  const short = own
    .filter((r) => isShort(r.status) && !notComparable(r))
    // A stable sort: FALTA before JUSTO, each in the home's order
    .sort((a, b) => Number(a.status === "JUSTO") - Number(b.status === "JUSTO"))
    .map((r) => {
      const status = r.status as "FALTA" | "JUSTO";
      const words = NEAR_BUT_SHORT[r.row]?.[status] ?? (status === "FALTA" ? "hay pocos" : "van justos");
      return { row: r.row, status, text: `${ROW_NAME[r.row]}${where}: ${words}.` };
    });
  const covered = own.some((r) => r.status === "CUBIERTO" && !notComparable(r));
  const unknown = own.filter((r) => r.status === "SIN_DATOS" || notComparable(r)).map((r) => r.row);
  return { short, covered, unknown };
}

/**
 * zona.esencial.nada: none of the rows that matter is short, some has enough (`covered`) and none
 * is unknown (review R-01 of PR #81). `many`: a home of more than one (speaksToMany). In a barrio,
 * the rows are its district's: «En Barajas no falta nada de lo que buscáis.»
 */
export function nothingMissingText(many: boolean, place: string | null = null): string {
  const { buscas } = voice(many);
  return place ? `En ${place} no falta nada de lo que ${buscas}.` : `No le falta nada de lo que ${buscas}.`;
}

/** zona.esencial.comparable: none short, some has enough, and some cannot be told: no green tick. */
export function comparableFineText(place: string | null = null): string {
  return place ? `En ${place}, de lo que podemos comparar, no falta nada.` : "De lo que podemos comparar, no le falta nada.";
}

/** «a», «a o b», «a, b o c». */
function joinOr(names: readonly string[]): string {
  return names.length <= 1 ? (names[0] ?? "") : `${names.slice(0, -1).join(", ")} o ${names.at(-1)}`;
}

/**
 * zona.esencial.no_sabemos (decided by Mariano: it stays): the rows that matter and cannot be told
 * («No comparable» or SIN DATOS), so «no falta» never stands for «no lo sabemos». Null with none.
 */
export function unknownRowsText(rows: readonly GapRowKey[], place: string | null = null): string | null {
  if (!rows.length) return null;
  const names = joinOr(rows.map((r) => ROW_IN_LIST[r]));
  return place ? `No sabemos si en ${place} faltan ${names}.` : `No sabemos si le faltan ${names}.`;
}

/**
 * Where the zone is, beside its band in the card («Madrid · Muy buena opción», zona.esencial.lugar):
 * the city of a district or a barrio; nothing for a municipio, whose name already is its place.
 */
export function cityOf(zone: { level: string; municipio_name?: string | null }): string | null {
  return zone.level === "municipio" ? null : (zone.municipio_name ?? "Madrid");
}

/**
 * A row of the list says where its zone is only when it is needed to tell two rows apart
 * (resultados.fila.lugar): two rows in view with the same name. The list no longer says «Distrito de
 * Madrid» on every row (second delivery).
 */
export function rowPlace(zone: { level: string; name: string; municipio_name?: string | null }, shownNames: readonly string[]): string | null {
  const twice = shownNames.filter((name) => name === zone.name).length > 1;
  return twice ? cityOf(zone) : null;
}
