/**
 * «Vivienda nueva y lo que viene» of a zone (pure, unit tested): D-241. How much of what is sold
 * is new, what a new home is appraised at next to an older one, the Plan Vive homes, in a Madrid
 * district the planning areas for housing not yet finished and, since D-246, the public land
 * offered to build housing (Portal del Suelo), parcel by parcel. Context only: none of it scores,
 * filters or ranks, it is not part of «Qué falta» and it never takes status or alarm colours.
 * Copy from pitch/textos_web.md (zona.vivienda_nueva.*).
 */
import type { ContextItem, FeatureValueRow } from "@/lib/features";
import { formatNumber } from "@/lib/format";

export type NewHousingLevel = "municipio" | "distrito";
export type NewHousingKey = "sales" | "newValue" | "usedValue" | "planVive" | "areas" | "land";

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
  land: "suelo_publico_vivienda_m2",
};

/**
 * The answers a zone's lines come from. Sales and appraisals are only published by municipio, so
 * a district asks for the city's; Plan Vive, the planning areas and the public land have their own district rows.
 */
export function newHousingRequests(level: NewHousingLevel): NewHousingRequest[] {
  const at = (key: NewHousingKey, own: NewHousingLevel): NewHousingRequest => ({ key, featureId: FEATURES[key], level: own });
  const city = [at("sales", "municipio"), at("newValue", "municipio"), at("usedValue", "municipio")];
  return level === "municipio"
    ? [...city, at("planVive", "municipio"), at("land", "municipio")]
    : [...city, at("planVive", "distrito"), at("areas", "distrito"), at("land", "distrito")];
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
  /** D-246: the public parcels behind the line, listed under it (folded) */
  parcels?: LandParcels | null;
}

/** One public parcel for housing (D-246): where, its buildable m², how it is offered and by whom. */
export interface LandParcel {
  key: string;
  /** «UZPp 2.04 Desarrollo del Este–Los Berrocales · Parcela RC.5.3.1» */
  place: string;
  /** «9.685 m² edificables», or that the portal does not publish them */
  area: string;
  /** Only when the Comunidad publishes what its code means (venta, concesión); null otherwise */
  regime: string | null;
  manager: string | null;
  /** The parcel in the Comunidad's map viewer */
  url: string | null;
}

export interface LandParcels {
  /** «Ver las 16 parcelas» */
  toggle: string;
  /** zona.vivienda_nueva.suelo.visor */
  viewer: string;
  items: LandParcel[];
}

// The figure and its unit never part at the end of a line on a phone («28 %», «5.432 €/m²»)
const NBSP = " ";
const MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
const QUARTERS = ["1.er", "2.º", "3.er", "4.º"];

export const TEXT = {
  city: "En toda la ciudad de Madrid, ",
  cityNote: "La fuente no lo da por distritos.",
  provisional: " Incluye datos aún provisionales.",
  salesSource: "Ministerio de Transportes, Movilidad y Agenda Urbana, en el portal de datos abiertos de la Comunidad de Madrid",
  valueSource: "Valor tasado medio de {año} del Ministerio de Vivienda y Agenda Urbana, en el portal de datos abiertos de la Comunidad de Madrid; «usada» es la de más de 5 años.",
  planViveSource: "Página del Plan Vive de la Comunidad de Madrid, consultada el {fecha}.",
  areasSource: "Ayuntamiento de Madrid, estado de desarrollo de los ámbitos del Plan General a {fecha}. Dice dónde se prepara suelo para vivienda, no cuántas viviendas habrá ni cuándo.",
  areasNone: "En este distrito no queda ningún ámbito de vivienda del Plan General por terminar.",
  land: "Suelo público para vivienda: {parcelas}, {m2} m² edificables.",
  landNoArea: "Suelo público para vivienda: {parcelas}.",
  landNote: "Parcelas que la Comunidad de Madrid o los ayuntamientos ofrecen en venta o en concesión para construir vivienda. No dice cuántas viviendas caben.",
  landNoAreaNote: " De alguna parcela no se publica la superficie edificable.",
  landSource: "Portal del Suelo 4.0 de la Comunidad de Madrid, en su portal de datos abiertos, a {fecha}.",
  landToggle: "Ver las {n} parcelas",
  landToggleOne: "Ver la parcela",
  landArea: "{m2} m² edificables",
  landAreaMissing: "Superficie edificable sin publicar",
  landViewer: "Ver en el visor de la Comunidad",
  landReference: "Referencia {ref}",
} as const;

