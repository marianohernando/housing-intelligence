import { ExternalLink, Footprints } from "lucide-react";

import type { GapRow } from "@/contracts/zone_gap_list_response";
import { confidenceText } from "@/lib/confidence";
import { gapFigures, NULL_REASON, ROW_MEASURE, walking, walkingText, WALK_TO } from "@/lib/gaps";
import { datasetLines, sortDatasets } from "@/lib/provenance";

import GapBadge from "./GapBadge";
import styles from "./GapRowItem.module.css";

// Copy from pitch/textos_web.md (falta.fila.*, confianza.aria, estado.sin_datos).
const TEXT = {
  noData: "Sin datos",
  walk: "A pie hasta",
  note: "Ojo:",
  sources: "De dónde sale:", // falta.fila.fuente; the count is provisional (pending line D)
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
      <dd title={extra.value === null && extra.null_reason ? NULL_REASON[extra.null_reason] : undefined}>{walkingText(extra)}</dd>
    </div>
  );
}

/** One row of «Qué falta»: status, value against the region, walking minutes, confidence and sources. */
export default function GapRowItem({ row, zoneName }: { row: GapRow; zoneName: string }) {
  const figures = gapFigures(row.indicator.value, row.reference);
  const reason = row.indicator.value === null ? row.indicator.null_reason : null;
  const confidence = confidenceText(row.indicator.confidence);

  return (
    <li className={`glass ${styles.row}`}>
      <div className={styles.head}>
        <h3>{row.label}</h3>
        <GapBadge status={row.status} />
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
        <WalkingFigure row={row} />
      </dl>

      {reason && <p className={styles.reason}>{NULL_REASON[reason]}</p>}
      {row.indicator.value !== null && (
        <p className={styles.confidence} title={confidence.help}>
          <span className="visually-hidden">{TEXT.confidence}</span>
          {confidence.label}
        </p>
      )}
      {row.proxy_note && (
        <p className={styles.note}>
          <strong>{TEXT.note}</strong> {row.proxy_note}
        </p>
      )}

      <details className={styles.sources} open={wideScreen()}>
        <summary>
          {TEXT.sources} {sourcesCount(row.datasets.length)}
        </summary>
        <ul>
          {sortDatasets(row.datasets).map((ref) => {
            const lines = datasetLines(ref);
            return (
              <li key={ref.dataset_id}>
                {lines.url ? (
                  <a href={lines.url} target="_blank" rel="noopener noreferrer" aria-label={lines.openLabel}>
                    {ref.name}
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
