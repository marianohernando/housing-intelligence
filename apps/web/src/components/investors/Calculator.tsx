"use client";

import { Info } from "lucide-react";
import { useEffect, useId, useMemo, useState } from "react";

import type { AssumptionPart, LandItem, SourcedValue, ViabilityDefaults } from "@/contracts/investor_zone_response";
import type { ScenarioOutcome, ViabilityResponse } from "@/contracts/viability_response";
import Button from "@/components/ui/Button";
import { ApiError, createApi } from "@/lib/api";
import { errorMessage } from "@/lib/errors";
import { formatNumber } from "@/lib/format";
import {
  breakEvenFreeText,
  breakEvenText,
  breakEvenValue,
  type CalculatorFields,
  CALCULATOR_TEXT as TEXT,
  costNowValue,
  defaultLand,
  initialFields,
  landArea,
  landKey,
  landName,
  fieldErrors,
  landCaution,
  missingFields,
  money,
  parseNumber,
  percent,
  viabilityRequest,
  withoutMark,
} from "@/lib/investors";

import { MarkTag, VerdictBadge } from "./Figures";
import MethodLink from "./MethodLink";
import styles from "./Investors.module.css";

const DEBOUNCE_MS = 400;
const CUSTOM = "otra";

interface FieldProps {
  name: keyof CalculatorFields;
  label: string;
  unit: string;
  fields: CalculatorFields;
  initial: CalculatorFields;
  onChange: (name: keyof CalculatorFields, value: string) => void;
  source?: SourcedValue;
  /** The note under the field instead of the default's source */
  help?: string;
  /** The mark when the field has no default of its own (the area of the chosen land is data) */
  mark?: SourcedValue["mark"] | "sin_dato";
  /** What is wrong with the value (out of range, not a whole number): said under the field */
  error?: string;
  /** A data default used as an assumption (the PEM of the permits for the person's own works) */
  assumed?: boolean;
}

/** A number the person can edit, with its unit, its mark (data, assumption or theirs) and its source. */
function NumberField({ name, label, unit, fields, initial, onChange, source, help, mark: own, error, assumed }: FieldProps) {
  const id = useId();
  const value = fields[name] as string;
  const edited = own === undefined && value !== initial[name];
  // A default without its data says so («Sin dato»), never «Dato»
  const unknown = !edited && own === undefined && source !== undefined && (source.value === null || source.value === undefined);
  const mark = edited ? "usuario" : unknown ? "sin_dato" : (own ?? (assumed ? "supuesto" : source?.mark) ?? "usuario");
  const described = error ? `${id}-error ${id}-help` : `${id}-help`;
  return (
    <div className={styles.field}>
      <label htmlFor={id}>{label}</label>
      <span className={styles.inputRow}>
        <input
          id={id}
          name={name}
          type="text"
          inputMode="decimal"
          autoComplete="off"
          value={value}
          onChange={(event) => onChange(name, event.target.value)}
          aria-invalid={error ? true : undefined}
          aria-describedby={described}
        />
        <span className={styles.unit}>{unit}</span>
      </span>
      {error && (
        <span id={`${id}-error`} className={styles.fieldError}>
          {error}
        </span>
      )}
      <span id={`${id}-help`} className={styles.fieldHelp}>
        <MarkTag mark={mark} /> {edited ? TEXT.edited : (help ?? (source ? withoutMark(source.source.text) : ""))}
      </span>
    </div>
  );
}

function PartsList({ title, parts }: { title: string; parts: AssumptionPart[] }) {
  return (
    <details className={styles.parts}>
      <summary>{title}</summary>
      <ul>
        {parts.map((part) => (
          <li key={part.key}>
            <strong>
              {percent(part.pct, 0)} · {part.label}.
            </strong>{" "}
            {part.source}
          </li>
        ))}
      </ul>
    </details>
  );
}

/** What the construction cost counts and what it leaves out (D-252), from what viability.py models. */
function CostScope({ parts }: { parts: AssumptionPart[] }) {
  return (
    <details className={styles.parts}>
      <summary>{TEXT.costScopeTitle}</summary>
      <p>{TEXT.costIncludes(parts.map((p) => `${p.label.charAt(0).toLowerCase()}${p.label.slice(1)}`))}</p>
      <p>{TEXT.costExcludesTitle}</p>
      <ul>
        {TEXT.costExcludes.map((line) => (
          <li key={line}>{line}</li>
        ))}
      </ul>
    </details>
  );
}

