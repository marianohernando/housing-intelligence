"use client";

import { Briefcase, Heart, House, type LucideIcon, X } from "lucide-react";
import { type KeyboardEvent, type RefObject, useCallback, useEffect, useId, useMemo, useRef, useState } from "react";

import { useMapZones } from "@/components/map/MapProvider";
import type { Anchor } from "@/contracts/scenario_state";
import Help from "@/components/ui/Help";
import Segmented from "@/components/ui/Segmented";
import { createApi } from "@/lib/api";
import {
  commuteMinutesOptions,
  FEW_OFFICE_DAYS,
  officeDays,
  officeDaysOptions,
  type OlderPlaceKind,
  olderPlace,
  type PlaceKind,
  placeOf,
  setOlderPlace,
  setOlderPlaceKind,
  setPlace,
  setPlaceMaxMinutes,
  setWorkDays,
} from "@/lib/scenario";
import { findPlaces, STATION_KINDS, stationPlaces, stepActive, type WorkPlace, zonePlaces } from "@/lib/workPlaces";

import styles from "./SearchCard.module.css";
import { useScenario } from "./ScenarioProvider";

// Copy from pitch/textos_web.md (trabajo.*, familia.*). The placeholder and «no results» name stations
// instead of streets: there is no street search without an external geocoder.
const TEXT = {
  placeholder: "Escribe una estación, un distrito o un municipio",
  noMatch: "No encontramos ese lugar. Prueba con una estación o con el nombre del municipio.",
  found: (n: number) => (n === 1 ? "1 lugar encontrado. Usa las flechas para elegirlo." : `${n} lugares encontrados. Usa las flechas para elegir uno.`),
  remove: "Quitar este lugar",
  // Both places are optional, said by their name (UX mobile audit, C4: «Trabajo en» did not say it)
  optional: "(opcional)",
  // trabajo.max_min, «Tardar como mucho {n} min en transporte público», with the minutes as a selector
  commuteBefore: "Tardar como mucho",
  commuteAfter: "en transporte público",
  noLimit: "Sin límite",
  // trabajo.dias (D-240): how many days the person goes weighs the trip to work
  days: "¿Cuántos días vas a la oficina?",
  daysOption: (n: number) => (n === 0 ? "Teletrabajo total" : n === 1 ? "1 día" : `${n} días`),
  fewDays: "Como vas pocos días, el trayecto cuenta la mitad.",
  telework: "Con teletrabajo total, el trayecto no cuenta para ordenar las zonas. Si pones un límite, lo respetamos.",
  // lugar.* (D-244): «Somos mayores» is asked where they want to live, in place of «Trabajo en»
  older: {
    title: "¿Cerca de dónde queréis vivir?",
    options: { other: "Donde vivimos ahora", family: "Cerca de nuestra familia" } satisfies Record<OlderPlaceKind, string>,
    search: { other: "¿Dónde vivís ahora?", family: "¿Dónde vive vuestra familia?" } satisfies Record<OlderPlaceKind, string>,
    help: "Miramos cuánto se tarda en transporte público hasta ese sitio, llegando a las 9:00 de un día laborable, y contamos el trayecto como si fuerais 3 días a la semana. Ponemos 30 min como mucho: puedes cambiarlo o quitarlo.",
    // A family place picked before this field knew its name (a shared link): said in plain words
    family: "Vuestra familia",
  },
};

/** What changes from «Trabajo en» to «Cerca de mi familia o amigos» and «Donde vivimos ahora»; the rest is the same field. */
const KINDS: Record<PlaceKind, { title: string; help: string; commuteAria: string; icon: LucideIcon }> = {
  work: {
    title: "Trabajo en",
    // trabajo.ayuda: the commute in public transport minutes (CORE-009, D-220), every CRTM feed, without acronyms
    help: "Miramos cuánto tardarías en llegar a las 9:00 en transporte público: metro, autobús, Cercanías y Metro Ligero.",
    // trabajo.max_min.aria: names the place, as the family one does
    commuteAria: "Tardar como mucho hasta el trabajo, en transporte público",
    icon: Briefcase,
  },
  family: {
    title: "Cerca de mi familia o amigos",
    // familia.ayuda: the same trip as the work place, so it says the declared proxy (D-240)
    help: "Miramos cuánto tardarías en transporte público llegando a las 9:00 de un día laborable.",
    commuteAria: "Tardar como mucho hasta mi familia o amigos, en transporte público",
    icon: Heart,
  },
  // lugar.ahora (D-244): where a retired household lives now, only with «Somos mayores»
  other: {
    title: "Donde vivimos ahora",
    help: "Miramos cuánto se tarda en transporte público hasta donde vivís ahora, llegando a las 9:00 de un día laborable.",
    commuteAria: "Tardar como mucho hasta donde vivimos ahora, en transporte público",
    icon: House,
  },
};

