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

import { WALK_MINUTES_FEATURE_PREFIX } from "./fit";
import { type HouseholdLike, householdRows, NEAR_BUT_SHORT, notComparable, ROW_IN_LIST, ROW_NAME, walkMinutesText } from "./gaps";

/** «Me importa» measured by walking to a service (PRIORITY_NEED of hi_domain/fit.py). */
const PRIORITY_NEED: Partial<Record<PriorityKey, NeedKey>> = { transporte: "transporte", salud: "centro_salud", colegios: "colegio" };

/**
 * The services the API adds as context when the person asked for fewer than three things
 * (CONTEXT_NEEDS of hi_domain/fit.py): nobody asked for them, so they wait in «Ver más».
 */
const CONTEXT_NEEDS: readonly NeedKey[] = ["transporte", "centro_salud", "colegio", "farmacia"];

/**
 * A fact about the % (D-243's limits, hi_domain/fit.py: «… el % se queda en la mitad», «… como
 * mucho 74 %», «Faltan colegios: como mucho 89 %»): the % is in «Ver más».
 */
const ABOUT_PCT = /el % se queda|como mucho \d+\s*%/;

/** «Colegio con primaria a 10 min andando como mucho» -> «Colegio con primaria» (the API's label of `near:*`). */
const NEAR_LABEL = /^(.+) a \d+ min andando como mucho$/;

/** One line of what the person asked for: a fact of the API, or a condition it met without one. */
export interface AskedLine {
  kind: FactKind;
  topic: FactTopic;
  text: string;
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

/**
 * What the person asked for, with its minutes: the API's facts in their order (most important
 * first) without the cost (said apart), those about the % and the walks it adds as context; then
 * the walks of «Lo quiero a un paseo» and the trips with a limit that the zone meets and no fact
 * says (the API keeps at most five facts). Nothing for a zone the search did not rank.
 */
export function askedLines(ranked: Ranked | null, scenario: Asked): AskedLine[] {
  if (!ranked) return [];
  const asked = askedNeeds(scenario);
  const facts = ranked.facts.filter((f) => f.topic !== "coste" && !ABOUT_PCT.test(f.text) && !isContext(f, asked));
  const met = ranked.constraints.filter((c) => c.status === "PASS");
  const nears = met.filter((c) => c.constraint_id.startsWith("near:")).map((c) => nearLine(c, ranked));
  const trips = met.filter((c) => c.constraint_id.startsWith("commute:")).map((c) => tripLine(c, ranked, scenario));
  return [...facts.map(({ kind, topic, text }) => ({ kind, topic, text })), ...[...nears, ...trips].filter((line) => line !== null)];
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
 * What the zone lacks that matters to the home: the rows of `householdRows` (the rule of the first
 * delivery, D-244) that «Qué falta» marks FALTA or JUSTO, in plain words (zona.esencial.falta).
 * `place` is the district when the card is a barrio's: its rows are the whole district's.
 */
export function householdGaps(rows: readonly GapRowLike[], household: HouseholdLike | null | undefined, place: string | null = null): HouseholdGaps {
  const own = householdRows(household).flatMap((key) => rows.filter((r) => r.row === key));
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
 * zona.esencial.nada: none of the home's rows is short and some has enough (`covered`): never said
 * of rows that are all unknown or missing. `many`: a home of more than one (speaksToMany).
 */
export function nothingMissingText(many: boolean): string {
  return `No le falta nada de lo que ${many ? "buscáis" : "buscas"}.`;
}

/** «a», «a o b», «a, b o c». */
function joinOr(names: readonly string[]): string {
  return names.length <= 1 ? (names[0] ?? "") : `${names.slice(0, -1).join(", ")} o ${names.at(-1)}`;
}

/**
 * zona.esencial.no_sabemos: said under «No le falta nada…» when some of the home's rows cannot be
 * told («No comparable» or SIN DATOS), so «no falta» never stands for «no lo sabemos». Null with none.
 */
export function unknownRowsText(rows: readonly GapRowKey[]): string | null {
  return rows.length ? `No sabemos si le faltan ${joinOr(rows.map((r) => ROW_IN_LIST[r]))}.` : null;
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
