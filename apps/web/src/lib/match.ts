/**
 * The % of fit in words (pure, unit tested): its band («Muy buena opción · 94 %») and the zones
 * that tie at the same shown % (F5 of the fit-0.9 formula, decided by Mariano). The web never
 * recomputes the %: it reads the band the API sends (`match_band`, fit-0.9, D-243 §4) or, from an
 * API that does not send it, the same thresholds over `match_pct`.
 */
import type { MatchBand, RankedZone, ZoneMatch } from "@/contracts/search_response";

import { type ZoneWord, zonesText } from "./fit";

/**
 * What a band is read from: the shown %, the API's `match_band` and, in a ZoneMatch, whether the
 * zone passes every condition. A RankedZone of `results` carries no `passes_all`: it passes them all.
 */
type Banded = Pick<ZoneMatch, "match_pct" | "match_band"> & Partial<Pick<ZoneMatch, "passes_all">>;

/** Lower bound of each band (resultados.banda.*), best first: the API's thresholds (fit-0.9). */
export const BAND_FROM: readonly [MatchBand, number][] = [
  ["muy_bien", 90],
  ["bien", 75],
  ["regular", 60],
  ["poco", 0],
];

const BANDS = new Set<string>(BAND_FROM.map(([band]) => band));

/**
 * resultados.banda.*: what the band says to the person, in plain words (UX mobile audit, §4: «encaja»
 * was a word to decode). The API's values (`muy_bien`, `bien`, `regular`, `poco`) do not change.
 */
export const BAND_TEXT: Record<MatchBand, string> = {
  muy_bien: "Muy buena opción",
  bien: "Buena opción",
  regular: "Opción regular",
  poco: "Poco recomendable",
};

/**
 * The band of a zone: none for one that fails some condition, which reads by what it lacks
 * (D-243 §4), nor without a % (unknown is never «poco»). Otherwise the API's band or, when it comes
 * null or missing (an API before fit-0.9), the band of its % with the same thresholds. The types
 * are not checked at run time: a band this web does not know is also read from the %.
 */
export function matchBand(zone: Banded): MatchBand | null {
  if (zone.passes_all === false || zone.match_pct == null) return null;
  if (zone.match_band != null && BANDS.has(zone.match_band)) return zone.match_band;
  return BAND_FROM.find(([, from]) => zone.match_pct! >= from)![0];
}

/**
 * The table of «Cómo lo calculamos», from the same thresholds: «90 % o más», «De 75 a 89 %»,
 * «De 60 a 74 %» and «Menos del 60 %», each with its band.
 */
export function bandRanges(): [string, string][] {
  return BAND_FROM.map(([band, from], i) => {
    const above = BAND_FROM[i - 1]?.[1];
    const range = above === undefined ? `${from} % o más` : from === 0 ? `Menos del ${above} %` : `De ${from} a ${above - 1} %`;
    return [range, BAND_TEXT[band]];
  });
}

/** What the % says, in its parts: «Muy buena opción» and «94 %». */
export interface MatchText {
  band: string;
  pct: string;
  /** Read aloud and in one line: «Muy buena opción · 94 %» */
  text: string;
}

export function matchText(zone: Banded): MatchText | null {
  const band = matchBand(zone);
  if (band === null) return null;
  // A no-break space: «94 %» never splits at the end of a line
  const pct = `${zone.match_pct}\u00a0%`;
  return { band: BAND_TEXT[band], pct, text: `${BAND_TEXT[band]} · ${pct}` };
}

type Keyed = { zone: { level: string; code: string } };
type Named = Pick<ZoneMatch, "match_pct" | "passes_all"> & { zone: { level: string; code: string; name: string } };

const keyOf = (z: Keyed) => `${z.zone.level}/${z.zone.code}`;

/**
 * The other zones that meet everything with the same shown % as this one: the zones it ties
 * with, in the order of the ranking (`ranking`, the API's `results`) and, beyond it, of
 * `all_zones`. Empty for a zone that fails, has no % or ties with none.
 */
export function tiedWith(zone: Pick<ZoneMatch, "match_pct" | "zone">, all: readonly Named[], ranking: readonly Keyed[] = []): Named[] {
  if (zone.match_pct == null) return [];
  const self = keyOf(zone);
  const place = new Map(ranking.map((z, i) => [keyOf(z), i]));
  const at = (z: Keyed) => place.get(keyOf(z)) ?? ranking.length;
  const tied = all.filter((z) => z.passes_all && z.match_pct === zone.match_pct && keyOf(z) !== self);
  // A stable sort: the zones beyond the ranking keep the order of all_zones
  return tied.sort((a, b) => at(a) - at(b));
}

/** With this many other zones or fewer they are named; with more, counted. */
const NAMED_TIES = 3;

function joinNames(names: readonly string[]): string {
  return names.length === 1 ? names[0]! : `${names.slice(0, -1).join(", ")} y ${names.at(-1)}`;
}

/**
 * Whom a zone ties with: «Latina», «Latina, Usera y Moratalaz», or with more than three «12 zonas
 * más» (in the scope's word); null when it ties with none.
 */
export function tiedNames(
  zone: Pick<ZoneMatch, "match_pct" | "zone">,
  all: readonly Named[],
  word: ZoneWord = "zona",
  ranking: readonly Keyed[] = [],
): string | null {
  const others = tiedWith(zone, all, ranking);
  if (others.length === 0) return null;
  return others.length <= NAMED_TIES ? joinNames(others.map((z) => z.zone.name)) : `${zonesText(others.length, word)} más`;
}

/**
 * zona.empate, in the zone card: «Igual de buena que Latina (94 %).», «Igual de bueno que…» for a
 * barrio, municipio or pueblo; null when it ties with none.
 */
export function tieText(
  zone: Pick<ZoneMatch, "match_pct" | "zone">,
  all: readonly Named[],
  word: ZoneWord = "zona",
  ranking: readonly Keyed[] = [],
): string | null {
  const whom = tiedNames(zone, all, word, ranking);
  const good = word === "zona" ? "buena" : "bueno";
  return whom === null ? null : `Igual de ${good} que ${whom} (${zone.match_pct}\u00a0%).`;
}

/** One row of the ranking with where it stands in a run of rows tied at its %. */
export interface RankingRow<Z extends RankedZone = RankedZone> {
  zone: Z;
  /** The run of rows in view with this row's %, when it ties with some zone (null otherwise) */
  tie: { first: boolean; last: boolean; label: string } | null;
}

/**
 * The rows of the ranking in view, with their ties marked (resultados.empate.grupo): consecutive
 * rows with the same shown % form a run headed «Empatan al 94 %». When the tie goes on beyond the
 * rows in view, the label counts them all, also over a single row of the folded list: «Empatan al
 * 92 % (3 zonas)».
 */
export function rankingRows<Z extends RankedZone>(shown: readonly Z[], all: readonly Named[], word: ZoneWord = "zona"): RankingRow<Z>[] {
  return shown.map((zone, i) => {
    const same = (other: RankedZone | undefined) => other !== undefined && other.match_pct === zone.match_pct;
    const before = same(shown[i - 1]);
    const after = same(shown[i + 1]);
    const total = Math.max(tiedWith(zone, all).length + 1, shown.filter((z) => z.match_pct === zone.match_pct).length);
    if (total < 2) return { zone, tie: null };
    const inView = shown.filter((z) => z.match_pct === zone.match_pct).length;
    const label = total > inView ? `Empatan al ${zone.match_pct} % (${zonesText(total, word)})` : `Empatan al ${zone.match_pct} %`;
    return { zone, tie: { first: !before, last: !after, label } };
  });
}
