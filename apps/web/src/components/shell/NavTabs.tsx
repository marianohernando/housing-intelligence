"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { activeTab, tabHref, TABS } from "@/lib/nav";

import styles from "./SiteHeader.module.css";

export default function NavTabs() {
  const pathname = usePathname();
  const current = activeTab(pathname);
  return (
    <nav aria-label="Secciones" className={styles.nav}>
      <ul className={styles.tabs}>
        {TABS.map((tab) => (
          <li key={tab.href}>
            <Link
              href={tabHref(tab, pathname)}
              className={styles.tab}
              aria-current={tab.href === current ? "page" : undefined}
            >
              {tab.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
