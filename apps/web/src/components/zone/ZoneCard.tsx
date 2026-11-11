"use client";

import { ArrowRight, X } from "lucide-react";
import { useId } from "react";

import { useScenario } from "@/components/search/ScenarioProvider";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import { errorMessage } from "@/lib/errors";
import { rowsPending, topRows } from "@/lib/gaps";
import { type ZoneFeature, zoneHref } from "@/lib/map/zones";

import GapBadge from "./GapBadge";
import styles from "./ZoneCard.module.css";
import { useZoneGaps } from "./useZoneGaps";

// Copy from pitch/textos_web.md (zona.*, falta.*, carga.falta, error.reintentar, leyenda.antes_de_buscar)
const TEXT = {
  municipio: "Municipio",
  close: "Cerrar",
  beforeSearch: "Haz tu búsqueda para ver qué zonas encajan contigo.",
  missing: "Qué falta aquí",
  pending: "Estamos calculando el resto de servicios para esta zona.",
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
  const { result } = useScenario();
  const gaps = useZoneGaps(level, code);
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
      {!result && <p className={styles.hint}>{TEXT.beforeSearch}</p>}

      <section className={styles.missing} aria-labelledby={`${titleId}-missing`}>
        <h3 id={`${titleId}-missing`}>{TEXT.missing}</h3>
        {gaps.loading && (
          <p role="status" className={styles.hint}>
            Calculando qué falta en {name}…
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
            {topRows(gaps.data.data.rows).map((row) => (
              <li key={row.row}>
                <span>{row.label}</span>
                <GapBadge status={row.status} />
              </li>
            ))}
          </ul>
        )}
        {gaps.data && rowsPending(gaps.data.warnings) && <p className={styles.hint}>{TEXT.pending}</p>}
      </section>

      {mode === "overview" ? (
        <Button href={zoneHref(zone.properties)} className={styles.action}>
          {TEXT.open}
          <ArrowRight size={20} aria-hidden="true" />
        </Button>
      ) : (
        <Button href={`/que-falta?zona=${encodeURIComponent(`${level}/${code}`)}`} variant="secondary" className={styles.action}>
          {TEXT.all}
          <ArrowRight size={20} aria-hidden="true" />
        </Button>
      )}
    </GlassCard>
  );
}
