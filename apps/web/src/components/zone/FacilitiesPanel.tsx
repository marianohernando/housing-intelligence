"use client";

import { Baby, Cross, GraduationCap, HeartHandshake, Hospital, type LucideIcon, Pill } from "lucide-react";
import { useId } from "react";

import { useFacilityLayer } from "@/components/map/FacilityLayerProvider";
import { useDatasets } from "@/components/provenance/useDatasets";
import Button from "@/components/ui/Button";
import Chip from "@/components/ui/Chip";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { errorMessage } from "@/lib/errors";
import { formatNumber } from "@/lib/format";
import { capacitySources, type Facility, type FacilityKey, facilityCountText, FACILITY_TYPES } from "@/lib/map/facilities";

import styles from "./FacilitiesPanel.module.css";

// Copy of pitch/textos_web.md, section 5b (T3). «Camas:» and «algunos de estos centros» (HOSP-001)
// are provisional, listed for line D in the PR.
const TEXT = {
  title: "Todos los centros",
  show: "Ver en el mapa",
  loading: (zone: string) => `Buscando los centros de ${zone}…`,
  retry: "Reintentar",
  none: "Toca un tipo de centro para verlo en el mapa.",
  list: (n: number) => `Ver la lista (${formatNumber(n, 0)})`,
  // The same schools as the row «Colegios» (gap_rows of places-1): public and concertado
  rowSchools: "Públicos y concertados: los mismos que cuenta «Qué falta».",
  noName: "La fuente oficial no publica el nombre de cada centro de este tipo.",
  // Since HOSP-001 most hospitals and centros de salud have their name; a few still do not
  someNoName: "La fuente oficial no publica el nombre de algunos de estos centros.",
  // HOSP-001 (D-218): where the beds come from, named by /datasets (publisher, then the dataset)
  source: "Camas: ",
  newTab: " (se abre en una pestaña nueva)",
};

/** «Camas: Ministerio de Sanidad, Catálogo Nacional de Hospitales 2025», named by /datasets (a fixed source until it answers). */
function CapacitySourceLine({ type, items }: { type: FacilityKey; items: Facility[] }) {
  const { data } = useDatasets();
  const sources = capacitySources(type, items, data?.datasets ?? null);
  if (sources.length === 0) return null;
  return (
    <p className={styles.muted}>
      {TEXT.source}
      {sources.map((source, i) => (
        <span key={source.id}>
          {i > 0 && "; "}
          {source.url ? (
            <a href={source.url} target="_blank" rel="noopener noreferrer">
              {source.label}
              <span className="visually-hidden">{TEXT.newTab}</span>
            </a>
          ) : (
            source.label
          )}
        </span>
      ))}
    </p>
  );
}

export const FACILITY_ICON: Record<FacilityKey, LucideIcon> = {
  colegio: GraduationCap,
  escuela_infantil: Baby,
  centro_salud: Cross,
  hospital: Hospital,
  farmacia: Pill,
  mayores: HeartHandshake,
};

/** «Hospital La Paz · 1.300 camas» when the API gives the name and the capacity; the label alone otherwise. */
export function facilityLine(f: Facility): { label: string; rest: string | null } {
  const rest = [f.name, f.detail].filter(Boolean).join(" · ");
  return { label: f.label, rest: rest || null };
}

function FacilityList({ items, count }: { items: Facility[]; count: string }) {
  return (
    <details className={styles.details}>
      <summary>{TEXT.list(items.length)}</summary>
      {/* Focusable, so the list can be scrolled with the keyboard */}
      <ul className={styles.list} tabIndex={0} aria-label={count}>
        {items.map((f) => {
          const { label, rest } = facilityLine(f);
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

/**
 * «Todos los centros» (FASE_PRUEBAS, T3): every facility of the zone, not only its key points. A
 * button per type with how many there are; the type pressed is shown on the map, grouped, and
 * listed here, which is also the way to see them without the map.
 */
export default function FacilitiesPanel({ zone }: { zone: string }) {
  const { status, groups, error, retry, type, setType } = useFacilityLayer();
  const titleId = useId();
  const slow = useSlow(status === "loading");
  const items = type && groups ? groups[type] : null;
  const count = type && items ? facilityCountText(type, items.length, zone) : null;

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
              {FACILITY_TYPES.map((t) => (
                <li key={t.key}>
                  <Chip
                    label={t.chip}
                    icon={FACILITY_ICON[t.key]}
                    count={formatNumber(groups[t.key].length, 0)}
                    pressed={type === t.key}
                    onToggle={() => setType(type === t.key ? null : t.key)}
                  />
                </li>
              ))}
            </ul>
          </div>
          <div aria-live="polite" className={styles.summary}>
            {type && count && items ? (
              <>
                <p className={styles.count}>{count}</p>
                {type === "colegio" && items.length > 0 && <p className={styles.muted}>{TEXT.rowSchools}</p>}
                {items.some((f) => f.name === null) && (
                  <p className={styles.muted}>{items.every((f) => f.name === null) ? TEXT.noName : TEXT.someNoName}</p>
                )}
                <CapacitySourceLine type={type} items={items} />
              </>
            ) : (
              <p className={styles.muted}>{TEXT.none}</p>
            )}
          </div>
          {count && items && items.length > 0 && <FacilityList key={type} items={items} count={count} />}
        </>
      )}
    </GlassCard>
  );
}
