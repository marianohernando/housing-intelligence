"use client";

import { ExternalLink, Footprints } from "lucide-react";
import { useState } from "react";

import type { GapRow } from "@/contracts/zone_gap_list_response";
import { confidenceText } from "@/lib/confidence";
import { GAP_STATUS, gapFigures, isSmallZone, NULL_REASON, ROW_MEASURE, SMALL_ZONE, walking, walkingText, WALK_TO } from "@/lib/gaps";
import { datasetLines, sortDatasets } from "@/lib/provenance";

import GapBadge from "./GapBadge";
import SmallZoneTag from "./SmallZoneTag";
import styles from "./GapRowItem.module.css";

// Copy from pitch/textos_web.md (falta.fila.*, confianza.aria, estado.sin_datos).
const TEXT = {
  noData: "Sin datos",
  regional: "En toda la Comunidad de Madrid:", // falta.fila.region (gap-0.2 context)
  walk: "A pie hasta",
  note: "Ojo:",
  sources: "De dónde sale:", // falta.fila.fuente, with the number of datasets
  confidence: "Fiabilidad del dato: ",
};

/** Sources start open on desktop, where they fit; on a phone they are one tap away. */
function wideScreen(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(min-width: 1101px)").matches;
}

function sourcesCount(n: number): string {
  return n === 1 ? "1 conjunto de datos" : `${n} conjuntos de datos`;
}

function WalkingFigure({ row }: { row: GapRow }) {
  const extra = walking(row.extra_indicators);
  if (!extra) return null;
  const to = WALK_TO[row.row];
  return (
    <div className={styles.walk}>
      <dt>
        <Footprints size={16} aria-hidden="true" /> {to ? `${TEXT.walk} ${to}` : extra.label}
      </dt>
      <dd>
        {walkingText(extra)}
        {extra.value === null && <span className="visually-hidden"> ({NULL_REASON[extra.null_reason ?? "UNKNOWN"]})</span>}
      </dd>
    </div>
  );
}

/** Why the row shows as it does when it is not a plain status: no value, or too small to tell. */
function reasonOf(row: GapRow): string | null {
  if (row.indicator.value === null) return NULL_REASON[row.indicator.null_reason ?? "UNKNOWN"];
  if (row.status === "SIN_DATOS") return GAP_STATUS.SIN_DATOS.help;
  if (isSmallZone(row)) return SMALL_ZONE.help;
  return null;
}

/**
 * One row of «Qué falta»: status (with «Zona pequeña para comparar»), value against the zones of the same type and
 * the whole region, walking minutes, confidence and sources.
 */
export default function GapRowItem({ row, zoneName }: { row: GapRow; zoneName: string }) {
  const figures = gapFigures(row.indicator.value, row.reference, row.regional_reference ?? null);
  const reason = reasonOf(row);
  const confidence = confidenceText(row.indicator.confidence);
  // Fixed once, so a resize never closes what the person opened
  const [sourcesOpen] = useState(wideScreen);

  return (
    <li className={`glass ${styles.row}`}>
      <div className={styles.head}>
        <h2>{row.label}</h2>
        <span className={styles.badges}>
          <GapBadge status={row.status} />
          {isSmallZone(row) && <SmallZoneTag />}
        </span>
      </div>
      <p className={styles.measure}>{ROW_MEASURE[row.row]}</p>

      <dl className={styles.figures}>
        <div className={styles.figure}>
          <dt>{zoneName}</dt>
          <dd className={row.indicator.value === null ? styles.missing : undefined}>{figures.value ?? TEXT.noData}</dd>
        </div>
        <div className={styles.figure}>
          <dt>{row.reference_label}</dt>
          <dd>{figures.reference ?? TEXT.noData}</dd>
        </div>
        {figures.regional && figures.regional !== figures.reference && (
          <div className={styles.regional}>
            <dt>{TEXT.regional}</dt>
            <dd>{figures.regional}</dd>
          </div>
        )}
        <WalkingFigure row={row} />
      </dl>

      {reason && <p className={styles.reason}>{reason}</p>}
      {row.indicator.value !== null && (
        <p className={styles.confidence} title={confidence.help}>
          <span className="visually-hidden">{TEXT.confidence}</span>
          {confidence.label}
          <span className="visually-hidden">. {confidence.help}</span>
        </p>
      )}
      {row.proxy_note && (
        <p className={styles.note}>
          <strong>{TEXT.note}</strong> {row.proxy_note}
        </p>
      )}

      <details className={styles.sources} open={sourcesOpen}>
        <summary>
          {TEXT.sources} {sourcesCount(row.datasets.length)}
        </summary>
        <ul>
          {sortDatasets(row.datasets).map((ref) => {
            const lines = datasetLines(ref);
            return (
              <li key={ref.dataset_id}>
                {lines.url ? (
                  <a href={lines.url} target="_blank" rel="noopener noreferrer">
                    {ref.name}
                    <span className="visually-hidden">, {lines.openHint}</span>
                    <ExternalLink size={14} aria-hidden="true" />
                  </a>
                ) : (
                  ref.name
                )}
              </li>
            );
          })}
        </ul>
      </details>
    </li>
  );
}
