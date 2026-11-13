"use client";

import { ChevronUp } from "lucide-react";
import { type CSSProperties, type PointerEvent, type ReactNode, useId, useRef, useState } from "react";

import { SHEET_PEEK } from "@/lib/map/camera";

import styles from "./MapSheet.module.css";

// Copy from pitch/textos_web.md (movil.hoja.tirador, movil.hoja.mapa).
const TEXT = {
  more: "Desliza hacia arriba para ver más",
  map: "Ver el mapa",
};

/** A swipe on the handle longer than this (px) opens or folds the sheet instead of toggling it. */
const SWIPE = 30;

/**
 * Bottom sheet over the map on mobile: folded it leaves the map in view, open it shows all the
 * content. The handle is a real button (tap, keyboard) that also takes a swipe. On desktop the
 * sheet is not drawn and its content flows as usual.
 */
export default function MapSheet({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const contentId = useId();
  const startY = useRef<number | null>(null);
  const swipe = useRef(0);

  const onPointerDown = (event: PointerEvent<HTMLButtonElement>) => {
    startY.current = event.clientY;
    swipe.current = 0;
    event.currentTarget.setPointerCapture(event.pointerId);
  };
  const onPointerUp = (event: PointerEvent<HTMLButtonElement>) => {
    if (startY.current !== null) swipe.current = event.clientY - startY.current;
    startY.current = null;
  };
  const onClick = () => {
    const dy = swipe.current;
    swipe.current = 0;
    if (dy <= -SWIPE) setOpen(true);
    else if (dy >= SWIPE) setOpen(false);
    else setOpen((value) => !value);
  };

  return (
    <div className={styles.sheet} data-sheet={open ? "open" : "folded"} style={{ "--sheet-peek": `${SHEET_PEEK * 100}dvh` } as CSSProperties}>
      <button
        type="button"
        className={styles.handle}
        aria-expanded={open}
        aria-controls={contentId}
        onPointerDown={onPointerDown}
        onPointerUp={onPointerUp}
        onClick={onClick}
      >
        <span className={styles.grip} aria-hidden="true" />
        <span className={styles.handleText}>
          <ChevronUp size={18} aria-hidden="true" className={open ? styles.flip : undefined} />
          {open ? TEXT.map : TEXT.more}
        </span>
      </button>
      <div id={contentId} className={styles.content}>
        {children}
      </div>
    </div>
  );
}
