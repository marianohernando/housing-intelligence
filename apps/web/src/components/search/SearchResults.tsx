"use client";

import { ChevronDown, Undo2 } from "lucide-react";
import { type ReactNode, useEffect, useId, useRef, useState } from "react";

import type { RankedZone, SearchResult } from "@/contracts/search_response";
import { useMapZones } from "@/components/map/MapProvider";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { errorMessage } from "@/lib/errors";
import { constraintLabels, failedLabels, passingText, unknownText, zoneKeyOf, zonesText } from "@/lib/fit";
import { MOBILE_QUERY } from "@/lib/map/camera";

import RealityCheck from "./RealityCheck";
import styles from "./Results.module.css";
import { useScenario } from "./ScenarioProvider";

// Copy from pitch/textos_web.md (carga.busqueda, vacio.sin_resultados, rc.aplicado, rc.deshacer,
// zona.cerca_de_encajar.*, error.reintentar). The title, «De {n} zonas…», «Ver las {n} primeras»,
// «Y {n} más en el mapa» and the stale notice are provisional (pending line D).
const TEXT = {
  title: "Zonas que encajan",
  loading: "Buscando zonas que encajan…",
  none: "Ninguna zona cumple todo lo que pides. Mira abajo qué pasa si cambias algo.",
  of: (n: number) => `De ${n} zonas de la Comunidad de Madrid.`,
  applied: "Ahora ves las zonas con:",
  undo: "Volver a mi búsqueda",
  stale: "Has cambiado tu búsqueda. Pulsa «Ver zonas que encajan» para ponerla al día.",
  first: (n: number) => `Ver las ${n} primeras`,
  fewer: "Ver menos",
  rest: (n: number) => `Y ${zonesText(n)} más en el mapa.`,
  near: "Casi encajan",
  nearHelp: "Fallan en una sola cosa.",
  fails: "No cumple:",
  retry: "Reintentar",
  district: (city: string | null | undefined) => `Distrito de ${city ?? "Madrid"}`,
  municipio: "Municipio",
  fit: "de encaje",
};

/** Rows of the ranking in view before «Ver las 10 primeras». */
const FIRST_ROWS = 5;

function ZoneRow({ zone, fails }: { zone: RankedZone; fails?: string[] }) {
  const { select } = useMapZones();
  const { name, level, municipio_name } = zone.zone;
  return (
    <button type="button" className={styles.row} onClick={() => select(zoneKeyOf(zone.zone))}>
      {!fails && <span className={styles.rank}>{zone.rank}</span>}
      <span className={styles.rowName}>
        {name}
        <small>{fails ? `${TEXT.fails} ${fails.join(" · ")}` : level === "distrito" ? TEXT.district(municipio_name) : TEXT.municipio}</small>
      </span>
      <span className={styles.pct}>
        {zone.match_pct} %<span className="visually-hidden"> {TEXT.fit}</span>
      </span>
    </button>
  );
}

function Ranking({ result }: { result: SearchResult }) {
  const [all, setAll] = useState(false);
  const shown = all ? result.results : result.results.slice(0, FIRST_ROWS);
  const rest = result.reality_check.zones_passing - result.results.length;
  return (
    <>
      <ol className={styles.ranking}>
        {shown.map((zone) => (
          <li key={zoneKeyOf(zone.zone)}>
            <ZoneRow zone={zone} />
          </li>
        ))}
      </ol>
      {result.results.length > FIRST_ROWS && (
        <button type="button" className={styles.toggle} aria-expanded={all} onClick={() => setAll((v) => !v)}>
          {all ? TEXT.fewer : TEXT.first(result.results.length)}
          <ChevronDown size={18} aria-hidden="true" className={all ? styles.flip : undefined} />
        </button>
      )}
      {all && rest > 0 && <p className={styles.muted}>{TEXT.rest(rest)}</p>}
    </>
  );
}

