"use client";

import { ChevronDown } from "lucide-react";
import { useId, useState } from "react";

import type { ScenarioState } from "@/contracts/scenario_state";
import { useMapZones } from "@/components/map/MapProvider";
import { useScenario } from "@/components/search/ScenarioProvider";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import Help from "@/components/ui/Help";
import PriceTag from "@/components/ui/PriceTag";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { type BarrioRow, barrioRows, barriosText, barriosTitle, FIRST_BARRIOS } from "@/lib/barrios";
import { errorMessage } from "@/lib/errors";
import { nearHelpText, speaksToMany, unknownText, voice, WALK_MEDIAN } from "@/lib/fit";
import type { ZoneProperties } from "@/lib/map/zones";

import styles from "./BarrioFit.module.css";
import { useBarrioFit } from "./useBarrioFit";

// Copy from pitch/textos_web.md (zona.cerca_de_encajar.*, resultados.casi.ayuda, resultados.menos, resultados.banda.*
// in lib/match.ts, resultados.casi.* and zona.no_cumple in lib/shortfall.ts, zona.encaje.ayuda, a_pie.mediana,
// error.reintentar). The title is Mariano's (13 nov); the rest is B's draft for line D (barrios.encajan.*).
// «tú» or «vosotros» by the household of the search (voice of lib/fit.ts, review R-03 of PR #81)
const TEXT = {
  loading: (district: string, many: boolean) => `Buscando los barrios de ${district} que ${voice(many).te} convienen…`,
  pick: "Toca uno para verlo en el mapa.",
  // barrios.encajan.ayuda, behind «¿Qué es el %?» where the % shows (wide screens); it was a tooltip
  fitHelpLabel: "¿Qué es el %?",
  fitHelpAbout: "de los barrios",
  fitHelp: (many: boolean) => `Cuánto se parece este barrio a lo que ${voice(many).buscas}. No es una nota del barrio.`,
  // zona.empate, read after the % of a tied barrio
  tiesWith: (whom: string) => `empata con ${whom}`,
  all: (n: number) => `Ver los ${n} barrios`,
  fewer: "Ver menos",
  near: "Casi valen",
  retry: "Reintentar",
};

/**
 * One barrio, as a row of the list (second delivery of the UX mobile audit): its name, its band in
 * words (the % small after it on a wide screen) or what it lacks, and «Unos 1.129 € al mes». The row
 * is a button that outlines the barrio on the map (pressed again, back to the whole district) and
 * then shows its first facts under it. Without its outline (the map's barrios not loaded, or no
 * admin unit), the same row without a button, with its facts.
 */
function Barrio({ row }: { row: BarrioRow }) {
  const { barrios, barrio, focusBarrio } = useMapZones();
  const detailsId = useId();
  const outlined = row.id !== null && (barrios?.some((b) => b.properties.admin_unit_id === row.id) ?? false);
  const pressed = outlined && barrio?.properties.admin_unit_id === row.id;
  const showFacts = pressed || !outlined;
  const head = (
    <>
      <span className={styles.rowText}>
        <span className={styles.name}>{row.name}</span>
        {row.lacks && (
          <span className={styles.fails}>
            <span aria-hidden="true">{row.lacks.text}</span>
            <span className="visually-hidden">{row.lacks.aria}</span>
          </span>
        )}
        {row.fit && (
          <span className={styles.band}>
            {row.fit.band}
            <span className={styles.pct}>
              {` · ${row.fit.pct}`}
              {row.tie && <span className="visually-hidden">{`, ${TEXT.tiesWith(row.tie)}`}</span>}
            </span>
          </span>
        )}
        {row.price && <PriceTag price={row.price} variant="row" />}
      </span>
      {outlined && <ChevronDown size={20} aria-hidden="true" className={[styles.chevron, pressed && styles.flip].filter(Boolean).join(" ")} />}
    </>
  );
  return (
    <div className={[styles.row, outlined && styles.pickable, pressed && styles.pressed].filter(Boolean).join(" ")}>
      {outlined ? (
        <button
          type="button"
          className={styles.head}
          aria-pressed={pressed}
          aria-describedby={showFacts ? detailsId : undefined}
          onClick={() => focusBarrio(pressed ? null : row.id)}
        >
          {head}
        </button>
      ) : (
        <span className={styles.head}>{head}</span>
      )}
      {/* Its panel, once outlined: the band with its %, whom it ties with, what the price is for and how sure, its facts (review R-05 of PR #81) */}
      {showFacts && (
        <span id={detailsId} className={styles.details}>
          {row.fit && <span className={styles.fact}>{row.fit.text}</span>}
          {row.tieLine && <span className={styles.fact}>{row.tieLine}</span>}
          {row.price && (
            <span className={styles.fact}>
              {[row.price.long, row.price.area].filter(Boolean).join(" ")}
              {row.price.confidence && ` · ${row.price.confidence.label}`}
            </span>
          )}
          {row.facts.map((fact, i) => (
            <span key={i} className={styles.fact}>
              {fact}
            </span>
          ))}
        </span>
      )}
    </div>
  );
}

