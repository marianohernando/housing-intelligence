/**
 * The search result in plain words (pure, unit tested): POST /api/v1/search (CORE-003, method
 * fit-0.1, D-215). The web never recomputes the fit: it joins the API's figures to the map, the
 * list and the zone card, with the copy of pitch/textos_web.md (zona.*, rc.*, leyenda.*).
 */
import type {
  CostRange,
  Fact,
  RankedZone,
  RealityCheck,
  Relaxation,
  ScenarioState,
  SearchResult,
  SearchScope,
  ZoneMatch,
  ZoneRef,
} from "@/contracts/search_response";
import type { GapRowKey } from "@/contracts/zone_gap_list_response";

import { type ConfidenceText, confidenceText } from "./confidence";
import { formatEuros } from "./format";
import { floorArea } from "./scenario";
import type { ZoneCollection, ZoneGeometry, ZoneProperties } from "./map/zones";

/** How a zone is painted after a search: by its % when it meets everything, otherwise apart. */
export type FitClass = "ENCAJA" | "NO_CUMPLE" | "SIN_DATOS";

/**
 * `match_pct: null` is unknown, never 0 (some condition could not be checked). A zone that fails
 * a condition keeps its % to compare, but it is not one of the zones that fit.
 */
export function fitClass(zone: Pick<ZoneMatch, "match_pct" | "passes_all">): FitClass {
  if (zone.match_pct == null) return "SIN_DATOS";
  return zone.passes_all ? "ENCAJA" : "NO_CUMPLE";
}

/** The map's key for a zone of the API (`zone_key` of lib/map/zones.ts). */
export function zoneKeyOf(zone: Pick<ZoneRef, "level" | "code">): string {
  return `${zone.level}/${zone.code}`;
}

/** Ends of the violet ramp of the map and its legend, in % of fit (lower values take the low end). */
export const FIT_RAMP = { low: 60, high: 100 } as const;

export type FitProperties = ZoneProperties & { fit?: FitClass; fit_pct?: number };
export type FitCollection = GeoJSON.FeatureCollection<ZoneGeometry, FitProperties>;

/** The zones of the map with their class in `fit` and, when known, their % in `fit_pct`. */
export function paintFit(zones: ZoneCollection, allZones: readonly ZoneMatch[]): FitCollection {
  const byKey = new Map(allZones.map((z) => [zoneKeyOf(z.zone), z]));
  return {
    ...zones,
    features: zones.features.map((f) => {
      const match = byKey.get(f.properties.zone_key);
      if (!match) return f;
      const pct = match.match_pct;
      return { ...f, properties: { ...f.properties, fit: fitClass(match), ...(pct == null ? {} : { fit_pct: pct }) } };
    }),
  };
}

export type FitCounts = Record<FitClass, number> & { pending: number };

/** How many zones of the map fall in each class; a zone the search did not carry is `pending`. */
export function countFit(painted: FitCollection): FitCounts {
  const counts: FitCounts = { ENCAJA: 0, NO_CUMPLE: 0, SIN_DATOS: 0, pending: 0 };
  for (const f of painted.features) counts[f.properties.fit ?? "pending"] += 1;
  return counts;
}

/** What the result says about one zone of the map: its match and, when listed, its ranked entry. */
export interface ZoneFit {
  match: ZoneMatch | null;
  ranked: RankedZone | null;
}

export function zoneFit(result: SearchResult, zoneKey: string): ZoneFit {
  const same = (z: { zone: ZoneRef }) => zoneKeyOf(z.zone) === zoneKey;
  return {
    match: result.all_zones.find(same) ?? null,
    ranked: result.results.find(same) ?? result.near_misses?.find(same) ?? null,
  };
}

