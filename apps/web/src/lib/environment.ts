/**
 * «Entorno» of a zone (pure, unit tested), D-237: street noise, air and car parks. Context in the
 * zone view only, asked for by people who tried the demo («pensando en comprar una casa, el ruido
 * también importa», «facilidad de aparcar»): it does not score, rank or enter «Qué falta», and it
 * is never shown with status or alarm colours. Copy of pitch/textos_web.md (zona.entorno.*).
 */
import { formatNumber } from "@/lib/format";
import type { FeatureValueRow } from "@/lib/features";
import type { Facility } from "@/lib/map/facilities";

/** Features of GET /api/v1/features/{id}/values behind the block (data/catalog/features). */
export const ENVIRONMENT_FEATURES = {
  noiseDay: "pct_calle_ruido_dia",
  noiseNight: "pct_calle_ruido_noche",
  air: "no2_media_anual",
  parking: "min_a_pie_aparcamiento_publico",
} as const;

export type EnvironmentFeature = (typeof ENVIRONMENT_FEATURES)[keyof typeof ENVIRONMENT_FEATURES];
export type EnvironmentRows = Partial<Record<EnvironmentFeature, readonly FeatureValueRow[]>>;

/** Annual NO₂ limit of the EU from 2030 (Directive (EU) 2024/2881), µg/m³. */
export const EU_NO2_LIMIT_2030 = 20;
/** Further than this on foot, a car park is not «near» and the minutes are not said. */
export const PARKING_MAX_MINUTES = 30;

export const ENVIRONMENT_TEXT = {
  title: "Entorno",
  context: "Datos de contexto: no cuentan en el encaje ni en «Qué falta».",
  noiseSource: "Mapa Estratégico de Ruido 2021, Ayuntamiento de Madrid",
  noiseHint: "Ruido del tráfico medido en la propia calle: más de 65 dB de día o de 55 dB de noche, los límites para zonas residenciales.",
  noData: "sin dato publicado",
  airSource: "Redes de calidad del aire de la Comunidad de Madrid y del Ayuntamiento de Madrid, horas válidas del año.",
  parkingSource:
    "Aparcamientos publicados en abierto: los de disuasión del Consorcio Regional de Transportes y los del Ayuntamiento de Madrid. Lo fácil que es aparcar en la calle no tiene dato abierto.",
} as const;

/** The zone's latest row with a value; null without one (never 0). */
export function latestValue(rows: readonly FeatureValueRow[] | undefined, code: string): FeatureValueRow | null {
  const known = (rows ?? []).filter((r) => r.territory_code === code && r.value !== null);
  return known.sort((a, b) => b.period_start.localeCompare(a.period_start))[0] ?? null;
}

const pct = (value: number) => formatNumber(Math.round(value), 0);

/** «Calles con ruido alto: 38 % de día, 48 % de noche (Mapa Estratégico de Ruido 2021, Ayuntamiento de Madrid)». */
export function noiseText(day: FeatureValueRow | null, night: FeatureValueRow | null): string {
  if (day?.value == null || night?.value == null) return `Calles con ruido alto: ${ENVIRONMENT_TEXT.noData}`;
  return `Calles con ruido alto: ${pct(day.value)} % de día, ${pct(night.value)} % de noche (${ENVIRONMENT_TEXT.noiseSource})`;
}

interface StationDetail {
  station: string;
  own: boolean;
  distanceKm: number | null;
}

function stationOf(row: FeatureValueRow): StationDetail | null {
  const detail = row.detail;
  if (!detail || typeof detail.station !== "string") return null;
  const distance = typeof detail.distance_km === "number" ? detail.distance_km : null;
  return { station: detail.station, own: detail.own === true, distanceKm: distance };
}

/**
 * «Aire: NO₂ medio 2025, 25,6 µg/m³ en la estación de Getafe (límite UE 2030: 20)». A zone
 * without a station of its own says which one it takes and how far it is; the value never goes
 * without its station.
 */
