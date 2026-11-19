import type { Metadata } from "next";
import { notFound } from "next/navigation";

import InvestorSheet from "@/components/investors/InvestorSheet";
import styles from "@/components/investors/Investors.module.css";
import SiteFooter from "@/components/shell/SiteFooter";
import { adminUnitId } from "@/lib/investors";

export const metadata: Metadata = { title: "Ficha de barrio para inversores" };

/** One pilot barrio's sheet (D-248): /inversores/28079164. */
export default async function InversoresBarrioPage({ params }: { params: Promise<{ barrio: string }> }) {
  const { barrio } = await params;
  const id = adminUnitId(barrio);
  if (!id) notFound();
  return (
    <div className={styles.page}>
      <InvestorSheet adminUnitId={id} />
      <SiteFooter />
    </div>
  );
}
