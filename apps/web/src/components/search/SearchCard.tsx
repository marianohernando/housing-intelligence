"use client";

import { Baby, Bus, ChevronDown, Cross, GraduationCap, HeartHandshake, type LucideIcon, Search, Sunset, TrainFront, Trees, User, Users, Wine } from "lucide-react";
import { useId, useState } from "react";

import type { PriorityKey, ScenarioState, SearchScope } from "@/contracts/scenario_state";
import { useDatasets } from "@/components/provenance/useDatasets";
import Button from "@/components/ui/Button";
import Chip from "@/components/ui/Chip";
import Counter from "@/components/ui/Counter";
import GlassCard from "@/components/ui/GlassCard";
import Help from "@/components/ui/Help";
import Segmented from "@/components/ui/Segmented";
import { errorMessage } from "@/lib/errors";
import { FIELD_ID, rentReferenceAvailable } from "@/lib/fit";
import { leisureAvailable } from "@/lib/map/facilities";
import {
  floorArea,
  isOlderHousehold,
  nearbyServices,
  peopleAtHome,
  placeOf,
  SCOPE_LABEL,
  SCOPES,
  scopeOf,
  setAdults,
  setMinors,
  setOlderHousehold,
  setScope,
  setSeniors,
  togglePriority,
} from "@/lib/scenario";

import BudgetField, { budgetText } from "./BudgetField";
import FloorAreaField from "./FloorAreaField";
import LeisureField from "./LeisureField";
import NearbyField from "./NearbyField";
import PlaceField, { OlderPlaceField, type StationList, useStations } from "./PlaceField";
import { useScenario } from "./ScenarioProvider";
import styles from "./SearchCard.module.css";

// Copy from pitch/textos_web.md (busqueda.*, donde.*, hogar.*, importa.*, trabajo.*, familia.*, mas.*)
const TEXT = {
  title: "Tu búsqueda",
  where: "¿Dónde?",
  show: "Ver mi búsqueda",
  hide: "Ocultar mi búsqueda",
  home: "¿Quién va a vivir en la casa?",
  alone: "Solo/a",
  couple: "En pareja",
  children: "Con hijos",
  childrenCount: "¿Cuántos hijos?",
  // hogar.somos_mayores (D-244): who the adults are, not one more person
  older: "Somos mayores",
  olderHelp: "Para personas de 65 años o más. Elige también si vives solo/a o en pareja.",
  seniors: "Con una persona mayor a la que cuidas",
  seniorsCount: "¿Cuántas personas mayores?",
  matters: "¿Qué quieres tener cerca?",
  mattersHelp: "Toca primero lo más importante: cuenta más.",
  mattersAbout: "¿Qué quieres tener cerca?",
  work: "Trabajo en",
  workHelp: "Así miraremos lo lejos que te queda cada zona.",
  soon: "Muy pronto",
  more: "Más opciones",
  moreWhat: (older: boolean) => (older ? "Trabajo, servicios a un paseo y tamaño del piso" : "Servicios a un paseo, familia o amigos y tamaño del piso"),
  moreChosen: (n: number) => (n === 1 ? "1 elegida" : `${n} elegidas`),
  submit: "Buscar zonas para mí",
  loading: "Buscando zonas…",
  // busqueda.pronto: instead of the button while POST /search of line A is not published
  searchSoon: "Muy pronto podrás ver qué zonas te convienen. Mientras, toca una zona del mapa para ver qué le falta.",
};

/**
 * Every priority the search scores today. Zonas verdes (fit-0.3, D-222) scores the walk to an urban
 * park of 1 ha or more. «Metro o tren sin escaleras» (fit-0.4, DATA-019, D-223) is a preference the
 * person marks, never a label about them (D-204, CLAUDE.md §13): its icon is the station it measures,
 * not a wheelchair, and its help names the Consorcio because it is a proxy. Seguridad has no chip and
 * is not announced (D-224). Ocio (fit-0.8, D-236) opens its own boxes: it only counts for what is ticked.
 */
const PRIORITIES: { key: PriorityKey; label: string; icon: LucideIcon; help: string }[] = [
  { key: "transporte", label: "Transporte", icon: Bus, help: "Paradas cerca de casa y con autobuses o trenes a menudo." },
  { key: "salud", label: "Centro de salud", icon: Cross, help: "Centro de salud cerca de casa." },
  { key: "colegios", label: "Colegios", icon: GraduationCap, help: "Colegios con primaria, públicos o concertados, cerca de casa." },
  { key: "zonas_verdes", label: "Zonas verdes", icon: Trees, help: "Parques de una hectárea o más, cerca de casa." },
  {
    key: "sin_escaleras",
    label: "Metro o tren sin escaleras",
    icon: TrainFront,
    help: "Estación de metro o tren accesible (sin escaleras) según el Consorcio Regional de Transportes, cerca de casa.",
  },
  { key: "ocio", label: "Ocio", icon: Wine, help: "Bares, restaurantes, gimnasios y cultura (museos, bibliotecas, teatros y cines) cerca de casa: tú eliges cuáles." },
];

