import Link from "next/link";

import Logo from "./Logo";
import NavTabs from "./NavTabs";
import styles from "./SiteHeader.module.css";

/** Brand and tabs. No login or user icon (brief). */
export default function SiteHeader() {
  return (
    <header className={styles.header}>
      <Link href="/" className={styles.brand}>
        <Logo />
      </Link>
      <NavTabs />
    </header>
  );
}
