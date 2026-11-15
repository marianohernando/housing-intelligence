"use client";

import { ArrowRight, Footprints, X } from "lucide-react";
import Link from "next/link";
import { useId } from "react";

import type { ComparisonGroup, GapStatus } from "@/contracts/zone_gap_list_response";
import { useScenario } from "@/components/search/ScenarioProvider";
import Button from "@/components/ui/Button";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import GlassCard from "@/components/ui/GlassCard";
import Help from "@/components/ui/Help";
import PriceTag from "@/components/ui/PriceTag";
import { errorMessage } from "@/lib/errors";
import { nearbyWalks, zoneFit, zonePriceOf } from "@/lib/fit";
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
  SMALL_ZONE,
  topRows,
  walking,
  walkingText,
} from "@/lib/gaps";
import { screenZone, type ZoneProperties, zoneHref, zoneTitle } from "@/lib/map/zones";

import FitDetails from "./FitDetails";
import GapBadge from "./GapBadge";
import PendingRows from "./PendingRows";
import SmallZoneTag from "./SmallZoneTag";
import styles from "./ZoneCard.module.css";
import { useZoneGaps } from "./useZoneGaps";

// Copy from pitch/textos_web.md (zona.*, falta.*, carga.falta, error.reintentar, leyenda.antes_de_buscar);
// zona.falta.ayuda and zona.cerca_pocas in lib/gaps.ts
// «A pie» with the minutes is falta.fila.a_pie, shortened for the card.
const TEXT = {
  municipio: "Municipio",
  close: "Cerrar",
  beforeSearch: "Haz tu búsqueda para ver qué zonas te convienen.",
  fitSoon: "Muy pronto verás si esta zona te conviene.", // zona.encaje.pronto
  // zona.encaje.ayuda, behind «¿Qué es el %?» (a tooltip never showed on a phone)
  fitHelpLabel: "¿Qué es el %?",
  fitHelp: "Cuánto se parece esta zona a lo que buscas. No es una nota de la zona.",
  // zona.encaje.aria: «Muy buena opción para tu búsqueda: 94 %»
  fitAria: (band: string, pct: string) => `${band} para tu búsqueda: ${pct}`,
  stale: "Esto es de tu búsqueda anterior.", // zona.encaje.antiguo
  missing: "Lo que le falta a esta zona",
  walk: "A pie:",
  retry: "Reintentar",
  open: "Ver la zona",
  all: "Ver todo lo que falta",
  // A barrio of a search over Madrid capital (D-238): its «Qué falta» and screen are its district's
  barrio: (city: string) => `Barrio de ${city}`, // zona.barrio.antetitulo
  barrioMissing: (district: string) => `Lo que le falta a ${district}`, // zona.barrio.falta.titulo
  barrioMissingHelp: "Las cifras de «Qué falta» son del distrito entero.", // zona.barrio.falta.ayuda
  openDistrict: "Ver el distrito", // zona.barrio.boton
};

interface Props {
  zone: ZoneProperties;
  /** Overview: from the map, with «Ver la zona». Zone: on its own screen, with the full list link. */
  mode: "overview" | "zone";
  onClose?: () => void;
}

type RowStatus = { status: GapStatus; reliable?: boolean; comparison_group?: ComparisonGroup | null };

/**
 * What each label of the card's rows means, for the labels on view (estado.*.corto): visible text,
 * since the tooltips never showed on a phone (UX mobile audit, A5).
 */
function statusLines(rows: readonly RowStatus[]): [string, string][] {
  const lines = new Map<string, string>();
  for (const row of rows) {
    if (notComparable(row)) lines.set(SMALL_ZONE.label, SMALL_ZONE.short);
    else lines.set(GAP_STATUS[row.status].label, GAP_STATUS[row.status].short);
    if (inGroup(row)) lines.set(GROUP.label, GROUP.short);
  }
  return [...lines];
}

