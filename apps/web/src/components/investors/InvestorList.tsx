"use client";

import Link from "next/link";
import { useState } from "react";

import type { InvestorZoneSummary } from "@/contracts/investor_zone_list_response";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { errorMessage } from "@/lib/errors";
import { formatNumber } from "@/lib/format";
import { districtHeading, INVESTOR_TEXT as TEXT, gapsLine, parcelsLine, remainingLine } from "@/lib/investors";

import styles from "./Investors.module.css";
import { useInvestorZones } from "./useInvestors";

function byDistrict(zones: InvestorZoneSummary[]): [string, InvestorZoneSummary[]][] {
  const groups = new Map<string, InvestorZoneSummary[]>();
  for (const zone of zones) {
    const name = zone.district.name;
    groups.set(name, [...(groups.get(name) ?? []), zone]);
  }
  return [...groups];
}

function ZoneRow({ zone }: { zone: InvestorZoneSummary }) {
  const land = [parcelsLine(zone.parcels, zone.parcels_m2), remainingLine(zone.remaining_m2, zone.remaining_shared_areas)].filter(Boolean).join(" · ");
  const price = zone.sale_price_m2 ? `Unos ${formatNumber(zone.sale_price_m2, 0)} €/m² (estimado)` : null;
  return (
    <li>
      <Link href={`/inversores/${zone.zone.code}`} className={styles.zoneLink}>
        <span className={styles.zoneName}>{zone.zone.name}</span>
        <span className={styles.zoneFacts}>{gapsLine(zone)}</span>
        {(land || price) && <span className={styles.zoneFacts}>{[land, price].filter(Boolean).join(" · ")}</span>}
        <span aria-hidden="true" className={styles.chevron}>
          ›
        </span>
      </Link>
    </li>
  );
}

/** The pilot barrios by district, with what is missing in their district, their public land and price. */
export default function InvestorList() {
  const zones = useInvestorZones();
  const slow = useSlow(zones.loading);
  const [onlyLand, setOnlyLand] = useState(false);

  if (zones.loading) {
    return (
      <GlassCard role="status" className={styles.card}>
        <p>
          {TEXT.loading}
          {slow && ` ${SLOW_TEXT}`}
        </p>
      </GlassCard>
    );
  }
  if (zones.error || !zones.data) {
    return (
      <GlassCard role="alert" className={styles.card}>
        <p>{zones.error ? errorMessage(zones.error) : TEXT.loading}</p>
        <Button variant="secondary" onClick={zones.retry}>
          {TEXT.retry}
        </Button>
      </GlassCard>
    );
  }

  const all = zones.data.data.zones;
  if (all.length === 0) {
    return (
      <GlassCard role="status" className={styles.card}>
        <p>{TEXT.emptyPilot}</p>
      </GlassCard>
    );
  }
  const withLand = all.filter((z) => (z.parcels ?? 0) > 0 || (z.remaining_m2 ?? 0) > 0);
  const shown = onlyLand ? withLand : all;
  return (
    <GlassCard as="section" aria-labelledby="barrios-piloto" className={styles.card}>
      <h2 id="barrios-piloto">{TEXT.listTitle}</h2>
      <p className={styles.lead}>{TEXT.listSummary(all.length, withLand.length)}</p>
      <button type="button" className={styles.toggle} aria-pressed={onlyLand} onClick={() => setOnlyLand((on) => !on)}>
        {TEXT.withLand}
      </button>
      {byDistrict(shown).map(([district, barrios]) => (
        <section key={district} aria-label={district} className={styles.district}>
          <h3>{districtHeading(district, barrios.length)}</h3>
          <ul className={styles.zoneList}>
            {barrios.map((zone) => (
              <ZoneRow key={zone.zone.code} zone={zone} />
            ))}
          </ul>
        </section>
      ))}
    </GlassCard>
  );
}