function NearMisses({ result }: { result: SearchResult }) {
  const [open, setOpen] = useState(false);
  const nearId = useId();
  const near = result.near_misses ?? [];
  if (near.length === 0) return null;
  const labels = constraintLabels(result);
  return (
    <div className={styles.near}>
      <button type="button" className={styles.toggle} aria-expanded={open} aria-controls={nearId} onClick={() => setOpen((v) => !v)}>
        {TEXT.near} ({near.length})
        <ChevronDown size={18} aria-hidden="true" className={open ? styles.flip : undefined} />
      </button>
      <div id={nearId} hidden={!open}>
        <p className={styles.muted}>{TEXT.nearHelp}</p>
        <ul className={styles.ranking}>
          {near.map((zone) => (
            <li key={zoneKeyOf(zone.zone)}>
              <ZoneRow zone={zone} fails={failedLabels(zone.failed_constraints, labels)} />
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

/**
 * Right column of the overview once there is a search: the zones that fit (POST /search
 * `results`, best first), the near misses and «¿Y si cambias algo?». Before the first search it
 * shows `children` («Así funciona»).
 */
export default function SearchResults({ children }: { children: ReactNode }) {
  const { status, result, error, stale, applied, undoRelaxation, retry } = useScenario();
  const slow = useSlow(status === "loading");
  const titleId = useId();
  const ref = useRef<HTMLDivElement>(null);
  const title = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    if (!result) return;
    // Mobile: the results are down in the bottom sheet; bring them into view when they arrive.
    if (window.matchMedia(MOBILE_QUERY).matches) {
      const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      ref.current?.scrollIntoView({ block: "start", behavior: reduced ? "auto" : "smooth" });
    }
    // The button pressed may be gone with the old result (an option, «Volver a mi búsqueda»):
    // the focus goes to the new results instead of being lost.
    if (document.activeElement === document.body) title.current?.focus({ preventScroll: true });
  }, [result]);

  // One live region, always there, so screen readers hear each change of the search.
  const announce =
    status === "loading" ? TEXT.loading : status === "done" && result ? passingText(result.reality_check.zones_passing, applied !== null) : "";
  const live = (
    <p role="status" className="visually-hidden">
      {announce}
    </p>
  );

  if (status === "idle") {
    return (
      <>
        {live}
        {children}
      </>
    );
  }

  const loading = status === "loading" && (
    <p className={styles.muted}>
      {TEXT.loading}
      {slow && ` ${SLOW_TEXT}`}
    </p>
  );
  const failure = status === "error" && error && (
    <div role="alert" className={styles.error}>
      <p>{errorMessage(error)}</p>
      <Button variant="secondary" onClick={retry}>
        {TEXT.retry}
      </Button>
    </div>
  );
  const heading = (
    <h2 id={titleId} ref={title} tabIndex={-1} className={styles.heading}>
      {TEXT.title}
    </h2>
  );

  if (!result) {
    return (
      <div ref={ref}>
        {live}
        <GlassCard as="section" aria-labelledby={titleId} className={styles.card}>
          {heading}
          {loading}
          {failure}
        </GlassCard>
      </div>
    );
  }

  const rc = result.reality_check;
  return (
    <div ref={ref} className={styles.stack}>
      {live}
      <GlassCard as="section" aria-labelledby={titleId} className={styles.card}>
        {heading}
        {loading}
        {failure}
        {applied && (
          <div className={styles.applied}>
            <p>
              {TEXT.applied} <strong>{applied}</strong>
            </p>
            <Button
              variant="secondary"
              aria-disabled={status === "loading"}
              onClick={() => {
                if (status !== "loading") undoRelaxation();
              }}
            >
              <Undo2 size={18} aria-hidden="true" />
              {TEXT.undo}
            </Button>
          </div>
        )}
        {stale && status !== "loading" && <p className={styles.stale}>{TEXT.stale}</p>}
        <p className={styles.summary}>
          <strong>{passingText(rc.zones_passing, applied !== null)}</strong> {TEXT.of(rc.zones_evaluated)}
        </p>
        {rc.zones_passing === 0 && <p>{TEXT.none}</p>}
        {rc.zones_passing === 0 && rc.zones_unknown > 0 && <p className={styles.muted}>{unknownText(rc.zones_unknown)}</p>}
        {rc.zones_passing > 0 && <Ranking result={result} />}
        <NearMisses result={result} />
      </GlassCard>
      <RealityCheck result={result} />
    </div>
  );
}
