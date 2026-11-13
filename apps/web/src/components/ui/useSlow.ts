"use client";

import { useEffect, useState } from "react";

/** pitch/textos_web.md, carga.lento: shown when something takes more than 5 s. */
export const SLOW_TEXT = "Está tardando un poco más de lo normal. Gracias por esperar.";
const SLOW_MS = 5000;

/** Whether `active` (a loading state) has lasted longer than usual. */
export function useSlow(active: boolean, ms: number = SLOW_MS): boolean {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    if (!active) return;
    const timer = window.setTimeout(() => setSlow(true), ms);
    return () => {
      window.clearTimeout(timer);
      setSlow(false);
    };
  }, [active, ms]);
  return active && slow;
}
