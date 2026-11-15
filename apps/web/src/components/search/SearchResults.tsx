"use client";

import { ChevronDown, ChevronRight, Undo2 } from "lucide-react";
import { type ReactNode, useEffect, useId, useRef, useState } from "react";

import type { RankedZone, SearchResult } from "@/contracts/search_response";
import { useMapZones } from "@/components/map/MapProvider";
import { useDatasets } from "@/components/provenance/useDatasets";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import PriceTag from "@/components/ui/PriceTag";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { rowPlace } from "@/lib/essentials";
import { errorMessage } from "@/lib/errors";
import {
  asksForPlace,
  constraintLabels,
  evaluatedText,
  FIELD_ID,
  noneText,
  passingText,
  rentNotice,
  rentReferenceAvailable,
  rentUnknownText,
  resultsTitle,
  speaksToMany,
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
import { districtOf, type ZoneCollection, zoneTitle } from "@/lib/map/zones";
import { matchText, tiedNames } from "@/lib/match";
import { nearMissText, type Spoken } from "@/lib/shortfall";

import RealityCheck from "./RealityCheck";
import styles from "./Results.module.css";
import { useScenario } from "./ScenarioProvider";

// Copy from pitch/textos_web.md (resultados.*, with resultados.titulo, resultados.empate, resultados.aviso_2024 and resultados.sin_lugar in
// lib/fit.ts, resultados.banda.* in lib/match.ts, resultados.casi.* in lib/shortfall.ts, resultados.fila.lugar in
// lib/essentials.ts, carga.busqueda, vacio.sin_resultados, rc.aplicado, rc.deshacer, zona.cerca_de_encajar.*,
// error.reintentar).
const TEXT = {
  loading: "Buscando zonas para ti…",
  applied: "Ahora ves las zonas con:",
  undo: "Volver a mi búsqueda",
  stale: "Has cambiado tu búsqueda. Pulsa «Buscar zonas para mí» para ponerla al día.",
  first: (n: number) => `Ver las ${n} primeras`,
  fewer: "Ver menos",
  rest: (n: number, word: ZoneWord) => `Y ${zonesText(n, word)} más en el mapa.`,
  near: "Casi valen",
  nearHelp: "Les falta una sola cosa de lo que pides.",
  retry: "Reintentar",
  // zona.empate, read after the % of a tied row where the % shows (wide screens)
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

interface RowProps {
  zone: RankedZone;
  buying: boolean;
  /** Where the zone is, only when two rows would read the same (rowPlace of lib/essentials.ts) */
  place?: string | null;
  /** A near miss: what it lacks instead of its band (resultados.casi.*) */
  lacks?: Spoken;
  /** Read after its %: whom it ties with (`tiedNames`); the ties are told in the card's «Ver más» */
  tie?: string | null;
}

/**
 * One row of the list, all of it a button that opens the zone card (second delivery of the UX
 * mobile audit, decided by Mariano): its name, its band in words and «Unos 1.129 € al mes», with a
 * «›». The %, the kind of zone, the m², the confidence words and the ties go to the card. On a wide
 * screen the % stays, small, after the band.
 */
function ZoneRow({ zone, buying, place, lacks, tie }: RowProps) {
  const { select, zones } = useMapZones();
  const key = zoneKeyOf(zone.zone);
  const price = zonePrice(zone, buying);
  const fit = lacks ? null : matchText(zone);
  return (
    <button type="button" className={styles.row} data-zone={key} onClick={() => select(key)}>
      {!lacks && <span className={styles.rank}>{zone.rank}</span>}
      <span className={styles.rowText}>
        <span className={styles.rowName}>
          {rowTitle(zone, zones)}
          {place && <span className={styles.place}> · {place}</span>}
        </span>
        {lacks && (
          <span className={styles.lacks}>
            <span aria-hidden="true">{lacks.text}</span>
            <span className="visually-hidden">{lacks.aria}</span>
          </span>
        )}
        {fit && (
          <span className={styles.band}>
            {fit.band}
            <span className={styles.pct}>
              {` · ${fit.pct}`}
              {tie && <span className="visually-hidden">{`, ${TEXT.tiesWith(tie)}`}</span>}
            </span>
          </span>
        )}
        {price && <PriceTag price={price} variant="row" />}
      </span>
      <ChevronRight size={20} aria-hidden="true" className={styles.chevron} />
    </button>
  );
}

/** «Berruguete · Tetuán»: a barrio's district comes from the start of its code (D-238) */
function rowTitle({ zone }: RankedZone, zones: ZoneCollection | null): string {
  const district = zone.level === "barrio" && zones ? districtOf(zones, zone.code) : undefined;
  return zoneTitle({ name: zone.name, district_name: district?.name });
}

function Ranking({ result }: { result: SearchResult }) {
  const [all, setAll] = useState(false);
  const shown = all ? result.results : result.results.slice(0, FIRST_ROWS);
  const rest = result.reality_check.zones_passing - result.results.length;
  const word = zoneWord(result);
  const names = shown.map((z) => z.zone.name);
  return (
    <>
      <ol className={styles.ranking}>
        {shown.map((zone) => (
          <li key={zoneKeyOf(zone.zone)}>
            <ZoneRow
              zone={zone}
              buying={result.scenario.budget?.kind === "buy"}
              place={rowPlace(zone.zone, names)}
              tie={tiedNames(zone, result.all_zones, word, result.results)}
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
      {all && rest > 0 && <p className={styles.muted}>{TEXT.rest(rest, word)}</p>}
    </>
  );
}

function NearMisses({ result }: { result: SearchResult }) {
  const [open, setOpen] = useState(false);
  const nearId = useId();
  const near = result.near_misses ?? [];
  if (near.length === 0) return null;
  const labels = constraintLabels(result);
  // F5 of fit-0.9: no % here, what each one lacks («Se pasa unos 11.000 € de tu presupuesto»)
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
              <ZoneRow zone={zone} buying={result.scenario.budget?.kind === "buy"} lacks={nearMissText(zone, labels, result.scenario)} />
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

/**
 * Takes the person to a field of «Tu búsqueda» (FIELD_ID) and puts the focus in it, as a skip link
 * does; a field folded in «Más opciones» is unfolded first.
 */
function focusField(id: string) {
  const field = document.getElementById(id);
  if (!field) return;
  const fold = field.closest("details");
  if (fold) fold.open = true;
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
  const { scenario, status, result, error, stale, applied, undoRelaxation, retry } = useScenario();
  // The title speaks to the household of the result, or of the search on its way
  const many = speaksToMany((result?.scenario ?? scenario).household);
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
        ? passingText(result.reality_check.zones_passing, applied !== null, zoneWord(result), speaksToMany(result.scenario.household))
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
      {resultsTitle(many)}
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
  const tied = rc.zones_passing > 0 ? tiedText(result) : null;
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
            {/* Not over changes made since: it would bring back what the person changed (lib/searchState.ts) */}
            {!stale && (
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
            )}
          </div>
        )}
        {stale && status !== "loading" && <p className={styles.stale}>{TEXT.stale}</p>}
        {/* One line over the list (second delivery of the UX mobile audit): how many zones; the notes go under it */}
        <p className={styles.summary}>{passingText(rc.zones_passing, applied !== null, word, speaksToMany(result.scenario.household))}</p>
        {rc.zones_passing === 0 && <p>{noneText(word)}</p>}
        {rc.zones_passing > 0 && <Ranking result={result} />}
        <div className={styles.notes}>
          {rentNotice(result) && <p>{rentNotice(result)}</p>}
          {tied && <p>{tied}</p>}
          {asksForPlace(result) && <PlaceHint />}
          <p>{evaluatedText(result)}</p>
          {/* Renting in «Pueblos» most villages have no rent: why they come out «Sin datos» (D-238) */}
          {rentUnknown && <p>{rentUnknown}</p>}
          {!rentUnknown && rc.zones_passing === 0 && rc.zones_unknown > 0 && <p>{unknownText(rc.zones_unknown, word, zonesWithoutPrice(result))}</p>}
        </div>
        <NearMisses result={result} />
      </GlassCard>
      <RealityCheck result={result} />
    </div>
  );
}
