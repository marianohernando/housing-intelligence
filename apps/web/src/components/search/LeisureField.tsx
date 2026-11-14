"use client";

import { useId } from "react";

import {
  LEISURE_KEYS,
  LEISURE_MINUTES,
  type LeisureKey,
  leisureConfig,
  setLeisureMinutes,
  setLeisureRequired,
  toggleLeisureGroup,
  walkMinutesOptions,
} from "@/lib/scenario";

import { useScenario } from "./ScenarioProvider";
import styles from "./SearchCard.module.css";

// Copy from pitch/textos_web.md (importa.ocio.*, D-236)
const TEXT = {
  title: "¿Qué ocio quieres cerca?",
  // importa.ocio.minutos, «A [10] min andando como mucho», like cerca.item
  before: "A",
  after: "min andando como mucho",
  minutesAria: "Minutos andando hasta el ocio",
  required: "Imprescindible",
  requiredHelp: "Si lo marcas, solo verás zonas que lo cumplen.",
  none: "Marca al menos una casilla para que el ocio cuente.",
  source: "Según OpenStreetMap, un mapa hecho por voluntarios: en los pueblos pequeños puede faltar algún local.",
};

export const LEISURE_NAME: Record<LeisureKey, string> = {
  bares: "Bares y cafeterías",
  restaurantes: "Restaurantes",
  gimnasios: "Gimnasios",
  cines_teatros: "Cines y teatros",
};

/**
 * The small configurator that opens under «Me importa» when «Ocio» is marked (D-236): a box per
 * group and the walking minutes they share. Each ticked group goes to `nearby`, like the services
 * of «Lo quiero a un paseo».
 */
export default function LeisureField() {
  const { scenario, update } = useScenario();
  const id = useId();
  const { groups, minutes, required } = leisureConfig(scenario);

  return (
    <fieldset className={styles.leisure}>
      <legend>{TEXT.title}</legend>
      <div className={styles.leisureBoxes}>
        {LEISURE_KEYS.map((key) => (
          <label key={key} className={styles.check}>
            <input type="checkbox" checked={groups.includes(key)} onChange={() => update((s) => toggleLeisureGroup(s, key))} />
            {LEISURE_NAME[key]}
          </label>
        ))}
      </div>
      {groups.length > 0 ? (
        <div className={styles.leisureRow}>
          <span className={styles.nearMinutes}>
            {TEXT.before}
            <select
              className={styles.select}
              aria-label={TEXT.minutesAria}
              value={minutes}
              onChange={(e) => update((s) => setLeisureMinutes(s, Number(e.target.value)))}
            >
              {walkMinutesOptions(minutes, LEISURE_MINUTES).map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
            {TEXT.after}
          </span>
          <label className={styles.check} title={TEXT.requiredHelp}>
            <input
              type="checkbox"
              checked={required}
              aria-describedby={`${id}-required`}
              onChange={(e) => update((s) => setLeisureRequired(s, e.target.checked))}
            />
            {TEXT.required}
          </label>
          <span id={`${id}-required`} className="visually-hidden">
            {TEXT.requiredHelp}
          </span>
        </div>
      ) : (
        <p className={styles.help}>{TEXT.none}</p>
      )}
      <p className={styles.help}>{TEXT.source}</p>
    </fieldset>
  );
}
