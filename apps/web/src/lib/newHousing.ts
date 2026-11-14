/**
 * «Vivienda nueva y lo que viene» of a zone (pure, unit tested): D-241. How much of what is sold
 * is new, what a new home is appraised at next to an older one, the Plan Vive homes and, in a
 * Madrid district, the planning areas for housing not yet finished. Context only: none of it
 * scores, filters or ranks, it is not part of «Qué falta» and it never takes status or alarm
 * colours. Copy from pitch/textos_web.md (zona.vivienda_nueva.*).
 */
import type { ContextItem, FeatureValueRow } from "@/lib/features";
import { formatNumber } from "@/lib/format";

export type NewHousingLevel = "municipio" | "distrito";
export type NewHousingKey = "sales" | "newValue" | "usedValue" | "planVive" | "areas";

export interface NewHousingZone {
  level: NewHousingLevel;
  code: string;
}

export interface NewHousingRequest {
  key: NewHousingKey;
  /** Feature of GET /api/v1/features/{id}/values */
  featureId: string;
  level: NewHousingLevel;
}

const FEATURES: Record<NewHousingKey, string> = {
  sales: "compraventas_obra_nueva_pct",
  newValue: "valor_tasado_vivienda_nueva_m2",
  usedValue: "valor_tasado_vivienda_usada_m2",
  planVive: "plan_vive_viviendas",
  areas: "ambitos_residenciales_en_desarrollo",
};

/**
 * The answers a zone's lines come from. Sales and appraisals are only published by municipio, so
 * a district asks for the city's; Plan Vive and the planning areas have their own district rows.
 */
export function newHousingRequests(level: NewHousingLevel): NewHousingRequest[] {
  const at = (key: NewHousingKey, own: NewHousingLevel): NewHousingRequest => ({ key, featureId: FEATURES[key], level: own });
  const city = [at("sales", "municipio"), at("newValue", "municipio"), at("usedValue", "municipio")];
  return level === "municipio" ? [...city, at("planVive", "municipio")] : [...city, at("planVive", "distrito"), at("areas", "distrito")];
}

/** Rows of each answer; a key is missing when the API does not have that feature (its line is not shown). */
export type NewHousingRows = Partial<Record<NewHousingKey, readonly FeatureValueRow[]>>;

export interface NewHousingLine {
  key: string;
  /** The figure in a plain sentence */
  text: string;
  /** What it is not, when the figure could be read wrong (a city figure, a shared Plan Vive entry) */
  note: string | null;
  /** Who publishes it and when */
  source: string;
}

// The figure and its unit never part at the end of a line on a phone («28 %», «5.432 €/m²»)
const NBSP = " ";
const MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
const QUARTERS = ["1.er", "2.º", "3.er", "4.º"];

export const TEXT = {
  city: "En toda la ciudad de Madrid, ",
  cityNote: "La fuente no lo da por distritos.",
  provisional: " El último trimestre aún es provisional.",
  salesSource: "Ministerio de Transportes, Movilidad y Agenda Urbana, en el portal de datos abiertos de la Comunidad de Madrid",
  valueSource: "Valor tasado medio de {año} del Ministerio de Vivienda y Agenda Urbana, en el portal de datos abiertos de la Comunidad de Madrid; «usada» es la de más de 5 años.",
  planViveSource: "Página del Plan Vive de la Comunidad de Madrid, consultada el {fecha}.",
  areasSource: "Ayuntamiento de Madrid, estado de desarrollo de los ámbitos del Plan General a {fecha}. Dice dónde se prepara suelo para vivienda, no cuántas viviendas habrá ni cuándo.",
  areasNone: "En este distrito no queda ningún ámbito de vivienda del Plan General por terminar.",
} as const;

const STAGES: Record<string, { label: string; tail: string }> = {
  obras: { label: "En desarrollo", tail: "urbanización en obras" },
  tramitacion: { label: "En tramitación", tail: "planeamiento, gestión o proyecto en marcha" },
  sin_empezar: { label: "Previstos", tail: "aún sin empezar" },
};
const MAX_NAMES = 4;

