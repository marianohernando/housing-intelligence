import type { Metadata } from "next";
import Link from "next/link";

import InvestorList from "@/components/investors/InvestorList";
import styles from "@/components/investors/Investors.module.css";
import SiteFooter from "@/components/shell/SiteFooter";
import { INVESTOR_TEXT as TEXT } from "@/lib/investors";

export const metadata: Metadata = { title: TEXT.title };

/** «Para inversores» (D-248): the pilot barrios, with what they lack and their public land. */
export default function InversoresPage() {
  return (
    <div className={styles.page}>
      <div className={styles.sheet} data-investors>
        <header className={styles.header}>
          <p className={styles.plan}>{TEXT.plan}</p>
          <h1 className={styles.title}>{TEXT.title}</h1>
          <p className={styles.lead}>{TEXT.intro}</p>
          <p className={styles.note}>
            {TEXT.pilot} {TEXT.model}
          </p>
          <p className={`${styles.devLink} no-print`}>
            <Link href="/desarrolladores">{TEXT.developers}</Link>
          </p>
        </header>
        <InvestorList />
      </div>
      <SiteFooter />
    </div>
  );
}
