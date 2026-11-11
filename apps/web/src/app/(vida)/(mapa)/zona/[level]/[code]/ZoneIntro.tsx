"use client";

import { ChevronRight } from "lucide-react";
import Link from "next/link";

import { useMapZones } from "@/components/map/MapProvider";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";

import styles from "./zone.module.css";

// Copy from pitch/textos_web.md (migas.*, mapa.volver, carga.zona, error.zona_no_existe).
const TEXT = {
  region: "Comunidad de Madrid",
  back: "Volver al mapa de la región",
  loading: "Preparando la zona…",
  notFound: "No encontramos esa zona. Elige otra en el mapa.",
  lead: "Mira sus servicios y puntos clave, con datos oficiales.",
};

export default function ZoneIntro() {
  const { status, activeZone } = useMapZones();

  if (!activeZone) {
    const message = status === "loading" ? TEXT.loading : TEXT.notFound;
    return (
      <GlassCard className={styles.state} role={status === "loading" ? "status" : "alert"}>
        <p>{message}</p>
        {status !== "loading" && <Button href="/">{TEXT.back}</Button>}
      </GlassCard>
    );
  }

  const { name, level, municipio_name } = activeZone.properties;
  const parent = level === "distrito" ? municipio_name : TEXT.region;
  return (
    <div className={styles.page}>
      <nav aria-label="Estás en" className={`glass ${styles.crumbs}`}>
        <ol>
          <li>
            <Link href="/">{parent}</Link>
          </li>
          <li aria-hidden="true" className={styles.separator}>
            <ChevronRight size={16} />
          </li>
          <li aria-current="page">{name}</li>
        </ol>
      </nav>
      <h1 className={styles.title}>
        Explora <span className={styles.accent}>{name}</span>
      </h1>
      <p className={styles.lead}>{TEXT.lead}</p>
      <Button href="/" variant="secondary" className={styles.back}>
        {TEXT.back}
      </Button>
    </div>
  );
}
