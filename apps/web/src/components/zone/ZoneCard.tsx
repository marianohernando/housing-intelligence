"use client";

import { ArrowRight, ChevronDown, ChevronLeft, CircleAlert, CircleCheck, CircleQuestionMark, Euro, Footprints, Info } from "lucide-react";
import Link from "next/link";
import { useEffect, useId, useRef } from "react";

import type { SearchResult } from "@/contracts/search_response";
import type { ComparisonGroup, GapRowKey, GapStatus } from "@/contracts/zone_gap_list_response";
import { useScenario } from "@/components/search/ScenarioProvider";
import Button from "@/components/ui/Button";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import GlassCard from "@/components/ui/GlassCard";
import Help from "@/components/ui/Help";
import PriceTag from "@/components/ui/PriceTag";
import {
  askedLines,
  comparableFineText,
  type HouseholdGaps,
  householdGaps,
  markedRows,
  nothingMissingText,
  unknownRowsText,
} from "@/lib/essentials";
import { errorMessage } from "@/lib/errors";
import { nearbyWalks, speaksToMany, voice, zoneFit, zonePriceOf } from "@/lib/fit";
import { matchText } from "@/lib/match";
import {
  fitsButShortText,
  GAP_STATUS,
  GAPS_HELP,
  gapsHref,
  GROUP,
  inGroup,
  nearButShort,
  notComparable,
  notComparableText,
  ROW_IN_LIST,
  SMALL_ZONE,
  topRows,
  walking,
  walkingText,
} from "@/lib/gaps";
import { screenZone, type ZoneProperties, zoneHref, zoneTitle } from "@/lib/map/zones";

import FitDetails, { FitVerdict, KIND_CLASS, TOPIC_ICON } from "./FitDetails";
import GapBadge from "./GapBadge";
import PendingRows from "./PendingRows";
import SmallZoneTag from "./SmallZoneTag";
import styles from "./ZoneCard.module.css";
import { useZoneGaps } from "./useZoneGaps";

// Copy from pitch/textos_web.md (zona.*, zona.esencial.* and zona.ver_mas of the second delivery of the UX
// mobile audit, falta.*, carga.falta, error.reintentar, leyenda.antes_de_buscar); zona.falta.ayuda and
// zona.cerca_pocas in lib/gaps.ts. «A pie» with the minutes is falta.fila.a_pie, shortened for the card.
const TEXT = {
  municipio: "Municipio",
  // zona.volver_lista: a button with words at the top of the card (it was an «X» without them, audit A4)
  back: "Volver a la lista",
  backNoList: "Volver", // zona.volver: before a search there is no list to go back to
  beforeSearch: "Haz tu búsqueda para ver qué zonas te convienen.",
  fitSoon: "Muy pronto verás si esta zona te conviene.", // zona.encaje.pronto
  // zona.encaje.ayuda, behind «¿Qué es el %?» (a tooltip never showed on a phone); «buscáis» to a household of more than one
  fitHelpLabel: "¿Qué es el %?",
  fitHelp: (many: boolean) => `Cuánto se parece esta zona a lo que ${voice(many).buscas}. No es una nota de la zona.`,
  // zona.encaje.aria: «Muy buena opción para tu búsqueda: 94 %» («vuestra búsqueda»)
  fitAria: (band: string, pct: string, many: boolean) => `${band} para ${voice(many).tu} búsqueda: ${pct}`,
  stale: "Esto es de tu búsqueda anterior.", // zona.encaje.antiguo
  essentials: (zone: string) => `Lo esencial de ${zone}`, // zona.esencial.aria
  more: (zone: string) => `Ver más sobre ${zone}`, // zona.ver_mas
  missing: "Lo que le falta a esta zona",
  walk: "A pie:",
  retry: "Reintentar",
  open: "Ver la zona",
  all: "Ver todo lo que falta",
  loadingGaps: (zone: string) => `Calculando qué falta en ${zone}…`,
  // A barrio of a search over Madrid capital (D-238): its «Qué falta» and screen are its district's
  barrio: (city: string) => `Barrio de ${city}`, // zona.barrio.antetitulo
  barrioMissing: (district: string) => `Lo que le falta a ${district}`, // zona.barrio.falta.titulo
  barrioMissingHelp: "Las cifras de «Qué falta» son del distrito entero.", // zona.barrio.falta.ayuda
  openDistrict: "Ver el distrito", // zona.barrio.boton
};

interface Props {
  zone: ZoneProperties;
  /** Overview: from the map or the list, with «Ver la zona». Zone: on its own screen, with the full list link. */
  mode: "overview" | "zone";
  /** «Volver a la lista», at the top of the card on the overview */
  onBack?: () => void;
}

