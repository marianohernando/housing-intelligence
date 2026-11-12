"use client";

import { Footprints, X } from "lucide-react";
import { useId, useRef } from "react";

import type { NeedKey } from "@/contracts/scenario_state";
import {
  addNearby,
  NEED_KEYS,
  removeNearby,
  setNearbyMinutes,
  setNearbyRequired,
  walkMinutesOptions,
} from "@/lib/scenario";

import styles from "./SearchCard.module.css";
import { useScenario } from "./ScenarioProvider";

// Copy from pitch/textos_web.md (cerca.*, 8c49e33).
const TEXT = {
  title: "Lo quiero a un paseo",
  required: "Imprescindible",
  requiredHelp: "Si lo marcas, solo verás zonas que lo cumplen.",
  add: "Añadir un servicio a un paseo",
  addPlaceholder: "Añadir un servicio…",
  remove: (name: string) => `Quitar ${name.toLowerCase()}`,
  // cerca.item, «{servicio} a {n} min andando como mucho», with the minutes as a selector
  before: "a",
  after: "min andando como mucho",
  minutesAria: (name: string) => `Minutos andando hasta ${name.toLowerCase()}`,
};

export const NEED_NAME: Record<NeedKey, string> = {
  escuela_infantil: "Escuela infantil",
  colegio: "Colegio",
  centro_salud: "Centro de salud",
  farmacia: "Farmacia",
  mayores: "Centro de mayores",
  transporte: "Parada de transporte público",
};

/** «Lo quiero a un paseo»: each service with its walking minutes and whether it is a must. */
export default function NearbyField() {
  const { scenario, update } = useScenario();
  const id = useId();
  const nearby = scenario.nearby ?? [];
  const left = NEED_KEYS.filter((key) => !nearby.some((n) => n.need === key));
  // After «Quitar», the focus goes to «Añadir un servicio» instead of being lost with the row
  const addRef = useRef<HTMLSelectElement>(null);

  return (
    <fieldset className={styles.group}>
      <legend>{TEXT.title}</legend>
      {nearby.length > 0 && (
        <ul className={styles.nearList}>
          {nearby.map((n) => {
            const name = NEED_NAME[n.need];
            const minutes = n.max_walk_minutes ?? 10;
            return (
              <li key={n.need} className={styles.nearItem}>
                <span className={styles.nearSentence}>
                  <span className={styles.nearName}>
                    <Footprints size={18} aria-hidden="true" />
                    {name}
                  </span>
                  <span className={styles.nearMinutes}>
                    {TEXT.before}
                    <select
                      className={styles.select}
                      aria-label={TEXT.minutesAria(name)}
                      value={minutes}
                      onChange={(e) => update((s) => setNearbyMinutes(s, n.need, Number(e.target.value)))}
                    >
                      {walkMinutesOptions(minutes).map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>
                    {TEXT.after}
                  </span>
                </span>
                <label className={styles.check} title={TEXT.requiredHelp}>
                  <input
                    type="checkbox"
                    checked={n.required ?? true}
                    aria-describedby={`${id}-required`}
                    onChange={(e) => update((s) => setNearbyRequired(s, n.need, e.target.checked))}
                  />
                  {TEXT.required}
                </label>
                <button
                  type="button"
                  className={styles.remove}
                  aria-label={TEXT.remove(name)}
                  onClick={() => {
                    update((s) => removeNearby(s, n.need));
                    requestAnimationFrame(() => addRef.current?.focus());
                  }}
                >
                  <X size={18} aria-hidden="true" />
                </button>
              </li>
            );
          })}
        </ul>
      )}
      <p id={`${id}-required`} className="visually-hidden">
        {TEXT.requiredHelp}
      </p>
      {left.length > 0 && (
        <select
          ref={addRef}
          className={styles.select}
          aria-label={TEXT.add}
          value=""
          onChange={(e) => {
            const need = left.find((key) => key === e.target.value);
            if (need) update((s) => addNearby(s, need));
          }}
        >
          <option value="">{TEXT.addPlaceholder}</option>
          {left.map((key) => (
            <option key={key} value={key}>
              {NEED_NAME[key]}
            </option>
          ))}
        </select>
      )}
    </fieldset>
  );
}
