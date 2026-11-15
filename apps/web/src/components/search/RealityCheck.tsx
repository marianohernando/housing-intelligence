"use client";

import { ChevronDown, Sparkles } from "lucide-react";
import { useId, useState } from "react";

import type { SearchResult } from "@/contracts/search_response";
import GlassCard from "@/components/ui/GlassCard";
import {
  constraintLabels,
  fewZones,
  limitingConstraint,
  optionText,
  passingText,
  relaxOptions,
  speaksToMany,
  unknownText,
  zonesWithoutPrice,
  zoneWord,
} from "@/lib/fit";

import styles from "./Results.module.css";
import { useScenario } from "./ScenarioProvider";

// Copy from pitch/textos_web.md (rc.*). Each option is named by its visible text: a different name
// (the old rc.opcion.aria) breaks WCAG 2.5.3 (label in name).
const TEXT = {
  title: "¿Quieres ver más zonas?",
  intro: "Mira cuántas salen si cambias una sola cosa:",
  tryIt: "Ver esas zonas",
  limit: "Lo que más limita tu búsqueda es:",
  note: "No te decimos que gastes más: te enseñamos qué cuesta cada alternativa.",
  more: "Ver todas las opciones",
  less: "Ver menos",
  none: "Cambiar una sola cosa no añade zonas.",
  // rc.anterior: the options were computed for the search before the person's last changes
  stale: "Estas propuestas eran de tu búsqueda anterior. Pulsa «Buscar zonas para mí» para ver las de ahora.",
};

/**
 * «¿Quieres ver más zonas?» (Reality Check): how many zones appear when one condition is relaxed,
 * with the API's figures; each option is applied with one tap. Always there, folded to the option
 * that adds most zones, and unfolded when few zones or none come out (decision of datamad-10).
 * Once the search on screen changes, its options are those of the previous search: they are not
 * offered, since applying one would bring back what the person changed (lib/searchState.ts).
 */
export default function RealityCheck({ result }: { result: SearchResult }) {
  const { applyRelaxation, applied, status, stale } = useScenario();
  const titleId = useId();
  const rc = result.reality_check;
  const options = relaxOptions(rc);
  // Unfolded by default with few zones; the choice is kept until the next result.
  const [choice, setChoice] = useState<{ for: SearchResult; open: boolean } | null>(null);
  const open = choice?.for === result ? choice.open : fewZones(rc);
  const word = zoneWord(result);
  // Not when what leaves zones out is missing data rather than the condition (lib/fit.ts)
  const limiting = limitingConstraint(result);
  const limit = limiting ? constraintLabels(result).get(limiting) : undefined;
  const shown = stale ? [] : open ? options : options.slice(0, 1);
  const hasMore = !stale && (options.length > 1 || rc.zones_unknown > 0 || Boolean(limit));

  return (
    <GlassCard as="section" aria-labelledby={titleId} className={styles.rc}>
      <h2 id={titleId} className={styles.rcTitle}>
        <Sparkles size={20} aria-hidden="true" />
        {TEXT.title}
      </h2>
      {stale && <p className={styles.muted}>{TEXT.stale}</p>}
      {open && !stale && (
        <p>
          {passingText(rc.zones_passing, applied !== null, word, speaksToMany(result.scenario.household))} {options.length > 0 && TEXT.intro}
        </p>
      )}
      {!stale && options.length === 0 && <p className={styles.muted}>{TEXT.none}</p>}
      {shown.length > 0 && (
        <ul className={styles.options}>
          {shown.map((r) => {
            const { label, count } = optionText(r, word);
            return (
              <li key={r.constraint_id}>
                <button
                  type="button"
                  className={styles.option}
                  // aria-disabled, not disabled: the focus stays on the option while it loads
                  aria-disabled={status === "loading"}
                  onClick={() => {
                    if (status !== "loading") applyRelaxation(r);
                  }}
                >
                  <span className={styles.optionText}>
                    <strong>{label}</strong>
                    <span>{count}</span>
                  </span>
                  <span className={styles.try}>{TEXT.tryIt}</span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
      {open && !stale && limit && (
        <p className={styles.muted}>
          {TEXT.limit} <strong>{limit}</strong>
        </p>
      )}
      {open && !stale && rc.zones_unknown > 0 && <p className={styles.muted}>{unknownText(rc.zones_unknown, word, zonesWithoutPrice(result))}</p>}
      {open && !stale && options.length > 0 && <p className={styles.note}>{TEXT.note}</p>}
      {hasMore && (
        <button type="button" className={styles.toggle} aria-expanded={open} onClick={() => setChoice({ for: result, open: !open })}>
          {open ? TEXT.less : TEXT.more}
          <ChevronDown size={18} aria-hidden="true" className={open ? styles.flip : undefined} />
        </button>
      )}
    </GlassCard>
  );
}
