"use client";

import { ministryAttribution } from "@/lib/provenance";

import { useDatasets } from "./useDatasets";

/** pie.sanidad, with the catalogues and update dates of /datasets (line D's text until it answers). */
export default function MinistryAttribution() {
  const { data } = useDatasets();
  return ministryAttribution(data?.datasets ?? null);
}
