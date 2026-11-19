import Link from "next/link";

import { METHOD_LINK } from "@/lib/investors";

import styles from "./Investors.module.css";

/** «Cómo lo calculamos» → the investor section of the method page (D-251), a 44 px target. */
export default function MethodLink() {
  return (
    <p className={`${styles.note} no-print`}>
      <Link href={METHOD_LINK.href}>
        {METHOD_LINK.text}
        <span className="visually-hidden">{METHOD_LINK.context}</span>
      </Link>
    </p>
  );
}