/** The approximate price of a zone for the household's m² (D-234), in the rows and the zone card. */
export interface ZonePrice {
  /** In a ranking row: «≈ 385.000 €» (zona.precio.compra) or «≈ 1.101 €/mes» (zona.precio.alquiler) */
  short: string;
  /** In the zone card head: «Comprar ≈ 385.000 €» (zona.precio.cabecera.compra) or «Alquiler ≈ 1.101 €/mes» */
  long: string;
  /** The m² the API priced (zona.precio.m2): «por 68 m²», under the row's figure and after the card's; null when unknown */
  area: string | null;
  /** Read aloud instead of «≈»: «Comprar: unos 385.000 € por 68 m²» (zona.precio.aria.*) */
  aria: string;
  /** The card's words for a figure that is not a reliable one («Dato aproximado» for the D-234 estimate), else null */
  confidence: ConfidenceText | null;
  /** D-242: where half the leases fall and who says so, in the zone card head (zona.precio.rango); null without it */
  range: PriceRange | null;
  /** A rent: the 2024 leases it comes from, by the card's price (zona.precio.aviso_2024); null buying */
  notice: string | null;
}

/**
 * zona.precio.aviso_2024 and resultados.aviso_2024 (F5 of fit-0.9): every rent is the leases of
 * 2024, and today's listings tend to ask more (16-33 % more in the formula's bench). Said by the
 * card's price and once over the results when renting; never buying.
 */
export const RENT_2024_NOTICE = "Precio de contratos firmados en 2024. Los anuncios de hoy suelen pedir más.";

/** The same warning as the API's rent fact says it: the card says it once, by the price. */
const RENT_FACT_NOTICE = /;\s*un anuncio de hoy puede pedir más/;

/**
 * The text of a fact as the card shows it: renting, the rent fact no longer repeats in other
 * words what RENT_2024_NOTICE already says by the price («…, contratos firmados en 2024)»).
 */
export function factText(fact: Pick<Fact, "topic" | "text">, buying: boolean): string {
  return !buying && fact.topic === "coste" ? fact.text.replace(RENT_FACT_NOTICE, "") : fact.text;
}

/** resultados.aviso_2024: over the results whose prices are rents (renting, or without a budget), with some price shown. */
export function rentNotice(result: Pick<SearchResult, "scenario" | "results" | "near_misses">): string | null {
  if (result.scenario.budget?.kind === "buy") return null;
  const priced = [...result.results, ...(result.near_misses ?? [])].some((z) => z.estimated_cost_eur != null);
  return priced ? RENT_2024_NOTICE : null;
}

/** «La mitad de los contratos, entre 510 y 820 €/mes» and «Ministerio de Vivienda (SERPAVI), 2024» (zona.precio.rango) */
export interface PriceRange {
  text: string;
  source: string;
  /** Read aloud: «La mitad de los contratos están entre 510 y 820 € al mes, según Ministerio de Vivienda (SERPAVI), 2024» */
  aria: string;
}

/** At or above this confidence the figure is «Dato fiable» and goes without a mark (lib/confidence.ts). */
const RELIABLE = 0.8;

/**
 * The price the API gives a zone (`estimated_cost_eur`: the purchase price when buying, else the
 * monthly rent), or null without one: nothing is shown and the general notice says why. `m2` is the
 * area the API priced it for (`floorAreaOf` the result's scenario), said with it.
 */
export function zonePrice(
  zone: Pick<ZoneMatch, "estimated_cost_eur" | "estimated_cost_confidence" | "estimated_cost_range">,
  buying: boolean,
  m2: number | null = null,
): ZonePrice | null {
  const cost = zone.estimated_cost_eur;
  if (cost == null) return null;
  const amount = formatEuros(cost);
  const confidence = zone.estimated_cost_confidence;
  const area = m2 === null ? null : `por ${m2} m²`;
  const aria = buying ? `Comprar: unos ${amount}` : `Alquiler: unos ${amount} al mes`;
  return {
    short: buying ? `≈ ${amount}` : `≈ ${amount}/mes`,
    long: buying ? `Comprar ≈ ${amount}` : `Alquiler ≈ ${amount}/mes`,
    area,
    aria: area ? `${aria} ${area}` : aria,
    confidence: confidence != null && confidence < RELIABLE ? confidenceText(confidence) : null,
    range: buying ? null : priceRange(zone.estimated_cost_range),
    notice: buying ? null : RENT_2024_NOTICE,
  };
}

