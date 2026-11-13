"use client";

import { ExternalLink, Footprints, Hospital } from "lucide-react";
import { useState } from "react";

import type { GapRow, IndicatorValue } from "@/contracts/zone_gap_list_response";
import { confidenceText } from "@/lib/confidence";
import {
  GAP_STATUS,
  gapFigures,
  groupText,
  HOSPITAL_WALK,
  hospitalText,
  hospitalWalking,
  inGroup,
  NULL_REASON,
  notComparable,
  peopleAffectedText,
  referenceLabel,
  ROW_MEASURE,
  rowComparison,
  SMALL_ZONE,
  walking,
  walkingText,
  WALK_TO,
} from "@/lib/gaps";
import { datasetLines, sortDatasets } from "@/lib/provenance";

import GapBadge from "./GapBadge";
import GroupTag from "./GroupTag";
import SmallZoneTag from "./SmallZoneTag";
import styles from "./GapRowItem.module.css";

// Copy from pitch/textos_web.md (falta.fila.*, hospital.*, confianza.aria, estado.sin_datos).
const TEXT = {
  noData: "Sin datos",
  regional: "En toda la Comunidad de Madrid:", // falta.fila.region (gap-0.2 context)
  walk: "A pie hasta",
  figure: "Ver la cifra", // falta.fila.ver_cifra
  note: "Ojo:",
  hospital: "El hospital:", // hospital.titulo
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

interface WalkingProps {
  extra: IndicatorValue | undefined;
  label: string;
  text: (extra: IndicatorValue) => string;
  hospital?: boolean;
}

function WalkingFigure({ extra, label, text, hospital = false }: WalkingProps) {
  if (!extra) return null;
  const Icon = hospital ? Hospital : Footprints;
  return (
    <div className={styles.walk}>
      <dt>
        <Icon size={16} aria-hidden="true" /> {label}
      </dt>
      <dd>
        {text(extra)}
        {extra.value === null && <span className="visually-hidden"> ({NULL_REASON[extra.null_reason ?? "UNKNOWN"]})</span>}
      </dd>
    </div>
  );
}

/**
 * Why the row shows as it does when it is not a plain status: no value, or too small to tell. The
 * API's `explanation` gives the real reason when nobody of the row's age lives there
 * (NOT_APPLICABLE) and when the zone is not comparable (D-230); our own words otherwise.
 */
function reasonOf(row: GapRow): string | null {
  if (row.indicator.null_reason === "NOT_APPLICABLE" && row.explanation) return row.explanation;
  if (row.indicator.value === null) return NULL_REASON[row.indicator.null_reason ?? "UNKNOWN"];
  if (row.status === "SIN_DATOS") return GAP_STATUS.SIN_DATOS.help;
  if (notComparable(row)) return row.explanation.startsWith("No comparable") ? row.explanation : SMALL_ZONE.help;
  return null;
}

/** The technical figure behind «Ver la cifra»: what the row measures, the zone against its reference and the region. */
function TechnicalFigure({ row, zoneName, zoneLevel }: { row: GapRow; zoneName: string; zoneLevel: string }) {
  const figures = gapFigures(row.indicator.value, row.reference, row.regional_reference ?? null);
  return (
    <details className={styles.technical}>
      <summary>{TEXT.figure}</summary>
      <p className={styles.measure}>{ROW_MEASURE[row.row]}</p>
      <dl className={styles.figures}>
        <div className={styles.figure}>
          <dt>{zoneName}</dt>
          <dd className={row.indicator.value === null ? styles.missing : undefined}>{figures.value ?? TEXT.noData}</dd>
        </div>
        <div className={styles.figure}>
          <dt>{referenceLabel(row.reference_label, zoneLevel)}</dt>
          <dd>{figures.reference ?? TEXT.noData}</dd>
        </div>
        {figures.regional && figures.regional !== figures.reference && (
          <div className={styles.regional}>
            <dt>{TEXT.regional}</dt>
            <dd>{figures.regional}</dd>
          </div>
        )}
      </dl>
    </details>
  );
}

interface Props {
  row: GapRow;
  zoneName: string;
  /** municipio or distrito: a district is compared with the other urban municipios, without Madrid */
  zoneLevel: string;
}

/**
 * One row of «Qué falta»: status (with «Zona pequeña para comparar»), «Aquí hay n por cada 100 que
 * hay en municipios parecidos», the people a FALTA leaves short, walking minutes, confidence, the
 * technical figure behind «Ver la cifra» and sources.
 */
export default function GapRowItem({ row, zoneName, zoneLevel }: Props) {
  const reason = reasonOf(row);
  const confidence = confidenceText(row.indicator.confidence);
  const group = inGroup(row);
  const hospital = hospitalWalking(row.extra_indicators);
  const comparison = rowComparison(row);
  const affected = peopleAffectedText(row);
  const walk = walking(row.extra_indicators, row.row);
  const walkTo = WALK_TO[row.row];
  // Fixed once, so a resize never closes what the person opened
  const [sourcesOpen] = useState(wideScreen);

  return (
    <li className={`glass ${styles.row}`}>
      <div className={styles.head}>
        <h2>{row.label}</h2>
        <span className={styles.badges}>
          {notComparable(row) ? <SmallZoneTag /> : <GapBadge status={row.status} />}
          {group && <GroupTag described={false} />}
        </span>
      </div>
      {comparison && <p className={styles.comparison}>{comparison}</p>}
      {affected && <p className={styles.affected}>{affected}</p>}
      {group && <p className={styles.group}>{groupText(zoneName, group)}</p>}

      {(walk || hospital) && (
        <dl className={styles.walking}>
          <WalkingFigure extra={walk} label={walkTo ? `${TEXT.walk} ${walkTo}` : (walk?.label ?? "")} text={walkingText} />
          <WalkingFigure extra={hospital} label={HOSPITAL_WALK.label} text={hospitalText} hospital />
        </dl>
      )}

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
      {hospital && (
        <p className={styles.note}>
          <strong>{TEXT.hospital}</strong> {HOSPITAL_WALK.note}
        </p>
      )}

      <TechnicalFigure row={row} zoneName={zoneName} zoneLevel={zoneLevel} />

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