type RowStatus = { row: GapRowKey; status: GapStatus; reliable?: boolean; comparison_group?: ComparisonGroup | null };
type Gaps = ReturnType<typeof useZoneGaps>;

/**
 * What each label of the card's rows means, for the labels on view (estado.*.corto): visible text,
 * since the tooltips never showed on a phone (UX mobile audit, A5). «No comparable» is said of each
 * row in its own unit (review R-07 of PR #81).
 */
function statusLines(rows: readonly RowStatus[]): [string, string][] {
  const lines = new Map<string, string>();
  for (const row of rows) {
    if (notComparable(row)) lines.set(`${SMALL_ZONE.label} (${ROW_IN_LIST[row.row]})`, notComparableText(row.row));
    else lines.set(GAP_STATUS[row.status].label, GAP_STATUS[row.status].short);
    if (inGroup(row)) lines.set(GROUP.label, GROUP.short);
  }
  return [...lines];
}

/** The district a barrio's rows of «Qué falta» belong to; null for any other zone. */
const districtOfBarrio = (zone: ZoneProperties) => (zone.level === "barrio" ? (zone.district_name ?? zone.municipio_name) : null);

function GapsState({ zone, gaps }: { zone: ZoneProperties; gaps: Gaps }) {
  const slow = useSlow(gaps.loading);
  return (
    <>
      {gaps.loading && (
        <p role="status" className={styles.hint}>
          {TEXT.loadingGaps(districtOfBarrio(zone) ?? zone.name)}
          {slow && ` ${SLOW_TEXT}`}
        </p>
      )}
      {gaps.error && (
        <div role="alert" className={styles.error}>
          <p>{errorMessage(gaps.error)}</p>
          <Button variant="secondary" onClick={gaps.retry}>
            {TEXT.retry}
          </Button>
        </div>
      )}
    </>
  );
}

/**
 * «Lo que le falta a esta zona»: three rows, what matters to the household of the search first
 * (D-244), with what each label means, «Ver todo lo que falta» and, when the search found a service
 * close that the row marks short, why both are true. Before a search it is the card's content;
 * after one, it waits behind «Ver más», and its loading and errors are said among the essentials.
 */
function MissingSection({ zone, gaps, mode, withStates }: { zone: ZoneProperties; gaps: Gaps; mode: Props["mode"]; withStates: boolean }) {
  const titleId = useId();
  const { result } = useScenario();
  const isBarrio = zone.level === "barrio";
  const gapsOf = screenZone(zone);
  const rows = gaps.data?.data.rows ?? [];
  const match = result?.all_zones.find((z) => z.zone.level === zone.level && z.zone.code === zone.code);
  // What matters to the household and what the person marks first (review R-02 of PR #81)
  const shown = topRows(rows, 3, result?.scenario.household ?? null, result ? markedRows(result.scenario) : []);
  // A service the search found close that «Qué falta» marks FALTA or JUSTO: both are true, and one
  // line says why (zona.cerca_pocas). For a barrio, its walks against its district's rows
  const nearLines = result ? nearButShort(rows, nearbyWalks(zoneFit(result, zone.zone_key).ranked), districtOfBarrio(zone)) : [];
  // The rows those lines explain are not said again in encaje.aviso_* (review R-06 of PR #70); not
  // for a barrio either: its rows are the whole district's, and the line says «aquí»
  const explained = new Set(nearLines.map((line) => line.row));
  const fitsButShort = match?.match_pct != null && match.passes_all && !isBarrio ? fitsButShortText(rows.filter((r) => !explained.has(r.row))) : null;
  const district = districtOfBarrio(zone);

  return (
    <section className={styles.missing} aria-labelledby={titleId}>
      <h3 id={titleId}>{district ? TEXT.barrioMissing(district) : TEXT.missing}</h3>
      <p className={styles.hint}>{GAPS_HELP}</p>
      {isBarrio && <p className={styles.hint}>{TEXT.barrioMissingHelp}</p>}
      {fitsButShort && <p className={styles.fitsButShort}>{fitsButShort}</p>}
      {nearLines.map((line) => (
        <p key={line.row} className={styles.nearButShort}>
          <Footprints size={18} aria-hidden="true" />
          <span>{line.text}</span>
        </p>
      ))}
      {withStates && <GapsState zone={zone} gaps={gaps} />}
      {gaps.data && (
        <ul className={styles.rows}>
          {shown.map((row) => {
            const walk = walking(row.extra_indicators, row.row);
            return (
              <li key={row.row}>
                <span className={styles.rowName}>
                  {row.label}
                  {walk && (
                    <small>
                      {TEXT.walk} {walkingText(walk)}
                    </small>
                  )}
                  {inGroup(row) && <small>{GROUP.label}</small>}
                </span>
                {notComparable(row) ? <SmallZoneTag /> : <GapBadge status={row.status} />}
              </li>
            );
          })}
        </ul>
      )}
      {gaps.data && rows.length > 0 && (
        <ul className={styles.statusKey}>
          {statusLines(shown).map(([label, meaning]) => (
            <li key={label}>
              <strong>{label}:</strong> {meaning}
            </li>
          ))}
        </ul>
      )}
      {gaps.data && <PendingRows warnings={gaps.data.warnings} className={styles.pending} />}
      {gaps.data && mode === "overview" && (
        <Link href={gapsHref(gapsOf.level, gapsOf.code)} className={styles.all}>
          {TEXT.all}
        </Link>
      )}
    </section>
  );
}

