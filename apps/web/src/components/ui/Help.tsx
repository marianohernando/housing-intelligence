import { CircleQuestionMark } from "lucide-react";
import type { ReactNode } from "react";

import styles from "./Help.module.css";

interface Props {
  /** What it explains, read after the button's text so each one has its own name («¿Qué es esto? ¿Dónde?») */
  about: string;
  /** id of the explanation, for the aria-describedby of the control it explains */
  id?: string;
  /** The button's text; «¿Qué es esto?» unless a question says it better («¿Qué es el %?») */
  label?: string;
  children: ReactNode;
  className?: string;
}

/**
 * A help folded behind a button (native details and summary, so keyboard and screen readers get
 * it for free). It replaces the `title` tooltips, which a phone never shows (UX mobile audit, A5).
 */
export default function Help({ about, id, label = "¿Qué es esto?", children, className }: Props) {
  return (
    <details className={[styles.help, className].filter(Boolean).join(" ")}>
      <summary>
        <CircleQuestionMark size={18} aria-hidden="true" />
        <span>
          {label}
          <span className="visually-hidden"> {about}</span>
        </span>
      </summary>
      <div id={id} className={styles.body}>
        {children}
      </div>
    </details>
  );
}
