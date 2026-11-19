import type { Metadata } from "next";
import { notFound } from "next/navigation";

import ParcelSheetView from "@/components/investors/ParcelSheet";
import styles from "@/components/investors/Investors.module.css";
import SiteFooter from "@/components/shell/SiteFooter";
import { parcelRc } from "@/lib/parcels";

export const metadata: Metadata = { title: "Ficha de parcela para inversores" };

/** One parcel of Madrid capital (D-250): /inversores/parcela/2122202VK4722A, shareable. */
export default async function InversoresParcelaPage({ params }: { params: Promise<{ rc: string }> }) {
  const { rc } = await params;
  const rc14 = parcelRc(decodeURIComponent(rc));
  if (!rc14) notFound();
  return (
    <div className={styles.page}>
      <ParcelSheetView rc14={rc14} />
      <SiteFooter />
    </div>
  );
}
