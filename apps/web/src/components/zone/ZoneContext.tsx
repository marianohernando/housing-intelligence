"use client";

import { useEffect, useState } from "react";

import { useMapZones } from "@/components/map/MapProvider";
import GlassCard from "@/components/ui/GlassCard";
import { createApi } from "@/lib/api";
import type { FeatureValueRow } from "@/lib/features";
import { once } from "@/lib/once";
import { type ContextLevel, contextLines, type ContextRequest, contextRequests, type ContextRows, type ContextZone } from "@/lib/zoneContext";

import styles from "./ZoneContext.module.css";

// Copy from pitch/textos_web.md (zona.contexto.titulo, zona.contexto.no_puntua).
const TEXT = {
  title: "Otros datos de la zona",
  footer: "Son datos informativos: no cambian el encaje ni el orden de las zonas.",
};

const TIMEOUT_MS = 15_000;
// One small answer per feature and level for the whole visit: every zone of the level is in it
const cache = new Map<string, Promise<readonly FeatureValueRow[] | undefined>>();

/** A feature the API does not have yet (404), or a boundary failure, only hides that line. */
function loadFeature({ featureId, level }: ContextRequest): Promise<readonly FeatureValueRow[] | undefined> {
  return once(cache, `${featureId}|${level}`, () =>
    createApi()
      .featureValues(featureId, level, { timeoutMs: TIMEOUT_MS })
      .then((body) => body.data.values)
      .catch((exc: unknown) => {
        console.warn(`Dato de contexto no disponible (${featureId}):`, exc);
        return undefined;
      }),
  );
}

async function loadRows(level: ContextLevel): Promise<ContextRows> {
  const requests = contextRequests(level);
  const answers = await Promise.all(requests.map(loadFeature));
  const rows: ContextRows = {};
  requests.forEach((request, i) => {
    const answer = answers[i];
    if (answer) rows[request.key] = answer;
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
    <GlassCard as="section" aria-label={TEXT.title} className={styles.card}>
      <h2 className={styles.title}>{TEXT.title}</h2>
      <ul className={styles.list}>
        {lines.map((line) => (
          <li key={line.key}>
            {line.text}
            {line.note && <span className={styles.note}>{line.note}</span>}
          </li>
        ))}
      </ul>
      <p className={styles.footer}>{TEXT.footer}</p>
    </GlassCard>
  );
}