/** «Ver la zona» (or «Ver el distrito» for a barrio) on the overview; «Ver todo lo que falta» on the zone's own screen. */
function CardAction({ zone, mode }: { zone: ZoneProperties; mode: Props["mode"] }) {
  const gapsOf = screenZone(zone);
  if (mode === "zone") {
    return (
      <Button href={gapsHref(gapsOf.level, gapsOf.code)} variant="secondary" className={styles.action}>
        {TEXT.all}
        <ArrowRight size={20} aria-hidden="true" />
      </Button>
    );
  }
  return (
    <Button href={zoneHref(gapsOf)} className={styles.action}>
      {zone.level === "barrio" ? TEXT.openDistrict : TEXT.open}
      <ArrowRight size={20} aria-hidden="true" />
    </Button>
  );
}

/** The essentials' line of what is missing: what is short of what matters, or that nothing is, or that we cannot tell. */
function HomeGaps({ home, many, place }: { home: HouseholdGaps; many: boolean; place: string | null }) {
  const unsure = unknownRowsText(home.unknown, place);
  const nothing = home.short.length === 0 && home.covered;
  return (
    <>
      {home.short.map((line) => (
        <li key={line.row} className={styles.short}>
          <CircleAlert size={20} aria-hidden="true" />
          <span>{line.text}</span>
        </li>
      ))}
      {/* The green tick only when every row that matters can be compared (review R-01 of PR #81) */}
      {nothing && home.unknown.length === 0 && (
        <li className={styles.fine}>
          <CircleCheck size={20} aria-hidden="true" />
          <span>{nothingMissingText(many, place)}</span>
        </li>
      )}
      {nothing && home.unknown.length > 0 && (
        <li className={styles.partly}>
          <Info size={20} aria-hidden="true" />
          <span>{comparableFineText(place)}</span>
        </li>
      )}
      {unsure && (
        <li className={styles.unsure}>
          <CircleQuestionMark size={20} aria-hidden="true" />
          <span>{unsure}</span>
        </li>
      )}
    </>
  );
}

/**
 * The three essentials of the second delivery (decided by Mariano): what it costs, what the person
 * asked for with its minutes, and what it lacks that matters to the home or the person marked
 * (lib/essentials.ts). Before them, what the zone fails, if anything (FitVerdict).
 */
function Essentials({ zone, result, gaps }: { zone: ZoneProperties; result: SearchResult; gaps: Gaps }) {
  const { ranked } = zoneFit(result, zone.zone_key);
  const price = zonePriceOf(result, zone.zone_key);
  const place = districtOfBarrio(zone);
  const home = householdGaps(gaps.data?.data.rows ?? [], result.scenario, place);
  // A shortage the API caps the % for («Faltan colegios») goes once the home's gaps say it themselves
  const said = new Set(gaps.data ? home.short.map((line) => line.row) : []);
  const asked = askedLines(ranked, result.scenario).filter((line) => !line.rows?.length || !line.rows.every((row) => said.has(row)));
  return (
    <>
      <FitVerdict result={result} zoneKey={zone.zone_key} />
      <ul className={styles.essentials} aria-label={TEXT.essentials(zone.name)}>
        {price && (
          <li className={styles.cost}>
            <Euro size={20} aria-hidden="true" />
            <PriceTag price={price} variant="essential" />
          </li>
        )}
        {asked.map((line, i) => {
          // A topic this web does not know yet still shows, with the «otro» icon
          const Icon = TOPIC_ICON[line.topic] ?? Info;
          return (
            <li key={`${i}-${line.topic}`} className={KIND_CLASS[line.kind]}>
              <Icon size={20} aria-hidden="true" />
              <span>{line.text}</span>
            </li>
          );
        })}
        {gaps.data && <HomeGaps home={home} many={speaksToMany(result.scenario.household)} place={place} />}
      </ul>
      <GapsState zone={zone} gaps={gaps} />
    </>
  );
}