/** D-242: the quartiles of the Ministry's reference rent for the household's m², as the API gives them. */
export function priceRange(range: CostRange | null | undefined): PriceRange | null {
  if (!range) return null;
  const low = formatEuros(range.low_eur).replace(" €", "");
  const high = formatEuros(range.high_eur);
  return {
    // A no-break space keeps «1.190 €/mes» on one line in a narrow card
    text: `La mitad de los contratos, entre ${low} y ${high.replace(" €", "\u00a0€")}/mes`,
    source: range.source,
    aria: `La mitad de los contratos están entre ${low} y ${high} al mes, según ${range.source}`,
  };
}

/**
 * The m² behind the prices of a result: those the person chose (`min_floor_area_m2`), or the usual
 * for the household the API assumes with null (D-214); null for an answer without its scenario.
 */
export function floorAreaOf(result: { scenario?: Pick<ScenarioState, "household" | "min_floor_area_m2"> }): number | null {
  return result.scenario ? floorArea(result.scenario).m2 : null;
}

/** The price of the zone of the card: from `all_zones` (every zone), else its ranked entry (older API). */
export function zonePriceOf(result: SearchResult, zoneKey: string): ZonePrice | null {
  const { match, ranked } = zoneFit(result, zoneKey);
  const buying = result.scenario.budget?.kind === "buy";
  const withCost = match?.estimated_cost_eur != null ? match : ranked;
  return withCost ? zonePrice(withCost, buying, floorAreaOf(result)) : null;
}

/**
 * Plain-language name of each condition of the search («Colegio con primaria a 10 min andando como
 * mucho»), from POST /search or POST /search/barrios.
 */
export function constraintLabels(result: Pick<SearchResult, "results" | "near_misses">): Map<string, string> {
  const ranked = [...result.results, ...(result.near_misses ?? [])];
  return new Map(ranked.flatMap((z) => z.constraints.map((c) => [c.constraint_id, c.label] as const)));
}

/** Options of «¿Y si cambias algo?» that add zones, in the API order (most zones first). */
export function relaxOptions(rc: RealityCheck): Relaxation[] {
  return rc.relaxations.filter((r) => r.added_zones > 0);
}

/** With this many zones or fewer, «¿Y si cambias algo?» opens unfolded (the brief: «pocas o ninguna»). */
export const FEW_ZONES = 5;

export function fewZones(rc: Pick<RealityCheck, "zones_passing">): boolean {
  return rc.zones_passing <= FEW_ZONES;
}

/**
 * What the zones of a search are called («¿Dónde?», D-238): barrios in Madrid capital, municipios
 * around it, pueblos beyond; «zonas» for the whole region, where they are of every kind.
 */
export type ZoneWord = "zona" | "barrio" | "municipio" | "pueblo";

const WORDS: Record<ZoneWord, { many: string; feminine: boolean }> = {
  zona: { many: "zonas", feminine: true },
  barrio: { many: "barrios", feminine: false },
  municipio: { many: "municipios", feminine: false },
  pueblo: { many: "pueblos", feminine: false },
};

const WORD_OF_SCOPE: Record<SearchScope, ZoneWord> = { all: "zona", madrid: "barrio", alrededores: "municipio", pueblos: "pueblo" };

/** The scope of a result: an answer without one (an API before D-238) is the whole region. */
export function resultScope(result: { scenario: { scope?: SearchScope } }): SearchScope {
  return result.scenario.scope ?? "all";
}

export function zoneWord(result: { scenario: { scope?: SearchScope } }): ZoneWord {
  return WORD_OF_SCOPE[resultScope(result)];
}