/** D-246: only the codes whose meaning the Comunidad publishes (V and C); the rest come without a regime. */
const REGIMES: Record<string, string> = {
  venta: "En venta",
  concesion: "En concesión, derecho de superficie o alquiler",
};

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

const parcelsInWords = (n: number) => (n === 1 ? "1 parcela" : `${count(n)} parcelas`);
const m2 = (value: number) => count(Math.round(value));

/** Only links to the Comunidad's map viewer become links (the pipeline quarantines any other, D-246). */
export const VIEWER_PREFIX = "https://idem.comunidad.madrid/";

function landParcel(item: ContextItem, i: number): LandParcel {
  // Without a location or a parcel name, its reference in the portal; never the link's text
  const place = [item.name, item.parcel].filter(Boolean).join(" · ") || TEXT.landReference.replace("{ref}", item.code ?? String(i + 1));
  return {
    key: item.code ?? String(i),
    place,
    area: item.value == null ? TEXT.landAreaMissing : TEXT.landArea.replace("{m2}", m2(item.value)),
    regime: item.regime ? (REGIMES[item.regime] ?? null) : null,
    manager: item.manager ?? null,
    url: item.url?.startsWith(VIEWER_PREFIX) ? item.url : null,
  };
}

/**
 * «Suelo público para vivienda: 16 parcelas, 67.808 m² edificables.» (D-246), with the parcels
 * under it. A zone without parcels says nothing (never «0 parcelas»); when a parcel does not
 * publish its buildable m², the sum is unknown and the line gives the parcels alone.
 */
export function landLine(zone: NewHousingZone, rows: readonly FeatureValueRow[]): NewHousingLine | null {
  const row = latest(rows, zone.code);
  const items = row?.detail?.items ?? [];
  if (!row || items.length === 0) return null;
  const parcels = parcelsInWords(items.length);
  const total = row.value;
  return {
    key: "land",
    text: total == null ? TEXT.landNoArea.replace("{parcelas}", parcels) : TEXT.land.replace("{parcelas}", parcels).replace("{m2}", m2(total)),
    note: total == null ? `${TEXT.landNote}${TEXT.landNoAreaNote}` : TEXT.landNote,
    source: TEXT.landSource.replace("{fecha}", dateInWords(row.period_start)),
    parcels: {
      toggle: items.length === 1 ? TEXT.landToggleOne : TEXT.landToggle.replace("{n}", count(items.length)),
      viewer: TEXT.landViewer,
      items: items.map(landParcel),
    },
  };
}

/**
 * One short line per figure, in a fixed order: what is sold, what it is appraised at, then what is
 * coming and the public land to build on. A feature the API does not have gives no line; a figure
 * the source does not publish for the zone gives none either, never a 0.
 */
export function newHousingLines(zone: NewHousingZone, rows: NewHousingRows): NewHousingLine[] {
  const lines: (NewHousingLine | null)[] = [
    rows.sales ? salesLine(zone, rows.sales) : null,
    rows.newValue && rows.usedValue ? valueLine(zone, rows.newValue, rows.usedValue) : null,
    ...(rows.planVive ? planViveLines(zone, rows.planVive) : []),
    ...(rows.areas && zone.level === "distrito" ? areaLines(zone, rows.areas) : []),
    rows.land ? landLine(zone, rows.land) : null,
  ];
  return lines.filter((line): line is NewHousingLine => line !== null);
}