/** «2026-11-14» -> «14 de noviembre de 2026» */
export function dateInWords(iso: string): string {
  const [year, month, day] = iso.slice(0, 10).split("-").map(Number);
  return `${day} de ${MONTHS[(month ?? 1) - 1]} de ${year}`;
}

/** «2025-07-01» -> «3.er trimestre de 2025» */
export function quarterInWords(iso: string): string {
  const [year, month] = iso.slice(0, 10).split("-").map(Number);
  return `${QUARTERS[Math.floor(((month ?? 1) - 1) / 3)]} trimestre de ${year}`;
}

/** «A», «A y B», «A, B y C»; more than `max`, «A, B, C, D y 2 más». */
export function listInWords(names: readonly string[], max: number = MAX_NAMES): string {
  const shown = names.length > max ? [...names.slice(0, max), `${names.length - max} más`] : [...names];
  return shown.length <= 1 ? (shown[0] ?? "") : `${shown.slice(0, -1).join(", ")} y ${shown[shown.length - 1]}`;
}

const count = (n: number) => formatNumber(n, 0);
const pct = (value: number) => `${formatNumber(value, value < 10 ? 1 : 0)}${NBSP}%`;
const perM2 = (value: number) => `${count(Math.round(value))}${NBSP}€/m²`;

/** The latest row of a territory, or undefined without one. */
function latest(rows: readonly FeatureValueRow[], code: string): FeatureValueRow | undefined {
  return [...rows.filter((r) => r.territory_code === code)].sort((a, b) => b.period_start.localeCompare(a.period_start))[0];
}

/** Sales: «650 de las 2.311 compraventas de vivienda del último año fueron de obra nueva (28 %).» */
export function salesSentence(newSales: number, total: number, share: number | null): string | null {
  if (total === 0) return "No hubo compraventas de vivienda en el último año.";
  if (total === 1) return `La única compraventa de vivienda del último año fue ${newSales === 1 ? "de obra nueva" : "de segunda mano"}.`;
  if (newSales === 0) return `Ninguna de las ${count(total)} compraventas de vivienda del último año fue de obra nueva.`;
  if (share === null) return null;
  const verb = newSales === 1 ? "fue" : "fueron";
  return `${count(newSales)} de las ${count(total)} compraventas de vivienda del último año ${verb} de obra nueva (${pct(share)}).`;
}

const lowerFirst = (text: string) => text.charAt(0).toLowerCase() + text.slice(1);

function salesLine(zone: NewHousingZone, rows: readonly FeatureValueRow[]): NewHousingLine | null {
  const inCity = zone.level === "distrito";
  const row = latest(rows, zone.code.slice(0, 5));
  const detail = row?.detail;
  if (!row || !detail || detail.numerator == null || detail.denominator == null) return null;
  const sentence = salesSentence(detail.numerator, detail.denominator, row.value);
  if (!sentence) return null;
  const window = `del ${quarterInWords(row.period_start)} al ${detail.period_end ? quarterInWords(detail.period_end) : "último publicado"}`;
  return {
    key: "sales",
    text: `${inCity ? `${TEXT.city}${lowerFirst(sentence)}` : sentence}${detail.provisional ? TEXT.provisional : ""}`,
    note: inCity ? TEXT.cityNote : null,
    source: `${TEXT.salesSource}, ${window}.`,
  };
}

/** Appraisals: «Una vivienda de menos de 5 años se tasa a 5.432 €/m², un 13 % más que la usada.» */
export function valueSentence(newValue: number, usedValue: number): string {
  const diff = Math.round((newValue / usedValue - 1) * 100);
  const compared = diff === 0 ? "casi lo mismo que la usada" : `un ${Math.abs(diff)}${NBSP}% ${diff > 0 ? "más" : "menos"} que la usada`;
  return `Una vivienda de menos de 5 años se tasa a ${perM2(newValue)}, ${compared}.`;
}

