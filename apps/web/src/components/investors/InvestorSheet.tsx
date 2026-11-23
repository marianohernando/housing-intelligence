"use client";

import { ExternalLink, Printer } from "lucide-react";
import Link from "next/link";
import { type ReactNode, useEffect } from "react";

import type { GapRow, InvestorZone, LandItem } from "@/contracts/investor_zone_response";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import GapBadge from "@/components/zone/GapBadge";
import SmallZoneTag from "@/components/zone/SmallZoneTag";
import { errorMessage } from "@/lib/errors";
import { notComparable, peopleAffectedText, rowComparison } from "@/lib/gaps";
import {
  areaFacts,
  COMMERCE_LABEL,
  emptyLandText,
  uniqueDatasets,
  INVESTOR_TEXT as TEXT,
  landArea,
  landName,
  REGIME_TEXT,
  rentRange,
  SHEET_TEXT,
  today,
} from "@/lib/investors";

import Calculator from "./Calculator";
import { Figure } from "./Figures";
import styles from "./Investors.module.css";
import { useInvestorZone } from "./useInvestors";

export function Section({ id, title, children }: { id: string; title: string; children: ReactNode }) {
  return (
    <GlassCard as="section" aria-labelledby={id} className={`${styles.card} ${styles.section}`}>
      <h2 id={id}>{title}</h2>
      {children}
    </GlassCard>
  );
}

/** The sections below are also those of a parcel's sheet (D-250), with its own titles. */
export function Demand({ sheet, title = TEXT.sections.demand }: { sheet: InvestorZone; title?: string }) {
  const d = sheet.demand;
  return (
    <Section id="demanda" title={title}>
      <dl className={styles.figures}>
        <Figure label={SHEET_TEXT.income} value={d.income} />
        <Figure label={SHEET_TEXT.householdSize} value={d.household_size} decimals={2} />
        <Figure label={SHEET_TEXT.onePerson} value={d.one_person_pct} />
        <Figure label={SHEET_TEXT.fivePlus} value={d.five_plus_pct} />
        <Figure label={SHEET_TEXT.over65} value={d.over_65_pct} />
        <Figure label={SHEET_TEXT.under15} value={d.under_15_pct} />
        <Figure label={SHEET_TEXT.population} value={d.population} />
      </dl>
      <p className={styles.note}>{SHEET_TEXT.demandNote}</p>
    </Section>
  );
}

export function Prices({ sheet, title = TEXT.sections.prices }: { sheet: InvestorZone; title?: string }) {
  const p = sheet.prices;
  return (
    <Section id="precios" title={title}>
      <dl className={styles.figures}>
        <Figure label={SHEET_TEXT.sale} value={p.sale_m2} note={SHEET_TEXT.saleNote} />
        <Figure label={SHEET_TEXT.premium} value={p.new_build_premium_pct} decimals={1} />
        <Figure label={SHEET_TEXT.saleNew} value={p.new_build_sale_m2} />
        <Figure label={SHEET_TEXT.rent} value={p.rent_m2_month} decimals={2} note={rentRange(p.rent_m2_month)} />
      </dl>
    </Section>
  );
}

function GapItem({ row, district }: { row: GapRow; district: string }) {
  const comparison = rowComparison(row);
  const affected = peopleAffectedText(row);
  return (
    <li className={styles.gapRow}>
      <span className={styles.gapHead}>
        <h3>{row.label}</h3>
        {notComparable(row) ? <SmallZoneTag /> : <GapBadge status={row.status} />}
      </span>
      {comparison && <span>{comparison}</span>}
      {affected && <span>{affected}</span>}
      <span className={styles.levelNote}>{SHEET_TEXT.gapsLevel(district)}</span>
    </li>
  );
}