type Stations = WorkPlace[] | "loading" | "failed" | null;

/** The stations (about 130 KB) fail after this long if the API hangs, and the field asks again when used (M4). */
const STATIONS_TIMEOUT_MS = 15_000;

export interface StationList {
  stations: WorkPlace[];
  load: () => void;
}

/**
 * CRTM stations, asked when a field is first used (again after a failure); without them, the zones
 * still show. The search card holds them once for its two fields.
 */
export function useStations(): StationList {
  const [stations, setStations] = useState<Stations>(null);
  const load = useCallback(() => {
    if (stations !== null && stations !== "failed") return;
    setStations("loading");
    createApi()
      .places({ category: "transport", subcategories: Object.keys(STATION_KINDS) }, { timeoutMs: STATIONS_TIMEOUT_MS })
      .then((features) => setStations(stationPlaces(features)))
      .catch(() => setStations("failed"));
  }, [stations]);
  return { stations: Array.isArray(stations) ? stations : [], load };
}

/** «Tardar como mucho [n] en transporte público»: the trip limit of a place («Sin límite» sends null). */
function TripLimit({ kind, anchor }: { kind: PlaceKind; anchor: Anchor }) {
  const { update } = useScenario();
  return (
    <span className={`${styles.nearMinutes} ${styles.commuteLimit}`}>
      {TEXT.commuteBefore}
      <select
        className={styles.select}
        aria-label={KINDS[kind].commuteAria}
        value={anchor.max_minutes ?? ""}
        onChange={(e) => update((s) => setPlaceMaxMinutes(s, kind, e.target.value === "" ? null : Number(e.target.value)))}
      >
        <option value="">{TEXT.noLimit}</option>
        {commuteMinutesOptions(anchor.max_minutes).map((m) => (
          <option key={m} value={m}>
            {m} min
          </option>
        ))}
      </select>
      {TEXT.commuteAfter}
    </span>
  );
}

/** «¿Cuántos días vas a la oficina?» (D-240): with 1 or 2 the trip weighs half; with none it is not scored. */
function OfficeDays({ anchor }: { anchor: Anchor }) {
  const { update } = useScenario();
  const helpId = useId();
  const days = officeDays(anchor);
  const help = days > FEW_OFFICE_DAYS ? null : days === 0 ? TEXT.telework : TEXT.fewDays;
  return (
    <>
      <span className={`${styles.nearMinutes} ${styles.commuteLimit}`}>
        {TEXT.days}
        <select
          className={styles.select}
          aria-label={TEXT.days}
          aria-describedby={help ? helpId : undefined}
          value={days}
          onChange={(e) => update((s) => setWorkDays(s, Number(e.target.value)))}
        >
          {officeDaysOptions(days).map((n) => (
            <option key={n} value={n}>
              {TEXT.daysOption(n)}
            </option>
          ))}
        </select>
      </span>
      {help && (
        <p id={helpId} className={styles.help}>
          {help}
        </p>
      )}
    </>
  );
}

interface PickedProps {
  kind: PlaceKind;
  anchor: Anchor;
  /** The name of the place picked, when the anchor is called otherwise («Donde vivimos ahora») */
  placeName?: string | null;
  removeRef: RefObject<HTMLButtonElement | null>;
  onRemove: () => void;
}

