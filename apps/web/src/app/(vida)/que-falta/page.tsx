import type { Metadata } from "next";

import SiteFooter from "@/components/shell/SiteFooter";
import ZoneGapsView from "@/components/zone/ZoneGapsView";
import { parseZoneParam } from "@/lib/gaps";

import styles from "./page.module.css";

export const metadata: Metadata = { title: "Qué falta" };

export default async function QueFaltaPage({ searchParams }: { searchParams: Promise<Record<string, string | string[] | undefined>> }) {
  const { zona } = await searchParams;
  const zone = parseZoneParam(zona);
  return (
    <div className={styles.page}>
      <ZoneGapsView zone={zone} invalid={zona !== undefined && zone === null} />
      <SiteFooter />
    </div>
  );
}
