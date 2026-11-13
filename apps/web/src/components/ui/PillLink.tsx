import Link from "next/link";
import type { ReactNode } from "react";

import styles from "./PillLink.module.css";

/** One link on a glass pill, readable over the map (AA on the white glass). */
export default function PillLink({ href, children, className }: { href: string; children: ReactNode; className?: string }) {
  return (
    <p className={[styles.line, className].filter(Boolean).join(" ")}>
      <Link href={href}>{children}</Link>
    </p>
  );
}