function BarrioList({ distrito, name, scenario }: { distrito: string; name: string; scenario: ScenarioState }) {
  const titleId = useId();
  const [all, setAll] = useState(false);
  const { loading, data, error, retry } = useBarrioFit(distrito, scenario);
  const many = speaksToMany(scenario.household);
  const { barrios, barrio } = useMapZones();
  const slow = useSlow(loading);
  const rows = data ? barrioRows(data) : null;
  const shown = rows ? (all ? rows.fits : rows.fits.slice(0, FIRST_BARRIOS)) : [];
  // The facts of a barrio show once it is outlined (or always without its outline): say what their minutes are only then
  const factsShown = (row: BarrioRow) => row.id === null || !barrios?.some((b) => b.properties.admin_unit_id === row.id) || barrio?.properties.admin_unit_id === row.id;
  const walking = rows ? [...shown, ...rows.near].some((row) => row.walking && factsShown(row)) : false;

  return (
    <GlassCard as="section" aria-labelledby={titleId} className={styles.card}>
      <h2 id={titleId} className={styles.title}>
        {barriosTitle(many)}
      </h2>
      {loading && (
        <p role="status" className={styles.muted}>
          {TEXT.loading(name, many)}
          {slow && ` ${SLOW_TEXT}`}
        </p>
      )}
      {error && (
        <div role="alert" className={styles.error}>
          <p>{errorMessage(error)}</p>
          <Button variant="secondary" onClick={retry}>
            {TEXT.retry}
          </Button>
        </div>
      )}
      {data && rows && (
        <>
          <p className={styles.summary}>
            <strong>{barriosText(data.reality_check, many)}</strong>
            {barrios && (rows.fits.length > 0 || rows.near.length > 0) && ` ${TEXT.pick}`}
          </p>
          {data.reality_check.zones_unknown > 0 && <p className={styles.muted}>{unknownText(data.reality_check.zones_unknown, "barrio")}</p>}
          {shown.length > 0 && (
            <ol className={styles.list}>
              {shown.map((row) => (
                <li key={row.code}>
                  <Barrio row={row} />
                </li>
              ))}
            </ol>
          )}
          {rows.fits.length > FIRST_BARRIOS && (
            <button type="button" className={styles.toggle} aria-expanded={all} onClick={() => setAll((v) => !v)}>
              {all ? TEXT.fewer : TEXT.all(rows.fits.length)}
              <ChevronDown size={18} aria-hidden="true" className={all ? styles.flip : undefined} />
            </button>
          )}
          {rows.near.length > 0 && (
            <section className={styles.near} aria-labelledby={`${titleId}-casi`}>
              <h3 id={`${titleId}-casi`}>{TEXT.near}</h3>
              <p className={styles.muted}>{nearHelpText(many)}</p>
              <ul className={styles.list}>
                {rows.near.map((row) => (
                  <li key={row.code}>
                    <Barrio row={row} />
                  </li>
                ))}
              </ul>
            </section>
          )}
          {walking && <p className={styles.muted}>{WALK_MEDIAN}</p>}
          {shown.some((row) => row.fit) && (
            <Help about={TEXT.fitHelpAbout} label={TEXT.fitHelpLabel} className={styles.pctHelp}>
              <p>{TEXT.fitHelp(many)}</p>
            </Help>
          )}
        </>
      )}
    </GlassCard>
  );
}

/**
 * «Los barrios que mejor encajan» (D-232): in a district of Madrid, once there is a search, its
 * barrios by % of fit with 1–2 facts each, and those that fail one condition with it by name. One
 * request, only here; pressing a barrio outlines it on the map, as «Ir a un barrio» does.
 */
export default function BarrioFit({ zone }: { zone: ZoneProperties }) {
  const { result } = useScenario();
  if (!result || zone.level !== "distrito") return null;
  // A new district or search starts again with the first barrios
  return <BarrioList key={`${zone.code}#${JSON.stringify(result.scenario)}`} distrito={zone.code} name={zone.name} scenario={result.scenario} />;
}