export function Gaps({ sheet, title = TEXT.sections.gaps }: { sheet: InvestorZone; title?: string }) {
  const gaps = sheet.gaps;
  return (
    <Section id="que-falta" title={title}>
      {gaps ? (
        <>
          <p className={styles.lead}>{SHEET_TEXT.gapsIntro(gaps.zone_name)}</p>
          <ul className={styles.gapRows}>
            {gaps.rows.map((row) => (
              <GapItem key={row.row} row={row} district={gaps.zone_name} />
            ))}
          </ul>
          <h3 className={styles.subhead}>{SHEET_TEXT.commerce}</h3>
          <dl className={styles.figures}>
            {gaps.commerce.map((value) => (
              <Figure key={value.feature_id} label={COMMERCE_LABEL[value.feature_id ?? ""] ?? value.feature_id ?? ""} value={value} decimals={1} />
            ))}
          </dl>
          <p className={styles.note}>
            <Link href={`/que-falta?zona=distrito/${sheet.district.code}`}>{SHEET_TEXT.gapsMore(gaps.zone_name)}</Link>
          </p>
        </>
      ) : (
        <p>{TEXT.gapsUnknown}</p>
      )}
    </Section>
  );
}

function LandList({ items }: { items: LandItem[] }) {
  return (
    <ul className={styles.landList}>
      {items.map((item) => (
        <li key={`${item.kind}-${item.code ?? item.name}`}>
          <strong>{landName(item)}</strong>
          <span>{[landArea(item), ...areaFacts(item), item.regime ? REGIME_TEXT[item.regime] : null, item.manager].filter(Boolean).join(" · ")}</span>
          {item.note && <span className={styles.note}>{item.note}</span>}
          {item.url?.startsWith("https://") && (
            <a href={item.url} target="_blank" rel="noopener noreferrer" className={styles.external}>
              {item.kind === "parcela" ? SHEET_TEXT.viewer : SHEET_TEXT.record}
              <ExternalLink size={16} aria-hidden="true" />
              <span className="visually-hidden">: {landName(item)} (se abre en una pestaña nueva)</span>
            </a>
          )}
        </li>
      ))}
    </ul>
  );
}

export function Land({ sheet, title = TEXT.sections.land }: { sheet: InvestorZone; title?: string }) {
  const land = sheet.land;
  return (
    <Section id="suelo" title={title}>
      <p className={styles.lead}>{SHEET_TEXT.landIntro}</p>
      <h3 className={styles.subhead}>{SHEET_TEXT.parcels(land.parcels.length)}</h3>
      {land.parcels.length > 0 ? <LandList items={land.parcels} /> : <p>{emptyLandText(land.parcels_m2.value, "parcelas")}</p>}
      <p className={styles.source}>Fuente: {land.parcels_m2.source.text}</p>
      <h3 className={styles.subhead}>{SHEET_TEXT.remaining}</h3>
      {land.remaining.length > 0 ? (
        <LandList items={land.remaining} />
      ) : (
        <p>{emptyLandText(land.remaining_m2.value, "ambitos")}</p>
      )}
      {land.remaining.length > 0 && <p className={styles.source}>Fuente: {land.remaining_m2.source.text}</p>}
      <dl className={styles.figures}>
        <Figure label={SHEET_TEXT.vacant(land.vacant_units.source.level)} value={land.vacant_units} />
      </dl>
    </Section>
  );
}

