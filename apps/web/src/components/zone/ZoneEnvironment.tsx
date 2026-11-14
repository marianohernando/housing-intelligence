"use client";

import { CircleParking, type LucideIcon, Volume2, Wind } from "lucide-react";
import { useEffect, useId, useState } from "react";

import { useFacilityLayer } from "@/components/map/FacilityLayerProvider";
import GlassCard from "@/components/ui/GlassCard";
import { createApi } from "@/lib/api";
import { ENVIRONMENT_FEATURES, ENVIRONMENT_TEXT, type EnvironmentFeature, environmentFacts, type EnvironmentRows } from "@/lib/environment";
import type { FeatureValueRow } from "@/lib/features";
import { once } from "@/lib/once";

import styles from "./ZoneEnvironment.module.css";

const TIMEOUT_MS = 15_000;
// One small answer per feature and level for the whole visit (every zone of the level is in it)
const cache = new Map<string, Promise<readonly FeatureValueRow[]>>();

type Level = "municipio" | "distrito";

function loadValues(feature: EnvironmentFeature, level: Level): Promise<readonly FeatureValueRow[]> {
  return once(cache, `${feature}/${level}`, () =>
    createApi()
      .featureValues(feature, level, { timeoutMs: TIMEOUT_MS })
      .then((body) => body.data.values),
  );
}

/** Each feature on its own: one that fails leaves its line as «sin dato publicado», never the block. */
async function loadRows(level: Level): Promise<EnvironmentRows> {
  const features = Object.values(ENVIRONMENT_FEATURES);
  const settled = await Promise.allSettled(features.map((f) => loadValues(f, level)));
  const rows: EnvironmentRows = {};
  settled.forEach((result, i) => {
    const feature = features[i];
    if (feature && result.status === "fulfilled") rows[feature] = result.value;
    else if (result.status === "rejected") console.warn(`Entorno: ${feature} no disponible:`, result.reason);
  });
  return rows;
}

function Fact({ icon: Icon, text, note }: { icon: LucideIcon; text: string; note?: string | null }) {
  return (
    <li className={styles.fact}>
      <Icon size={20} aria-hidden="true" className={styles.icon} />
      <div>
        <p>{text}</p>
        {note && <p className={styles.note}>{note}</p>}
      </div>
    </li>
  );
}

/**
 * zona.entorno (D-237): street noise, air and car parks of a municipio or a Madrid district, with
 * where each figure comes from. Context only, in neutral colours; while it loads, or if nothing
 * comes for the zone, nothing is shown: it is not part of the fit.
 */
export default function ZoneEnvironment({ level, code, zone }: { level: Level; code: string; zone: string }) {
  const [rows, setRows] = useState<{ level: Level; rows: EnvironmentRows } | null>(null);
  const { groups } = useFacilityLayer();
  const titleId = useId();

  useEffect(() => {
    let cancelled = false;
    void loadRows(level).then((loaded) => {
      if (!cancelled) setRows({ level, rows: loaded });
    });
    return () => {
      cancelled = true;
    };
  }, [level]);

  if (!rows || rows.level !== level) return null;
  const facts = environmentFacts(code, rows.rows, groups?.aparcamiento ?? [], zone);
  if (!facts) return null;
  return (
    <GlassCard as="section" aria-labelledby={titleId} className={styles.card}>
      <h2 id={titleId} className={styles.title}>
        {ENVIRONMENT_TEXT.title}
      </h2>
      <ul className={styles.facts}>
        <Fact icon={Volume2} text={facts.noise} note={facts.noiseKnown ? ENVIRONMENT_TEXT.noiseHint : null} />
        <Fact icon={Wind} text={facts.air} note={ENVIRONMENT_TEXT.airSource} />
        {(facts.parking || facts.parkAndRide) && (
          <li className={styles.fact}>
            <CircleParking size={20} aria-hidden="true" className={styles.icon} />
            <div>
              {facts.parking && <p>{facts.parking}</p>}
              {facts.parkAndRide && <p>{facts.parkAndRide}</p>}
              <p className={styles.note}>{ENVIRONMENT_TEXT.parkingSource}</p>
            </div>
          </li>
        )}
      </ul>
      <p className={styles.note}>{ENVIRONMENT_TEXT.context}</p>
    </GlassCard>
  );
}
