"use client";

import { useId, useState } from "react";

import type { BudgetKind } from "@/contracts/scenario_state";
import Help from "@/components/ui/Help";
import Segmented from "@/components/ui/Segmented";
import { formatEuros } from "@/lib/format";
import { BUDGET_RANGE, QUICK_BUDGETS, setBudgetAmount, setBudgetKind, setNoBudgetLimit, setTypedBudget, typedBudget } from "@/lib/scenario";

import { useScenario } from "./ScenarioProvider";
import styles from "./SearchCard.module.css";

// Copy from pitch/textos_web.md (presupuesto.*)
const TEXT = {
  title: "Presupuesto",
  rent: "Alquilar",
  buy: "Comprar",
  indicative: "Orientativo",
  amounts: { rent: "¿Hasta cuánto al mes?", buy: "¿Hasta cuánto?" } satisfies Record<BudgetKind, string>,
  other: "Otra cantidad",
  typed: { rent: "Escribe la cantidad, en euros al mes", buy: "Escribe la cantidad, en euros" } satisfies Record<BudgetKind, string>,
  outOfRange: (kind: BudgetKind) => {
    const { min, max } = BUDGET_RANGE[kind];
    return `Escribe una cantidad entre ${formatEuros(min).replace(" €", "")} y ${formatEuros(max)}${kind === "rent" ? " al mes" : ""}.`;
  },
  sliderAria: "Presupuesto máximo",
  noLimit: "Sin límite de presupuesto",
  // presupuesto.compra.fuente (D-227, D-234), behind «¿Qué es esto?»
  buyAbout: "Precio de compra",
  buySource:
    "Precio de compra: el valor tasado medio de la vivienda libre (Ministerio de Vivienda), que solo se publica por municipio y en los de más de 25.000 habitantes. En los distritos y barrios de Madrid, el precio que veas es una estimación: el valor tasado de Madrid repartido según el valor catastral de cada zona. Donde no hay precio, no podemos comprobar tu presupuesto.",
};

export function budgetText(budget: { kind: BudgetKind; amount_eur: number } | null): string {
  if (!budget) return TEXT.noLimit;
  return budget.kind === "rent" ? `Hasta ${formatEuros(budget.amount_eur)} al mes` : `Hasta ${formatEuros(budget.amount_eur)}`;
}

const OTHER = "other";

/**
 * «Presupuesto» (D-203): renting or buying, then the amount with one tap (QUICK_BUDGETS), typed
 * («Otra cantidad») or on the slider; the three move the same figure.
 */
export default function BudgetField({ available }: { available: boolean }) {
  const { scenario, update } = useScenario();
  const id = useId();
  const budget = scenario.budget ?? null;
  const kind = budget?.kind ?? "rent";
  const range = BUDGET_RANGE[kind];
  // «Otra cantidad» stays chosen while the person types, even through an amount that has its own button
  const [other, setOther] = useState(false);
  // What the person is typing; null shows the amount of the search
  const [typed, setTyped] = useState<string | null>(null);
  const quick = budget !== null && !other && QUICK_BUDGETS[kind].includes(budget.amount_eur);
  const picked = quick ? String(budget.amount_eur) : OTHER;
  const wrong = typed !== null && typed.trim() !== "" && typedBudget(typed, kind) === null;

  return (
    <fieldset className={styles.group}>
      <legend>{TEXT.title}</legend>
      <Segmented
        legend={TEXT.title}
        value={budget?.kind ?? null}
        options={[
          { value: "rent", label: TEXT.rent },
          { value: "buy", label: TEXT.buy },
        ]}
        onChange={(next) => {
          setOther(false);
          setTyped(null);
          update((s) => setBudgetKind(s, next));
        }}
      />
      {budget && (
        <>
          <Segmented
            legend={TEXT.amounts[kind]}
            columns={2}
            value={picked}
            options={[...QUICK_BUDGETS[kind].map((amount) => ({ value: String(amount), label: formatEuros(amount) })), { value: OTHER, label: TEXT.other }]}
            onChange={(value) => {
              if (value === OTHER) {
                setOther(true);
                return;
              }
              setOther(false);
              setTyped(null);
              update((s) => setBudgetAmount(s, Number(value)));
            }}
          />
          {picked === OTHER && (
            <div className={styles.areaPick}>
              <label htmlFor={`${id}-typed`}>{TEXT.typed[kind]}</label>
              <input
                id={`${id}-typed`}
                className={styles.input}
                inputMode="numeric"
                autoComplete="off"
                value={typed ?? String(budget.amount_eur)}
                aria-invalid={wrong}
                aria-describedby={wrong ? `${id}-error` : undefined}
                onChange={(e) => {
                  setTyped(e.target.value);
                  const amount = typedBudget(e.target.value, kind);
                  if (amount !== null) update((s) => setTypedBudget(s, amount));
                }}
                onBlur={() => {
                  if (!wrong) setTyped(null);
                }}
              />
              {wrong && (
                <p id={`${id}-error`} className={styles.error}>
                  {TEXT.outOfRange(kind)}
                </p>
              )}
            </div>
          )}
          <p className={styles.amount}>
            <span>{budgetText(budget)}</span>
            {budget.kind === "buy" && <span className={styles.tag}>{TEXT.indicative}</span>}
          </p>
          <input
            type="range"
            className={styles.range}
            min={range.min}
            max={range.max}
            step={range.step}
            value={budget.amount_eur}
            aria-label={TEXT.sliderAria}
            aria-valuetext={budgetText(budget)}
            onChange={(e) => {
              setTyped(null);
              update((s) => setBudgetAmount(s, Number(e.target.value)));
            }}
          />
        </>
      )}
      {available && (
        <label className={styles.check}>
          <input
            type="checkbox"
            checked={!budget}
            onChange={(e) => {
              setOther(false);
              setTyped(null);
              update((s) => setNoBudgetLimit(s, e.target.checked));
            }}
          />
          {TEXT.noLimit}
        </label>
      )}
      {available && budget?.kind === "buy" && (
        <Help about={TEXT.buyAbout}>
          <p>{TEXT.buySource}</p>
        </Help>
      )}
    </fieldset>
  );
}
