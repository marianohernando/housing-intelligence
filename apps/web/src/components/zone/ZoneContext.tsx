"use client";

import { useEffect, useId, useState } from "react";

import { useMapZones } from "@/components/map/MapProvider";
import GlassCard from "@/components/ui/GlassCard";
import { createApi } from "@/lib/api";
import type { FeatureValueRow } from "@/lib/features";
import { once } from "@/lib/once";
import {
  CONTEXT_CARD,
  type ContextLevel,
  contextLines,
  type ContextRequest,
  contextRequests,
  type ContextRows,
  type ContextZone,
  valuesOrMissing,
} from "@/lib/zoneContext";

import styles from "./ZoneContext.module.css";

const TIMEOUT_MS = 15_000;
// One small answer per feature and level for the whole visit: every zone of the level is in it
const cache = new Map<string, Promise<readonly FeatureValueRow[] | undefined>>();

/** A 404 is remembered as «no such feature»; any other failure is not cached (`once` forgets it). */
function loadFeature({ featureId, level }: ContextRequest): Promise<readonly FeatureValueRow[] | undefined> {
  return once(cache, `${featureId}|${level}`, () => valuesOrMissing(createApi().featureValues(featureId, level, { timeoutMs: TIMEOUT_MS })));
}

/** Each answer on its own: a failed one only hides its line, the others still show. */
async function loadRows(level: ContextLevel): Promise<ContextRows> {
  const requests = contextRequests(level);
  const answers = await Promise.allSettled(requests.map(loadFeature));
  const rows: ContextRows = {};
  requests.forEach((request, i) => {
    const answer = answers[i];
    if (answer?.status === "fulfilled" && answer.value) rows[request.key] = answer.value;
    // A boundary failure only hides this line; the rest of the zone does not depend on it
    if (answer?.status === "rejected") console.warn(`Dato de contexto no disponible (${request.featureId}):`, answer.reason);
  });
  return rows;
}

/**
 * zona.contexto.* (D-235): known offences, the age of the dwellings and the income of the zone, one
 * short line each with its source and year. In a district, the barrio picked on the map shows its own
 * age and income. Context only, in neutral colours; while it loads, or without any figure, nothing
 * is shown: it is not part of the fit.
 */
export default function ZoneContext({ zone }: { zone: ContextZone }) {
  const { barrio } = useMapZones();
  const titleId = useId();
  const picked = zone.level === "distrito" && barrio ? barrio.properties : null;
  const shown: ContextZone = picked ? { level: "barrio", code: picked.code, name: picked.name ?? zone.name } : zone;
  const [loaded, setLoaded] = useState<{ level: ContextLevel; rows: ContextRows } | null>(null);
  useEffect(() => {
    let cancelled = false;
    void loadRows(shown.level).then((rows) => {
      if (!cancelled) setLoaded({ level: shown.level, rows });
    });
    return () => {
      cancelled = true;
    };
  }, [shown.level]);

  const lines = loaded?.level === shown.level ? contextLines(shown, loaded.rows) : [];
  if (lines.length === 0) return null;
  return (
    <GlassCard as="section" aria-labelledby={titleId} className={styles.card} data-context-card="">
      <h2 id={titleId} className={styles.title}>
        {CONTEXT_CARD.title}
      </h2>
      {/* role="list": the list keeps its semantics in Safari without bullets */}
      <ul className={styles.list} role="list">
        {lines.map((line) => (
          <li key={line.key}>
            {line.text}
            {line.note && <span className={styles.note}>{line.note}</span>}
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
