"use client";

import { Baby, Bus, ChevronDown, Cross, GraduationCap, HeartHandshake, type LucideIcon, Search, TrainFront, Trees, User, Users } from "lucide-react";
import { useId, useState } from "react";

import type { BudgetKind, PriorityKey } from "@/contracts/scenario_state";
import Button from "@/components/ui/Button";
import Chip from "@/components/ui/Chip";
import Counter from "@/components/ui/Counter";
import GlassCard from "@/components/ui/GlassCard";
import Segmented from "@/components/ui/Segmented";
import { errorMessage } from "@/lib/errors";
import { formatEuros } from "@/lib/format";
import {
  BUDGET_RANGE,
  peopleAtHome,
  setAdults,
  setBudgetAmount,
  setBudgetKind,
  setMinors,
  setNoBudgetLimit,
  setSeniors,
  togglePriority,
} from "@/lib/scenario";

import NearbyField from "./NearbyField";
import { useScenario } from "./ScenarioProvider";
import styles from "./SearchCard.module.css";
import WorkField from "./WorkField";

// Copy from pitch/textos_web.md (busqueda.*, hogar.*, importa.*, trabajo.*, presupuesto.*)
const TEXT = {
  title: "Tu búsqueda",
  show: "Ver mi búsqueda",
  hide: "Ocultar mi búsqueda",
  home: "Tu hogar",
  homeHelp: "¿Quién va a vivir contigo?",
  alone: "Solo/a",
  couple: "En pareja",
  children: "Con hijos",
  childrenCount: "¿Cuántos hijos?",
  seniors: "Con mayores a cargo",
  seniorsCount: "¿Cuántas personas mayores?",
  matters: "Me importa",
  mattersHelp: "Marca lo que más te importa. Lo primero que marques cuenta más.",
  work: "Trabajo en",
  workHelp: "Así miraremos lo lejos que te queda cada zona.",
  soon: "Muy pronto",
  noLimit: "Sin límite de presupuesto",
  // B's draft for D after fit-0.5 (D-227): where buying has an official price and where it does not
  buySource:
    "Precio de compra: el valor tasado medio de la vivienda libre (Ministerio de Vivienda). Solo se publica para los municipios de más de 25.000 habitantes; en los distritos de Madrid y en los pueblos no podemos comprobar tu presupuesto.",
  budget: "Presupuesto",
  rent: "Alquilar",
  buy: "Comprar",
  indicative: "Orientativo",
  budgetAria: "Presupuesto máximo",
  submit: "Ver zonas que encajan",
  loading: "Buscando zonas…",
  // busqueda.pronto: instead of the button while POST /search of line A is not published
  searchSoon: "Muy pronto podrás ver qué zonas encajan contigo. Mientras, toca una zona del mapa para ver qué le falta.",
};

/**
 * Every priority the search scores today. Zonas verdes (fit-0.3, D-222) scores the walk to an urban
 * park of 1 ha or more. Sin escaleras (fit-0.4, DATA-019, D-223) is a preference the person marks,
 * never a label about them (D-204, CLAUDE.md §13): its icon is the station it measures, not a
 * wheelchair, and its help names the CRTM because it is a proxy. Seguridad has no chip and is not
 * announced (D-224).
 */
const PRIORITIES: { key: PriorityKey; label: string; icon: LucideIcon; help: string }[] = [
  { key: "transporte", label: "Transporte", icon: Bus, help: "Paradas cerca de casa y con autobuses o trenes a menudo." },
  { key: "salud", label: "Salud", icon: Cross, help: "Centro de salud cerca de casa." },
  { key: "colegios", label: "Colegios", icon: GraduationCap, help: "Colegios con primaria, públicos o concertados, cerca de casa." },
  { key: "zonas_verdes", label: "Zonas verdes", icon: Trees, help: "Parques de una hectárea o más, cerca de casa." },
  { key: "sin_escaleras", label: "Sin escaleras", icon: TrainFront, help: "Estación de metro o tren accesible (sin escaleras) según el CRTM, cerca de casa." },
];

function peopleText(n: number): string {
  return n === 1 ? "1 persona en casa" : `${n} personas en casa`;
}

function budgetText(budget: { kind: BudgetKind; amount_eur: number } | null): string {
  if (!budget) return TEXT.noLimit;
  return budget.kind === "rent" ? `Hasta ${formatEuros(budget.amount_eur)} al mes` : `Hasta ${formatEuros(budget.amount_eur)}`;
}

