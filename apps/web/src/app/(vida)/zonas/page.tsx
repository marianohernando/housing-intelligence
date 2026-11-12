import type { Metadata } from "next";

import SiteFooter from "@/components/shell/SiteFooter";
import GlassCard from "@/components/ui/GlassCard";
import ZoneDirectory from "@/components/zone/ZoneDirectory";
import { ROW_NAME } from "@/lib/gaps";
import { isGapRow } from "@/lib/map/gapMap";

import styles from "../section.module.css";

export const metadata: Metadata = { title: "Zonas" };

// zonas.fila.intro of pitch/textos_web.md (D-213), with the neighbours of gap-0.3 (provisional, listed for line D)
const rowIntro = (name: string) =>
  `Con su estado en ${name.toLowerCase()} frente a los municipios de su tipo: FALTA, JUSTO, CUBIERTO o SIN DATOS. Los pueblos muy pequeños se comparan junto con sus vecinos.`;

/**
 * The zones in a list (pitch/textos_web.md, mapa.alternativa): the same zones as the map, without
 * it. With ?fila=<row>, the same row of «Qué falta» the map is coloured by.
 */
export default async function ZonasPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const { fila } = await searchParams;
  const row = isGapRow(fila) ? fila : null;
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Todas las zonas</h1>
      {row && <p className={styles.para}>{rowIntro(ROW_NAME[row])}</p>}
      <GlassCard className={styles.card}>
        <ZoneDirectory row={row} wholeCities />
      </GlassCard>
      <SiteFooter />
    </div>
  );
}