/**
 * «¿Dónde?» (D-238): what each part of the region compares (donde.ayuda.*), by the statistical
 * zoning of the Comunidad de Madrid. «Toda la Comunidad» is the search as it always was. The
 * villages' rent is the Ministry's reference once its dataset is published (D-242); until then,
 * the D-238 warning that almost none has one (`VILLAGES_WITHOUT_REFERENCE`).
 */
const VILLAGES_WITHOUT_REFERENCE =
  "Los 138 municipios de fuera del área metropolitana, según el Instituto de Estadística de la Comunidad de Madrid. Casi ninguno publica su alquiler: si buscas alquiler, la mayoría saldrán «Sin datos».";
const WHERE_HELP: Record<SearchScope, string> = {
  all: "Madrid capital por distritos y el resto de la Comunidad por municipios.",
  madrid: "Comparamos sus 131 barrios.",
  alrededores: "Los 40 municipios del área metropolitana, según el Instituto de Estadística de la Comunidad de Madrid.",
  pueblos:
    "Los 138 municipios de fuera del área metropolitana, según el Instituto de Estadística de la Comunidad de Madrid. Su alquiler es la referencia del Ministerio de Vivienda, un dato aproximado; los que tienen muy pocas viviendas alquiladas salen «Sin datos».",
};

function peopleText(n: number): string {
  return n === 1 ? "1 persona en casa" : `${n} personas en casa`;
}

/**
 * What the person set inside «Más opciones», so a folded choice is never a hidden one. With «Somos
 * mayores» the work place is there, and the family goes in «¿Cerca de dónde queréis vivir?».
 */
function chosenInMore(s: ScenarioState, older: boolean): number {
  const work = older && placeOf(s, "work") ? 1 : 0;
  const family = !older && placeOf(s, "family") ? 1 : 0;
  const area = floorArea(s).household ? 0 : 1;
  return nearbyServices(s).length + work + family + area;
}

/** «¿Quién va a vivir en la casa?»: who lives there, and «Somos mayores» (D-244), which adds no one. */
function HomeField() {
  const { scenario, update } = useScenario();
  const helpId = useId();
  const household = scenario.household ?? { adults: 1, minors: 0, seniors_in_care: 0 };
  const minors = household.minors ?? 0;
  const seniors = household.seniors_in_care ?? 0;
  const older = isOlderHousehold(scenario);
  return (
    <fieldset className={styles.group} aria-describedby={older ? helpId : undefined}>
      <legend>{TEXT.home}</legend>
      <div className={styles.grid}>
        <Chip label={TEXT.alone} icon={User} pressed={household.adults === 1} onToggle={() => update((s) => setAdults(s, 1))} />
        <Chip label={TEXT.couple} icon={Users} pressed={household.adults === 2} onToggle={() => update((s) => setAdults(s, 2))} />
        <Chip label={TEXT.children} icon={Baby} pressed={minors > 0} onToggle={() => update((s) => setMinors(s, minors > 0 ? 0 : 1))} />
        <Chip label={TEXT.older} icon={Sunset} pressed={older} onToggle={() => update((s) => setOlderHousehold(s, !older))} />
        <Chip label={TEXT.seniors} icon={HeartHandshake} pressed={seniors > 0} onToggle={() => update((s) => setSeniors(s, seniors > 0 ? 0 : 1))} />
      </div>
      {older && (
        <p id={helpId} className={styles.help}>
          {TEXT.olderHelp}
        </p>
      )}
      {minors > 0 && <Counter label={TEXT.childrenCount} value={minors} min={1} max={8} onChange={(n) => update((s) => setMinors(s, n))} />}
      {seniors > 0 && <Counter label={TEXT.seniorsCount} value={seniors} min={1} max={4} onChange={(n) => update((s) => setSeniors(s, n))} />}
    </fieldset>
  );
}

