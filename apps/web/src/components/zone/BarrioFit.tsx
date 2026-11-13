"use client";

import { ChevronDown } from "lucide-react";
import { useId, useState } from "react";

import type { ScenarioState } from "@/contracts/scenario_state";
import { useMapZones } from "@/components/map/MapProvider";
import { useScenario } from "@/components/search/ScenarioProvider";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { type BarrioRow, barrioRows, barriosText, FIRST_BARRIOS } from "@/lib/barrios";
import { errorMessage } from "@/lib/errors";
import { hasWalkingFact, unknownText, WALK_MEDIAN } from "@/lib/fit";
import type { ZoneProperties } from "@/lib/map/zones";

import styles from "./BarrioFit.module.css";
import { useBarrioFit } from "./useBarrioFit";

// Copy from pitch/textos_web.md (zona.cerca_de_encajar.*, resultados.casi.ayuda, resultados.menos,
// zona.no_cumple, zona.encaje.ayuda, a_pie.mediana, error.reintentar). The title is Mariano's (13 nov); the rest is
// B's draft for line D (barrios.encajan.*).
const TEXT = {
  title: "Los barrios que mejor encajan",
  loading: (district: string) => `Buscando los barrios de ${district} que encajan contigo…`,
  pick: "Pulsa uno para verlo en el mapa.",
  fitHelp: "Cuánto se parece este barrio a lo que buscas. No es una nota del barrio.",
  fit: "de encaje",
  all: (n: number) => `Ver los ${n} barrios`,
  fewer: "Ver menos",
  near: "Casi encajan",
  nearHelp: "Cumplen todo menos una cosa.",
  fails: "No cumple:",
  failsUnnamed: "No cumple todo lo que pides.",
  retry: "Reintentar",
};

/**
 * One barrio: its name and % are a button that outlines it on the map (pressed again, back to the
 * whole district), and the whole row takes the tap; why it is a near miss and its facts describe it.
 * Without its outline (the map's barrios not loaded, or no admin unit), the same row without a button.
 */
function Barrio({ row }: { row: BarrioRow }) {
  const { barrios, barrio, focusBarrio } = useMapZones();
  const detailsId = useId();
  const outlined = row.id !== null && (barrios?.some((b) => b.properties.admin_unit_id === row.id) ?? false);
  const pressed = outlined && barrio?.properties.admin_unit_id === row.id;
  const head = (
    <>
      <span className={styles.name}>{row.name}</span>
      <span className={styles.pct} title={TEXT.fitHelp}>
        {row.pct} %<span className="visually-hidden"> {TEXT.fit}</span>
      </span>
    </>
  );
  return (
    <div className={[styles.row, outlined && styles.pickable, pressed && styles.pressed].filter(Boolean).join(" ")}>
      {outlined ? (
        <button
          type="button"
          className={styles.head}
          aria-pressed={pressed}
          aria-describedby={detailsId}
          onClick={() => focusBarrio(pressed ? null : row.id)}
        >
          {head}
        </button>
      ) : (
        <span className={styles.head}>{head}</span>
      )}
      <span id={detailsId} className={styles.details}>
        {row.fails && (
          <span className={styles.fails}>{row.fails.length > 0 ? `${TEXT.fails} ${row.fails.join(" · ")}` : TEXT.failsUnnamed}</span>
        )}
        {row.facts.map((fact, i) => (
          <span key={i} className={styles.fact}>
            {fact}
          </span>
        ))}
      </span>
    </div>
  );
}

function BarrioList({ distrito, name, scenario }: { distrito: string; name: string; scenario: ScenarioState }) {
  const titleId = useId();
  const [all, setAll] = useState(false);
  const { loading, data, error, retry } = useBarrioFit(distrito, scenario);
  const { barrios } = useMapZones();
  const slow = useSlow(loading);
  const rows = data ? barrioRows(data) : null;
  const shown = rows ? (all ? rows.fits : rows.fits.slice(0, FIRST_BARRIOS)) : [];
  const walking = rows ? hasWalkingFact([...shown, ...rows.near].flatMap((row) => row.facts.map((text) => ({ text })))) : false;

  return (
    <GlassCard as="section" aria-labelledby={titleId} className={styles.card}>
      <h2 id={titleId} className={styles.title}>
        {TEXT.title}
      </h2>
      {loading && (
        <p role="status" className={styles.muted}>
          {TEXT.loading(name)}
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
            <strong>{barriosText(data.reality_check)}</strong>
            {barrios && (rows.fits.length > 0 || rows.near.length > 0) && ` ${TEXT.pick}`}
          </p>
          {data.reality_check.zones_unknown > 0 && <p className={styles.muted}>{unknownText(data.reality_check.zones_unknown)}</p>}
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
              <p className={styles.muted}>{TEXT.nearHelp}</p>
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
