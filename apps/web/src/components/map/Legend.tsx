"use client";

import Link from "next/link";
import { useId } from "react";

import { useScenario } from "@/components/search/ScenarioProvider";
import Button from "@/components/ui/Button";
import { errorMessage } from "@/lib/errors";
import { countFit, type FitClass, paintFit } from "@/lib/fit";
import { GAP_STATUS, ROW_NAME, SMALL_ZONE } from "@/lib/gaps";
import { countByStatus, isGapRow, type MapCategory, MAP_ROWS, paintZones } from "@/lib/map/gapMap";

import { useGapLayer } from "./GapLayerProvider";
import styles from "./Legend.module.css";
import { useMapZones } from "./MapProvider";

// Copy from pitch/textos_web.md (leyenda.*, 8c49e33).
const TEXT = {
  title: "Encaje con tu búsqueda",
  less: "Encaja menos",
  more: "Encaja más",
  noData: "Sin datos",
  before: "Haz tu búsqueda para ver qué zonas encajan contigo.",
  soon: "Muy pronto verás aquí qué zonas encajan contigo.", // leyenda.pronto
  show: "¿Qué quieres ver?",
  legend: "Leyenda del mapa",
  missing: "Qué falta",
  loading: "Cargando el mapa…",
  retry: "Reintentar",
  // leyenda against D-213, with the neighbours of gap-0.3 (leyenda.fila.frente)
  against: "frente a los municipios de su tipo (urbanos o rurales); los pueblos muy pequeños, junto con sus vecinos.",
  zones: (n: number) => (n === 1 ? "1 zona" : `${n} zonas`),
  pending: (n: number) => `${n === 1 ? "1 zona" : `${n} zonas`} sin calcular todavía.`,
  failedLevel: { municipio: "los municipios", distrito: "los distritos de Madrid" } as const,
  failed: (what: string) => `No hemos podido cargar ${what}: salen sin calcular.`,
  list: "Ver estas zonas en una lista",
  // After a search: leyenda.cumple, leyenda.no_cumple and leyenda.sin_datos
  fit: { ENCAJA: "Cumple todo", NO_CUMPLE: "No cumple todo", SIN_DATOS: "Sin datos" } satisfies Record<FitClass, string>,
};

const FIT_CLASSES: FitClass[] = ["ENCAJA", "NO_CUMPLE", "SIN_DATOS"];

const CATEGORIES: MapCategory[] = ["FALTA", "JUSTO", "CUBIERTO", "ZONA_PEQUENA", "SIN_DATOS"];
const categoryLabel = (c: MapCategory) => (c === "ZONA_PEQUENA" ? SMALL_ZONE.label : GAP_STATUS[c].label);

function FitLegend({ id }: { id: string }) {
  const { result, available } = useScenario();
  const { resultZones } = useMapZones();
  if (result && resultZones) {
    const counts = countFit(paintFit(resultZones, result.all_zones));
    return (
      <figure className={styles.figure} aria-labelledby={id}>
        <figcaption id={id} className={styles.title}>
          {TEXT.title}
        </figcaption>
        <div className={styles.ramp} aria-hidden="true" />
        <div className={`${styles.ends} ${styles.fitEnds}`}>
          <span>{TEXT.less}</span>
          <span>{TEXT.more}</span>
        </div>
        <ul className={`${styles.statuses} ${styles.fitClasses}`}>
          {FIT_CLASSES.map((c) => (
            <li key={c}>
              <span className={`${styles.patch} ${styles[`fit_${c}`]}`} aria-hidden="true" />
              <span className={styles.small}>{TEXT.fit[c]}</span>
              <span className={styles.count}>{TEXT.zones(counts[c])}</span>
            </li>
          ))}
        </ul>
      </figure>
    );
  }
  return (
    <figure className={`${styles.figure} ${result ? "" : styles.waiting}`} aria-labelledby={id}>
      <figcaption id={id} className={styles.title}>
        {TEXT.title}
      </figcaption>
      <div className={styles.ramp} aria-hidden="true" />
      <div className={styles.ends}>
        <span>{TEXT.less}</span>
        <span>{TEXT.more}</span>
      </div>
      <p className={styles.noData}>
        <span className={styles.swatch} aria-hidden="true" />
        {TEXT.noData}
      </p>
      {!result && <p className={styles.before}>{available ? TEXT.before : TEXT.soon}</p>}
    </figure>
  );
}

/** One row of «Qué falta» on the map: each status with its colour and pattern, and how many zones have it. */
function RowLegend({ id }: { id: string }) {
  const { row, loading, data, error, retry } = useGapLayer();
  const { zones } = useMapZones();
  if (loading || !row) return <p role="status">{TEXT.loading}</p>;
  if (error || !data) {
    return (
      <div role="alert" className={styles.error}>
        <p>{error ? errorMessage(error) : TEXT.loading}</p>
        <Button variant="secondary" onClick={retry}>
          {TEXT.retry}
        </Button>
      </div>
    );
  }
  const counts = zones ? countByStatus(paintZones(zones, data.byZone)) : null;
  return (
    <figure className={styles.figure} aria-labelledby={id}>
      <figcaption id={id} className={styles.rowTitle}>
        <strong>{data.info.indicator_label}</strong>, {TEXT.against}
      </figcaption>
      <ul className={styles.statuses}>
        {CATEGORIES.map((status) => (
          <li key={status}>
            <span className={`${styles.patch} ${styles[status]}`} aria-hidden="true" />
            <span className={status === "ZONA_PEQUENA" ? styles.small : styles.status}>{categoryLabel(status)}</span>
            {counts && <span className={styles.count}>{TEXT.zones(counts[status])}</span>}
          </li>
        ))}
      </ul>
      {counts && counts.pending > 0 && <p className={styles.before}>{TEXT.pending(counts.pending)}</p>}
      {data.failed.length > 0 && (
        <div role="alert" className={styles.error}>
          <p>{TEXT.failed(data.failed.map((level) => TEXT.failedLevel[level]).join(" y "))}</p>
          <Button variant="secondary" onClick={retry}>
            {TEXT.retry}
          </Button>
        </div>
      )}
      <Link href={`/zonas?fila=${row}`} className={styles.list}>
        {TEXT.list}
      </Link>
    </figure>
  );
}

/**
 * «¿Qué quieres ver?»: the fit with the search (violet ramp, «Sin datos» never 0) or one row of
 * «Qué falta» by zone. A native select, so it works with the keyboard and screen readers.
 */
export default function Legend() {
  const { row, setRow } = useGapLayer();
  const selectId = useId();
  const titleId = useId();
  return (
    <section className={`glass ${styles.legend}`} aria-label={TEXT.legend}>
      <div className={styles.picker}>
        <label htmlFor={selectId} className={styles.pickerLabel}>
          {TEXT.show}
        </label>
        <select id={selectId} className={styles.select} value={row ?? ""} onChange={(e) => setRow(isGapRow(e.target.value) ? e.target.value : null)}>
          <option value="">{TEXT.title}</option>
          <optgroup label={TEXT.missing}>
            {MAP_ROWS.map((key) => (
              <option key={key} value={key}>
                {ROW_NAME[key]}
              </option>
            ))}
          </optgroup>
        </select>
      </div>
      <div aria-live="polite">{row ? <RowLegend id={titleId} /> : <FitLegend id={titleId} />}</div>
    </section>
  );
}
