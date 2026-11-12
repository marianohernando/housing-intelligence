"use client";

import { useEffect, useState } from "react";

import GlassCard from "@/components/ui/GlassCard";
import { createApi, type FeatureValuesResponse } from "@/lib/api";
import { once } from "@/lib/once";
import { PERCEIVED_SAFETY_FEATURES, perceivedSafety, perceivedSafetyText, type SafetyRows } from "@/lib/safety";

import styles from "./PerceivedSafety.module.css";

const TIMEOUT_MS = 15_000;
// Four small answers for the whole visit (every district is in them): never asked outside Madrid
const cache = new Map<string, Promise<SafetyRows>>();

function loadRows(): Promise<SafetyRows> {
  return once(cache, "rows", async () => {
    const api = createApi();
    const values = (body: FeatureValuesResponse) => body.data.values;
    const ask = (id: string, level: "distrito" | "municipio") => api.featureValues(id, level, { timeoutMs: TIMEOUT_MS }).then(values);
    const { night, day } = PERCEIVED_SAFETY_FEATURES;
    const [nightRows, dayRows, nightCity, dayCity] = await Promise.all([
      ask(night, "distrito"),
      ask(day, "distrito"),
      ask(night, "municipio"),
      ask(day, "municipio"),
    ]);
    return { night: nightRows, day: dayRows, nightCity, dayCity };
  });
}

/**
 * zona.seguridad_vecinos (DATA-020, D-226 §1): in a Madrid district, how its neighbours rate the
 * safety of their barrio, with the city's and the survey. Context only, in neutral colours; while it
 * loads, or if it fails or the district has no rating, nothing is shown: it is not part of the fit.
 */
export default function PerceivedSafety({ districtCode }: { districtCode: string }) {
  const [rows, setRows] = useState<SafetyRows | null>(null);
  useEffect(() => {
    let cancelled = false;
    loadRows()
      .then((loaded) => {
        if (!cancelled) setRows(loaded);
      })
      // A boundary failure only hides this context line; the rest of the zone does not depend on it
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, []);

  const safety = rows ? perceivedSafety(districtCode, rows) : null;
  if (!safety) return null;
  const { rating, source } = perceivedSafetyText(safety);
  return (
    <GlassCard className={styles.card}>
      <p>{rating}</p>
      <p className={styles.source}>{source}</p>
    </GlassCard>
  );
}
