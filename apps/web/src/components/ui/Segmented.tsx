import { useId } from "react";

import styles from "./Segmented.module.css";

interface Props<T extends string> {
  legend: string;
  options: { value: T; label: string }[];
  /** null: none chosen (no budget limit) */
  value: T | null;
  onChange: (value: T) => void;
  /** Options in a grid of this many columns instead of one row (four long labels on a phone) */
  columns?: 2;
}

/** Two to four exclusive options as native radios (arrow keys work), styled as a pill switch. */
export default function Segmented<T extends string>({ legend, options, value, onChange, columns }: Props<T>) {
  const name = useId();
  return (
    <fieldset className={columns ? `${styles.group} ${styles.columns}` : styles.group}>
      <legend className="visually-hidden">{legend}</legend>
      {options.map((option) => (
        <label key={option.value} className={styles.option}>
          <input
            type="radio"
            name={name}
            value={option.value}
            checked={option.value === value}
            onChange={() => onChange(option.value)}
            className={styles.input}
          />
          <span>{option.label}</span>
        </label>
      ))}
    </fieldset>
  );
}
