"use client";

import { ArrowRight, X } from "lucide-react";
import Link from "next/link";
import { useId } from "react";

import { useScenario } from "@/components/search/ScenarioProvider";
import Button from "@/components/ui/Button";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import GlassCard from "@/components/ui/GlassCard";
import { errorMessage } from "@/lib/errors";
import { gapsHref, isSmallZone, SMALL_ZONE, topRows, walking, walkingText } from "@/lib/gaps";
import { type ZoneFeature, zoneHref } from "@/lib/map/zones";

import GapBadge from "./GapBadge";
import PendingRows from "./PendingRows";
import styles from "./ZoneCard.module.css";
import { useZoneGaps } from "./useZoneGaps";

// Copy from pitch/textos_web.md (zona.*, falta.*, carga.falta, error.reintentar, leyenda.antes_de_buscar)
// «A pie» with the minutes is falta.fila.a_pie, shortened for the card.
const TEXT = {
  municipio: "Municipio",
  close: "Cerrar",
  beforeSearch: "Haz tu búsqueda para ver qué zonas encajan contigo.",
  fitSoon: "Muy pronto verás cuánto encaja esta zona contigo.", // zona.encaje.pronto
  missing: "Qué falta aquí",
  walk: "A pie:",
  retry: "Reintentar",
  open: "Ver la zona",
  all: "Ver todo lo que falta",
};

interface Props {
  zone: ZoneFeature;
  /** Overview: from the map, with «Ver la zona». Zone: on its own screen, with the full list link. */
  mode: "overview" | "zone";
  onClose?: () => void;
}

/** Zone card of the mockups: name, % of fit once there is a search, and «Qué falta aquí». */
export default function ZoneCard({ zone, mode, onClose }: Props) {
  const { level, code, name, municipio_name } = zone.properties;
  const titleId = useId();
  const { result, available } = useScenario();
  const gaps = useZoneGaps(level, code);
  const slow = useSlow(gaps.loading);
  const match = result?.all_zones.find((z) => z.zone.level === level && z.zone.code === code);
  const pct = match?.match_pct;

  return (
    <GlassCard as="aside" aria-labelledby={titleId} className={styles.card}>
      <div className={styles.head}>
        <p className={styles.eyebrow}>{level === "distrito" ? `Distrito de ${municipio_name}` : TEXT.municipio}</p>
        {onClose && (
          <button type="button" className={styles.close} aria-label={TEXT.close} onClick={onClose}>
            <X size={20} aria-hidden="true" />
          </button>
        )}
      </div>
      <div className={styles.titleRow}>
        <h2 id={titleId} className={styles.name}>
          {name}
        </h2>
        {pct != null && (
          <span className={styles.pct} aria-label={`Esta zona encaja en un ${pct} % con tu búsqueda`}>
            {pct} %<small> de encaje</small>
          </span>
        )}
      </div>
      {!result && <p className={styles.hint}>{available ? TEXT.beforeSearch : TEXT.fitSoon}</p>}

      <section className={styles.missing} aria-labelledby={`${titleId}-missing`}>
        <h3 id={`${titleId}-missing`}>{TEXT.missing}</h3>
        {gaps.loading && (
          <p role="status" className={styles.hint}>
            Calculando qué falta en {name}…{slow && ` ${SLOW_TEXT}`}
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
            {topRows(gaps.data.data.rows).map((row) => {
              const walk = walking(row.extra_indicators);
              return (
                <li key={row.row}>
                  <span className={styles.rowName}>
                    {row.label}
                    {walk && (
                      <small>
                        {TEXT.walk} {walkingText(walk)}
                      </small>
                    )}
                    {isSmallZone(row) && <small title={SMALL_ZONE.help}>{SMALL_ZONE.label}</small>}
                  </span>
                  <GapBadge status={row.status} />
                </li>
              );
            })}
          </ul>
        )}
        {gaps.data && <PendingRows warnings={gaps.data.warnings} className={styles.pending} />}
        {gaps.data && mode === "overview" && (
          <Link href={gapsHref(level, code)} className={styles.all}>
            {TEXT.all}
          </Link>
        )}
      </section>

      {mode === "overview" ? (
        <Button href={zoneHref(zone.properties)} className={styles.action}>
          {TEXT.open}
          <ArrowRight size={20} aria-hidden="true" />
        </Button>
      ) : (
        <Button href={gapsHref(level, code)} variant="secondary" className={styles.action}>
          {TEXT.all}
          <ArrowRight size={20} aria-hidden="true" />
        </Button>
      )}
    </GlassCard>
  );
}
