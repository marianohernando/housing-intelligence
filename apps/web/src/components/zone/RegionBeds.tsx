"use client";

import { useEffect, useState } from "react";

import type { DatasetRef } from "@/contracts/dataset_list_response";
import { useDatasets } from "@/components/provenance/useDatasets";
import { createApi } from "@/lib/api";
import { once } from "@/lib/once";
import { publishedIn } from "@/lib/provenance";
import { lineageDataset, type RegionBedsLine, regionBedsLine, REGION_BEDS_FEATURES, type RegionFigure } from "@/lib/regionBeds";

const TIMEOUT_MS = 15_000;
// Two tiny answers (one value each) for the whole visit, only where a hospital note shows
const cache = new Map<string, Promise<RegionBedsLine | null>>();

function loadLine(): Promise<RegionBedsLine | null> {
  return once(cache, "line", async () => {
    const api = createApi();
    const ask = async (id: string): Promise<RegionFigure> => {
      const body = await api.featureValues(id, "ccaa", { timeoutMs: TIMEOUT_MS });
      return { row: body.data.values[0], datasetId: lineageDataset(body.data.lineage.dataset_versions) };
    };
    const [hospitals, beds] = await Promise.all([ask(REGION_BEDS_FEATURES.hospitals), ask(REGION_BEDS_FEATURES.beds)]);
    return regionBedsLine(hospitals, beds);
  });
}

/** A figure linked to its dataset in /datasets, with where it opens said to screen readers; plain without it. */
function Figure({ text, dataset }: { text: string; dataset: DatasetRef | undefined }) {
  if (!dataset?.url) return <>{text}</>;
  return (
    <a href={dataset.url} target="_blank" rel="noopener noreferrer">
      {text}
      <span className="visually-hidden">
        , {dataset.name}, {publishedIn(dataset.source_name)} (se abre en una pestaña nueva)
      </span>
    </a>
  );
}

/**
 * hospital.camas_region (D-231, B's draft for line D): «En toda la Comunidad hay 85 hospitales y 3,0
 * camas instaladas por cada 1.000 habitantes (2023).», each figure linked to its CM dataset. Context
 * under the hospital note: while it loads, or if it fails, nothing is shown.
 */
export default function RegionBeds({ className }: { className?: string }) {
  const [line, setLine] = useState<RegionBedsLine | null>(null);
  const { data: datasets } = useDatasets();
  useEffect(() => {
    let cancelled = false;
    loadLine()
      .then((loaded) => {
        if (!cancelled) setLine(loaded);
      })
      // A boundary failure only hides this context line; the row does not depend on it
      .catch((exc: unknown) => console.warn("Camas de la Comunidad no disponibles:", exc));
    return () => {
      cancelled = true;
    };
  }, []);
  if (!line) return null;
  const byId = (id: string | null) => datasets?.datasets.find((d) => d.dataset_id === id);
  return (
    <p className={className}>
      En toda la Comunidad hay <Figure text={line.hospitals.text} dataset={byId(line.hospitals.datasetId)} /> y{" "}
      <Figure text={line.beds.text} dataset={byId(line.beds.datasetId)} /> ({line.year}).
    </p>
  );
}