export function zonesText(n: number, word: ZoneWord = "zona"): string {
  return n === 1 ? `1 ${word}` : `${n} ${WORDS[word].many}`;
}

/**
 * rc.ninguna, rc.una, rc.varias; after applying an option of «¿Y si cambias algo?» it is no longer
 * the search «tal cual»: «Con este cambio…» (rc.cambio). With the word of its scope: «salen 78 barrios».
 */
export function passingText(n: number, changed = false, word: ZoneWord = "zona"): string {
  const start = changed ? "Con este cambio" : "Con tu búsqueda tal cual";
  if (n === 0) return `${start} no sale ${WORDS[word].feminine ? "ninguna" : "ningún"} ${word}.`;
  return `${start} ${n === 1 ? "sale" : "salen"} ${zonesText(n, word)}.`;
}

/** vacio.sin_resultados, with the word of the scope. */
export function noneText(word: ZoneWord = "zona"): string {
  return `${WORDS[word].feminine ? "Ninguna" : "Ningún"} ${word} cumple todo lo que pides. Mira abajo qué pasa si cambias algo.`;
}

/** resultados.de: how many zones the search compared, and where (D-238). */
const EVALUATED: Record<SearchScope, (n: number) => string> = {
  all: (n) => `De ${n} zonas de la Comunidad de Madrid.`,
  madrid: (n) => `De ${n} barrios de Madrid capital.`,
  alrededores: (n) => `De ${n} municipios de los alrededores de Madrid.`,
  pueblos: (n) => `De ${n} pueblos de la Comunidad de Madrid.`,
};

export function evaluatedText(result: { scenario: { scope?: SearchScope }; reality_check: Pick<RealityCheck, "zones_evaluated"> }): string {
  return EVALUATED[resultScope(result)](result.reality_check.zones_evaluated);
}

/**
 * D-242: the villages get the Ministry's reference rent once its dataset is published (GET
 * /datasets); before the sync the texts keep saying that only the bigger municipios have it, as
 * the leisure chip of D-236 waits for its own dataset.
 */
export const RENT_REFERENCE_DATASET = "mivau_serpavi_alquiler";

export function rentReferenceAvailable(datasets: readonly { dataset_id: string }[] | null | undefined): boolean {
  return datasets?.some((d) => d.dataset_id === RENT_REFERENCE_DATASET) ?? false;
}

/**
 * resultados.pueblos_sin_alquiler (D-238, D-242): renting, why the villages come out «Sin datos»:
 * with the reference rent, so few rented homes that none is published; without it (before the
 * sync), the rent only published for municipios of more than 20.000 people. Null in any other search.
 */
export function rentUnknownText(
  result: { scenario: { scope?: SearchScope; budget?: { kind: string } | null }; reality_check: Pick<RealityCheck, "zones_unknown" | "zones_evaluated"> },
  rentReference: boolean = true,
): string | null {
  const { zones_unknown: n, zones_evaluated: total } = result.reality_check;
  if (resultScope(result) !== "pueblos" || result.scenario.budget?.kind !== "rent" || n === 0) return null;
  const come = n === 1 ? "sale" : "salen";
  const why = rentReference
    ? "tienen tan pocas viviendas alquiladas que no se publica su alquiler"
    : "el alquiler solo se publica en los municipios de más de 20.000 habitantes";
  return `${n} de los ${total} pueblos ${come} «Sin datos», sobre todo porque ${why}: no podemos comprobar tu presupuesto.`;
}

/** A search over Madrid capital ranks its barrios (D-238), not its districts. */
export function byBarrio(result: { scenario: { scope?: SearchScope } } | null): boolean {
  return result !== null && resultScope(result) === "madrid";
}

/** More zones than this with the best % of the ranking and the web says so (resultados.empate, D-239). */
export const MANY_TIED = 10;

/** Zones that meet everything with the same shown % as the first of the ranking. */
export function tiedAtTop(result: Pick<SearchResult, "results" | "all_zones">): number {
  const best = result.results[0]?.match_pct;
  if (best === undefined) return 0;
  return result.all_zones.filter((z) => z.passes_all && z.match_pct === best).length;
}