/** The place picked, with its selectors: the days (work only) and its limit, which applies whatever the days. */
function PickedPlace({ kind, anchor, placeName, removeRef, onRemove }: PickedProps) {
  const Icon = KINDS[kind].icon;
  const name = placeName && placeName !== anchor.label ? `${anchor.label}: ${placeName}` : anchor.label;
  return (
    <>
      <p className={styles.place}>
        <Icon size={18} aria-hidden="true" />
        <span className={styles.placeName}>{name}</span>
        <button ref={removeRef} type="button" className={styles.remove} aria-label={`${TEXT.remove}: ${anchor.label}`} onClick={onRemove}>
          <X size={18} aria-hidden="true" />
        </button>
      </p>
      {kind === "work" && <OfficeDays anchor={anchor} />}
      <TripLimit kind={kind} anchor={anchor} />
    </>
  );
}

interface SearchProps {
  /** id of the text field, for its label */
  inputId: string;
  /** Name of the list of places («Trabajo en») */
  listLabel: string;
  helpId: string;
  stationList: StationList;
  inputRef: RefObject<HTMLInputElement | null>;
  onPick: (place: WorkPlace) => void;
}

/** The combobox (ARIA 1.2) over stations and zones that every place field shares. */
function PlaceSearch({ inputId, listLabel, helpId, stationList, inputRef, onPick }: SearchProps) {
  const { zones } = useMapZones();
  const { stations, load } = stationList;
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const places = useMemo(() => [...stations, ...(zones ? zonePlaces(zones) : [])], [stations, zones]);
  const found = useMemo(() => findPlaces(places, query), [places, query]);
  // No option is active until the arrows move into the list; a new list starts again from none
  const [cursor, setCursor] = useState<{ list: WorkPlace[]; index: number }>({ list: found, index: -1 });
  const active = cursor.list === found ? cursor.index : -1;
  const listed = open && found.length > 0;
  const typed = query.trim().length >= 2;

  const pick = (place: WorkPlace) => {
    onPick(place);
    setQuery("");
    setOpen(false);
  };

  const onKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      setOpen(true);
      setCursor({ list: found, index: stepActive(active, event.key === "ArrowDown" ? 1 : -1, found.length) });
    } else if (event.key === "Enter" && listed) {
      event.preventDefault();
      const place = found[active];
      if (place) pick(place);
    } else if (event.key === "Escape") {
      if (open) setOpen(false);
      else setQuery("");
    }
  };

  const status = !open || !typed ? "" : found.length === 0 ? TEXT.noMatch : TEXT.found(found.length);
  return (
    <div className={styles.combo}>
      <input
        ref={inputRef}
        id={inputId}
        className={styles.input}
        role="combobox"
        aria-expanded={listed}
        aria-controls={`${inputId}-list`}
        aria-autocomplete="list"
        aria-activedescendant={listed && active >= 0 ? `${inputId}-option-${active}` : undefined}
        aria-describedby={helpId}
        autoComplete="off"
        placeholder={TEXT.placeholder}
        value={query}
        onFocus={() => {
          load();
          setOpen(true);
        }}
        onBlur={() => setOpen(false)}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
        }}
        onKeyDown={onKeyDown}
      />
      <ul id={`${inputId}-list`} role="listbox" aria-label={listLabel} className={styles.options} hidden={!listed}>
        {listed &&
          found.map((place, i) => (
            <li
              key={place.id}
              id={`${inputId}-option-${i}`}
              role="option"
              aria-selected={i === active}
              className={styles.option}
              // Keep the focus in the field: the option is picked on click, not on blur
              onMouseDown={(e) => e.preventDefault()}
              onClick={() => pick(place)}
            >
              <span>{place.label}</span>
              <small>{place.kind}</small>
            </li>
          ))}
      </ul>
      {open && typed && found.length === 0 && <p className={styles.help}>{TEXT.noMatch}</p>}
      {/* Always there, so screen readers hear how many places match while typing */}
      <p role="status" className="visually-hidden">
        {status}
      </p>
    </div>
  );
}

/** Where the focus goes once the field and the picked place swap places, after the anchor changes. */
function useSwapFocus(anchor: Anchor | null) {
  const input = useRef<HTMLInputElement>(null);
  const remove = useRef<HTMLButtonElement>(null);
  const next = useRef<"input" | "remove" | null>(null);
  useEffect(() => {
    if (next.current === "remove") remove.current?.focus();
    if (next.current === "input") input.current?.focus();
    next.current = null;
  }, [anchor]);
  const focusNext = (where: "input" | "remove") => {
    next.current = where;
  };
  return { input, remove, focusNext };
}

