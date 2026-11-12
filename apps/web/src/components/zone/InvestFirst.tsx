"use client";

import { ArrowRight } from "lucide-react";
import Link from "next/link";

import type { GapImpactRow } from "@/contracts/gap_impact_response";
import Button from "@/components/ui/Button";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { errorMessage } from "@/lib/errors";
import { impactContext, impactFigure, impactSentence, moreZonesText, type RankedZone, rankedZone, SHOWN_FIRST, splitImpactRows } from "@/lib/impact";

import styles from "./InvestFirst.module.css";
import { useGapImpact } from "./useGapImpact";

// B's draft for line D (D-229: «dónde invertir primero»); the figures and the zones come from the API.
const TEXT = {
  title: "Dónde invertir primero",
  intro: "Cuánta gente vive en zonas donde falta cada servicio, y qué zonas van primero porque tienen más gente afectada.",
  loading: "Calculando dónde falta en toda la Comunidad…",
  retry: "Reintentar",
  ranking: (label: string) => `Zonas donde faltan ${label}, de más a menos gente afectada`,
  rest: (label: string) => `Resto de zonas donde faltan ${label}`,
  note:
    "Solo cuentan las zonas en FALTA. Contamos a toda la gente de la zona a la que sirve cada servicio (por ejemplo, los niños de 0 a 4 años para las escuelas infantiles), según el censo y, en los distritos de Madrid, el padrón: no estimamos nada. Dentro de una zona, unas calles están mejor servidas que otras.",
  pick: "Ver lo que falta en otra zona",
};

function ZoneItem({ zone, rank }: { zone: RankedZone; rank: number }) {
  return (
    <li className={styles.zone}>
      <span className={styles.rank}>{rank}</span>
      <span className={styles.zoneText}>
        {zone.href ? (
          <Link href={zone.href} className={styles.zoneName}>
            {zone.name}
            <ArrowRight size={16} aria-hidden="true" />
          </Link>
        ) : (
          <span className={styles.zoneName}>{zone.name}</span>
        )}
        <span className={styles.people}>{zone.people}</span>
        <span className={styles.comparison}>{zone.comparison}</span>
      </span>
    </li>
  );
}

function ImpactCard({ row }: { row: GapImpactRow }) {
  const zones = row.ranking.map((zone) => rankedZone(zone, row.people_label));
  const [first, rest] = [zones.slice(0, SHOWN_FIRST), zones.slice(SHOWN_FIRST)];
  const label = row.label.charAt(0).toLowerCase() + row.label.slice(1);
  return (
    <li className={`glass ${styles.card}`}>
      <h3>{row.label}</h3>
      <p className={styles.headline}>
        <strong className={styles.figure}>{impactFigure(row)}</strong> {impactSentence(row)}
      </p>
      <p className={styles.context}>{impactContext(row)}</p>
      {/* role="list": Safari drops the list semantics of a list without markers */}
      <ol className={styles.ranking} role="list" aria-label={TEXT.ranking(label)}>
        {first.map((zone, i) => (
          <ZoneItem key={zone.key} zone={zone} rank={i + 1} />
        ))}
      </ol>
      {rest.length > 0 && (
        <details className={styles.more}>
          <summary>{moreZonesText(rest.length)}</summary>
          <ol className={styles.ranking} role="list" aria-label={TEXT.rest(label)} start={SHOWN_FIRST + 1}>
            {rest.map((zone, i) => (
              <ZoneItem key={zone.key} zone={zone} rank={SHOWN_FIRST + i + 1} />
            ))}
          </ol>
        </details>
      )}
    </li>
  );
}

/**
 * «Dónde invertir primero» (D-229): for each row of «Qué falta», how many people live in zones in
 * FALTA in the whole region, and those zones from most to fewest people, each linking to its list.
 */
export default function InvestFirst({ pickId }: { pickId: string }) {
  const impact = useGapImpact();
  const slow = useSlow(impact.loading);
  const { affected, clear } = splitImpactRows(impact.data?.rows ?? []);

  return (
    <section aria-labelledby="invertir" className={styles.section}>
      <div className={styles.header}>
        <h2 id="invertir">{TEXT.title}</h2>
        <p className={styles.intro}>{TEXT.intro}</p>
        <a href={`#${pickId}`} className={styles.pick}>
          {TEXT.pick}
        </a>
      </div>
      {impact.loading && (
        <p role="status" className={styles.state}>
          {TEXT.loading}
          {slow && ` ${SLOW_TEXT}`}
        </p>
      )}
      {impact.error && (
        <div role="alert" className={styles.state}>
          <p>{errorMessage(impact.error)}</p>
          <Button variant="secondary" onClick={impact.retry}>
            {TEXT.retry}
          </Button>
        </div>
      )}
      {impact.data && (
        <>
          <ul className={styles.cards}>
            {affected.map((row) => (
              <ImpactCard key={row.row} row={row} />
            ))}
          </ul>
          {clear.length > 0 && (
            <ul className={styles.clear}>
              {clear.map((row) => (
                <li key={row.row}>{row.summary.replace(/\.?$/, ".")}</li>
              ))}
            </ul>
          )}
          <p className={styles.note}>{TEXT.note}</p>
        </>
      )}
    </section>
  );
}
