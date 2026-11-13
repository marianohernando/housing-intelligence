"use client";

import { createContext, type ReactNode, useContext, useMemo, useState } from "react";

import type { GapRowKey } from "@/contracts/zone_gap_list_response";

import { useGapRowMap } from "./useGapRowMap";

type GapLayerValue = ReturnType<typeof useGapRowMap> & {
  /** Row of «Qué falta» the overview map is coloured by; null: «Encaje con tu búsqueda». */
  row: GapRowKey | null;
  setRow: (row: GapRowKey | null) => void;
};

const GapLayerContext = createContext<GapLayerValue | null>(null);

export function useGapLayer(): GapLayerValue {
  const value = useContext(GapLayerContext);
  if (!value) throw new Error("useGapLayer must be used inside <GapLayerProvider>");
  return value;
}

/** What the overview map shows («¿Qué quieres ver?»), shared by the map and its legend. */
export default function GapLayerProvider({ children }: { children: ReactNode }) {
  const [row, setRow] = useState<GapRowKey | null>(null);
  const rowMap = useGapRowMap(row);
  // One value per change, so the map and the legend do not re-render on every render of the layout
  const value = useMemo(() => ({ ...rowMap, row, setRow }), [rowMap, row]);
  return <GapLayerContext.Provider value={value}>{children}</GapLayerContext.Provider>;
}