function LandPicker({
  items,
  chosen,
  onChoose,
}: {
  items: LandItem[];
  chosen: string;
  onChoose: (key: string, item: LandItem | null) => void;
}) {
  return (
    <fieldset className={styles.landPicker}>
      <legend>{TEXT.landPick}</legend>
      {items.map((item) => {
        const key = landKey(item);
        return (
          <label key={key} className={styles.choice}>
            <input type="radio" name="suelo" checked={chosen === key} onChange={() => onChoose(key, item)} />
            <span>
              <strong>{landName(item)}</strong>
              <span className={styles.choiceNote}>
                {item.kind === "parcela" ? TEXT.parcel : TEXT.area} · {landArea(item)}
              </span>
            </span>
          </label>
        );
      })}
      <label className={styles.choice}>
        <input type="radio" name="suelo" checked={chosen === CUSTOM} onChange={() => onChoose(CUSTOM, null)} />
        <span>
          <strong>{TEXT.custom}</strong>
        </span>
      </label>
    </fieldset>
  );
}

function ScenarioCard({ scenario }: { scenario: ScenarioOutcome }) {
  const rows: [string, string][] = [
    [TEXT.revenue, money(scenario.revenue)],
    [TEXT.construction, money(scenario.construction)],
    [TEXT.salesCosts, money(scenario.sales_costs)],
    [TEXT.land, scenario.land === null || scenario.land === undefined ? TEXT.landUnknown : money(scenario.land)],
  ];
  if (scenario.margin_pct !== null && scenario.margin_pct !== undefined) {
    rows.push([TEXT.profit, money(scenario.profit ?? 0)], [TEXT.margin, percent(scenario.margin_pct)]);
  }
  rows.push([
    TEXT.residual,
    `${money(scenario.residual_land_value)} (${formatNumber(Math.round(scenario.residual_land_value_m2), 0)} €/m² edificable)`,
  ]);
  // Never without land: with the price given, or without one at the residual land value
  if (scenario.break_even) rows.push([TEXT.breakEvenRow, breakEvenValue(scenario.break_even)]);
  if (scenario.break_even_free_land) rows.push([TEXT.breakEvenFreeRow, breakEvenValue(scenario.break_even_free_land)]);
  if (scenario.rental_yield_pct !== null && scenario.rental_yield_pct !== undefined) {
    rows.push([scenario.yield_land === "valor_residual" ? TEXT.yieldResidual : TEXT.yield, percent(scenario.rental_yield_pct)]);
  } else if (scenario.annual_rent !== null && scenario.annual_rent !== undefined) {
    rows.push([TEXT.noYield, "—"]);
  }
  return (
    <article className={styles.scenario} aria-labelledby={`escenario-${scenario.key}`}>
      <h4 id={`escenario-${scenario.key}`}>{scenario.label}</h4>
      {scenario.verdict ? (
        <p className={styles.verdictLine}>
          <VerdictBadge verdict={scenario.verdict} /> {scenario.headline}
        </p>
      ) : (
        <p className={styles.headline}>{scenario.headline}</p>
      )}
      <dl className={styles.scenarioFigures}>
        {rows.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </article>
  );
}

/** The base scenario's break-even, and the construction cost the scenarios count now. */
function BreakEvenBlock({ scenario, costMark }: { scenario: ScenarioOutcome; costMark: "supuesto" | "usuario" }) {
  const be = scenario.break_even;
  if (!be) return null;
  return (
    <section aria-labelledby="equilibrio" className={styles.demand}>
      <h4 id="equilibrio">{TEXT.breakEvenTitle}</h4>
      <p>{breakEvenText(be)}</p>
      {scenario.break_even_free_land && <p>{breakEvenFreeText(scenario.break_even_free_land)}</p>}
      <p>
        <MarkTag mark={costMark} /> {TEXT.costNow}: {costNowValue(be)}.
      </p>
    </section>
  );
}

function Results({ result, costMark }: { result: ViabilityResponse["data"]; costMark: "supuesto" | "usuario" }) {
  const base = result.scenarios.find((s) => s.key === "base") ?? result.scenarios[0];
  return (
    <>
      <p className={styles.lead}>
        {TEXT.newPrice(result.sale_price_m2_new)} {result.land_known ? TEXT.withLand : TEXT.withoutLand}
      </p>
      <div className={styles.scenarios}>
        {result.scenarios.map((scenario) => (
          <ScenarioCard key={scenario.key} scenario={scenario} />
        ))}
      </div>
      {base && <BreakEvenBlock scenario={base} costMark={costMark} />}
      <p className={styles.thresholds}>{TEXT.thresholds}</p>
      {result.demand && (
        <section aria-labelledby="demanda-check" className={styles.demand}>
          <h4 id="demanda-check">{TEXT.demandTitle}</h4>
          <ul>
            {result.demand.lines.map((line) => (
              <li key={line}>{line}</li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}

/** A parcel's sheet (D-250): the calculator starts from its buildable m², marked as the sheet marks it. */
export interface ParcelStart {
  m2: number | null;
  mark: SourcedValue["mark"] | "sin_dato";
  help: string;
}

interface Props {
  defaults: ViabilityDefaults;
  parcels: LandItem[];
  remaining: LandItem[];
  parcel?: ParcelStart;
  /** «Cómo lo calculamos» under the results; off where the sheet already has it (a parcel's) */
  methodLink?: boolean;
}

/** The viability v0 (D-248): the land, the editable inputs with their sources, three scenarios and the demand check. */
export default function Calculator({ defaults, parcels, remaining, parcel, methodLink = true }: Props) {
  const firstLand = defaultLand(parcels, remaining);
  const initial = useMemo(() => {
    const fields = initialFields(defaults, firstLand);
    return parcel ? { ...fields, buildable_m2: parcel.m2 === null ? "" : String(Math.round(parcel.m2)) } : fields;
  }, [defaults, firstLand, parcel]);
  const [fields, setFields] = useState<CalculatorFields>(initial);
  const [chosen, setChosen] = useState(firstLand ? landKey(firstLand) : CUSTOM);
  const [state, setState] = useState<{ result?: ViabilityResponse["data"]; error?: ApiError; busy: boolean }>({ busy: false });
  const request = useMemo(() => viabilityRequest(fields), [fields]);
  const body = JSON.stringify(request);
  const land = useMemo(() => [...parcels, ...remaining], [parcels, remaining]);

  useEffect(() => {
    if (!request) return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      setState((s) => ({ ...s, busy: true }));
      createApi()
        .viability(request, { signal: controller.signal })
        .then((response) => setState({ result: response.data, busy: false }))
        .catch((exc: unknown) => {
          if (controller.signal.aborted) return;
          setState({ error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)), busy: false });
        });
    }, DEBOUNCE_MS);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
    // The body says what changed; the request object is rebuilt on every edit
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [body]);

  const set = (name: keyof CalculatorFields, value: string) => setFields((f) => ({ ...f, [name]: value }));
  const choose = (key: string, item: LandItem | null) => {
    setChosen(key);
    if (item?.buildable_m2) set("buildable_m2", String(Math.round(item.buildable_m2)));
    else if (key === CUSTOM) set("buildable_m2", "");
  };
  const chosenItem = land.find((item) => landKey(item) === chosen) ?? null;
  const fromLand = chosenItem?.buildable_m2 != null && parseNumber(fields.buildable_m2) === Math.round(chosenItem.buildable_m2);
  // A parcel's figure keeps its mark (dato, supuesto or sin dato) until the person changes it
  const fromParcel = parcel !== undefined && fields.buildable_m2 === initial.buildable_m2;
  const buildableMark = fromParcel ? parcel.mark : fromLand ? "dato" : "usuario";
  const buildableHelp = fromParcel ? parcel.help : fromLand ? TEXT.buildableFrom : TEXT.buildableHelp;
  const missing = missingFields(fields);
  const errors = fieldErrors(fields);
  const invalid = Object.keys(errors).length > 0;
  const caution = landCaution(chosenItem);
  const ready = missing.length === 0 && !invalid;
  const common = { fields, initial, onChange: set };
  const costEdited = fields.pem_m2 !== initial.pem_m2 || fields.cost_coefficient !== initial.cost_coefficient;
  const costsEdited = costEdited || fields.sales_costs_pct !== initial.sales_costs_pct;
  const resetCosts = () =>
    setFields((f) => ({ ...f, pem_m2: initial.pem_m2, cost_coefficient: initial.cost_coefficient, sales_costs_pct: initial.sales_costs_pct }));
  const pemKnown = defaults.pem_m2.value !== null && defaults.pem_m2.value !== undefined;
  const err = (name: keyof CalculatorFields) => ({ error: errors[name] });

  return (
    <div className={styles.calculator}>
      <p className={styles.lead}>{TEXT.intro}</p>
      {land.length > 0 && <LandPicker items={land} chosen={chosen} onChoose={choose} />}
      {caution && (
        <p className={styles.caution}>
          <Info size={18} aria-hidden="true" />
          <span>{caution}</span>
        </p>
      )}
      <div className={styles.fieldGroups}>
        <fieldset className={styles.group}>
          <legend>{TEXT.groupRevenue}</legend>
          <NumberField
            name="buildable_m2"
            label={TEXT.buildable}
            unit="m²"
            {...common}
            {...err("buildable_m2")}
            mark={buildableMark}
            help={buildableHelp}
          />
          <NumberField name="sale_price_m2" label={TEXT.price} unit="€/m²" source={defaults.sale_price_m2} {...common} {...err("sale_price_m2")} />
          <NumberField name="new_build_premium_pct" label={TEXT.premium} unit="%" source={defaults.new_build_premium_pct} {...common} {...err("new_build_premium_pct")} />
          <NumberField name="rent_m2_month" label={TEXT.rent} unit="€/m² al mes" source={defaults.rent_m2_month} {...common} {...err("rent_m2_month")} />
        </fieldset>
        <fieldset className={styles.group}>
          <legend>{TEXT.groupCosts}</legend>
          <NumberField
            name="pem_m2"
            label={TEXT.pem}
            unit="€/m²"
            source={defaults.pem_m2}
            {...common}
            {...err("pem_m2")}
            assumed={pemKnown}
            help={pemKnown ? TEXT.pemAssumed(withoutMark(defaults.pem_m2.source.text)) : undefined}
          />
          <p className={styles.caution}>
            <Info size={18} aria-hidden="true" />
            <span>{TEXT.costCaution}</span>
          </p>
          <CostScope parts={defaults.cost_parts} />
          <NumberField name="cost_coefficient" label={TEXT.coefficient} unit="×" source={defaults.cost_coefficient} {...common} {...err("cost_coefficient")} />
          <PartsList title={TEXT.coefficientParts} parts={defaults.cost_parts} />
          <NumberField name="sales_costs_pct" label={TEXT.salesCostsField} unit="% de las ventas" source={defaults.sales_costs_pct} {...common} {...err("sales_costs_pct")} />
          <PartsList title={TEXT.salesParts} parts={defaults.sales_cost_parts} />
          {costsEdited && (
            <Button variant="secondary" onClick={resetCosts}>
              {TEXT.costReset}
            </Button>
          )}
          <NumberField name="land" label={TEXT.landField} unit={fields.land_unit === "m2" ? "€/m² edificable" : "€ en total"} {...common} {...err("land")} help={TEXT.landHelp} />
          <label className={styles.selectRow}>
            <span>{TEXT.landUnit}</span>
            <select value={fields.land_unit} onChange={(event) => set("land_unit", event.target.value)}>
              <option value="total">{TEXT.landTotal}</option>
              <option value="m2">{TEXT.landPerM2}</option>
            </select>
          </label>
          <NumberField name="target_margin_pct" label={TEXT.target} unit="%" source={defaults.target_margin_pct} {...common} {...err("target_margin_pct")} />
        </fieldset>
        <fieldset className={styles.group}>
          <legend>{TEXT.groupDemand}</legend>
          <NumberField name="household_income" label={TEXT.income} unit="€ al año" source={defaults.household_income} {...common} {...err("household_income")} />
          <NumberField name="home_m2" label={TEXT.home} unit="m²" source={defaults.home_m2} {...common} {...err("home_m2")} />
          <NumberField name="ltv_pct" label={TEXT.ltv} unit="%" source={defaults.ltv_pct} {...common} {...err("ltv_pct")} />
          <NumberField name="loan_years" label={TEXT.years} unit="años" source={defaults.loan_years} {...common} {...err("loan_years")} />
          <NumberField name="loan_rate_pct" label={TEXT.rate} unit="%" source={defaults.loan_rate_pct} {...common} {...err("loan_rate_pct")} />
          <p className={styles.fieldHelp}>
            <MarkTag mark={defaults.effort_threshold_pct.mark} /> {TEXT.threshold(defaults.effort_threshold_pct)}
          </p>
        </fieldset>
      </div>
      <section aria-labelledby="resultado" className={styles.results}>
        <h3 id="resultado">{TEXT.results}</h3>
        <div aria-live="polite" aria-busy={state.busy}>
          {missing.length > 0 && <p className={styles.lead}>{TEXT.missing}</p>}
          {missing.length === 0 && invalid && <p className={styles.lead}>{TEXT.invalid}</p>}
          {ready && state.error && <p role="alert">{errorMessage(state.error)}</p>}
          {ready && !state.error && !state.result && <p>{TEXT.calculating}</p>}
          {ready && state.result && <Results result={state.result} costMark={costEdited ? "usuario" : "supuesto"} />}
        </div>
      </section>
      {methodLink && <MethodLink />}
    </div>
  );
}
