"use client";

import { Briefcase, X } from "lucide-react";
import { type KeyboardEvent, useCallback, useEffect, useId, useMemo, useRef, useState } from "react";

import { useMapZones } from "@/components/map/MapProvider";
import { createApi } from "@/lib/api";
import { setWorkPlace, workPlace } from "@/lib/scenario";
import { findPlaces, STATION_KINDS, stationPlaces, stepActive, type WorkPlace, zonePlaces } from "@/lib/workPlaces";

import styles from "./SearchCard.module.css";
import { useScenario } from "./ScenarioProvider";

// Copy from pitch/textos_web.md (trabajo.*). The placeholder and «no results» name stations instead
// of streets (there is no street search without an external geocoder), and the count of places
// found is new: provisional, pending line D.
const TEXT = {
  title: "Trabajo en",
  help: "Así miramos lo lejos que te queda cada zona.",
  placeholder: "Escribe una estación, un distrito o un municipio",
  noMatch: "No encontramos ese lugar. Prueba con una estación o con el nombre del municipio.",
  found: (n: number) => (n === 1 ? "1 lugar encontrado. Usa las flechas para elegirlo." : `${n} lugares encontrados. Usa las flechas para elegir uno.`),
  remove: "Quitar este lugar",
  // trabajo.max_min is not shown until CORE-009 (the search sends the work place without a limit)
  transitSoon: "Tiempo en transporte: muy pronto",
};

type Stations = WorkPlace[] | "loading" | "failed" | null;

/** CRTM stations, asked when the field is first used (again after a failure); without them, the zones still show. */
function useStations(): { stations: WorkPlace[]; load: () => void } {
  const [stations, setStations] = useState<Stations>(null);
  const load = useCallback(() => {
    if (stations !== null && stations !== "failed") return;
    setStations("loading");
    createApi()
      .places({ category: "transport", subcategories: Object.keys(STATION_KINDS) })
      .then((features) => setStations(stationPlaces(features)))
      .catch(() => setStations("failed"));
  }, [stations]);
  return { stations: Array.isArray(stations) ? stations : [], load };
}

/**
 * «Trabajo en»: a combobox (ARIA 1.2) over stations and zones. The place goes to the search as a
 * reference without a minutes limit: the zone card says how far each zone is.
 */
export default function WorkField() {
  const { scenario, update } = useScenario();
  const { zones } = useMapZones();
  const { stations, load } = useStations();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const id = useId();
  const anchor = workPlace(scenario);
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
    update((s) => setWorkPlace(s, place));
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
          {TEXT.title} <span className={styles.legendHelp}>{TEXT.help}</span>
        </p>
      ) : (
        <label htmlFor={`${id}-input`} className={styles.legend}>
          {TEXT.title} <span className={styles.legendHelp}>{TEXT.help}</span>
        </label>
      )}
      {anchor ? (
        <p className={styles.place}>
          <Briefcase size={18} aria-hidden="true" />
          <span className={styles.placeName}>{anchor.label}</span>
          <button
            ref={remove}
            type="button"
            className={styles.remove}
            aria-label={`${TEXT.remove}: ${anchor.label}`}
            onClick={() => {
              focusNext.current = "input";
              update((s) => setWorkPlace(s, null));
            }}
          >
            <X size={18} aria-hidden="true" />
          </button>
        </p>
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
          <ul id={`${id}-list`} role="listbox" aria-label={TEXT.title} className={styles.options} hidden={!listed}>
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
      <p className={styles.help}>
        <span className={styles.soonTag}>{TEXT.transitSoon}</span>
      </p>
    </div>
  );
}
