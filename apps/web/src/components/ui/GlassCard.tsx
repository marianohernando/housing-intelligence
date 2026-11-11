import type { HTMLAttributes } from "react";

import styles from "./GlassCard.module.css";

interface Props extends HTMLAttributes<HTMLElement> {
  as?: "div" | "section" | "aside" | "article" | "figure";
}

/** White glass card of the brief. Opacity is AA-checked over the map in tokens.test.ts. */
export default function GlassCard({ as: Tag = "div", className, ...rest }: Props) {
  return <Tag className={["glass", styles.card, className].filter(Boolean).join(" ")} {...rest} />;
}
