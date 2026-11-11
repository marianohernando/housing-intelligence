import { Minus, Plus } from "lucide-react";
import { useId } from "react";

import styles from "./Counter.module.css";

interface Props {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
}

// Copy from pitch/textos_web.md (hogar.contador.*)
const TEXT = { less: "Quitar uno", more: "Añadir uno" };

/** − value + with 44 px buttons; the value is announced when it changes. */
export default function Counter({ label, value, min, max, onChange }: Props) {
  const id = useId();
  return (
    <div className={styles.counter} role="group" aria-labelledby={id}>
      <span id={id} className={styles.label}>
        {label}
      </span>
      <button type="button" className={styles.step} aria-label={TEXT.less} disabled={value <= min} onClick={() => onChange(value - 1)}>
        <Minus size={18} aria-hidden="true" />
      </button>
      <output className={styles.value} aria-live="polite">
        {value}
      </output>
      <button type="button" className={styles.step} aria-label={TEXT.more} disabled={value >= max} onClick={() => onChange(value + 1)}>
        <Plus size={18} aria-hidden="true" />
      </button>
    </div>
  );
}
