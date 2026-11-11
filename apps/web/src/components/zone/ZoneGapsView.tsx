"use client";

import { ArrowRight } from "lucide-react";
import Link from "next/link";

import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { errorMessage } from "@/lib/errors";
import { GAP_STATUS, gapsHref, SMALL_ZONE, sortRows } from "@/lib/gaps";
import { isWholeCity, type ZoneLevel, zoneHref } from "@/lib/map/zones";

import GapBadge from "./GapBadge";
import GapRowItem from "./GapRowItem";
import PendingRows from "./PendingRows";
import SmallZoneTag from "./SmallZoneTag";
import ZoneDirectory from "./ZoneDirectory";
import styles from "./ZoneGapsView.module.css";
import { useZoneGaps } from "./useZoneGaps";

// Copy from pitch/textos_web.md (falta.*, falta.leyenda.*, fila.zona_pequena, zona.boton, carga.falta,
// error.reintentar).
const TEXT = {
  title: "Qué falta",
  titleIn: (zona: string) => `Qué falta en ${zona}`,
  intro: "Comparamos cada servicio con los demás municipios de su tipo, urbanos o rurales, según cuánta gente vive aquí.",
  pick: "Elige una zona en el mapa o escríbela aquí para ver qué le falta.",
  placeholder: "Escribe un municipio o un distrito de Madrid",
  loading: "Calculando qué falta en esta zona…",
  retry: "Reintentar",
  other: "Elegir otra zona",
  open: "Ver la zona",
  how: "¿Cómo lo decidimos?",
  municipio: "Municipio",
  notFound: "No encontramos esa zona. Elige otra en el mapa.",
  legend: "Cómo leer esta lista",
  walking:
    "Los minutos a pie son andando por la calle, no en línea recta, a paso tranquilo (4 km/h). Desde la mitad de las calles de la zona se llega en ese tiempo o menos.",
};

function ZonePicker() {
  return (
    <GlassCard as="section" aria-label={TEXT.pick} className={styles.picker}>
      <p>{TEXT.pick}</p>
      <ZoneDirectory hrefFor={(zone) => gapsHref(zone.level, zone.code)} placeholder={TEXT.placeholder} wholeCities />
    </GlassCard>
  );
}

function Legend() {
  return (
    <GlassCard as="section" aria-labelledby="como-leer" className={styles.legend}>
      <h2 id="como-leer">{TEXT.legend}</h2>
      <ul>
        {(Object.keys(GAP_STATUS) as (keyof typeof GAP_STATUS)[]).map((status) => (
          <li key={status}>
            <GapBadge status={status} />
            <span>{GAP_STATUS[status].help}</span>
          </li>
        ))}
        <li>
          <SmallZoneTag />
          <span aria-hidden="true">{SMALL_ZONE.help}</span>
        </li>
      </ul>
      <p className={styles.walking}>{TEXT.walking}</p>
      <Link href="/como-lo-calculamos#que-falta" className={styles.how}>
        {TEXT.how}
      </Link>
    </GlassCard>
  );
}

function ZoneGaps({ level, code }: { level: ZoneLevel; code: string }) {
  const gaps = useZoneGaps(level, code);
  const slow = useSlow(gaps.loading);

  if (gaps.loading) {
    return (
      <>
        <h1 className={styles.title}>{TEXT.title}</h1>
        <GlassCard role="status" className={styles.state}>
          <p>
            {TEXT.loading}
            {slow && ` ${SLOW_TEXT}`}
          </p>
        </GlassCard>
      </>
    );
  }
  if (gaps.error || !gaps.data) {
    const notFound = gaps.error?.code === "NOT_FOUND";
    return (
      <>
        <h1 className={styles.title}>{TEXT.title}</h1>
        <GlassCard role="alert" className={styles.state}>
          <p>{gaps.error ? errorMessage(gaps.error) : TEXT.loading}</p>
          {notFound ? (
            <Button href="/que-falta">{TEXT.other}</Button>
          ) : (
            <Button variant="secondary" onClick={gaps.retry}>
              {TEXT.retry}
            </Button>
          )}
        </GlassCard>
      </>
    );
  }

  const { zone, rows } = gaps.data.data;
  return (
    <>
      <header className={styles.header}>
        <p className={styles.eyebrow}>{zone.level === "distrito" ? `Distrito de ${zone.municipio_name}` : TEXT.municipio}</p>
        <h1 className={styles.title}>{TEXT.titleIn(zone.name)}</h1>
        <p className={styles.intro}>{TEXT.intro}</p>
        <div className={styles.actions}>
          {/* Madrid capital is on the map by its districts: its whole list has no zone screen */}
          {!isWholeCity(zone.admin_unit_id) && (
            <Button href={zoneHref({ level, code })}>
              {TEXT.open}
              <ArrowRight size={20} aria-hidden="true" />
            </Button>
          )}
          <Button href="/que-falta" variant="secondary">
            {TEXT.other}
          </Button>
        </div>
      </header>
      {rows.length > 0 && (
        <ul className={styles.rows}>
          {sortRows(rows).map((row) => (
            <GapRowItem key={row.row} row={row} zoneName={zone.name} />
          ))}
        </ul>
      )}
      <PendingRows warnings={gaps.data.warnings} className={styles.pending} />
      <Legend />
    </>
  );
}

interface Props {
  zone: { level: ZoneLevel; code: string } | null;
  /** ?zona= came with something that is not a zone of the map */
  invalid?: boolean;
}

/** The «Qué falta» tab: one zone's full list (?zona=distrito/2807905), or a zone picker. */
export default function ZoneGapsView({ zone, invalid = false }: Props) {
  if (!zone) {
    return (
      <>
        <h1 className={styles.title}>{TEXT.title}</h1>
        {invalid && (
          <p role="alert" className={styles.invalid}>
            {TEXT.notFound}
          </p>
        )}
        <ZonePicker />
      </>
    );
  }
  return <ZoneGaps key={`${zone.level}/${zone.code}`} level={zone.level} code={zone.code} />;
}
