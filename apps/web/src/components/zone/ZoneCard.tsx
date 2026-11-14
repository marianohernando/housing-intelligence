"use client";

import { ArrowRight, X } from "lucide-react";
import Link from "next/link";
import { useId } from "react";

import { useScenario } from "@/components/search/ScenarioProvider";
import Button from "@/components/ui/Button";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import GlassCard from "@/components/ui/GlassCard";
import PriceTag from "@/components/ui/PriceTag";
import { errorMessage } from "@/lib/errors";
import { zonePriceOf } from "@/lib/fit";
import { fitsButShortText, gapsHref, GROUP, inGroup, notComparable, topRows, walking, walkingText } from "@/lib/gaps";
import { screenZone, type ZoneProperties, zoneHref, zoneTitle } from "@/lib/map/zones";

import FitDetails from "./FitDetails";
import GapBadge from "./GapBadge";
import PendingRows from "./PendingRows";
import SmallZoneTag from "./SmallZoneTag";
import styles from "./ZoneCard.module.css";
import { useZoneGaps } from "./useZoneGaps";

// Copy from pitch/textos_web.md (zona.*, falta.*, carga.falta, error.reintentar, leyenda.antes_de_buscar)
// «A pie» with the minutes is falta.fila.a_pie, shortened for the card.
const TEXT = {
  municipio: "Municipio",
  close: "Cerrar",
  beforeSearch: "Haz tu búsqueda para ver qué zonas encajan contigo.",
  fitSoon: "Muy pronto verás cuánto encaja esta zona contigo.", // zona.encaje.pronto
  fitHelp: "Cuánto se parece esta zona a lo que buscas. No es una nota de la zona.", // zona.encaje.ayuda
  stale: "Este encaje es de tu búsqueda anterior.", // zona.encaje.antiguo
  missing: "Qué falta aquí",
  walk: "A pie:",
  retry: "Reintentar",
  open: "Ver la zona",
  all: "Ver todo lo que falta",
  // A barrio of a search over Madrid capital (D-238): its «Qué falta» and screen are its district's
  barrio: (city: string) => `Barrio de ${city}`, // zona.barrio.antetitulo
  barrioMissing: (district: string) => `Qué falta en ${district}`, // zona.barrio.falta.titulo
  barrioMissingHelp: "Las cifras de «Qué falta» son del distrito entero.", // zona.barrio.falta.ayuda
  openDistrict: "Ver el distrito", // zona.barrio.boton
};

interface Props {
  zone: ZoneProperties;
  /** Overview: from the map, with «Ver la zona». Zone: on its own screen, with the full list link. */
  mode: "overview" | "zone";
  onClose?: () => void;
}

/** Zone card of the mockups: name, % of fit once there is a search, and «Qué falta aquí». */
export default function ZoneCard({ zone, mode, onClose }: Props) {
  const { level, code, name, municipio_name, zone_key } = zone;
  const titleId = useId();
  const { result, available, stale } = useScenario();
  const isBarrio = level === "barrio";
  const gapsOf = screenZone(zone);
  const gaps = useZoneGaps(gapsOf.level, gapsOf.code);
  const slow = useSlow(gaps.loading);
  const match = result?.all_zones.find((z) => z.zone.level === level && z.zone.code === code);
  const pct = match?.match_pct;
  // D-234: the approximate price, in the head; none without a price (the search's notice says why)
  const price = result ? zonePriceOf(result, zone_key) : null;
  const rows = gaps.data?.data.rows ?? [];
  // A zone that fits everything asked, with FALTA or JUSTO rows: one line says both are true, with
  // every such row of the API, also those beyond the three the card shows. Not for a barrio: its
  // rows are the whole district's, and the line says «aquí»
  const fitsButShort = pct != null && match?.passes_all && !isBarrio ? fitsButShortText(rows) : null;
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
        {pct != null && (
          <span className={styles.pct} title={TEXT.fitHelp}>
            <span aria-hidden="true">
              {pct} %<small> de encaje</small>
            </span>
            <span className="visually-hidden">Esta zona encaja en un {pct} % con tu búsqueda</span>
          </span>
        )}
      </div>
      {price && <PriceTag price={price} variant="card" />}
      {result && stale && pct != null && <p className={styles.hint}>{TEXT.stale}</p>}
      {result ? <FitDetails result={result} zoneKey={zone_key} /> : <p className={styles.hint}>{available ? TEXT.beforeSearch : TEXT.fitSoon}</p>}

      <section className={styles.missing} aria-labelledby={`${titleId}-missing`}>
        <h3 id={`${titleId}-missing`}>{missingTitle}</h3>
        {isBarrio && <p className={styles.hint}>{TEXT.barrioMissingHelp}</p>}
        {fitsButShort && <p className={styles.fitsButShort}>{fitsButShort}</p>}
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
            {topRows(rows).map((row) => {
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
                    {inGroup(row) && <small title={GROUP.help}>{GROUP.label}</small>}
                  </span>
                  {notComparable(row) ? <SmallZoneTag /> : <GapBadge status={row.status} />}
                </li>
              );
            })}
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
