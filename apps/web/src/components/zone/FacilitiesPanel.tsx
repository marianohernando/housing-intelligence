"use client";

import { Baby, Cross, Dumbbell, GraduationCap, HeartHandshake, Hospital, Landmark, type LucideIcon, Pill, Trees, Utensils, Wine } from "lucide-react";
import { useId } from "react";

import { useFacilityLayer } from "@/components/map/FacilityLayerProvider";
import { useDatasets } from "@/components/provenance/useDatasets";
import Button from "@/components/ui/Button";
import Chip from "@/components/ui/Chip";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { errorMessage } from "@/lib/errors";
import { formatNumber } from "@/lib/format";
import {
  capacitySources,
  type Facility,
  FACILITY_COLOR_TOKEN,
  type FacilityKey,
  facilityCountText,
  facilityType,
  offeredTypes,
  orderedTypes,
  selectedCountText,
} from "@/lib/map/facilities";

import styles from "./FacilitiesPanel.module.css";

// Copy of pitch/textos_web.md, section 5b (T3), with centros.camas and centros.sin_nombre_algunos (HOSP-001).
const TEXT = {
  title: "Todos los centros",
  show: "Ver en el mapa",
  loading: (zone: string) => `Buscando los centros de ${zone}…`,
  retry: "Reintentar",
  none: "Toca uno o varios tipos de centro para verlos en el mapa.", // B's draft for D (several at once)
  all: "Todos",
  nothing: "Ninguno",
  list: (n: number) => `Ver la lista (${formatNumber(n, 0)})`,
  // The same schools as the row «Colegios» (gap_rows of places-1): public and concertado
  rowSchools: "Públicos y concertados: los mismos que cuenta «Qué falta».",
  noName: "La fuente oficial no publica el nombre de cada centro de este tipo.",
  // centros.sin_nombre_algunos: the name comes from the Ministry's catalogues; a few could not be matched
  someNoName: "Algunos centros salen sin nombre porque no hemos podido comprobarlo en las fuentes oficiales.",
  // centros.camas (HOSP-001, D-218): the date and the catalogue from /datasets
  // centros.ocio.fuente (D-236): leisure comes from OpenStreetMap, never an official register
  leisure: "Según OpenStreetMap, un mapa hecho por voluntarios: puede faltar algún local o salir sin nombre.",
  bedsBefore: (updated: string | null) => `Camas instaladas${updated ? ` a ${updated}` : ""}, según el `,
  bedsAfter: (publisher: string) => ` del ${publisher}.`,
  newTab: " (se abre en una pestaña nueva)",
};

/** centros.camas: «Camas instaladas a 31 de diciembre de 2024, según el Catálogo … 2025 del Ministerio de Sanidad.» */
function CapacitySourceLine({ type, items }: { type: FacilityKey; items: Facility[] }) {
  const { data } = useDatasets();
  return capacitySources(type, items, data?.datasets ?? null).map((source) => (
    <p key={source.id} className={styles.muted}>
      {TEXT.bedsBefore(source.updated)}
      {source.href ? (
        <a href={source.href} target="_blank" rel="noopener noreferrer">
          {source.catalogue}
          <span className="visually-hidden">{TEXT.newTab}</span>
        </a>
      ) : (
        source.catalogue
      )}
      {TEXT.bedsAfter(source.publisher)}
    </p>
  ));
}

export const FACILITY_ICON: Record<FacilityKey, LucideIcon> = {
  colegio: GraduationCap,
  escuela_infantil: Baby,
  centro_salud: Cross,
  hospital: Hospital,
  farmacia: Pill,
  mayores: HeartHandshake,
  parque: Trees,
  bares: Wine,
  restaurantes: Utensils,
  gimnasios: Dumbbell,
  cultura: Landmark,
};

/** «Hospital La Paz · 1.300 camas» when the API gives the name and the capacity; the label alone otherwise. */
export function facilityLine(f: Facility): { label: string; rest: string | null } {
  const rest = [f.name, f.detail].filter(Boolean).join(" · ");
  return { label: f.label, rest: rest || null };
}

/** In the list a park leads with its own name («Parque del Retiro · 118 ha»): the list already says it is a park. */
function listLine(f: Facility): { label: string; rest: string | null } {
  return f.name && facilityType(f.type).nameFirst ? { label: f.name, rest: f.detail } : facilityLine(f);
}

