import type { Metadata } from "next";
import Link from "next/link";

import InvestorList from "@/components/investors/InvestorList";
import styles from "@/components/investors/Investors.module.css";
import ParcelSearch from "@/components/investors/ParcelSearch";
import SiteFooter from "@/components/shell/SiteFooter";
import { INVESTOR_TEXT as TEXT } from "@/lib/investors";
import { SEARCH_TEXT } from "@/lib/parcels";

export const metadata: Metadata = { title: TEXT.title };

/**
 * «Para inversores» (D-248, D-250): first «Busca tu parcela» (its reference, an address or the
 * map), in the first screen of a phone too; then «Explorar barrios», the pilot barrios.
 */
export default function InversoresPage() {
  return (
    <div className={styles.page}>
      <div className={styles.sheet} data-investors>
        <header className={styles.header}>
          <p className={styles.plan}>{TEXT.plan}</p>
          <h1 className={styles.title}>{SEARCH_TEXT.title}</h1>
          <p className={styles.lead}>{SEARCH_TEXT.intro}</p>
        </header>
        <ParcelSearch />
        <div className={styles.header}>
          <p className={styles.note}>
            {SEARCH_TEXT.coverage} {TEXT.model}
          </p>
          <p className={`${styles.devLink} no-print`}>
            <Link href="/desarrolladores">{TEXT.developers}</Link>
          </p>
        </div>
        <InvestorList />
      </div>
      <SiteFooter />
    </div>
  );
}
