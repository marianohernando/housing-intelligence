/**
 * Context figures of a zone (pure, unit tested): known criminal offences, how old its dwellings are
 * and its income (D-235). They never score, filter or rank, are not part of «Qué falta» and are never
 * shown with status or alarm colours. Municipios and Madrid's districts and barrios have different
 * measures of age and income: each says what it is, and they are never put on one scale.
 */
import type { FeatureValueRow } from "@/lib/features";
import { formatEuros, formatNumber } from "@/lib/format";

export type ContextLevel = "municipio" | "distrito" | "barrio";
export type ContextKey = "crime" | "age" | "income";

/** What is shown: a municipio, a district of Madrid, or the barrio picked inside a district. */
export interface ContextZone {
  level: ContextLevel;
  code: string;
  name: string;
}

export interface ContextRequest {
  key: ContextKey;
  /** Feature of GET /api/v1/features/{id}/values */
  featureId: string;
  level: ContextLevel;
}

/**
 * The three answers a zone's figures come from. The offences are only published by municipio, so a
 * district or a barrio asks for the city's; age and income have their own measure inside Madrid.
 */
export function contextRequests(level: ContextLevel): ContextRequest[] {
  if (level === "municipio") {
    return [
      { key: "crime", featureId: "infracciones_penales_por_1000_hab", level: "municipio" },
      { key: "age", featureId: "viviendas_desde_2001_pct", level: "municipio" },
      { key: "income", featureId: "renta_per_capita", level: "municipio" },
    ];
  }
  return [
    { key: "crime", featureId: "infracciones_penales_por_1000_hab", level: "municipio" },
    { key: "age", featureId: "ano_medio_construccion_residencial", level },
    { key: "income", featureId: "renta_neta_media_hogar", level },
  ];
}

/** Rows of each answer; a key is missing when the API does not have that feature (its line is not shown). */
export type ContextRows = Partial<Record<ContextKey, readonly FeatureValueRow[]>>;

export interface ContextLine {
  key: ContextKey;
  /** The figure with its source and year, or that there is none and why */
  text: string;
  /** What the figure does and does not say (offences only) */
  note: string | null;
}

// Copy from pitch/textos_web.md (zona.contexto.*).
const TEXT = {
  crime: "Infracciones penales conocidas",
  crimeSource: "Ministerio del Interior",
  crimeNote: "Mide hechos conocidos por la policía, sin los delitos por internet; sube donde hay mucha gente de paso.",
  crimeSmall: "El Ministerio solo lo publica para municipios de más de 20.000 habitantes.",
  crimeCity: "Dato de toda la ciudad de Madrid; no se publica por distrito.",
  builtSince2001: "Viviendas construidas desde 2001",
  builtSource: "censo anual de la Comunidad de Madrid",
  meanYear: "Año medio de construcción de los edificios de viviendas",
  meanYearSource: "Catastro",
  incomePerson: "Renta disponible bruta por persona",
  incomePersonSource: "Instituto de Estadística de la Comunidad de Madrid",
  incomeHousehold: "Renta media por hogar",
  incomeHouseholdSource: "INE",
  none: "sin dato",
};

// The figure and its unit never part at the end of a line on a phone («32,7 %»)
const NBSP = "\u00a0";

interface Known {
  value: number;
  year: string;
}

/** The latest row of a territory: its value and year, null when the source gives none (never 0), undefined without a row. */
function latest(rows: readonly FeatureValueRow[], code: string): Known | null | undefined {
  const own = rows.filter((r) => r.territory_code === code);
  const last = [...own].sort((a, b) => b.period_start.localeCompare(a.period_start))[0];
  if (!last) return undefined;
  return last.value === null ? null : { value: last.value, year: last.period_start.slice(0, 4) };
}

const cited = (label: string, figure: string, source: string, year: string) => `${label}: ${figure} (${source}, ${year}).`;

function crimeLine(zone: ContextZone, rows: readonly FeatureValueRow[]): ContextLine | null {
  const inMunicipio = zone.level === "municipio";
  // A district's or barrio's code starts with its municipio's five digits («2807905» is in «28079»)
  const known = latest(rows, zone.code.slice(0, 5));
  if (!known) {
    // Inside Madrid the city's figure is all there is: without it, nothing to say about the district
    return inMunicipio ? { key: "crime", text: `${TEXT.crime}: ${TEXT.none}. ${TEXT.crimeSmall}`, note: null } : null;
  }
  const figure = `${formatNumber(known.value, 1)} por cada 1.000 habitantes`;
  const text = cited(TEXT.crime, figure, TEXT.crimeSource, known.year);
  return { key: "crime", text: inMunicipio ? text : `${text} ${TEXT.crimeCity}`, note: TEXT.crimeNote };
}

/** «… en Simancas» for the barrio picked inside a district; the zone's own page needs no name. */
const where = (zone: ContextZone) => (zone.level === "barrio" ? ` en ${zone.name}` : "");

function ageLine(zone: ContextZone, rows: readonly FeatureValueRow[]): ContextLine | null {
  const known = latest(rows, zone.code);
  if (zone.level === "municipio") {
    const text = known
      ? cited(TEXT.builtSince2001, `${formatNumber(known.value, 1)}${NBSP}%`, TEXT.builtSource, known.year)
      : `${TEXT.builtSince2001}: ${TEXT.none}.`;
    return { key: "age", text, note: null };
  }
  if (!known) return null;
  // A year, not a quantity: no thousands dot
  return { key: "age", text: cited(`${TEXT.meanYear}${where(zone)}`, String(Math.round(known.value)), TEXT.meanYearSource, known.year), note: null };
}

function incomeLine(zone: ContextZone, rows: readonly FeatureValueRow[]): ContextLine | null {
  const known = latest(rows, zone.code);
  if (!known) return null;
  const figure = `${formatEuros(Math.round(known.value))} al año`;
  const text =
    zone.level === "municipio"
      ? cited(TEXT.incomePerson, figure, TEXT.incomePersonSource, known.year)
      : cited(`${TEXT.incomeHousehold}${where(zone)}`, figure, TEXT.incomeHouseholdSource, known.year);
  return { key: "income", text, note: null };
}

/**
 * One short line per figure, in a fixed order, each with its source and year. A feature the API does
 * not have gives no line; a municipio the Ministerio does not publish says so, never 0.
 */
export function contextLines(zone: ContextZone, rows: ContextRows): ContextLine[] {
  const lines = [
    rows.crime && crimeLine(zone, rows.crime),
    rows.age && ageLine(zone, rows.age),
    rows.income && incomeLine(zone, rows.income),
  ];
  return lines.filter((line): line is ContextLine => Boolean(line));
}