/**
 * «Ver más sobre {zona}»: everything the card said before the second delivery, folded. The % with
 * its band and what it is, the place in the list and the ties, every fact with its confidence, the
 * full price with why it is orientative, the whole «Qué falta» of the card and «Ver la zona».
 */
function MoreAbout({ zone, result, gaps, mode }: { zone: ZoneProperties; result: SearchResult; gaps: Gaps; mode: Props["mode"] }) {
  const { match } = zoneFit(result, zone.zone_key);
  // F5 of fit-0.9: «Muy buena opción» over «94 %»; a zone that fails something shows what it lacks, not a %
  const fit = match?.passes_all ? matchText(match) : null;
  const price = zonePriceOf(result, zone.zone_key);
  const many = speaksToMany(result.scenario.household);
  return (
    <details className={styles.more}>
      <summary>
        <span>{TEXT.more(zone.name)}</span>
        <ChevronDown size={20} aria-hidden="true" className={styles.moreIcon} />
      </summary>
      <div className={styles.moreBody}>
        {fit && (
          <span className={styles.pct}>
            <span aria-hidden="true">
              <small>{fit.band}</small>
              {fit.pct}
            </span>
            <span className="visually-hidden">{TEXT.fitAria(fit.band, fit.pct, many)}</span>
          </span>
        )}
        {fit && (
          <Help about={zoneTitle(zone)} label={TEXT.fitHelpLabel} className={styles.fitHelp}>
            <p>{TEXT.fitHelp(many)}</p>
          </Help>
        )}
        <FitDetails result={result} zoneKey={zone.zone_key} />
        {/* The price is said once among the essentials and in the cost fact above: here, only what it is for and why it is orientative */}
        {price && <PriceTag price={price} variant="breakdown" />}
        <MissingSection zone={zone} gaps={gaps} mode={mode} withStates={false} />
        <CardAction zone={zone} mode={mode} />
      </div>
    </details>
  );
}

/**
 * Zone card. After a search, its essentials first and the rest behind «Ver más sobre {zona}»
 * (second delivery of the UX mobile audit); before one, «Lo que le falta a esta zona». On the
 * overview it opens with «Volver a la lista» and takes the focus, since the row it replaces is hidden.
 */
export default function ZoneCard({ zone, mode, onBack }: Props) {
  const { level, municipio_name } = zone;
  const titleId = useId();
  const title = useRef<HTMLHeadingElement>(null);
  const { result, available, stale } = useScenario();
  const gapsOf = screenZone(zone);
  const gaps = useZoneGaps(gapsOf.level, gapsOf.code);
  const match = result ? zoneFit(result, zone.zone_key).match : null;
  const band = match?.passes_all ? matchText(match)?.band : null;
  const eyebrow = level === "barrio" ? TEXT.barrio(municipio_name) : level === "distrito" ? `Distrito de ${municipio_name}` : TEXT.municipio;

  useEffect(() => {
    if (mode !== "overview") return;
    const active = document.activeElement;
    // The row or the map that opened it: the focus would be lost with the hidden list
    if (!active || active === document.body || active.closest("[hidden]")) title.current?.focus({ preventScroll: true });
  }, [mode]);

  return (
    <GlassCard as="aside" aria-labelledby={titleId} className={styles.card}>
      {onBack && (
        <button type="button" className={styles.back} onClick={onBack}>
          <ChevronLeft size={22} aria-hidden="true" />
          {result ? TEXT.back : TEXT.backNoList}
        </button>
      )}
      {!result && <p className={styles.eyebrow}>{eyebrow}</p>}
      <h2 id={titleId} ref={title} tabIndex={-1} className={styles.name}>
        {zoneTitle(zone)}
      </h2>
      {/* zona.esencial.lugar: what kind of zone it is and its band (review R-10 of PR #81) */}
      {result && (
        <p className={styles.place}>
          {eyebrow}
          {band && " · "}
          {band && <strong>{band}</strong>}
        </p>
      )}
      {result && stale && match?.match_pct != null && <p className={styles.hint}>{TEXT.stale}</p>}
      {result ? (
        <>
          <Essentials zone={zone} result={result} gaps={gaps} />
          <MoreAbout zone={zone} result={result} gaps={gaps} mode={mode} />
        </>
      ) : (
        <>
          <p className={styles.hint}>{available ? TEXT.beforeSearch : TEXT.fitSoon}</p>
          <MissingSection zone={zone} gaps={gaps} mode={mode} withStates />
          <CardAction zone={zone} mode={mode} />
        </>
      )}
    </GlassCard>
  );
}