export function airText(row: FeatureValueRow | null): string {
  const station = row ? stationOf(row) : null;
  if (!row || row.value === null || !station) return `Aire: ${ENVIRONMENT_TEXT.noData}`;
  const year = row.period_start.slice(0, 4);
  const where = station.own
    ? `en la estación de ${station.station}`
    : `en la estación de ${station.station}, la más cercana de su zona de calidad del aire${station.distanceKm === null ? "" : `, a ${formatNumber(station.distanceKm, 1)} km`}`;
  return `Aire: NO₂ medio ${year}, ${formatNumber(row.value, 1)} µg/m³ ${where} (límite UE 2030: ${EU_NO2_LIMIT_2030})`;
}

/** «Aparcamiento público a unos 12 min andando»; past 30 min, that none of the published ones is near. */
export function parkingText(row: FeatureValueRow | null): string | null {
  if (row?.value == null) return null;
  const minutes = Math.max(1, Math.round(row.value));
  if (minutes > PARKING_MAX_MINUTES) return `Ningún aparcamiento público de los publicados en abierto a menos de ${PARKING_MAX_MINUTES} min andando`;
  return `Aparcamiento público a unos ${formatNumber(minutes, 0)} min andando`;
}

const FEE_WORD = { free: "gratuito", paid: "de pago", mixed: "gratuito y de pago" } as const;
const DISUASORIO = "Aparcamiento disuasorio";

/**
 * The park-and-ride car parks of the zone, from «Todos los centros»: «Aparcamiento disuasorio
 * gratuito (210 plazas) en Usera: Doce de Octubre», or «3 aparcamientos disuasorios en Getafe, con
 * 1.519 plazas (todos gratuitos)». Spaces and fee only when every one says them; null without any.
 */
export function parkAndRideText(items: readonly Facility[], zone: string): string | null {
  const parks = items.filter((f) => f.label === DISUASORIO);
  if (!parks.length) return null;
  const spaces = parks.every((f) => typeof f.spaces === "number") ? parks.reduce((sum, f) => sum + (f.spaces ?? 0), 0) : null;
  const fees = parks.map((f) => f.fee ?? null);
  if (parks.length === 1) {
    const [park] = parks as [Facility];
    const fee = fees[0] ? ` ${FEE_WORD[fees[0]]}` : "";
    const size = spaces === null ? "" : ` (${formatNumber(spaces, 0)} plazas)`;
    const name = park.name?.replace(/^Aparcamiento disuasorio\s*/i, "").trim();
    return `${DISUASORIO}${fee}${size} en ${zone}${name ? `: ${name}` : ""}`;
  }
  const free = fees.filter((f) => f === "free").length;
  const freeText = free === parks.length ? "todos gratuitos" : free ? `${formatNumber(free, 0)} ${free === 1 ? "gratuito" : "gratuitos"}` : null;
  const size = spaces === null ? "" : `, con ${formatNumber(spaces, 0)} plazas`;
  return `${formatNumber(parks.length, 0)} aparcamientos disuasorios en ${zone}${size}${freeText ? ` (${freeText})` : ""}`;
}

export interface EnvironmentFacts {
  noise: string;
  /** Only when the zone has a figure: outside Madrid the source line would be about nothing */
  noiseKnown: boolean;
  air: string;
  parking: string | null;
  parkAndRide: string | null;
}

/** Every line of the block for one zone; null when the API gave nothing at all for it. */
export function environmentFacts(code: string, rows: EnvironmentRows, parks: readonly Facility[], zone: string): EnvironmentFacts | null {
  const day = latestValue(rows[ENVIRONMENT_FEATURES.noiseDay], code);
  const night = latestValue(rows[ENVIRONMENT_FEATURES.noiseNight], code);
  const air = latestValue(rows[ENVIRONMENT_FEATURES.air], code);
  const parking = latestValue(rows[ENVIRONMENT_FEATURES.parking], code);
  const parkAndRide = parkAndRideText(parks, zone);
  if (!day && !night && !air && !parking && !parkAndRide) return null;
  return {
    noise: noiseText(day, night),
    noiseKnown: day !== null && night !== null,
    air: airText(air),
    parking: parkingText(parking),
    parkAndRide,
  };
}
