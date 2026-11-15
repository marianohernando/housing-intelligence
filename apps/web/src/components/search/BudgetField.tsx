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
  // The two options' own name, not «Presupuesto» again (review H7 of PR #79)
  kind: "¿Alquilar o comprar?",
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

/** A budget as a key: «Otra cantidad» and what is typed belong to the figure they were set at. */
function budgetKey(budget: { kind: BudgetKind; amount_eur: number } | null): string {
  return budget ? `${budget.kind}:${budget.amount_eur}` : "none";
}

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
  const key = budgetKey(budget);
  // «Otra cantidad» stays chosen while the person types, even through an amount that has its own
  // button; it and what is typed belong to a figure, so a budget changed from outside (an example,
  // «¿Quieres ver más zonas?», «Volver a mi búsqueda») resets both (review R-07 of PR #79)
  const [otherAt, setOtherAt] = useState<string | null>(null);
  const [typing, setTyping] = useState<{ at: string; text: string } | null>(null);
  const other = otherAt === key;
  // What the person is typing; null shows the amount of the search
  const typed = typing?.at === key ? typing.text : null;
  const reset = () => {
    setOtherAt(null);
    setTyping(null);
  };
  const quick = budget !== null && !other && QUICK_BUDGETS[kind].includes(budget.amount_eur);
  const picked = quick ? String(budget.amount_eur) : OTHER;
  const wrong = typed !== null && typed.trim() !== "" && typedBudget(typed, kind) === null;

  return (
    <fieldset className={styles.group}>
      <legend>{TEXT.title}</legend>
      <Segmented
        legend={TEXT.kind}
        value={budget?.kind ?? null}
        options={[
          { value: "rent", label: TEXT.rent },
          { value: "buy", label: TEXT.buy },
        ]}
        onChange={(next) => {
          reset();
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
                setOtherAt(key);
                return;
              }
              reset();
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
                  const text = e.target.value;
                  const amount = typedBudget(text, kind);
                  if (amount === null) {
                    setTyping({ at: key, text });
                    return;
                  }
                  const at = budgetKey({ kind, amount_eur: amount });
                  setOtherAt(at);
                  setTyping({ at, text });
                  update((s) => setTypedBudget(s, amount));
                }}
                onBlur={() => {
                  if (!wrong) setTyping(null);
                }}
              />
              {wrong && (
                <p id={`${id}-error`} role="alert" className={styles.error}>
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
              reset();
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
              reset();
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
