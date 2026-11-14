"use client";

import { Briefcase, Heart, type LucideIcon, X } from "lucide-react";
import { type KeyboardEvent, type RefObject, useCallback, useEffect, useId, useMemo, useRef, useState } from "react";

import { useMapZones } from "@/components/map/MapProvider";
import type { Anchor } from "@/contracts/scenario_state";
import { createApi } from "@/lib/api";
import {
  commuteMinutesOptions,
  FEW_OFFICE_DAYS,
  officeDays,
  officeDaysOptions,
  type PlaceKind,
  placeOf,
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
  // trabajo.max_min, «Tardar como mucho {n} min en transporte público», with the minutes as a selector
  commuteBefore: "Tardar como mucho",
  commuteAfter: "en transporte público",
  noLimit: "Sin límite",
  // trabajo.dias (D-240): how many days the person goes weighs the trip to work
  days: "¿Cuántos días vas a la oficina?",
  daysOption: (n: number) => (n === 0 ? "Teletrabajo total" : n === 1 ? "1 día" : `${n} días`),
  fewDays: "Como vas pocos días, el trayecto cuenta la mitad.",
  telework: "Con teletrabajo total, el trayecto no cuenta en el encaje. Si pones un límite, lo respetamos.",
};

/** What changes from «Trabajo en» to «Cerca de mi familia o amigos»; the rest is the same field. */
const KINDS: Record<PlaceKind, { title: string; help: string; commuteAria: string; icon: LucideIcon }> = {
  work: {
    title: "Trabajo en",
    // trabajo.ayuda (14 nov): the commute is measured in public transport minutes (CORE-009, D-220), all the CRTM feeds
    help: "Miramos cuánto tardarías en llegar a las 9:00 en transporte público: metro, autobús (EMT e interurbanos), Cercanías y Metro Ligero.",
    commuteAria: "Tardar como mucho, en transporte público",
    icon: Briefcase,
  },
  family: {
    title: "Cerca de mi familia o amigos",
    // familia.ayuda: the same trip as the work place (the API measures it arriving by 9:00)
    help: "Opcional. Miramos cuánto tardarías en llegar en transporte público.",
    commuteAria: "Tardar como mucho hasta mi familia o amigos, en transporte público",
    icon: Heart,
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
  const days = officeDays(anchor);
  return (
    <>
      <span className={`${styles.nearMinutes} ${styles.commuteLimit}`}>
        {TEXT.days}
        <select className={styles.select} aria-label={TEXT.days} value={days} onChange={(e) => update((s) => setWorkDays(s, Number(e.target.value)))}>
          {officeDaysOptions(days).map((n) => (
            <option key={n} value={n}>
              {TEXT.daysOption(n)}
            </option>
          ))}
        </select>
      </span>
      {days <= FEW_OFFICE_DAYS && <p className={styles.help}>{days === 0 ? TEXT.telework : TEXT.fewDays}</p>}
    </>
  );
}

interface PickedProps {
  kind: PlaceKind;
  anchor: Anchor;
  removeRef: RefObject<HTMLButtonElement | null>;
  onRemove: () => void;
}

/** The place picked, with its selectors: the days (work only) and its limit, which applies whatever the days. */
function PickedPlace({ kind, anchor, removeRef, onRemove }: PickedProps) {
  const Icon = KINDS[kind].icon;
  return (
    <>
      <p className={styles.place}>
        <Icon size={18} aria-hidden="true" />
        <span className={styles.placeName}>{anchor.label}</span>
        <button ref={removeRef} type="button" className={styles.remove} aria-label={`${TEXT.remove}: ${anchor.label}`} onClick={onRemove}>
          <X size={18} aria-hidden="true" />
        </button>
      </p>
      {kind === "work" && <OfficeDays anchor={anchor} />}
      <TripLimit kind={kind} anchor={anchor} />
    </>
  );
}

/**
 * «Trabajo en» and «Cerca de mi familia o amigos»: a combobox (ARIA 1.2) over stations and zones. The
 * place goes to the search without a minutes limit until «Tardar como mucho» sets one.
 */
export default function PlaceField({ kind, stationList }: { kind: PlaceKind; stationList: StationList }) {
  const { scenario, update } = useScenario();
  const { zones } = useMapZones();
  const { stations, load } = stationList;
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const id = useId();
  const anchor = placeOf(scenario, kind);
  const { title, help } = KINDS[kind];
  const input = useRef<HTMLInputElement>(null);
  const remove = useRef<HTMLButtonElement>(null);
  // Where the focus goes once the field and the picked place swap places
  const focusNext = useRef<"input" | "remove" | null>(null);

  const places = useMemo(() => [...stations, ...(zones ? zonePlaces(zones) : [])], [stations, zones]);
  const found = useMemo(() => findPlaces(places, query), [places, query]);
  // No option is active until the arrows move into the list; a new list starts again from none
  const [cursor, setCursor] = useState<{ list: WorkPlace[]; index: number }>({ list: found, index: -1 });
  const active = cursor.list === found ? cursor.index : -1;
  const listed = open && found.length > 0;
  const typed = query.trim().length >= 2;

  useEffect(() => {
    if (focusNext.current === "remove") remove.current?.focus();
    if (focusNext.current === "input") input.current?.focus();
    focusNext.current = null;
  }, [anchor]);

  const pick = (place: WorkPlace) => {
    focusNext.current = "remove";
    update((s) => setPlace(s, kind, place));
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
    <div className={`${styles.group} ${styles.work}`}>
      {anchor ? (
        <p className={styles.legend}>
          {title} <span className={styles.legendHelp}>{help}</span>
        </p>
      ) : (
        <label htmlFor={`${id}-input`} className={styles.legend}>
          {title} <span className={styles.legendHelp}>{help}</span>
        </label>
      )}
      {anchor ? (
        <PickedPlace
          kind={kind}
          anchor={anchor}
          removeRef={remove}
          onRemove={() => {
            focusNext.current = "input";
            update((s) => setPlace(s, kind, null));
          }}
        />
      ) : (
        <div className={styles.combo}>
          <input
            ref={input}
            id={`${id}-input`}
            className={styles.input}
            role="combobox"
            aria-expanded={listed}
            aria-controls={`${id}-list`}
            aria-autocomplete="list"
            aria-activedescendant={listed && active >= 0 ? `${id}-option-${active}` : undefined}
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
          <ul id={`${id}-list`} role="listbox" aria-label={title} className={styles.options} hidden={!listed}>
            {listed &&
              found.map((place, i) => (
                <li
                  key={place.id}
                  id={`${id}-option-${i}`}
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
        </div>
      )}
      {/* Always there, so screen readers hear how many places match while typing */}
      <p role="status" className="visually-hidden">
        {status}
      </p>
    </div>
  );
}
