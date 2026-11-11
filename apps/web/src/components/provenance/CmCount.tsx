"use client";

import { useDatasets } from "./useDatasets";

/** How many datasets come from the CM open data portal (GET /api/v1/datasets), inline in a sentence. */
export default function CmCount() {
  const { data } = useDatasets();
  return <>{data ? data.cm_open_data_count.toLocaleString("es-ES") : "…"}</>;
}
