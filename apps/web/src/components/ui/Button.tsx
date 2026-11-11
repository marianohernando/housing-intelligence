import Link from "next/link";
import type { ButtonHTMLAttributes, ReactNode } from "react";

import styles from "./Button.module.css";

type Variant = "primary" | "secondary";

interface Common {
  variant?: Variant;
  children: ReactNode;
  className?: string;
}

type LinkProps = Common & { href: string };
type ActionProps = Common & Omit<ButtonHTMLAttributes<HTMLButtonElement>, "className">;

function classes(variant: Variant = "primary", className?: string): string {
  return [styles.button, styles[variant], className].filter(Boolean).join(" ");
}

/** Button, or a link that looks like one; always at least 44 px high (brief: older users). */
export default function Button(props: LinkProps | ActionProps) {
  if ("href" in props) {
    const { href, variant, className, children } = props;
    return (
      <Link href={href} className={classes(variant, className)}>
        {children}
      </Link>
    );
  }
  const { variant, className, children, ...rest } = props;
  return (
    <button type="button" {...rest} className={classes(variant, className)}>
      {children}
    </button>
  );
}
