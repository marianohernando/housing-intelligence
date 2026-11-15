/**
 * The % of fit in words (pure, unit tested): its band («Encaja muy bien · 94 %») and the zones
 * that tie at the same shown % (F5 of the fit-0.9 formula, decided by Mariano). The web never
 * recomputes the %: it reads the band the API sends (`match_band`, fit-0.9) or, from an API that
 * does not send it yet, the same thresholds over `match_pct`.
 */
import type { RankedZone, ZoneMatch } from "@/contracts/search_response";

import { type ZoneWord, zonesText } from "./fit";

/** The bands of the % (resultados.banda.*): «muy bien» from 90, «bien» from 75, «regular» from 60, «poco» below. */
export type MatchBand = "muy_bien" | "bien" | "regular" | "poco";

/**
 * `match_band` of RankedZone and ZoneMatch from fit-0.9 on. Optional here so the web works with
 * the API deployed before it; once line A publishes the contract, the generated types carry it too.
 */
export interface WithBand {
  match_band?: MatchBand | string | null;
}

/** Lower bound of each band, best first: the API's thresholds (fit-0.9). */
const BAND_FROM: readonly [MatchBand, number][] = [
  ["muy_bien", 90],
  ["bien", 75],
  ["regular", 60],
  ["poco", 0],
];

const BANDS = new Set<string>(BAND_FROM.map(([band]) => band));

const BAND_TEXT: Record<MatchBand, string> = {
  muy_bien: "Encaja muy bien",
  bien: "Encaja bien",
  regular: "Encaja regular",
  poco: "Encaja poco",
};

/**
 * The band of a zone: the API's when it sends a known one, else from its % with the same
 * thresholds; null without a % (unknown is never «poco»).
 */
export function matchBand(zone: Pick<ZoneMatch, "match_pct"> & WithBand): MatchBand | null {
  if (zone.match_pct == null) return null;
  if (zone.match_band != null && BANDS.has(zone.match_band)) return zone.match_band as MatchBand;
  return BAND_FROM.find(([, from]) => zone.match_pct! >= from)![0];
}

/** What the % says, in its parts: «Encaja muy bien» and «94 %». */
export interface MatchText {
  band: string;
  pct: string;
  /** Read aloud and in one line: «Encaja muy bien · 94 %» */
  text: string;
}

export function matchText(zone: Pick<ZoneMatch, "match_pct"> & WithBand): MatchText | null {
  const band = matchBand(zone);
  if (band === null) return null;
  const pct = `${zone.match_pct} %`;
  return { band: BAND_TEXT[band], pct, text: `${BAND_TEXT[band]} · ${pct}` };
}

type Named = Pick<ZoneMatch, "match_pct" | "passes_all"> & { zone: { level: string; code: string; name: string } };

/**
 * The other zones that meet everything with the same shown % as this one, in the API order
 * (`all_zones`): the zones it ties with. Empty for a zone that fails, has no % or ties with none.
 */
export function tiedWith(zone: Pick<ZoneMatch, "match_pct" | "zone">, all: readonly Named[]): Named[] {
  if (zone.match_pct == null) return [];
  const self = `${zone.zone.level}/${zone.zone.code}`;
  return all.filter((z) => z.passes_all && z.match_pct === zone.match_pct && `${z.zone.level}/${z.zone.code}` !== self);
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
export function tiedNames(zone: Pick<ZoneMatch, "match_pct" | "zone">, all: readonly Named[], word: ZoneWord = "zona"): string | null {
  const others = tiedWith(zone, all);
  if (others.length === 0) return null;
  return others.length <= NAMED_TIES ? joinNames(others.map((z) => z.zone.name)) : `${zonesText(others.length, word)} más`;
}

/** zona.empate, in the zone card: «Empata al 94 % con Latina.»; null when it ties with none. */
export function tieText(zone: Pick<ZoneMatch, "match_pct" | "zone">, all: readonly Named[], word: ZoneWord = "zona"): string | null {
  const whom = tiedNames(zone, all, word);
  return whom === null ? null : `Empata al ${zone.match_pct} % con ${whom}.`;
}

/** One row of the ranking with where it stands in a run of rows tied at its %. */
export interface RankingRow {
  zone: RankedZone;
  /** The run of consecutive rows with this row's %, when there are two or more (null otherwise) */
  tie: { first: boolean; last: boolean; label: string } | null;
}

/**
 * The rows of the ranking in view, with their ties marked (resultados.empate.grupo): consecutive
 * rows with the same shown % form a run headed «Empatan al 94 %». When the run goes on beyond the
 * rows in view, the label counts them all: «Empatan al 100 % (45 zonas)».
 */
export function rankingRows(shown: readonly RankedZone[], all: readonly Named[], word: ZoneWord = "zona"): RankingRow[] {
  return shown.map((zone, i) => {
    const same = (other: RankedZone | undefined) => other !== undefined && other.match_pct === zone.match_pct;
    const before = same(shown[i - 1]);
    const after = same(shown[i + 1]);
    if (!before && !after) return { zone, tie: null };
    const inView = shown.filter((z) => z.match_pct === zone.match_pct).length;
    const total = tiedWith(zone, all).length + 1;
    const label = total > inView ? `Empatan al ${zone.match_pct} % (${zonesText(total, word)})` : `Empatan al ${zone.match_pct} %`;
    return { zone, tie: { first: !before, last: !after, label } };
  });
}
