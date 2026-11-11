import type { Metadata } from "next";

import SiteFooter from "@/components/shell/SiteFooter";
import GlassCard from "@/components/ui/GlassCard";
import ZoneDirectory from "@/components/zone/ZoneDirectory";

import styles from "../section.module.css";

export const metadata: Metadata = { title: "Zonas" };

/** The zones in a list (pitch/textos_web.md, mapa.alternativa): the same zones as the map, without it. */
export default function ZonasPage() {
  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Todas las zonas</h1>
      <GlassCard className={styles.card}>
        <ZoneDirectory />
      </GlassCard>
      <SiteFooter />
    </div>
  );
}
