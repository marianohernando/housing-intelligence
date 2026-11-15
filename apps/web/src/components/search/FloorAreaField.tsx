"use client";

import { ChevronDown } from "lucide-react";
import { useId, useState } from "react";

import { floorArea, floorAreaOptions, setFloorArea } from "@/lib/scenario";

import { useScenario } from "./ScenarioProvider";
import styles from "./SearchCard.module.css";

// Copy from pitch/textos_web.md (presupuesto.m2.*, 15 nov)
const TEXT = {
  line: (m2: number, usual: boolean) => `${usual ? "Para unos" : "Para"} ${m2} m²`,
  change: "(cámbialo)",
  label: "Metros cuadrados",
  usual: (m2: number) => `Lo normal para tu hogar (${m2} m²)`,
  option: (m2: number) => `${m2} m²`,
  help: "Lo normal para tu hogar es la superficie habitual de las viviendas de hogares como el tuyo en la Comunidad de Madrid (Censo 2021): la mitad tiene menos metros y la otra mitad, más. El precio de cada zona es para estos metros.",
};

/**
 * «Para unos 68 m² (cámbialo)» under the budget: the m² every price is for. Unless the person picks
 * them, the search sends `min_floor_area_m2: null` and the API assumes the usual for the household
 * (D-214); «Lo normal para tu hogar» goes back to that.
 */
export default function FloorAreaField() {
  const { scenario, update } = useScenario();
  const [open, setOpen] = useState(false);
  const id = useId();
  const area = floorArea(scenario);
  const usual = floorArea({ household: scenario.household, min_floor_area_m2: null }).m2;
  const chosen = scenario.min_floor_area_m2 ?? null;

  return (
    <div className={styles.area}>
      <button type="button" className={styles.areaToggle} aria-expanded={open} aria-controls={id} onClick={() => setOpen((v) => !v)}>
        <span>
          {TEXT.line(area.m2, area.household)} <span className={styles.areaChange}>{TEXT.change}</span>
        </span>
        <ChevronDown size={18} aria-hidden="true" className={open ? styles.flip : undefined} />
      </button>
      <div id={id} hidden={!open} className={styles.areaBody}>
        <label className={styles.areaPick}>
          {TEXT.label}
          <select
            className={styles.select}
            value={chosen ?? ""}
            aria-describedby={`${id}-help`}
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
        <p id={`${id}-help`} className={styles.help}>
          {TEXT.help}
        </p>
      </div>
    </div>
  );
}
