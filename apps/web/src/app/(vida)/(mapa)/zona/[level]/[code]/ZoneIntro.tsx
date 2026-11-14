"use client";

import { ChevronRight } from "lucide-react";
import Link from "next/link";

import { useMapZones } from "@/components/map/MapProvider";
import ZoneListLink from "@/components/map/ZoneListLink";
import DataCounter from "@/components/provenance/DataCounter";
import SearchCard from "@/components/search/SearchCard";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import BarrioFit from "@/components/zone/BarrioFit";
import BarriosBar from "@/components/zone/BarriosBar";
import FacilitiesPanel from "@/components/zone/FacilitiesPanel";
import PerceivedSafety from "@/components/zone/PerceivedSafety";
import ZoneCard from "@/components/zone/ZoneCard";
import ZoneContext from "@/components/zone/ZoneContext";
import { errorMessage } from "@/lib/errors";

import styles from "./zone.module.css";

// Copy from pitch/textos_web.md (migas.*, mapa.volver, carga.zona, error.zona_no_existe).
const TEXT = {
  region: "Comunidad de Madrid",
  back: "Volver al mapa de la región",
  loading: "Preparando la zona…",
  notFound: "No encontramos esa zona. Elige otra en el mapa.",
  retry: "Reintentar",
  lead: "Mira sus servicios y puntos clave, con datos oficiales.",
};

export default function ZoneIntro() {
  // The zone by name from its small «Qué falta» answer: the screen does not wait for the outlines
  const { status, error, retry, routeZone } = useMapZones();
  const slow = useSlow(status === "loading");

  if (!routeZone) {
    if (status === "loading") {
      return (
        <GlassCard className={styles.state} role="status">
          <p>
            {TEXT.loading}
            {slow && ` ${SLOW_TEXT}`}
          </p>
        </GlassCard>
      );
    }
    // The zones could not be loaded (error) or this one does not exist (ready)
    return (
      <GlassCard className={styles.state} role="alert">
        <p>{error ? errorMessage(error) : TEXT.notFound}</p>
        {error ? (
          <Button variant="secondary" onClick={retry}>
            {TEXT.retry}
          </Button>
        ) : (
          <Button href="/">{TEXT.back}</Button>
        )}
        <ZoneListLink />
      </GlassCard>
    );
  }

  const { name, level, municipio_name } = routeZone;
  const parent = level === "distrito" ? municipio_name : TEXT.region;
  return (
    <div className={styles.layout}>
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
      {/* What the zone is missing comes before the search: first on mobile, right column on desktop */}
      <div className={styles.side}>
        <ZoneCard zone={routeZone} mode="zone" />
        {/* After a search, the district's barrios that fit it (D-232): under the card, so arriving later moves nothing above */}
        <BarrioFit zone={routeZone} />
        <DataCounter />
        <ZoneListLink />
        {/* Context only for Madrid's districts, the survey's coverage (D-226 §1); last, so arriving later moves nothing */}
        {level === "distrito" && <PerceivedSafety districtCode={routeZone.code} />}
        {/* Context that never scores (D-235): offences, age of the dwellings and income, next to the neighbours' view */}
        <ZoneContext zone={routeZone} />
      </div>
      {/* Every facility of the zone, not only its key points: left column on desktop */}
      <div className={styles.centres}>
        <FacilitiesPanel zone={name} />
      </div>
      <div className={styles.search}>
        <SearchCard collapsible />
      </div>
      <BarriosBar />
    </div>
  );
}