function FacilityList({ items, count }: { items: Facility[]; count: string }) {
  return (
    <details className={styles.details}>
      <summary>{TEXT.list(items.length)}</summary>
      {/* Focusable, so the list can be scrolled with the keyboard */}
      <ul className={styles.list} tabIndex={0} aria-label={count}>
        {items.map((f) => {
          const { label, rest } = listLine(f);
          return (
            <li key={f.id}>
              <strong>{label}</strong>
              {rest && <span> · {rest}</span>}
            </li>
          );
        })}
      </ul>
    </details>
  );
}

/** One type pressed: how many there are in the zone, what the source does not say, and its list. */
function TypeSummary({ type, items, zone }: { type: FacilityKey; items: Facility[]; zone: string }) {
  const count = facilityCountText(type, items.length, zone);
  return (
    <div className={styles.typeSummary}>
      <p className={styles.count}>
        <span className={styles.dot} style={{ background: `var(--${FACILITY_COLOR_TOKEN[type]})` }} aria-hidden="true" />
        {count}
      </p>
      {type === "colegio" && items.length > 0 && <p className={styles.muted}>{TEXT.rowSchools}</p>}
      {facilityType(type).leisure ? (
        <p className={styles.muted}>{TEXT.leisure}</p>
      ) : (
        items.some((f) => f.name === null) && (
          <p className={styles.muted}>{items.every((f) => f.name === null) ? TEXT.noName : TEXT.someNoName}</p>
        )
      )}
      <CapacitySourceLine type={type} items={items} />
      {items.length > 0 && <FacilityList items={items} count={count} />}
    </div>
  );
}

/**
 * «Todos los centros» (FASE_PRUEBAS, T3): every facility of the zone, not only its key points. A
 * button per type with how many there are; several types can be on at once (petición de Mariano,
 * 13 nov), each with its colour on the map, grouped, and listed here, which is also the way to see
 * them without the map. Filtered on the client: /places brought them all in one request.
 */
export default function FacilitiesPanel({ zone }: { zone: string }) {
  const { status, groups, error, retry, types, toggle, setAll } = useFacilityLayer();
  const titleId = useId();
  const slow = useSlow(status === "loading");
  // Leisure is only offered where the zone has some (D-236): a type not offered is never listed
  const offered = groups ? offeredTypes(groups) : [];
  const shown = orderedTypes(types).filter((key) => offered.some((t) => t.key === key));

  return (
    <GlassCard as="section" aria-labelledby={titleId} className={styles.card}>
      <h2 id={titleId} className={styles.title}>
        {TEXT.title}
      </h2>
      {status === "loading" && (
        <p role="status" className={styles.muted}>
          {TEXT.loading(zone)}
          {slow && ` ${SLOW_TEXT}`}
        </p>
      )}
      {status === "error" && error && (
        <div role="alert" className={styles.error}>
          <p>{errorMessage(error)}</p>
          <Button variant="secondary" onClick={retry}>
            {TEXT.retry}
          </Button>
        </div>
      )}
      {groups && (
        <>
          <div role="group" aria-labelledby={`${titleId}-show`} className={styles.types}>
            <p id={`${titleId}-show`} className="visually-hidden">
              {TEXT.show}
            </p>
            <ul className={styles.chips}>
              {offered.map((t) => (
                <li key={t.key}>
                  <Chip
                    label={t.chip}
                    icon={FACILITY_ICON[t.key]}
                    color={`var(--${FACILITY_COLOR_TOKEN[t.key]})`}
                    count={formatNumber(groups[t.key].length, 0)}
                    pressed={types.includes(t.key)}
                    onToggle={() => toggle(t.key)}
                  />
                </li>
              ))}
            </ul>
            <div className={styles.all}>
              <button type="button" onClick={() => setAll(true)} disabled={shown.length === offered.length}>
                {TEXT.all}
              </button>
              <button type="button" onClick={() => setAll(false)} disabled={shown.length === 0}>
                {TEXT.nothing}
              </button>
            </div>
          </div>
          {/* Told when the types change; the lists below are not read out each time */}
          <p role="status" aria-live="polite" className="visually-hidden">
            {selectedCountText(groups, shown, zone) ?? TEXT.none}
          </p>
          <div className={styles.summary}>
            {shown.length ? (
              shown.map((type) => <TypeSummary key={type} type={type} items={groups[type]} zone={zone} />)
            ) : (
              <p className={styles.muted}>{TEXT.none}</p>
            )}
          </div>
        </>
      )}
    </GlassCard>
  );
}
