"use client";

import Link from "next/link";

import { counterText } from "@/lib/provenance";

import styles from "./DataCounter.module.css";
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
    <p className={[styles.counter, className].filter(Boolean).join(" ")}>
      <Link href="/como-lo-calculamos">{data ? counterText(data.cm_open_data_count) : TEXT.como}</Link>
    </p>
  );
}
