"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { activeTab, TABS } from "@/lib/nav";

import styles from "./SiteHeader.module.css";

export default function NavTabs() {
  const current = activeTab(usePathname());
  return (
    <nav aria-label="Secciones" className={styles.nav}>
      <ul className={styles.tabs}>
        {TABS.map((tab) => (
          <li key={tab.href}>
            <Link
              href={tab.href}
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