function valueLine(zone: NewHousingZone, newRows: readonly FeatureValueRow[], usedRows: readonly FeatureValueRow[]): NewHousingLine | null {
  const code = zone.code.slice(0, 5);
  const [fresh, used] = [latest(newRows, code), latest(usedRows, code)];
  if (fresh?.value == null || used?.value == null || !used.value || fresh.period_start !== used.period_start) return null;
  const sentence = valueSentence(fresh.value, used.value);
  const inCity = zone.level === "distrito";
  return {
    key: "value",
    text: inCity ? `${TEXT.city}${lowerFirst(sentence)}` : sentence,
    note: inCity ? TEXT.cityNote : null,
    source: TEXT.valueSource.replace("{año}", fresh.period_start.slice(0, 4)),
  };
}

/** «en entrega y en obras» from the page's «Entrega y construcción». */
export function phaseInWords(stage: string): string {
  const words: Record<string, string> = { entrega: "en entrega", construcción: "en obras", comercialización: "en comercialización" };
  const parts = stage
    .toLowerCase()
    .split(/,\s*|\s+y\s+/)
    .map((part) => part.trim())
    .filter(Boolean);
  return listInWords(parts.map((part) => words[part] ?? `en fase de ${part}`), parts.length);
}

/** «Lo que viene: Plan Vive, 756 viviendas de alquiler asequible en obras (avda. Olímpica y …).» */
export function planViveSentence(item: ContextItem): string | null {
  if (!item.value || !item.stage) return null;
  const where = item.name ? ` (${item.name})` : "";
  return `Lo que viene: Plan Vive, ${count(item.value)} viviendas de alquiler asequible ${phaseInWords(item.stage)}${where}.`;
}

function planViveLines(zone: NewHousingZone, rows: readonly FeatureValueRow[]): NewHousingLine[] {
  const row = latest(rows, zone.code);
  const source = row ? TEXT.planViveSource.replace("{fecha}", dateInWords(row.period_start)) : "";
  return (row?.detail?.items ?? []).flatMap((item, i) => {
    const text = planViveSentence(item);
    return text ? [{ key: `plan-vive-${item.code ?? i}`, text, note: item.note ?? null, source }] : [];
  });
}

/** «En desarrollo: Los Berrocales, Los Ahijones, Los Cerros y Camino Viejo de Vicálvaro (urbanización en obras).» */
export function areasSentences(items: readonly ContextItem[]): { stage: string; text: string }[] {
  const order = Object.keys(STAGES);
  const stages = [...new Set(items.map((item) => item.stage ?? ""))].sort((a, b) => order.indexOf(a) - order.indexOf(b));
  return stages.flatMap((stage) => {
    const words = STAGES[stage];
    const names = items.filter((item) => item.stage === stage && item.name).map((item) => item.name as string);
    return words && names.length ? [{ stage, text: `${words.label}: ${listInWords(names)} (${words.tail}).` }] : [];
  });
}

function areaLines(zone: NewHousingZone, rows: readonly FeatureValueRow[]): NewHousingLine[] {
  const row = latest(rows, zone.code);
  if (!row || row.value === null) return [];
  const source = TEXT.areasSource.replace("{fecha}", dateInWords(row.period_start));
  const items = row.detail?.items ?? [];
  if (row.value === 0 && items.length === 0) return [{ key: "areas-none", text: TEXT.areasNone, note: null, source }];
  return areasSentences(items).map(({ stage, text }) => ({ key: `areas-${stage}`, text, note: null, source }));
}

/**
 * One short line per figure, in a fixed order: what is sold, what it is appraised at, then what is
 * coming. A feature the API does not have gives no line; a figure the source does not publish for
 * the zone gives none either, never a 0.
 */
export function newHousingLines(zone: NewHousingZone, rows: NewHousingRows): NewHousingLine[] {
  const lines: (NewHousingLine | null)[] = [
    rows.sales ? salesLine(zone, rows.sales) : null,
    rows.newValue && rows.usedValue ? valueLine(zone, rows.newValue, rows.usedValue) : null,
    ...(rows.planVive ? planViveLines(zone, rows.planVive) : []),
    ...(rows.areas && zone.level === "distrito" ? areaLines(zone, rows.areas) : []),
  ];
  return lines.filter((line): line is NewHousingLine => line !== null);
}
