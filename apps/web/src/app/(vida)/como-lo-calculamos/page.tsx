import type { Metadata } from "next";

import GlassCard from "@/components/ui/GlassCard";

import styles from "../section.module.css";

export const metadata: Metadata = { title: "Cómo lo calculamos" };

export default function ComoLoCalculamosPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Cómo lo calculamos</h1>
      <GlassCard as="section" aria-labelledby="principios" className={styles.card}>
        <h2 id="principios">Tres reglas que seguimos siempre</h2>
        <ul className={styles.text}>
          <li>Comparamos cada zona con el conjunto de la Comunidad de Madrid, siempre según cuánta gente vive en ella.</li>
          <li>Si un dato no existe, lo decimos: «sin datos» no es lo mismo que cero.</li>
          <li>Cada dato dice de dónde sale y cuánto podemos fiarnos de él.</li>
        </ul>
      </GlassCard>
    </div>
  );
}
