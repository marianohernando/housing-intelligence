"use client";

import Link from "next/link";
import { useEffect, useId, useState } from "react";

import { fetchZones } from "@/components/map/fetchZones";
import Button from "@/components/ui/Button";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { ApiError } from "@/lib/api";
import { errorMessage } from "@/lib/errors";
import { zoneDirectory, type ZoneCollection, zoneHref, type ZoneProperties } from "@/lib/map/zones";

import styles from "./ZoneDirectory.module.css";

// Copy: carga.mapa and error.reintentar from pitch/textos_web.md; the rest is provisional (pending line D).
const TEXT = {
  loading: "Cargando las zonas…",
  retry: "Reintentar",
  search: "Busca una zona",
  distritos: "Distritos de Madrid",
  municipios: "Municipios",
  none: "No hay ninguna zona con ese nombre.",
};

type Result = { zones: ZoneCollection } | { error: ApiError };

type HrefFor = (zone: ZoneProperties) => string;

function ZoneLinks({ title, zones, hrefFor }: { title: string; zones: ZoneProperties[]; hrefFor: HrefFor }) {
  const id = useId();
  if (zones.length === 0) return null;
  return (
    <section aria-labelledby={id} className={styles.group}>
      <h2 id={id}>
        {title} <span className={styles.count}>({zones.length})</span>
      </h2>
      <ul className={styles.list}>
        {zones.map((zone) => (
          <li key={zone.zone_key}>
            <Link href={hrefFor(zone)}>{zone.name}</Link>
          </li>
        ))}
      </ul>
    </section>
  );
}

interface Props {
  /** Where each zone leads: its screen by default, its «Qué falta» list from that tab. */
  hrefFor?: HrefFor;
  placeholder?: string;
}

/** The map's alternative: every zone as a link, with a filter by name (keyboard and screen readers). */
export default function ZoneDirectory({ hrefFor = zoneHref, placeholder }: Props) {
  const inputId = useId();
  const [result, setResult] = useState<Result | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState("");
  const slow = useSlow(result === null);

  useEffect(() => {
    let cancelled = false;
    fetchZones()
      .then((zones) => {
        if (!cancelled) setResult({ zones });
      })
      .catch((exc: unknown) => {
        if (!cancelled) setResult({ error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)) });
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  if (!result) {
    return (
      <p role="status">
        {TEXT.loading}
        {slow && ` ${SLOW_TEXT}`}
      </p>
    );
  }
  if ("error" in result) {
    return (
      <div role="alert" className={styles.error}>
        <p>{errorMessage(result.error)}</p>
        <Button
          variant="secondary"
          onClick={() => {
            setResult(null);
            setAttempt((n) => n + 1);
          }}
        >
          {TEXT.retry}
        </Button>
      </div>
    );
  }
  const { distritos, municipios } = zoneDirectory(result.zones, query);
  return (
    <div className={styles.directory}>
      <label htmlFor={inputId} className={styles.label}>
        {TEXT.search}
      </label>
      <input id={inputId} type="search" placeholder={placeholder} value={query} onChange={(e) => setQuery(e.target.value)} className={styles.input} />
      <p role="status" className="visually-hidden">
        {distritos.length + municipios.length} zonas
      </p>
      {distritos.length + municipios.length === 0 && <p>{TEXT.none}</p>}
      <ZoneLinks title={TEXT.distritos} zones={distritos} hrefFor={hrefFor} />
      <ZoneLinks title={TEXT.municipios} zones={municipios} hrefFor={hrefFor} />
    </div>
  );
}
