import { CircleCheck, CircleMinus, CircleX } from "lucide-react";

import type { SourcedValue } from "@/contracts/investor_zone_response";
import type { Verdict } from "@/contracts/viability_response";
import { figure, MARK_TEXT, sourceLine, VERDICT_TEXT } from "@/lib/investors";

import styles from "./Investors.module.css";

/** «Dato», «Supuesto» or «Lo pones tú»: a word on a quiet tag, never a state colour. */
export function MarkTag({ mark }: { mark: SourcedValue["mark"] | "sin_dato" }) {
  return <span className={`${styles.mark} ${styles[`mark_${mark}`]}`}>{MARK_TEXT[mark]}</span>;
}

interface FigureProps {
  label: string;
  value: SourcedValue;
  decimals?: number;
  /** A line under the value (a range, what it means) */
  note?: string | null;
}

/** One figure of the sheet: its label, value, mark and source, the source always in view. */
export function Figure({ label, value, decimals = 0, note }: FigureProps) {
  const link = value.source.url;
  return (
    <div className={styles.figure}>
      <dt>{label}</dt>
      <dd>
        <span className={styles.value}>{figure(value, decimals)}</span>
        {value.value !== null && value.value !== undefined && <MarkTag mark={value.mark} />}
        {note && <span className={styles.note}>{note}</span>}
        <span className={styles.source}>
          {sourceLine(value)}
          {link && (
            <>
              {" · "}
              <a href={link} target="_blank" rel="noopener noreferrer">
                Ver la fuente<span className="visually-hidden"> (se abre en una pestaña nueva)</span>
              </a>
            </>
          )}
        </span>
      </dd>
    </div>
  );
}

const VERDICT_ICON = { sale: CircleCheck, ajustar: CircleMinus, no_sale: CircleX } as const;

/** The semaphore: icon, word and colour together (WCAG 1.4.1). */
export function VerdictBadge({ verdict }: { verdict: Verdict }) {
  const Icon = VERDICT_ICON[verdict];
  return (
    <span className={`${styles.verdict} ${styles[`verdict_${verdict}`]}`}>
      <Icon size={18} aria-hidden="true" />
      {VERDICT_TEXT[verdict]}
    </span>
  );
}