/**
 * «Trabajo en» and «Cerca de mi familia o amigos»: the place search, then the place picked. It goes
 * to the search without a minutes limit until «Tardar como mucho» sets one.
 */
export default function PlaceField({ kind, stationList, id: fieldId }: { kind: PlaceKind; stationList: StationList; id?: string }) {
  const { scenario, update } = useScenario();
  const id = useId();
  const anchor = placeOf(scenario, kind);
  const { title, help } = KINDS[kind];
  const { input, remove, focusNext } = useSwapFocus(anchor);

  const name = (
    <>
      {title} <span className={styles.optional}>{TEXT.optional}</span>
    </>
  );
  return (
    <div id={fieldId} className={styles.group}>
      {anchor ? (
        <p className={styles.legend}>{name}</p>
      ) : (
        <label htmlFor={`${id}-input`} className={styles.legend}>
          {name}
        </label>
      )}
      {anchor ? (
        <PickedPlace
          kind={kind}
          anchor={anchor}
          removeRef={remove}
          onRemove={() => {
            focusNext("input");
            update((s) => setPlace(s, kind, null));
          }}
        />
      ) : (
        <PlaceSearch
          inputId={`${id}-input`}
          listLabel={title}
          helpId={`${id}-help`}
          stationList={stationList}
          inputRef={input}
          onPick={(place) => {
            focusNext("remove");
            update((s) => setPlace(s, kind, place));
          }}
        />
      )}
      <Help about={title} id={`${id}-help`}>
        <p>{help}</p>
      </Help>
    </div>
  );
}

/**
 * «¿Cerca de dónde queréis vivir?» (D-244, Mariano's design), in place of «Trabajo en» with «Somos
 * mayores»: where they live now or near their family, picked with the same place search, and
 * 30 min as most by public transport, which the person can change. Optional, and always in view.
 */
export function OlderPlaceField({ stationList, id: fieldId }: { stationList: StationList; id?: string }) {
  const { scenario, update } = useScenario();
  const id = useId();
  const current = olderPlace(scenario);
  // Which of the two before a place is picked; then, the kind of the place
  const [chosen, setChosen] = useState<OlderPlaceKind>("other");
  const kind = current?.kind ?? chosen;
  // The name of the place picked, kept to show it beside «Donde vivimos ahora» and to name the family's
  const [placeName, setPlaceName] = useState<string | null>(null);
  const { input, remove, focusNext } = useSwapFocus(current?.anchor ?? null);

  return (
    <fieldset id={fieldId} className={styles.group}>
      <legend>
        {TEXT.older.title} <span className={styles.optional}>{TEXT.optional}</span>
      </legend>
      <Segmented
        legend={TEXT.older.title}
        value={kind}
        options={(["other", "family"] as const).map((value) => ({ value, label: TEXT.older.options[value] }))}
        onChange={(next) => {
          setChosen(next);
          if (current) update((s) => setOlderPlaceKind(s, next, placeName ?? TEXT.older.family));
        }}
      />
      {current ? (
        <PickedPlace
          kind={current.kind}
          anchor={current.anchor}
          placeName={placeName}
          removeRef={remove}
          onRemove={() => {
            focusNext("input");
            setPlaceName(null);
            update((s) => setOlderPlace(s, kind, null));
          }}
        />
      ) : (
        <>
          <label htmlFor={`${id}-input`} className={styles.areaPick}>
            {TEXT.older.search[kind]}
          </label>
          <PlaceSearch
            inputId={`${id}-input`}
            listLabel={TEXT.older.search[kind]}
            helpId={`${id}-help`}
            stationList={stationList}
            inputRef={input}
            onPick={(place) => {
              focusNext("remove");
              setPlaceName(place.label);
              update((s) => setOlderPlace(s, kind, place));
            }}
          />
        </>
      )}
      <Help about={TEXT.older.title} id={`${id}-help`}>
        <p>{TEXT.older.help}</p>
      </Help>
    </fieldset>
  );
}