function Sources({ sheet, version, method }: { sheet: InvestorZone; version: string | null; method: string | null }) {
  const datasets = uniqueDatasets(sheet.datasets);
  // The PEM's dataset is in the list once loaded; before, its versioned figure cites the portal page
  const pemFallback = (sheet.defaults.pem_m2.source.dataset_ids ?? []).length === 0 && Boolean(sheet.defaults.pem_m2.source.url);
  return (
    <Section id="fuentes" title={TEXT.sections.sources}>
      <ul className={styles.notices}>
        {sheet.notices.map((notice) => (
          <li key={notice}>{notice}</li>
        ))}
      </ul>
      <p className={styles.note}>{SHEET_TEXT.version(version, method)}</p>
      <details className={styles.parts} open>
        <summary>{SHEET_TEXT.datasets(datasets.length + (pemFallback ? 1 : 0))}</summary>
        <ul className={styles.datasets}>
          {datasets.map((d) => (
            <li key={d.dataset_id}>
              {d.publisher}: {d.name}
              {d.version ? ` (versión ${d.version})` : ""}
              {d.url && (
                <>
                  {" · "}
                  <a href={d.url} target="_blank" rel="noopener noreferrer">
                    {SHEET_TEXT.open}
                    <span className="visually-hidden">: {d.name} (se abre en una pestaña nueva)</span>
                  </a>
                  <span className={styles.printOnly}>{d.url}</span>
                </>
              )}
            </li>
          ))}
          {pemFallback && (
            <li>
              {SHEET_TEXT.pemDataset} ·{" "}
              <a href={sheet.defaults.pem_m2.source.url ?? undefined} target="_blank" rel="noopener noreferrer">
                {SHEET_TEXT.open}
                <span className="visually-hidden">: {SHEET_TEXT.pemDataset} (se abre en una pestaña nueva)</span>
              </a>
              <span className={styles.printOnly}>{sheet.defaults.pem_m2.source.url}</span>
            </li>
          )}
        </ul>
      </details>
    </Section>
  );
}

/** One pilot barrio for whoever builds (D-248): demand, prices, what is missing, land and the calculator. */
export default function InvestorSheet({ adminUnitId }: { adminUnitId: string }) {
  const zone = useInvestorZone(adminUnitId);
  const slow = useSlow(zone.loading);

  // The printed sheet carries every breakdown: what is folded on screen opens on paper
  useEffect(() => {
    const unfold = () => document.querySelectorAll("[data-print-page] details").forEach((d) => d.setAttribute("open", ""));
    window.addEventListener("beforeprint", unfold);
    return () => window.removeEventListener("beforeprint", unfold);
  }, []);

  if (zone.loading) {
    return (
      <GlassCard role="status" className={styles.card}>
        <p>
          {TEXT.loadingSheet}
          {slow && ` ${SLOW_TEXT}`}
        </p>
      </GlassCard>
    );
  }
  if (zone.error || !zone.data) {
    const notFound = zone.error?.code === "NOT_FOUND";
    return (
      <GlassCard role="alert" className={styles.card}>
        <p>{notFound ? SHEET_TEXT.notPilot : zone.error ? errorMessage(zone.error) : TEXT.loadingSheet}</p>
        {notFound ? (
          <Button href="/inversores">{TEXT.back}</Button>
        ) : (
          <Button variant="secondary" onClick={zone.retry}>
            {TEXT.retry}
          </Button>
        )}
      </GlassCard>
    );
  }

  const sheet = zone.data.data;
  const version = zone.data.meta?.data_version ?? null;
  return (
    <div className={styles.sheet} data-print-page data-investors>
      <header className={styles.header}>
        <p className={`${styles.backLink} no-print`}>
          <Link href="/inversores">{TEXT.back}</Link>
        </p>
        <p className={styles.plan}>{TEXT.plan}</p>
        <p className={styles.eyebrow}>{SHEET_TEXT.eyebrow(sheet.district.name)}</p>
        <h1 className={styles.title}>{sheet.zone.name}</h1>
        <p className={styles.printOnly}>{TEXT.generated(today(), version)}</p>
        <div className={`${styles.actions} no-print`}>
          <Button variant="secondary" onClick={() => window.print()}>
            <Printer size={18} aria-hidden="true" />
            {TEXT.print}
          </Button>
          <span className={styles.note}>{TEXT.printHelp}</span>
        </div>
      </header>
      <Demand sheet={sheet} />
      <Prices sheet={sheet} />
      <Gaps sheet={sheet} />
      <Land sheet={sheet} />
      <Section id="viabilidad" title={TEXT.sections.viability}>
        <Calculator defaults={sheet.defaults} parcels={sheet.land.parcels} remaining={sheet.land.remaining} />
      </Section>
      <Sources sheet={sheet} version={version} method={zone.data.meta?.methodology_version ?? null} />
    </div>
  );
}
