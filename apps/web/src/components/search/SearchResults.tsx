"use client";

import { ChevronDown, Equal, Undo2 } from "lucide-react";
import { type ReactNode, useEffect, useId, useRef, useState } from "react";

import type { RankedZone, SearchResult } from "@/contracts/search_response";
import { useMapZones } from "@/components/map/MapProvider";
import { useDatasets } from "@/components/provenance/useDatasets";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import PriceTag from "@/components/ui/PriceTag";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { errorMessage } from "@/lib/errors";
import {
  asksForPlace,
  constraintLabels,
  evaluatedText,
  FIELD_ID,
  floorAreaOf,
  noneText,
  passingText,
  rentNotice,
  rentReferenceAvailable,
  rentUnknownText,
  tiedText,
  unknownText,
  zoneKeyOf,
  zonePrice,
  zonesText,
  zonesWithoutPrice,
  type ZoneWord,
  zoneWord,
} from "@/lib/fit";
import { MOBILE_QUERY } from "@/lib/map/camera";
import { districtOf, zoneTitle } from "@/lib/map/zones";
import { matchText, rankingRows, tiedNames } from "@/lib/match";
import { nearMissText, type Spoken } from "@/lib/shortfall";

import RealityCheck from "./RealityCheck";
import styles from "./Results.module.css";
import { useScenario } from "./ScenarioProvider";

// Copy from pitch/textos_web.md (resultados.*, with resultados.empate, resultados.aviso_2024 and resultados.sin_lugar in
// lib/fit.ts, resultados.banda.* and resultados.empate.grupo in lib/match.ts, resultados.casi.* in lib/shortfall.ts,
// carga.busqueda, vacio.sin_resultados, rc.aplicado, rc.deshacer, zona.cerca_de_encajar.*, error.reintentar; 8c49e33).
const TEXT = {
  title: "Zonas que encajan",
  loading: "Buscando zonas que encajan…",
  applied: "Ahora ves las zonas con:",
  undo: "Volver a mi búsqueda",
  stale: "Has cambiado tu búsqueda. Pulsa «Ver zonas que encajan» para ponerla al día.",
  first: (n: number) => `Ver las ${n} primeras`,
  fewer: "Ver menos",
  rest: (n: number, word: ZoneWord) => `Y ${zonesText(n, word)} más en el mapa.`,
  near: "Casi encajan",
  nearHelp: "Cumplen todo menos una cosa.",
  retry: "Reintentar",
  district: (city: string | null | undefined) => `Distrito de ${city ?? "Madrid"}`,
  // zona.barrio.antetitulo (D-238)
  barrio: (city: string | null | undefined) => `Barrio de ${city ?? "Madrid"}`,
  municipio: "Municipio",
  fit: "de encaje",
  // zona.empate, read after the % of a tied row
  tiesWith: (whom: string) => `empata con ${whom}`,
  // resultados.sin_lugar: the two buttons take the person to «Trabajo en» and to «¿Dónde?»
  place: {
    ask: "¿Trabajas fuera de casa?",
    work: "Dinos dónde",
    or: " o elige «Madrid capital» en ",
    where: "«¿Dónde?»",
    end: " y afinamos el orden.",
  },
};

/** Rows of the ranking in view before «Ver las 10 primeras». */
const FIRST_ROWS = 5;

function levelText({ level, municipio_name }: RankedZone["zone"]): string {
  if (level === "barrio") return TEXT.barrio(municipio_name);
  return level === "distrito" ? TEXT.district(municipio_name) : TEXT.municipio;
}

interface RowProps {
  zone: RankedZone;
  buying: boolean;
  m2: number | null;
  /** A near miss: what it lacks instead of its % (resultados.casi.*) */
  lacks?: Spoken;
  /** Read after its %: whom it ties with (`tiedNames`), for those who do not see the run's mark */
  tie?: string | null;
}

function ZoneRow({ zone, buying, m2, lacks, tie }: RowProps) {
  const { select, zones } = useMapZones();
  const { name, level, code } = zone.zone;
  // «Berruguete · Tetuán»: a barrio's district comes from the start of its code (D-238)
  const district = level === "barrio" && zones ? districtOf(zones, code) : undefined;
  const price = zonePrice(zone, buying, m2);
  const fit = lacks ? null : matchText(zone);
  return (
    <button type="button" className={styles.row} onClick={() => select(zoneKeyOf(zone.zone))}>
      {!lacks && <span className={styles.rank}>{zone.rank}</span>}
      <span className={styles.rowName}>
        {zoneTitle({ name, district_name: district?.name })}
        {lacks ? (
          <small className={styles.lacks}>
            <span aria-hidden="true">{lacks.text}</span>
            <span className="visually-hidden">{lacks.aria}</span>
          </small>
        ) : (
          <small>{levelText(zone.zone)}</small>
        )}
      </span>
      {/* The price under the %, not beside it: at 390 px the name keeps its width (D-234) */}
      <span className={styles.end}>
        {fit && (
          <span className={styles.pct}>
            <small className={styles.band}>{fit.band}</small>
            <span aria-hidden="true">{fit.pct}</span>
            <span className="visually-hidden">
              {` · ${fit.pct} ${TEXT.fit}`}
              {tie && `, ${TEXT.tiesWith(tie)}`}
            </span>
          </span>
        )}
        {price && <PriceTag price={price} variant="row" />}
      </span>
    </button>
  );
}