/**
 * resultados.empate: with many zones tied at the top the order says little (the API breaks the
 * tie by the services at a walk, D-239), so the person is told how to tell them apart; null otherwise.
 */
export function tiedText(result: Pick<SearchResult, "results" | "all_zones" | "scenario">): string | null {
  const n = tiedAtTop(result);
  const word = zoneWord(result);
  return n > MANY_TIED ? `Encajan ${zonesText(n, word)} igual de bien: marca qué te importa o dónde trabajas para afinar el orden.` : null;
}

/** Where «Trabajo en» and «¿Dónde?» are in «Tu búsqueda», for resultados.sin_lugar to take the person there. */
export const FIELD_ID = { work: "busqueda-trabajo", where: "busqueda-donde" } as const;

/**
 * resultados.sin_lugar: searching the whole region with no place to go (no work, family or other),
 * small villages well served on foot can come out first. They do fit, since nothing makes them far
 * (with fit-0.9, Titulcia 2.ª for a couple with a baby), but it surprises: the person is asked for
 * the work place or «Madrid capital». Only then, with zones to show and no crowd at the top
 * (resultados.empate already asks for the work place).
 */
export function asksForPlace(result: Pick<SearchResult, "results" | "all_zones" | "scenario" | "reality_check">): boolean {
  const noPlace = (result.scenario.anchors ?? []).length === 0;
  return noPlace && resultScope(result) === "all" && result.reality_check.zones_passing > 0 && tiedText(result) === null;
}

/** The zones a search to buy could not check for lack of a purchase price (D-234). */
export interface WithoutPrice {
  n: number;
  /** All of them municipios (no published appraised value); false when districts or barrios of Madrid are among them */
  onlyMunicipios: boolean;
}

const NO_GAP: WithoutPrice = { n: 0, onlyMunicipios: true };

/**
 * Buying, the zones of `all_zones` without a price that fail nothing and do not pass: those the
 * search could not check for the price. With the code deployed before the estimate is synced the
 * districts and barrios of Madrid are among them, so they are counted by level, never all called
 * municipios. Nothing when renting or with an API without `unknown_by_constraint` (before D-234).
 */
export function zonesWithoutPrice(result: Pick<SearchResult, "scenario" | "reality_check" | "all_zones">): WithoutPrice {
  if (result.scenario.budget?.kind !== "buy" || !result.reality_check.unknown_by_constraint?.budget) return NO_GAP;
  const unpriced = result.all_zones.filter((z) => z.estimated_cost_eur == null && !z.failed_constraints?.length && !z.passes_all);
  return { n: unpriced.length, onlyMunicipios: unpriced.every((z) => z.zone.level === "municipio") };
}

/**
 * rc.sin_dato: zones with some condition that could not be checked are never counted as good.
 * rc.sin_dato.compra: buying, the reason is said. Only municipios: they have no published appraised
 * value. Districts or barrios among them (the estimate not synced yet): «zonas», with a reason that
 * holds for both, never a promise of an estimate.
 */
export function unknownText(n: number, word: ZoneWord = "zona", withoutPrice: WithoutPrice = NO_GAP): string {
  const [one, many] = WORDS[word].feminine ? ["la contamos como buena", "las contamos como buenas"] : ["lo contamos como bueno", "los contamos como buenos"];
  const them = `No ${n === 1 ? one : many}.`;
  if (withoutPrice.n <= 0) return `En ${zonesText(n, word)} no podemos comprobarlo todo por falta de datos. ${them}`;
  const m = withoutPrice.n;
  const reason = withoutPrice.onlyMunicipios
    ? `sin precio de compra publicado en ${zonesText(m, word === "pueblo" ? "pueblo" : "municipio")} (solo lo tienen los de más de 25.000 habitantes)`
    : `sin precio de compra en ${zonesText(m, word)} (el valor tasado de la vivienda solo se publica por municipio, y solo en los de más de 25.000 habitantes)`;
  return `En ${zonesText(n, word)} no podemos comprobarlo todo: ${reason}. ${them}`;
}

