"use client";

import Link from "next/link";
import { useEffect, useId, useState } from "react";

import { fetchZones } from "@/components/map/fetchZones";
import { useGapRowMap } from "@/components/map/useGapRowMap";
import Button from "@/components/ui/Button";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import type { ZoneGapStatus } from "@/contracts/gap_row_map_response";
import type { GapRowKey } from "@/contracts/zone_gap_list_response";
import { ApiError } from "@/lib/api";
import { errorMessage } from "@/lib/errors";
import { gapsHref, isSmallZone } from "@/lib/gaps";
import { searchable, wholeCities, zoneDirectory, type ZoneCollection, zoneHref, type ZoneProperties } from "@/lib/map/zones";

import GapBadge from "./GapBadge";
import SmallZoneTag from "./SmallZoneTag";
import styles from "./ZoneDirectory.module.css";

// Copy: carga.mapa and error.reintentar from pitch/textos_web.md; the rest is provisional (pending line D).
const TEXT = {
  loading: "Cargando las zonas…",
  retry: "Reintentar",
  search: "Busca una zona",
  distritos: "Distritos de Madrid",
  municipios: "Municipios",
  none: "No hay ninguna zona con ese nombre.",
  wholeCity: (name: string) => `${name} (toda la ciudad)`,
  loadingRow: "Cargando el estado de cada zona…",
};

type Result = { zones: ZoneCollection } | { error: ApiError };

type HrefFor = (zone: ZoneProperties) => string;

interface LinksProps {
  title: string;
  zones: ZoneProperties[];
  hrefFor: HrefFor;
  /** Each zone's status in a row of «Qué falta», when the list shows one */
  statuses?: ReadonlyMap<string, ZoneGapStatus> | null;
}

function ZoneLinks({ title, zones, hrefFor, statuses }: LinksProps) {
  const id = useId();
  if (zones.length === 0) return null;
  return (
    <section aria-labelledby={id} className={styles.group}>
      <h2 id={id}>
        {title} <span className={styles.count}>({zones.length})</span>
      </h2>
      <ul className={styles.list}>
        {zones.map((zone) => {
          const gap = statuses?.get(zone.admin_unit_id);
          return (
            <li key={zone.zone_key}>
              <Link href={hrefFor(zone)}>{zone.name}</Link>
              {gap && <GapBadge status={gap.status} />}
              {gap && isSmallZone(gap) && <SmallZoneTag />}
            </li>
          );
        })}
      </ul>
    </section>
  );
}

interface Props {
  /** Where each zone leads: its screen by default, its «Qué falta» list from that tab. */
  hrefFor?: HrefFor;
  placeholder?: string;
  /** The map's alternative for a row of «Qué falta»: each zone with its status in that row. */
  row?: GapRowKey | null;
  /** Also list Madrid capital as a whole, whose «Qué falta» list exists although the map splits it. */
  wholeCities?: boolean;
}

/** The map's alternative: every zone as a link, with a filter by name (keyboard and screen readers). */
export default function ZoneDirectory({ hrefFor = zoneHref, placeholder, row = null, wholeCities: withCities = false }: Props) {
  const rowMap = useGapRowMap(row);
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
  // The whole city leads to its «Qué falta» list: on the map it is its districts
  const cities = withCities
    ? wholeCities(result.zones).filter((c) => searchable(TEXT.wholeCity(c.name)).includes(searchable(query)))
    : [];
  return (
    <div className={styles.directory}>
      <label htmlFor={inputId} className={styles.label}>
        {TEXT.search}
      </label>
      <input id={inputId} type="search" placeholder={placeholder} value={query} onChange={(e) => setQuery(e.target.value)} className={styles.input} />
      <p role="status" className="visually-hidden">
        {distritos.length + municipios.length} zonas
      </p>
      {distritos.length + municipios.length + cities.length === 0 && <p>{TEXT.none}</p>}
      {cities.length > 0 && (
        <ul className={styles.list}>
          {cities.map((city) => {
            const gap = rowMap.data?.byZone.get(city.admin_unit_id);
            return (
              <li key={city.admin_unit_id}>
                <Link href={gapsHref("municipio", city.code)}>{TEXT.wholeCity(city.name)}</Link>
                {gap && <GapBadge status={gap.status} />}
                {gap && isSmallZone(gap) && <SmallZoneTag />}
              </li>
            );
          })}
        </ul>
      )}
      {row && rowMap.loading && <p role="status">{TEXT.loadingRow}</p>}
      {row && rowMap.error && (
        <div role="alert" className={styles.error}>
          <p>{errorMessage(rowMap.error)}</p>
          <Button variant="secondary" onClick={rowMap.retry}>
            {TEXT.retry}
          </Button>
        </div>
      )}
      <ZoneLinks title={TEXT.distritos} zones={distritos} hrefFor={hrefFor} statuses={rowMap.data?.byZone} />
      <ZoneLinks title={TEXT.municipios} zones={municipios} hrefFor={hrefFor} statuses={rowMap.data?.byZone} />
    </div>
  );
}
