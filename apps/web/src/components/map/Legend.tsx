"use client";

import { useScenario } from "@/components/search/ScenarioProvider";

import styles from "./Legend.module.css";

// Copy from pitch/textos_web.md (leyenda.*)
const TEXT = {
  title: "Encaje con tu búsqueda",
  less: "Encaja menos",
  more: "Encaja más",
  noData: "Sin datos",
  before: "Haz tu búsqueda para ver qué zonas encajan contigo.",
};

/** «Encaje con tu búsqueda»: violet ramp, plus «Sin datos» (unknown is never 0). */
export default function Legend() {
  const { result } = useScenario();
  return (
    <figure className={`glass ${styles.legend}`} aria-labelledby="leyenda-titulo">
      <figcaption id="leyenda-titulo" className={styles.title}>
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
      {!result && <p className={styles.before}>{TEXT.before}</p>}
    </figure>
  );
}
