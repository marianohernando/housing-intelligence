"use client";

import { useId } from "react";

import Help from "@/components/ui/Help";
import { floorArea, floorAreaOptions, setFloorArea } from "@/lib/scenario";

import { useScenario } from "./ScenarioProvider";
import styles from "./SearchCard.module.css";

// Copy from pitch/textos_web.md (presupuesto.m2.*)
const TEXT = {
  label: "Tamaño del piso",
  prices: (m2: number, usual: boolean) => `Los precios son para un piso de ${usual ? "unos " : ""}${m2} metros cuadrados.`,
  usual: (m2: number) => `Lo normal para tu hogar (${m2} m²)`,
  option: (m2: number) => `${m2} m²`,
  about: "Tamaño del piso",
  help: "Lo normal para tu hogar es la superficie habitual de las viviendas de hogares como el tuyo en la Comunidad de Madrid (Censo 2021): la mitad tiene menos metros y la otra mitad, más. El precio de cada zona es para estos metros.",
};

/**
 * «Tamaño del piso», in «Más opciones»: the m² every price is for. Unless the person picks them,
 * the search sends `min_floor_area_m2: null` and the API assumes the usual for the household
 * (D-214); «Lo normal para tu hogar» goes back to that.
 */
export default function FloorAreaField() {
  const { scenario, update } = useScenario();
  const id = useId();
  const area = floorArea(scenario);
  const usual = floorArea({ household: scenario.household, min_floor_area_m2: null }).m2;
  const chosen = scenario.min_floor_area_m2 ?? null;

  return (
    <div className={styles.area}>
      <label className={styles.areaPick}>
        {TEXT.label}
        <select
          className={styles.select}
          value={chosen ?? ""}
          aria-describedby={`${id}-prices ${id}-help`}
          onChange={(e) => update((s) => setFloorArea(s, e.target.value === "" ? null : Number(e.target.value)))}
        >
          <option value="">{TEXT.usual(usual)}</option>
          {floorAreaOptions(chosen).map((m2) => (
            <option key={m2} value={m2}>
              {TEXT.option(m2)}
            </option>
          ))}
        </select>
      </label>
      <p id={`${id}-prices`} className={styles.help}>
        {TEXT.prices(area.m2, area.household)}
      </p>
      <Help about={TEXT.about} id={`${id}-help`}>
        <p>{TEXT.help}</p>
      </Help>
    </div>
  );
}