/** «¿Qué quieres tener cerca?» (D-204): the order of marking is the order of importance. */
function MattersField({ leisure }: { leisure: boolean }) {
  const { scenario, update } = useScenario();
  const priorities = scenario.priorities ?? [];
  const shown = PRIORITIES.filter((p) => p.key !== "ocio" || leisure);
  return (
    <fieldset className={styles.group}>
      <legend>{TEXT.matters}</legend>
      <p className={styles.help}>{TEXT.mattersHelp}</p>
      <div className={styles.chips}>
        {shown.map((p) => (
          <Chip
            key={p.key}
            label={p.label}
            icon={p.icon}
            pressed={priorities.includes(p.key)}
            badge={priorities.indexOf(p.key) + 1}
            onToggle={() => update((s) => togglePriority(s, p.key))}
          />
        ))}
      </div>
      <Help about={TEXT.mattersAbout}>
        <ul>
          {shown.map((p) => (
            <li key={p.key}>
              <strong>{p.label}:</strong> {p.help}
            </li>
          ))}
        </ul>
      </Help>
      {priorities.includes("ocio") && <LeisureField />}
    </fieldset>
  );
}

/**
 * «Más opciones», folded (UX mobile audit, option 1): what fewer people need. Nothing is lost: the
 * fold says how many choices it holds. With «Somos mayores» it holds «Trabajo en».
 */
function MoreOptions({ older, stationList }: { older: boolean; stationList: StationList }) {
  const { scenario } = useScenario();
  const chosen = chosenInMore(scenario, older);
  return (
    <details className={styles.more}>
      <summary>
        <span className={styles.moreTitle}>
          {TEXT.more}
          <ChevronDown size={18} aria-hidden="true" className={styles.moreChevron} />
        </span>
        <span className={styles.moreWhat}>
          {TEXT.moreWhat(older)}
          {chosen > 0 && ` · ${TEXT.moreChosen(chosen)}`}
        </span>
      </summary>
      <div className={styles.moreBody}>
        {older && <PlaceField kind="work" stationList={stationList} id={FIELD_ID.work} />}
        <NearbyField />
        {!older && <PlaceField kind="family" stationList={stationList} />}
        <FloorAreaField />
      </div>
    </details>
  );
}

/** «Tu búsqueda» (brief, mockup 1). Collapsible on the zone screen. */
export default function SearchCard({ collapsible = false }: { collapsible?: boolean }) {
  const { scenario, update, search, available, status, error } = useScenario();
  const [open, setOpen] = useState(!collapsible);
  const bodyId = useId();
  const stationList = useStations();
  const priorities = scenario.priorities ?? [];
  // «Ocio» is offered once its data is published; a search that already carries it keeps its chip
  const { data: datasets } = useDatasets();
  const leisure = leisureAvailable(datasets?.datasets) || priorities.includes("ocio");
  const rentReference = rentReferenceAvailable(datasets?.datasets);
  const budget = scenario.budget ?? null;
  const scope = scopeOf(scenario);
  const older = isOlderHousehold(scenario);
  const whereHelpId = `${bodyId}-where-help`;

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
      {!open && (
        <p className={styles.summary}>
          {peopleText(peopleAtHome(scenario))} · {budgetText(budget)}
          {/* presupuesto.m2.resumen: only the m² the person chose; the usual ones go unsaid */}
          {!floorArea(scenario).household && ` · ${floorArea(scenario).m2} m²`}
          {scope !== "all" && ` · ${SCOPE_LABEL[scope]}`}
        </p>
      )}

      <div id={bodyId} hidden={!open} className={styles.body}>
        {available && (
          <fieldset id={FIELD_ID.where} className={styles.group}>
            <legend>{TEXT.where}</legend>
            <Segmented
              legend={TEXT.where}
              columns={2}
              describedBy={whereHelpId}
              value={scope}
              options={SCOPES.map((value) => ({ value, label: SCOPE_LABEL[value] }))}
              onChange={(value) => update((s) => setScope(s, value))}
            />
            <Help about={TEXT.where} id={whereHelpId}>
              <p>{scope === "pueblos" && !rentReference ? VILLAGES_WITHOUT_REFERENCE : WHERE_HELP[scope]}</p>
            </Help>
          </fieldset>
        )}

        <HomeField />
        <MattersField leisure={leisure} />

        {/* «Somos mayores» (D-244): where they want to live, in view, instead of where they work */}
        {available && (older ? <OlderPlaceField stationList={stationList} /> : <PlaceField kind="work" stationList={stationList} id={FIELD_ID.work} />)}
        {!available && (
          // Off, the search cannot use the work place yet: «Muy pronto», as before the search existed
          <div className={styles.group}>
            <p className={styles.legend}>
              {TEXT.work} <span className={styles.tag}>{TEXT.soon}</span>
            </p>
            <p className={styles.help}>{TEXT.workHelp}</p>
          </div>
        )}

        <BudgetField available={available} />

        {available && <MoreOptions older={older} stationList={stationList} />}

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