/** Zone card of the mockups: name, % of fit once there is a search, and «Lo que le falta a esta zona». */
export default function ZoneCard({ zone, mode, onClose }: Props) {
  const { level, code, name, municipio_name, zone_key } = zone;
  const titleId = useId();
  const { result, available, stale, scenario } = useScenario();
  const isBarrio = level === "barrio";
  const gapsOf = screenZone(zone);
  const gaps = useZoneGaps(gapsOf.level, gapsOf.code);
  const slow = useSlow(gaps.loading);
  const match = result?.all_zones.find((z) => z.zone.level === level && z.zone.code === code);
  const pct = match?.match_pct;
  // F5 of fit-0.9: «Encaja muy bien» over «94 %»; a zone that fails something shows what it lacks, not a %
  const fit = match?.passes_all ? matchText(match) : null;
  // D-234: the approximate price, in the head; none without a price (the search's notice says why)
  const price = result ? zonePriceOf(result, zone_key) : null;
  const rows = gaps.data?.data.rows ?? [];
  // The three rows in view: what matters to the household first, then what is missing (D-244, review of PR #79)
  const shown = topRows(rows, 3, scenario.household);
  // A zone that fits everything asked, with FALTA or JUSTO rows: one line says both are true, with
  // every such row of the API, also those beyond the three the card shows. Not for a barrio: its
  // rows are the whole district's, and the line says «aquí»
  // A service the search found close that «Qué falta» marks FALTA or JUSTO: both are true, and one
  // line says why (zona.cerca_pocas). For a barrio, its walks against its district's rows
  const nearLines = result ? nearButShort(rows, nearbyWalks(zoneFit(result, zone_key).ranked), isBarrio ? (zone.district_name ?? null) : null) : [];
  // The rows those lines explain are not said again in encaje.aviso_* (review R-06 of PR #70)
  const explained = new Set(nearLines.map((line) => line.row));
  const fitsButShort = pct != null && match?.passes_all && !isBarrio ? fitsButShortText(rows.filter((r) => !explained.has(r.row))) : null;
  const eyebrow = isBarrio ? TEXT.barrio(municipio_name) : level === "distrito" ? `Distrito de ${municipio_name}` : TEXT.municipio;
  const missingTitle = isBarrio ? TEXT.barrioMissing(zone.district_name ?? municipio_name) : TEXT.missing;

  return (
    <GlassCard as="aside" aria-labelledby={titleId} className={styles.card}>
      <div className={styles.head}>
        <p className={styles.eyebrow}>{eyebrow}</p>
        {onClose && (
          <button type="button" className={styles.close} aria-label={TEXT.close} onClick={onClose}>
            <X size={20} aria-hidden="true" />
          </button>
        )}
      </div>
      <div className={styles.titleRow}>
        <h2 id={titleId} className={styles.name}>
          {zoneTitle(zone)}
        </h2>
        {fit && (
          <span className={styles.pct}>
            <span aria-hidden="true">
              <small>{fit.band}</small>
              {fit.pct}
            </span>
            <span className="visually-hidden">{TEXT.fitAria(fit.band, fit.pct)}</span>
          </span>
        )}
      </div>
      {price && <PriceTag price={price} variant="card" />}
      {fit && (
        <Help about={zoneTitle(zone)} label={TEXT.fitHelpLabel} className={styles.fitHelp}>
          <p>{TEXT.fitHelp}</p>
        </Help>
      )}
      {result && stale && pct != null && <p className={styles.hint}>{TEXT.stale}</p>}
      {result ? <FitDetails result={result} zoneKey={zone_key} /> : <p className={styles.hint}>{available ? TEXT.beforeSearch : TEXT.fitSoon}</p>}

      <section className={styles.missing} aria-labelledby={`${titleId}-missing`}>
        <h3 id={`${titleId}-missing`}>{missingTitle}</h3>
        <p className={styles.hint}>{GAPS_HELP}</p>
        {isBarrio && <p className={styles.hint}>{TEXT.barrioMissingHelp}</p>}
        {fitsButShort && <p className={styles.fitsButShort}>{fitsButShort}</p>}
        {nearLines.map((line) => (
          <p key={line.row} className={styles.nearButShort}>
            <Footprints size={18} aria-hidden="true" />
            <span>{line.text}</span>
          </p>
        ))}
        {gaps.loading && (
          <p role="status" className={styles.hint}>
            Calculando qué falta en {isBarrio ? (zone.district_name ?? name) : name}…{slow && ` ${SLOW_TEXT}`}
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

      {mode === "overview" ? (
        <Button href={zoneHref(gapsOf)} className={styles.action}>
          {isBarrio ? TEXT.openDistrict : TEXT.open}
          <ArrowRight size={20} aria-hidden="true" />
        </Button>
      ) : (
        <Button href={gapsHref(gapsOf.level, gapsOf.code)} variant="secondary" className={styles.action}>
          {TEXT.all}
          <ArrowRight size={20} aria-hidden="true" />
        </Button>
      )}
    </GlassCard>
  );
}
