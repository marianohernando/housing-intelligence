"use client";

import { ExternalLink } from "lucide-react";
import { useEffect, useState } from "react";

import GlassCard from "@/components/ui/GlassCard";
import { createApi } from "@/lib/api";
import type { FeatureValueRow } from "@/lib/features";
import {
  type LandParcels,
  type NewHousingLevel,
  newHousingLines,
  type NewHousingRequest,
  newHousingRequests,
  type NewHousingRows,
  type NewHousingZone,
} from "@/lib/newHousing";
import { once } from "@/lib/once";
import { CONTEXT_CARD } from "@/lib/zoneContext";

import styles from "./NewHousing.module.css";

// Copy from pitch/textos_web.md (zona.vivienda_nueva.titulo); its footer is zona.contexto.no_puntua (CONTEXT_CARD)
const TEXT = {
  title: "Vivienda nueva y lo que viene",
  // zona.vivienda_nueva.suelo.visor: said after the visible text, hidden on screen (WCAG 2.5.3)
  newTab: "(se abre en una pestaña nueva)",
};

const TIMEOUT_MS = 15_000;
// One small answer per feature and level for the whole visit: every zone of the level is in it
const cache = new Map<string, Promise<readonly FeatureValueRow[]>>();

/**
 * A feature the API does not have yet (404), or a boundary failure, only hides its lines. The
 * failure is caught outside `once`, so it is forgotten and the next zone asks again.
 */
function loadFeature({ featureId, level }: NewHousingRequest): Promise<readonly FeatureValueRow[] | undefined> {
  return once(cache, `${featureId}|${level}`, () =>
    createApi()
      .featureValues(featureId, level, { timeoutMs: TIMEOUT_MS })
      .then((body) => body.data.values),
  ).catch((exc: unknown) => {
    console.warn(`Dato de vivienda nueva no disponible (${featureId}):`, exc);
    return undefined;
  });
}

async function loadRows(level: NewHousingLevel): Promise<NewHousingRows> {
  const requests = newHousingRequests(level);
  const answers = await Promise.all(requests.map(loadFeature));
  const rows: NewHousingRows = {};
  requests.forEach((request, i) => {
    const answer = answers[i];
    if (answer) rows[request.key] = answer;
  });
  return rows;
}

/**
 * D-246: the public parcels for housing behind the line, folded; each one with its buildable m², its
 * regime (only when the Comunidad explains its code), who offers it and its link to the map viewer.
 */
function Parcels({ parcels }: { parcels: LandParcels }) {
  return (
    <details className={styles.parcels}>
      <summary>{parcels.toggle}</summary>
      <ul>
        {parcels.items.map((parcel) => (
          <li key={parcel.key}>
            <span className={styles.place}>{parcel.place}</span>
            <span>{[parcel.area, parcel.regime, parcel.manager].filter(Boolean).join(" · ")}</span>
            {parcel.url && (
              <a href={parcel.url} target="_blank" rel="noopener noreferrer">
                {parcels.viewer}
                <span className="visually-hidden">
                  : {parcel.place} {TEXT.newTab}
                </span>
                <ExternalLink size={14} aria-hidden="true" />
              </a>
            )}
          </li>
        ))}
      </ul>
    </details>
  );
}

/**
 * zona.vivienda_nueva.* (D-241): how much of what is sold is new, what a new home is appraised at,
 * the Plan Vive homes, in a Madrid district the planning areas for housing still to finish, and the
 * public land offered to build housing (D-246).
 * Each line says its source and date. Context only, in neutral colours; while it loads, or without
 * any line, nothing is shown: it is not part of the fit.
 */
export default function NewHousing({ zone }: { zone: NewHousingZone }) {
  const [loaded, setLoaded] = useState<{ level: NewHousingLevel; rows: NewHousingRows } | null>(null);
  useEffect(() => {
    let cancelled = false;
    void loadRows(zone.level).then((rows) => {
      if (!cancelled) setLoaded({ level: zone.level, rows });
    });
    return () => {
      cancelled = true;
    };
  }, [zone.level]);

  const lines = loaded?.level === zone.level ? newHousingLines(zone, loaded.rows) : [];
  if (lines.length === 0) return null;
  return (
    <GlassCard as="section" aria-label={TEXT.title} className={styles.card} data-context-card="">
      <h2 className={styles.title}>{TEXT.title}</h2>
      <ul className={styles.list}>
        {lines.map((line) => (
          <li key={line.key}>
            <span>{line.text}</span>
            {line.note && <span className={styles.note}>{line.note}</span>}
            <span className={styles.source}>{line.source}</span>
            {line.parcels && <Parcels parcels={line.parcels} />}
          </li>
        ))}
      </ul>
      {/* Said once under the last of the context cards (globals.css, [data-context-footer]) */}
      <p className={styles.footer} data-context-footer="">
        {CONTEXT_CARD.footer}
      </p>
    </GlassCard>
  );
}
