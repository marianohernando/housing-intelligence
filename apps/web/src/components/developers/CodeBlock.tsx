"use client";

import { useEffect, useRef, useState } from "react";

import { DEV_TEXT as TEXT } from "@/lib/developers";

import styles from "./Developers.module.css";

type CopyState = "idle" | "copied" | "failed";
const STATUS_MS = 2500;

/**
 * A code example with its «Copiar» button. A long line scrolls inside its own box (focusable, so
 * it scrolls with the keyboard too), never the page. `caption` is what the box says it holds
 * («curl»); `label` names it for the button and the box («POST /api/v1/search»).
 */
export default function CodeBlock({ code, caption, label }: { code: string; caption: string; label: string }) {
  const [state, setState] = useState<CopyState>("idle");
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
  useEffect(() => () => clearTimeout(timer.current), []);

  async function copy() {
    try {
      await navigator.clipboard.writeText(code);
      setState("copied");
    } catch {
      setState("failed");
    }
    clearTimeout(timer.current);
    timer.current = setTimeout(() => setState("idle"), STATUS_MS);
  }

  return (
    <figure className={styles.code}>
      <figcaption className={styles.codeHead}>
        <span className={styles.codeLabel}>{caption}</span>
        <span className={styles.copyArea}>
          <span role="status" className={styles.copyStatus}>
            {state === "copied" ? TEXT.copied : state === "failed" ? TEXT.copyFailed : ""}
          </span>
          <button type="button" className={`${styles.copy} no-print`} onClick={copy}>
            {TEXT.copy}
            <span className="visually-hidden">: {label}</span>
          </button>
        </span>
      </figcaption>
      {/* Focusable: a box that scrolls must scroll with the keyboard too (WCAG 2.1.1), and what
          takes the focus says what it is (review R-03 of #97) */}
      <pre className={styles.pre} tabIndex={0} role="region" aria-label={label}>
        <code>{code}</code>
      </pre>
    </figure>
  );
}
