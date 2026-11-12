import type { LucideIcon } from "lucide-react";

import styles from "./Chip.module.css";

interface Props {
  label: string;
  pressed: boolean;
  onToggle: () => void;
  icon?: LucideIcon;
  /** Small number shown when pressed (order of importance) */
  badge?: number;
  /** How many there are, always shown and part of the accessible name («Colegios 27») */
  count?: string;
  /** Disabled with a short note («Muy pronto») */
  soon?: string;
  title?: string;
}

/** Toggle chip, at least 44 px high; its state is told by aria-pressed, colour and border. */
export default function Chip({ label, pressed, onToggle, icon: Icon, badge, count, soon, title }: Props) {
  return (
    <button
      type="button"
      className={styles.chip}
      aria-pressed={pressed}
      disabled={Boolean(soon)}
      onClick={onToggle}
      title={title}
    >
      {Icon && <Icon size={18} aria-hidden="true" className={styles.icon} />}
      <span className={styles.label}>{label}</span>
      {count !== undefined && <span className={styles.count}>{count}</span>}
      {pressed && badge !== undefined && (
        <>
          <span className={styles.badge} aria-hidden="true">
            {badge}
          </span>
          <span className="visually-hidden">, importancia {badge}</span>
        </>
      )}
      {soon && <span className={styles.soon}>{soon}</span>}
    </button>
  );
}