/** One option of «¿Y si cambias algo?» (rc.opcion.cuenta): what it changes, how many zones there would be and how many more. */
export function optionText(r: Pick<Relaxation, "label" | "zones_if_relaxed" | "added_zones">, word: ZoneWord = "zona"): { label: string; count: string } {
  const would = r.zones_if_relaxed === 1 ? "saldría" : "saldrían";
  return { label: r.label, count: `${would} ${zonesText(r.zones_if_relaxed, word)}, ${r.added_zones} más` };
}

/**
 * rc.limite: the condition that leaves out the most zones, by its FAILs. The API counts a zone it
 * cannot check (UNKNOWN) as left out too (binding_constraint); when such zones outnumber the
 * FAILs, what limits the search is missing data, not the condition, and nothing is named (D-238:
 * renting in «Pueblos», where almost no village publishes its rent).
 */
export function limitingConstraint(result: Pick<SearchResult, "all_zones" | "reality_check">): string | null {
  const id = result.reality_check.binding_constraint;
  if (!id) return null;
  const failing = result.all_zones.filter((z) => z.failed_constraints?.includes(id)).length;
  return failing > 0 && failing >= result.reality_check.zones_unknown ? id : null;
}

/** zona.puesto: «La 3.ª que más encaja», and for a barrio, municipio or pueblo «El 3.º…» */
export function rankText(rank: number, word: ZoneWord = "zona"): string {
  return WORDS[word].feminine ? `La ${rank}.ª que más encaja` : `El ${rank}.º que más encaja`;
}

/**
 * a_pie.mediana: the walking minutes of the facts («Colegio con primaria a unos 9 min andando»)
 * are the median of the zone, said once under them, when one of them is a walk.
 */
export const WALK_MEDIAN = "Los minutos andando son los de la mitad de la zona: unos vecinos lo tienen más cerca y otros más lejos.";

/** feature_id prefix of the indicators that are minutes on foot (min_a_pie_colegio, min_a_pie_transporte…) */
export const WALK_MINUTES_FEATURE_PREFIX = "min_a_pie_";

export function hasWalkingFact(facts: readonly { indicator?: { feature_id: string } | null }[]): boolean {
  return facts.some((fact) => fact.indicator?.feature_id.startsWith(WALK_MINUTES_FEATURE_PREFIX) === true);
}

/** Rows of «Qué falta» a walk can reach: the services of «Lo quiero a un paseo» and of the walking facts. */
const WALK_ROWS: readonly GapRowKey[] = ["escuela_infantil", "colegio", "centro_salud", "mayores", "farmacia"];

/**
 * The services the search found a short walk away in a zone, in minutes by row of «Qué falta»: a
 * service of «Lo quiero a un paseo» it meets (`near:<row>` PASS), else a walking fact the API
 * counts as a strength («Centro de salud a unos 8 min andando»). For zona.cerca_pocas, which only
 * keeps those within the row's own walk (ROW_WALK_MIN in gaps.ts).
 */
export function nearbyWalks(ranked: Pick<RankedZone, "constraints" | "facts"> | null): Partial<Record<GapRowKey, number>> {
  const walks: Partial<Record<GapRowKey, number>> = {};
  for (const row of WALK_ROWS) {
    const near = ranked?.constraints.find((c) => c.constraint_id === `near:${row}` && c.status === "PASS" && typeof c.value === "number");
    const fact = ranked?.facts.find((f) => f.kind === "strength" && f.indicator?.feature_id === `${WALK_MINUTES_FEATURE_PREFIX}${row}`);
    const minutes = typeof near?.value === "number" ? near.value : fact?.indicator?.value;
    if (typeof minutes === "number") walks[row] = minutes;
  }
  return walks;
}