/** «Tu búsqueda» (brief, mockup 1). Collapsible on the zone screen. */
export default function SearchCard({ collapsible = false }: { collapsible?: boolean }) {
  const { scenario, update, search, available, status, error } = useScenario();
  const [open, setOpen] = useState(!collapsible);
  const bodyId = useId();
  const household = scenario.household ?? { adults: 1, minors: 0, seniors_in_care: 0 };
  const minors = household.minors ?? 0;
  const seniors = household.seniors_in_care ?? 0;
  const priorities = scenario.priorities ?? [];
  const budget = scenario.budget ?? null;
  const range = BUDGET_RANGE[budget?.kind ?? "rent"];

  return (
    <GlassCard as="section" aria-labelledby={`${bodyId}-title`} className={styles.card}>
      <div className={styles.head}>
        <h2 id={`${bodyId}-title`}>{TEXT.title}</h2>
        {collapsible && (
          <button type="button" className={styles.toggle} aria-expanded={open} aria-controls={bodyId} onClick={() => setOpen((v) => !v)}>
            {open ? TEXT.hide : TEXT.show}
            <ChevronDown size={18} aria-hidden="true" className={open ? styles.flip : undefined} />
          </button>
        )}
      </div>
      {!open && <p className={styles.summary}>{peopleText(peopleAtHome(scenario))} · {budgetText(budget)}</p>}

      <div id={bodyId} hidden={!open} className={styles.body}>
        <fieldset className={styles.group}>
          <legend>
            {TEXT.home} <span className={styles.legendHelp}>{TEXT.homeHelp}</span>
          </legend>
          <div className={styles.grid}>
            <Chip label={TEXT.alone} icon={User} pressed={household.adults === 1} onToggle={() => update((s) => setAdults(s, 1))} />
            <Chip label={TEXT.couple} icon={Users} pressed={household.adults === 2} onToggle={() => update((s) => setAdults(s, 2))} />
            <Chip label={TEXT.children} icon={Baby} pressed={minors > 0} onToggle={() => update((s) => setMinors(s, minors > 0 ? 0 : 1))} />
            <Chip label={TEXT.seniors} icon={HeartHandshake} pressed={seniors > 0} onToggle={() => update((s) => setSeniors(s, seniors > 0 ? 0 : 1))} />
          </div>
          {minors > 0 && <Counter label={TEXT.childrenCount} value={minors} min={1} max={8} onChange={(n) => update((s) => setMinors(s, n))} />}
          {seniors > 0 && <Counter label={TEXT.seniorsCount} value={seniors} min={1} max={4} onChange={(n) => update((s) => setSeniors(s, n))} />}
        </fieldset>

        <fieldset className={styles.group}>
          <legend>{TEXT.matters}</legend>
          <p className={styles.help}>{TEXT.mattersHelp}</p>
          <div className={styles.chips}>
            {PRIORITIES.map((p) => (
              <Chip
                key={p.key}
                label={p.label}
                icon={p.icon}
                title={p.help}
                pressed={priorities.includes(p.key)}
                badge={priorities.indexOf(p.key) + 1}
                onToggle={() => update((s) => togglePriority(s, p.key))}
              />
            ))}
          </div>
        </fieldset>

        {available ? (
          <>
            <NearbyField />
            <WorkField />
          </>
        ) : (
          // Off, the search cannot use the work place yet: «Muy pronto», as before the search existed
          <div className={`${styles.group} ${styles.work}`}>
            <p className={styles.legend}>
              {TEXT.work} <span className={styles.tag}>{TEXT.soon}</span>
            </p>
            <p className={styles.help}>{TEXT.workHelp}</p>
          </div>
        )}

        <fieldset className={styles.group}>
          <legend>{TEXT.budget}</legend>
          <div className={styles.budgetRow}>
            <Segmented
              legend={TEXT.budget}
              value={budget?.kind ?? null}
              options={[
                { value: "rent", label: TEXT.rent },
                { value: "buy", label: TEXT.buy },
              ]}
              onChange={(kind) => update((s) => setBudgetKind(s, kind))}
            />
            <p className={styles.amount}>
              <span>{budgetText(budget)}</span>
              {budget?.kind === "buy" && <span className={styles.tag}>{TEXT.indicative}</span>}
            </p>
          </div>
          {budget && (
            <input
              type="range"
              className={styles.range}
              min={range.min}
              max={range.max}
              step={range.step}
              value={budget.amount_eur}
              aria-label={TEXT.budgetAria}
              aria-valuetext={budgetText(budget)}
              onChange={(e) => update((s) => setBudgetAmount(s, Number(e.target.value)))}
            />
          )}
          {available && (
            <label className={styles.check}>
              <input type="checkbox" checked={!budget} onChange={(e) => update((s) => setNoBudgetLimit(s, e.target.checked))} />
              {TEXT.noLimit}
            </label>
          )}
          {available && budget?.kind === "buy" && <p className={styles.help}>{TEXT.buySource}</p>}
        </fieldset>

        {available ? (
          <Button className={styles.submit} onClick={() => void search()} disabled={status === "loading"}>
            <Search size={20} aria-hidden="true" />
            {status === "loading" ? TEXT.loading : TEXT.submit}
          </Button>
        ) : (
          <p className={styles.soonNote}>{TEXT.searchSoon}</p>
        )}
        {status === "error" && error && (
          <p role="alert" className={styles.error}>
            {errorMessage(error)}
          </p>
        )}
      </div>
    </GlassCard>
  );
}
