import type { Metadata } from "next";

import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";

import styles from "../section.module.css";

export const metadata: Metadata = { title: "Qué falta" };

export default function QueFaltaPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Qué falta</h1>
      <GlassCard as="section" aria-labelledby="sin-zona" className={styles.card}>
        <h2 id="sin-zona">Todavía no has elegido una zona</h2>
        <p className={styles.text}>
          Elige una zona en el mapa para ver qué le falta: colegios, centros de salud y otros servicios
          del día a día, comparados con el conjunto de la Comunidad de Madrid.
        </p>
        <Button href="/">Ir al mapa</Button>
      </GlassCard>
    </div>
  );
}
