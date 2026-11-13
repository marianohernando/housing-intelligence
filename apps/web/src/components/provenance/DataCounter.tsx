"use client";

import PillLink from "@/components/ui/PillLink";
import { counterText } from "@/lib/provenance";

import { useDatasets } from "./useDatasets";

// Copy from pitch/textos_web.md (pie.contador, pie.como)
const TEXT = { como: "Cómo lo calculamos" };

/**
 * Footer line of the brief: how many CM open datasets are behind the map, linking to «Cómo lo
 * calculamos». Until the count arrives (or if it fails) the link stays, without a number.
 */
export default function DataCounter({ className }: { className?: string }) {
  const { data } = useDatasets();
  return (
    <PillLink href="/como-lo-calculamos" className={className}>
      {data ? counterText(data.cm_open_data_count) : TEXT.como}
    </PillLink>
  );
}
