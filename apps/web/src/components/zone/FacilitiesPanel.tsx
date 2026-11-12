"use client";

import { Baby, Cross, GraduationCap, HeartHandshake, Hospital, type LucideIcon, Pill } from "lucide-react";
import { useId } from "react";

import { useFacilityLayer } from "@/components/map/FacilityLayerProvider";
import Button from "@/components/ui/Button";
import Chip from "@/components/ui/Chip";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { errorMessage } from "@/lib/errors";
import { formatNumber } from "@/lib/format";
import { type Facility, type FacilityKey, facilityCountText, FACILITY_TYPES } from "@/lib/map/facilities";

import styles from "./FacilitiesPanel.module.css";

// Provisional copy (T3), written with the rules of pitch/textos_web.md; listed for line D in the PR.
const TEXT = {
  title: "Todos los centros",
  show: "Ver en el mapa",
  loading: (zone: string) => `Buscando los centros de ${zone}…`,
  retry: "Reintentar",
  none: "Toca un tipo de centro para verlo en el mapa.",
  list: (n: number) => `Ver la lista (${formatNumber(n, 0)})`,
  // The row «Colegios» counts public and concertado schools only (titularidad, not in /places yet)
  privateSchools: "Aquí salen también los colegios privados. En «Qué falta» solo contamos los públicos y los concertados.",
  noName: "La fuente oficial no publica el nombre de cada centro de este tipo.",
};

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
            {count && items ? (
              <>
                <p className={styles.count}>{count}</p>
                {type === "colegio" && items.length > 0 && <p className={styles.muted}>{TEXT.privateSchools}</p>}
                {items.some((f) => f.name === null) && <p className={styles.muted}>{TEXT.noName}</p>}
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
