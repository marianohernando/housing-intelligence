import { useId } from "react";

import styles from "./Segmented.module.css";

interface Props<T extends string> {
  legend: string;
  options: { value: T; label: string }[];
  value: T;
  onChange: (value: T) => void;
}

/** Two or three exclusive options as native radios (arrow keys work), styled as a pill switch. */
export default function Segmented<T extends string>({ legend, options, value, onChange }: Props<T>) {
  const name = useId();
  return (
    <fieldset className={styles.group}>
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