function Ranking({ result }: { result: SearchResult }) {
  const [all, setAll] = useState(false);
  const shown = all ? result.results : result.results.slice(0, FIRST_ROWS);
  const rest = result.reality_check.zones_passing - result.results.length;
  const tied = tiedText(result);
  const word = zoneWord(result);
  return (
    <>
      {tied && <p className={styles.muted}>{tied}</p>}
      <ol className={styles.ranking}>
        {rankingRows(shown, result.all_zones, word).map(({ zone, tie }) => (
          <li
            key={zoneKeyOf(zone.zone)}
            className={tie ? [styles.tied, tie.first && styles.tieFirst, tie.last && styles.tieLast].filter(Boolean).join(" ") : undefined}
          >
            {/* Seen once over the run; each of its rows says it aloud with whom it ties */}
            {tie?.first && (
              <p className={styles.tie} aria-hidden="true">
                <Equal size={16} />
                {tie.label}
              </p>
            )}
            <ZoneRow
              zone={zone}
              buying={result.scenario.budget?.kind === "buy"}
              m2={floorAreaOf(result)}
              tie={tiedNames(zone, result.all_zones, word)}
            />
          </li>
        ))}
      </ol>
      {result.results.length > FIRST_ROWS && (
        <button type="button" className={styles.toggle} aria-expanded={all} onClick={() => setAll((v) => !v)}>
          {all ? TEXT.fewer : TEXT.first(result.results.length)}
          <ChevronDown size={18} aria-hidden="true" className={all ? styles.flip : undefined} />
        </button>
      )}
      {all && rest > 0 && <p className={styles.muted}>{TEXT.rest(rest, zoneWord(result))}</p>}
    </>
  );
}

function NearMisses({ result }: { result: SearchResult }) {
  const [open, setOpen] = useState(false);
  const nearId = useId();
  const near = result.near_misses ?? [];
  if (near.length === 0) return null;
  const labels = constraintLabels(result);
  // F5 of fit-0.9: no % here, what each one lacks («Se pasa ≈ 11.000 € de tu presupuesto»)
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
              <ZoneRow
                zone={zone}
                buying={result.scenario.budget?.kind === "buy"}
                m2={floorAreaOf(result)}
                lacks={nearMissText(zone, labels, result.scenario)}
              />
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

/** Takes the person to a field of «Tu búsqueda» (FIELD_ID) and puts the focus in it, as a skip link does. */
function focusField(id: string) {
  const field = document.getElementById(id);
  if (!field) return;
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  field.scrollIntoView({ block: "center", behavior: reduced ? "auto" : "smooth" });
  field.querySelector<HTMLElement>("input:checked, input, select, button")?.focus({ preventScroll: true });
}

/** resultados.sin_lugar: no place to go and the whole region, with a way to each of the two fields. */
function PlaceHint() {
  return (
    <p className={styles.muted}>
      {TEXT.place.ask}{" "}
      <button type="button" className={styles.inline} onClick={() => focusField(FIELD_ID.work)}>
        {TEXT.place.work}
      </button>
      {TEXT.place.or}
      <button type="button" className={styles.inline} onClick={() => focusField(FIELD_ID.where)}>
        {TEXT.place.where}
      </button>
      {TEXT.place.end}
    </p>
  );
}

/**
 * Right column of the overview once there is a search: the zones that fit (POST /search
 * `results`, best first), the near misses and «¿Y si cambias algo?». Before the first search it
 * shows `children` («Así funciona»).
 */
export default function SearchResults({ children }: { children: ReactNode }) {
  const { status, result, error, stale, applied, undoRelaxation, retry } = useScenario();
  const { data: datasets } = useDatasets();
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
    status === "loading"
      ? TEXT.loading
      : status === "done" && result
        ? passingText(result.reality_check.zones_passing, applied !== null, zoneWord(result))
        : "";
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
  const word = zoneWord(result);
  const rentUnknown = rentUnknownText(result, rentReferenceAvailable(datasets?.datasets));
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
          <strong>{passingText(rc.zones_passing, applied !== null, word)}</strong> {evaluatedText(result)}
        </p>
        {rc.zones_passing === 0 && <p>{noneText(word)}</p>}
        {/* Renting in «Pueblos» most villages have no rent: why they come out «Sin datos» (D-238) */}
        {rentUnknown && <p className={styles.muted}>{rentUnknown}</p>}
        {!rentUnknown && rc.zones_passing === 0 && rc.zones_unknown > 0 && <p className={styles.muted}>{unknownText(rc.zones_unknown, word, zonesWithoutPrice(result))}</p>}
        {rentNotice(result) && <p className={styles.muted}>{rentNotice(result)}</p>}
        {asksForPlace(result) && <PlaceHint />}
        {rc.zones_passing > 0 && <Ranking result={result} />}
        <NearMisses result={result} />
      </GlassCard>
      <RealityCheck result={result} />
    </div>
  );
}
