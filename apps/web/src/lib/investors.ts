/**
 * «Para inversores» (D-248): texts, formats and the calculator's request. Copy from
 * pitch/textos_web.md, section 11 (inversores.*). The figures and their sources come from the API
 * (GET /api/v1/investors/zones/{id}); this module never adds a number of its own.
 */
import type { InvestorZoneSummary } from "@/contracts/investor_zone_list_response";
import type { DatasetRef, LandItem, SourcedValue, ViabilityDefaults } from "@/contracts/investor_zone_response";
import type { ViabilityRequest } from "@/contracts/viability_request";
import type { BreakEven, Verdict } from "@/contracts/viability_response";
import { formatEuros, formatNumber } from "@/lib/format";
import { INVESTOR_METHOD as M } from "@/lib/investorMethod";

export const INVESTOR_TEXT = {
  plan: "Plan Inversor (acceso libre durante el concurso)",
  title: "Para inversores y promotores",
  intro:
    "Qué le falta a cada barrio, dónde hay suelo y si una promoción sale. Con datos abiertos y la fuente de cada cifra.",
  pilot: "Piloto: los barrios de Madrid capital dentro de la M-40.",
  model:
    "Las personas y los ayuntamientos usan Vida Fácil gratis. Inversores y promotores tendrán un plan de pago; durante el concurso, el acceso es libre y sin registro.",
  developers: "¿Integrarlo en tu sistema? API y MCP gratis", // inversores.desarrolladores (D-249)
  listTitle: "Explorar barrios", // inversores.lista.titulo (D-250: after «Busca tu parcela»)
  listIntro: "O empieza por un barrio del piloto: qué le falta, dónde hay suelo público y sus precios.",
  withLand: "Solo barrios con suelo público",
  loading: "Cargando los barrios…",
  loadingSheet: "Cargando la ficha del barrio…",
  retry: "Reintentar",
  back: "‹ Todos los barrios",
  listSummary: (total: number, withLand: number) =>
    `${total} barrios. ${withLand === 1 ? "1 tiene" : `${withLand} tienen`} suelo público para vivienda en el Portal del Suelo. Lo que falta es dato del distrito de cada barrio: «Qué falta» no se calcula por barrio.`,
  gapsUnknown: "Sin datos de lo que falta en su distrito.",
  emptyPilot: "La lista de barrios del piloto aún no está cargada. Vuelve a intentarlo en un rato.",
  print: "Guardar como PDF",
  printHelp: "Abre la versión para imprimir; en el cuadro de impresión, elige «Guardar como PDF».",
  generated: (date: string, version: string | null) =>
    `Generado el ${date}${version ? ` con los datos calculados el ${isoInWords(version)}` : ""} · Vida Fácil, proyecto para DATAMAD 2026`,
  sections: {
    demand: "1. Quién vive aquí",
    prices: "2. Precios",
    gaps: "3. Qué falta",
    land: "4. Suelo",
    viability: "5. ¿Sale la promoción?",
    sources: "Fuentes y avisos",
  },
} as const;

/**
 * D-251: «Cómo lo calculamos» from the parcel's sheet and the calculator to the investor section of
 * the method page; the hidden words tell it apart from the header tab for a screen reader.
 */
export const METHOD_LINK = {
  href: "/como-lo-calculamos#inversores",
  text: "Cómo lo calculamos",
  context: ": la ficha para inversores",
} as const;

/** «dato», «supuesto», «lo pones tú» next to a figure (never a colour alone). */
export const MARK_TEXT: Record<SourcedValue["mark"] | "sin_dato", string> = {
  dato: "Dato",
  supuesto: "Supuesto",
  usuario: "Lo pones tú",
  sin_dato: "Sin dato",
};

/** The semaphore: icon + word + colour (WCAG 1.4.1), the only state colours on these pages. */
export const VERDICT_TEXT: Record<Verdict, string> = {
  sale: "Sale",
  ajustar: "Ajustar",
  no_sale: "No sale",
};

export const LEVEL_TEXT: Record<string, string> = {
  barrio: "del barrio",
  distrito: "del distrito",
  municipio: "de toda la ciudad",
};

const MILLION = 1_000_000;

/** «850.000 €», «1,25 millones de €», «−200.000 €». */
export function money(amount: number): string {
  if (Math.abs(amount) >= MILLION) return `${formatNumber(amount / MILLION, 2)} millones de €`;
  return formatEuros(Math.round(amount));
}

export function percent(value: number, decimals = 1): string {
  return `${formatNumber(value, decimals)} %`;
}

/** A sourced figure in words, or «Sin dato» (never 0 for unknown). */
export function figure(value: SourcedValue, decimals = 0): string {
  if (value.value === null || value.value === undefined) return "Sin dato";
  const unit = value.unit;
  if (unit === "%") return percent(value.value, decimals);
  if (unit.startsWith("€/m²/mes")) return `${formatNumber(value.value, 2)} €/m² al mes`;
  if (unit.startsWith("€/hogar")) return `${formatEuros(Math.round(value.value))} al año`;
  if (unit.startsWith("€")) return `${formatNumber(value.value, decimals)} ${unit}`;
  return `${formatNumber(value.value, decimals)} ${unit}`;
}

/** An assumption's source without its leading «Supuesto:», which the tag next to it already says. */
export function withoutMark(source: string): string {
  const rest = source.replace(/^supuesto:\s*/i, "");
  return rest.charAt(0).toUpperCase() + rest.slice(1);
}

/** «Fuente: … · dato del distrito», as the API writes it. */
export function sourceLine(value: SourcedValue): string {
  return `Fuente: ${value.source.text}`;
}

export function rentRange(value: SourcedValue): string | null {
  if (value.low === null || value.low === undefined || value.high === null || value.high === undefined) return null;
  return `La mitad de los contratos, entre ${formatNumber(value.low, 1)} y ${formatNumber(value.high, 1)} €/m² al mes.`;
}

/** What a parcel or planning area is called in the picker and the list. */
export function landName(item: LandItem): string {
  const place = [item.name, item.parcel].filter(Boolean).join(" · ");
  return place || `Referencia ${item.code ?? "sin código"}`;
}

export function landArea(item: LandItem): string {
  return item.buildable_m2 === null || item.buildable_m2 === undefined
    ? "Superficie edificable sin publicar"
    : `${formatNumber(item.buildable_m2, 0)} m² edificables`;
}

const PROTECTED_MANAGER = /vivienda social|\bAVS\b|IVIMA/i;

/**
 * A caution for land whose homes are not sold at a free price: a parcel of the Agencia de
 * Vivienda Social (protected housing, with a maximum price) or one in concession (the land is
 * not bought). The free-market price and the residual land value do not apply to them.
 */
export function landCaution(item: LandItem | null): string | null {
  if (!item) return null;
  const notes: string[] = [];
  if (item.manager && PROTECTED_MANAGER.test(item.manager)) {
    notes.push("Es de la Agencia de Vivienda Social: suele ir a vivienda protegida, con precio máximo de venta o alquiler.");
  }
  if (item.regime === "concesion") {
    notes.push("Se ofrece en concesión, derecho de superficie o alquiler: el suelo no se compra.");
  }
  if (notes.length === 0) return null;
  return `${notes.join(" ")} El precio libre y el valor residual del suelo de esta cuenta no valen para vivienda protegida ni para una concesión: tómalos solo como referencia de mercado.`;
}

/** The situation of a planning area of line A (D-247, VEDA), in words. */
export const AREA_STAGE_TEXT: Record<string, string> = {
  // D-252 (B10): not «se puede construir ya»; it still takes a licence
  edificacion: "En fase de edificación, según el Ayuntamiento: no quiere decir que se pueda construir ya (hace falta licencia)",
  gestion_urbanizacion: "En gestión o urbanización",
  pendiente_planeamiento: "Pendiente de planeamiento de desarrollo",
  pendiente_sectorizacion: "Pendiente de plan de sectorización",
};

/** What a planning area says besides its m²: its situation and the type of home («colectiva»). */
export function areaFacts(item: LandItem): string[] {
  if (item.kind !== "ambito") return [];
  const stage = item.stage ? (AREA_STAGE_TEXT[item.stage] ?? null) : null;
  return [stage, item.use ? `vivienda ${item.use}` : null].filter((f): f is string => Boolean(f));
}

export const REGIME_TEXT: Record<string, string> = {
  venta: "En venta",
  concesion: "En concesión, derecho de superficie o alquiler",
};

/** The land the calculator starts with: the largest parcel, else the largest planning area. */
export function defaultLand(parcels: LandItem[], remaining: LandItem[]): LandItem | null {
  const known = (items: LandItem[]) =>
    items.filter((i) => typeof i.buildable_m2 === "number" && i.buildable_m2 > 0).sort((a, b) => (b.buildable_m2 ?? 0) - (a.buildable_m2 ?? 0));
  return known(parcels)[0] ?? known(remaining)[0] ?? null;
}

export function landKey(item: LandItem): string {
  return `${item.kind}:${item.code ?? item.name ?? ""}`;
}

/** The calculator's fields, as typed (strings: an empty field is «no value», never 0). */
export interface CalculatorFields {
  buildable_m2: string;
  sale_price_m2: string;
  new_build_premium_pct: string;
  rent_m2_month: string;
  pem_m2: string;
  cost_coefficient: string;
  land: string;
  land_unit: "total" | "m2";
  sales_costs_pct: string;
  target_margin_pct: string;
  household_income: string;
  home_m2: string;
  ltv_pct: string;
  loan_years: string;
  loan_rate_pct: string;
}

/** A default as the field shows it: Spanish decimals, no thousands dot («9,3», «12192»). */
const text = (value: number | null | undefined, decimals: number): string =>
  value === null || value === undefined ? "" : String(Number(value.toFixed(decimals))).replace(".", ",");

export function initialFields(defaults: ViabilityDefaults, land: LandItem | null): CalculatorFields {
  return {
    buildable_m2: text(land?.buildable_m2, 0),
    sale_price_m2: text(defaults.sale_price_m2.value, 0),
    new_build_premium_pct: text(defaults.new_build_premium_pct.value, 1),
    rent_m2_month: text(defaults.rent_m2_month.value, 2),
    pem_m2: text(defaults.pem_m2.value, 0),
    cost_coefficient: text(defaults.cost_coefficient.value, 4),
    land: "",
    land_unit: "total",
    sales_costs_pct: text(defaults.sales_costs_pct.value, 1),
    target_margin_pct: text(defaults.target_margin_pct.value, 1),
    household_income: text(defaults.household_income.value, 0),
    home_m2: text(defaults.home_m2.value, 0),
    ltv_pct: text(defaults.ltv_pct.value, 0),
    loan_years: text(defaults.loan_years.value, 0),
    loan_rate_pct: text(defaults.loan_rate_pct.value, 2),
  };
}

/** A typed number in Spanish or English decimals («1.234,5», «1234.5»); null if empty or not a number. */
export function parseNumber(raw: string): number | null {
  const trimmed = raw.trim().replace(/\s/g, "");
  if (trimmed === "") return null;
  // «12.192» is twelve thousand in Spanish; «1.36» and «9.3» are decimals typed the English way
  const thousands = /^-?\d{1,3}(\.\d{3})+$/.test(trimmed);
  const normalised = trimmed.includes(",") || thousands ? trimmed.replace(/\./g, "").replace(",", ".") : trimmed;
  const value = Number(normalised);
  return Number.isFinite(value) ? value : null;
}

/** The range and step of a field: the same as POST /api/v1/investors/viability accepts (a test reads its JSON Schema). */
export interface FieldLimit {
  min: number;
  max: number;
  integer?: boolean;
}

type NumberFieldName = Exclude<keyof CalculatorFields, "land_unit" | "land">;

export const FIELD_LIMITS: Record<NumberFieldName, FieldLimit> = {
  buildable_m2: { min: 50, max: 500_000 },
  sale_price_m2: { min: 500, max: 30_000 },
  new_build_premium_pct: { min: -20, max: 50 },
  rent_m2_month: { min: 1, max: 100 },
  pem_m2: { min: 200, max: 5_000 },
  cost_coefficient: { min: 1, max: 3 },
  sales_costs_pct: { min: 0, max: 30 },
  target_margin_pct: { min: 1, max: 50 },
  household_income: { min: 5_000, max: 500_000 },
  home_m2: { min: 20, max: 300 },
  ltv_pct: { min: 0, max: 100 },
  loan_years: { min: 5, max: 40, integer: true },
  loan_rate_pct: { min: 0, max: 15 },
};

/** The land price's range depends on its unit: in total or per m² buildable. */
export const LAND_LIMITS: Record<CalculatorFields["land_unit"], FieldLimit> = {
  total: { min: 0, max: 1_000_000_000 },
  m2: { min: 0, max: 30_000 },
};

const REQUIRED: NumberFieldName[] = ["buildable_m2", "sale_price_m2", "pem_m2"];

export function limitOf(fields: CalculatorFields, key: keyof CalculatorFields): FieldLimit | null {
  if (key === "land") return LAND_LIMITS[fields.land_unit];
  return key === "land_unit" ? null : FIELD_LIMITS[key];
}

/** «Pon un número entre 50 y 500.000.», «Pon un número entero entre 5 y 40.» */
function rangeText({ min, max, integer }: FieldLimit): string {
  const n = (v: number) => formatNumber(v, Number.isInteger(v) ? 0 : 2);
  return `Pon un número${integer ? " entero" : ""} entre ${n(min)} y ${n(max)}.`;
}

/** What is wrong with each field, by name: out of range, not a whole number, or not a number. Empty optional fields are fine. */
export function fieldErrors(fields: CalculatorFields): Partial<Record<keyof CalculatorFields, string>> {
  const errors: Partial<Record<keyof CalculatorFields, string>> = {};
  for (const key of [...(Object.keys(FIELD_LIMITS) as NumberFieldName[]), "land" as const]) {
    const raw = fields[key];
    const limit = limitOf(fields, key) as FieldLimit;
    if (raw.trim() === "") continue;
    const value = parseNumber(raw);
    const wrong = value === null || value < limit.min || value > limit.max || (limit.integer && !Number.isInteger(value));
    if (wrong) errors[key] = rangeText(limit);
  }
  return errors;
}

/** Which required fields are empty: the area, the price and the PEM. */
export function missingFields(fields: CalculatorFields): (keyof CalculatorFields)[] {
  return REQUIRED.filter((key) => fields[key].trim() === "");
}

/** The POST body; null while a required field is empty or any field is out of its range. Optional fields left empty are left out. */
export function viabilityRequest(fields: CalculatorFields): ViabilityRequest | null {
  if (missingFields(fields).length > 0 || Object.keys(fieldErrors(fields)).length > 0) return null;
  const n = (key: keyof CalculatorFields) => parseNumber(fields[key] as string);
  const optional = <K extends string>(key: K, value: number | null) => (value === null ? {} : ({ [key]: value } as Record<K, number>));
  const land = n("land");
  const income = n("household_income");
  return {
    buildable_m2: n("buildable_m2") as number,
    sale_price_m2: n("sale_price_m2") as number,
    pem_m2: n("pem_m2") as number,
    ...optional("new_build_premium_pct", n("new_build_premium_pct")),
    ...optional("rent_m2_month", n("rent_m2_month")),
    ...optional("cost_coefficient", n("cost_coefficient")),
    ...optional("sales_costs_pct", n("sales_costs_pct")),
    ...optional("target_margin_pct", n("target_margin_pct")),
    ...optional(fields.land_unit === "m2" ? "land_eur_m2" : "land_eur", land),
    ...(income === null
      ? {}
      : {
          demand: {
            household_income: income,
            ...optional("home_m2", n("home_m2")),
            ...optional("ltv_pct", n("ltv_pct")),
            ...optional("loan_years", n("loan_years")),
            ...optional("loan_rate_pct", n("loan_rate_pct")),
          },
        }),
  };
}

/** «Hortaleza (6 barrios)» heading of a district in the list. */
export function districtHeading(name: string, count: number): string {
  return `${name} (${count === 1 ? "1 barrio" : `${count} barrios`})`;
}

export function parcelsLine(parcels: number | null | undefined, m2: number | null | undefined): string | null {
  if (!parcels) return null;
  const count = parcels === 1 ? "1 parcela pública" : `${parcels} parcelas públicas`;
  return m2 ? `${count}, ${formatNumber(m2, 0)} m² edificables` : count;
}

/**
 * Line A's buildable area left in planning areas (D-247), with a caveat when some of them also
 * cover other barrios: they count whole in this one (review of #95).
 */
export function remainingLine(m2: number | null | undefined, shared: number | null | undefined): string | null {
  if (!m2) return null;
  const line = `${formatNumber(m2, 0)} m² edificables en ámbitos del Plan General`;
  return shared ? `${line} (alguno ocupa también otros barrios y cuenta entero aquí)` : line;
}

/** The barrio code from the address (/inversores/28079164) to the API id. */
export function adminUnitId(code: string): string | null {
  return /^28079\d{3}$/.test(code) ? `ES.28.BAR.${code}` : null;
}

/** «2026-11-18» in words («18 de noviembre de 2026»); anything else as it comes. */
export function isoInWords(iso: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso);
  return match ? today(new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))) : iso;
}

export function today(now: Date = new Date()): string {
  return new Intl.DateTimeFormat("es-ES", { day: "numeric", month: "long", year: "numeric" }).format(now);
}

const listOf = (labels: string[]) => labels.map((l, i) => (i === 0 ? l : l.toLowerCase())).join(", ");

/**
 * What the barrio's district lacks, in one line of the list (FALTA first, then JUSTO). «Qué falta»
 * has no list by barrio: the line names the district the figure is of.
 */
export function gapsLine(zone: { gaps?: InvestorZoneSummary["gaps"]; district: { name: string } }): string {
  const gaps = zone.gaps;
  const where = `el distrito de ${zone.district.name}`;
  if (!gaps) return `Sin datos de lo que falta en ${where}.`;
  const missing = gaps.rows.slice(0, gaps.falta);
  const tight = gaps.rows.slice(gaps.falta, gaps.falta + gaps.justo);
  if (missing.length > 0) {
    const rest = tight.length > 0 ? `; justo: ${listOf(tight).toLowerCase()}` : "";
    return `Falta en ${where}: ${listOf(missing).toLowerCase()}${rest}.`;
  }
  if (tight.length > 0) return `Justo en ${where}: ${listOf(tight).toLowerCase()}.`;
  return `En ${where} no falta nada de lo que medimos.`;
}

/** inversores.calculadora.* of pitch/textos_web.md */
export const CALCULATOR_TEXT = {
  intro:
    "Calcula solo vivienda, con los precios y alquileres de vivienda del barrio: no oficinas, locales ni naves. Elige una parcela o un ámbito, o pon tú los m². Todo se puede cambiar: cada cifra dice si es un dato, un supuesto nuestro o lo has puesto tú. Los m² son construidos, como los del precio y los del coste.",
  landPick: "¿Sobre qué suelo?",
  parcel: "Parcela pública",
  area: "Ámbito con edificabilidad",
  custom: "Otra superficie: la pongo yo",
  groupRevenue: "Superficie y precios",
  groupCosts: "Costes y objetivo",
  groupDemand: "Comprobación de demanda",
  buildable: "Superficie edificable residencial",
  buildableFrom: "La que publica la fuente para el suelo elegido",
  buildableHelp: "Ponla tú: por ejemplo, la de tu parcela",
  price: "Precio de venta (vivienda usada)",
  premium: "Prima de la vivienda nueva",
  rent: "Alquiler",
  pem: "Coste de ejecución material (PEM)",
  coefficient: "Coeficiente sobre el PEM",
  coefficientParts: "Ver de qué se compone el coeficiente",
  salesCostsField: "Comercialización y otros gastos",
  salesParts: "Ver de qué se componen estos gastos",
  landField: "Precio del suelo (opcional)",
  landHelp: "Sin él, te decimos lo máximo que podrías pagar por el suelo",
  landUnit: "El precio del suelo es",
  landTotal: "en total",
  landPerM2: "por m² edificable",
  target: "Margen objetivo sobre ventas",
  income: "Renta media de los hogares",
  home: "Vivienda tipo",
  ltv: "Parte del precio que financia el banco",
  years: "Plazo de la hipoteca",
  rate: "Tipo de interés",
  threshold: (value: SourcedValue) => `Umbral de esfuerzo: ${percent(value.value ?? 0, 0)} de la renta. ${value.source.text}.`,
  edited: "Has cambiado este valor",
  results: "Resultado: tres escenarios",
  missing: "Pon la superficie edificable, el precio de venta y el PEM para calcular.",
  calculating: "Calculando…",
  newPrice: (price: number) => `Vivienda nueva a unos ${formatNumber(Math.round(price), 0)} €/m².`,
  withLand: "Con el precio del suelo que has puesto: margen sobre ventas, antes de financiación e impuestos.",
  withoutLand:
    "Sin precio del suelo no hay veredicto: te decimos lo máximo que podrías pagar por él para llegar al margen objetivo (valor residual). Pon el precio del suelo para saber si sale. La rentabilidad del alquiler cuenta el suelo a ese valor máximo, así que sale igual en los tres escenarios: compara el alquiler con el precio de venta.",
  thresholds: thresholdsText(),
  priceProtected:
    "Precio libre del barrio: no vale para vivienda con protección pública, que tiene un precio máximo legal. Pon el de su régimen.",
  excludedLink: "Qué no incluye esta cuenta",
  costReset: "Volver a nuestros supuestos de coste",
  costScopeTitle: "Qué incluye el coste y qué no",
  costIncludes: (parts: string[]) =>
    `Incluye la obra en sí (el PEM: materiales, mano de obra, maquinaria e instalaciones) y, con el coeficiente, ${parts.join("; ")}. Los gastos de la venta van aparte, en «Comercialización y otros gastos».`,
  costExcludesTitle: "No incluye:",
  costExcludes: [
    "El suelo: va aparte, en «Precio del suelo». Si quieres contar lo que cuesta comprarlo (impuestos, notaría), súmalo ahí.",
    "La urbanización ni las cargas del ámbito (cesiones, cuotas de la junta de compensación), si las tiene.",
    "El derribo de lo que haya construido ni la limpieza del suelo.",
    "Los sótanos y garajes: el coste por m² se multiplica solo por la superficie edificable sobre rasante.",
    "La financiación (intereses y comisiones del préstamo) ni los plazos de la obra y de la venta.",
    "El IVA, que el PEM nunca lleva, ni los impuestos sobre el beneficio.",
    "Un colchón para imprevistos.",
  ],
  breakEvenTitle: "Hasta cuánto puede costar la construcción",
  breakEvenRow: "Construcción máxima para el margen objetivo",
  breakEvenFreeRow: "Lo mismo, con el suelo gratis",
  breakEvenNone: "Ni gratis",
  costNow: "Coste de construcción que usamos ahora",
  costCaution:
    "El coste de construcción es el dato que más cambia la cuenta. Partimos de una referencia pública (supuesto) y la puedes cambiar: el PEM se multiplica solo por la superficie edificable sobre rasante.",
  costReferencesTitle: "De dónde sale el coste y cuánto varía",
  /** With the sheet's figure of the permits (the CM dataset, from the API) when there is one */
  costReferences: (permits?: SourcedValue | null) => costReferenceLines(permits),
  revenue: "Ingresos por ventas",
  construction: "Construcción (PEM × coeficiente)",
  salesCosts: "Comercialización y otros",
  land: "Suelo",
  landUnknown: "Sin precio",
  profit: "Beneficio",
  margin: "Margen sobre ventas",
  residual: "Lo máximo que se puede pagar por el suelo",
  yield: "Rentabilidad bruta si se alquila",
  yieldResidual: "Rentabilidad bruta si se alquila, pagando por el suelo lo máximo que deja el margen objetivo",
  noYield: "Rentabilidad bruta si se alquila: ni con el suelo gratis se llega al margen objetivo, así que no hay precio de suelo con el que calcularla",
  invalid: "Revisa los campos marcados: hay alguno fuera de su rango.",
  demandTitle: "¿Lo pueden pagar los hogares del barrio?",
} as const;

const eurM2 = (value: number) => `${formatNumber(Math.round(value), 0)} €/m²`;

/** «2.800 €/m² construido», or «Ni gratis» when not even free construction keeps the margin. */
export function breakEvenValue(be: BreakEven): string {
  return be.reachable ? `${eurM2(be.construction_m2)} construido` : CALCULATOR_TEXT.breakEvenNone;
}

/** The break-even (D-252) in words: up to what construction cost the target margin holds. */
export function breakEvenText(be: BreakEven): string {
  const land = be.land_counted ? "Con el precio del suelo que has puesto" : "Sin pagar nada por el suelo";
  if (!be.reachable) return `${land}, ni con la construcción gratis llega la promoción al margen objetivo.`;
  const lead = `${land}, la promoción llega al margen objetivo mientras la construcción cueste menos de ${breakEvenValue(be)} (PEM × coeficiente).`;
  // Review of #109, R-04: a coefficient under 1 is not a cost a builder can quote
  if (be.coefficient < 1) return `${lead} Con tu PEM, ni con el PEM solo (coeficiente 1) llega.`;
  return `${lead} Es un PEM de hasta ${eurM2(be.pem_m2)} con tu coeficiente, o un coeficiente de hasta ${formatNumber(be.coefficient, 2)} sobre tu PEM.`;
}

/** The same with free land, when a land price is given. */
export function breakEvenFreeText(be: BreakEven): string {
  return be.reachable
    ? `Con el suelo gratis, hasta ${breakEvenValue(be)}.`
    : "Ni con el suelo gratis llega al margen objetivo.";
}

/** «876 €/m² construido (PEM × coeficiente)»: what the scenarios count now. */
export function costNowValue(be: BreakEven): string {
  return `${eurM2(be.current_construction_m2)} construido (PEM × coeficiente)`;
}

/** «1.064», «1,3575»: Spanish, no trailing zeros. Declarations: CALCULATOR_TEXT, above, uses them. */
function plain(value: number): string {
  return formatNumber(value, Number.isInteger(value) ? 0 : 4).replace(/(,\d*?)0+$/, "$1").replace(/,$/, "");
}
function pctText(value: number): string {
  return `${plain(value)} %`;
}
function signed(value: number): string {
  return `${value > 0 ? "+" : "−"}${pctText(Math.abs(value))}`;
}

/** The semaphore and the scenarios in words, from the code's figures (D-252, D8). */
function thresholdsText(): string {
  const floor = pctText(M.adjustFloorPct);
  const best = M.scenarios.find((s) => s.key === "optimista");
  const worst = M.scenarios.find((s) => s.key === "pesimista");
  const scenarios =
    best && worst
      ? ` Optimista: ${signed(best.pricePct)} de precio y ${signed(best.costPct)} de coste; pesimista: ${signed(worst.pricePct)} y ${signed(worst.costPct)}.`
      : "";
  return `Semáforo (supuesto), solo con precio del suelo: «Sale» si llega al margen objetivo; «Ajustar» entre el ${floor} y el objetivo; «No sale» por debajo del ${floor}. La tasación hipotecaria pide al menos un ${pctText(M.appraisalMinMarginPct)} en vivienda de primera residencia, sin financiación ni Impuesto sobre Sociedades (Orden ECO/805/2003, disposición adicional sexta).${scenarios}`;
}

/**
 * D-252 (D4): the three public references of the construction cost. The permits' PEM is the
 * CM dataset's figure as the API reads it from the Feature Store, with its source; without it,
 * the same versioned figure. The others come from the versioned tables.
 */
function costReferenceLines(permits?: SourcedValue | null): { text: string; href: string; link: string; mark?: SourcedValue["mark"] }[] {
  const { crg, st } = M.costReferences;
  const types = crg.types.map((t) => `${t.label.charAt(0).toLowerCase()}${t.label.slice(1)}, ${plain(t.low)}–${plain(t.high)} €/m²`);
  const known = permits?.value !== null && permits?.value !== undefined;
  const value = known ? Math.round(permits?.value ?? 0) : M.pem.eurM2;
  const year = (known && permits?.source.period) || String(M.pem.year);
  const source = known && permits ? ` Fuente: ${permits.source.text}.` : "";
  return [
    {
      text: `PEM medio de los visados de obra nueva de viviendas en bloque, Comunidad de Madrid (${year}): ${plain(value)} €/m². Es lo que declaran los proyectos al pedir el visado y suele quedarse corto: es la referencia baja.${source.replace(/\.\.$/, ".")}`,
      href: M.pem.url,
      link: "Ver los visados",
      mark: "dato",
    },
    {
      text: `Costes de Referencia General de la Comunidad de Madrid (actualizados al año ${crg.year}), en Madrid (área ${crg.area}): ${types.join("; ")}. Son PEM, sin gastos generales ni beneficio industrial, y los costes han subido desde entonces. La calculadora parte del punto medio del bloque abierto: ${plain(crg.defaultPem)} €/m² (supuesto).`,
      href: crg.url,
      link: "Ver los costes de referencia",
    },
    {
      text: `Sociedad de Tasación, ${st.period}, media de España: ${plain(st.eurM2)} €/m² de coste de construcción de obra nueva (${plain(st.aboveGround)} sobre rasante y ${plain(st.belowGround)} bajo rasante), según la prensa. No sabemos si incluye gastos generales y beneficio: no hemos podido leer el informe original.`,
      href: st.url,
      link: "Ver la noticia",
    },
  ];
}

/** «unos 67 millones de €», «unos 900.000 €»: an estimate on assumptions never says its cents (D-252, D7). */
export function roughMoney(amount: number): string {
  if (amount === 0) return "0 €";
  const digits = Math.abs(amount) >= 1 ? Math.floor(Math.log10(Math.abs(amount))) + 1 : 1;
  const factor = 10 ** (digits - 3);
  const rounded = Math.round(amount / factor) * factor;
  if (Math.abs(rounded) >= MILLION) {
    const millions = rounded / MILLION;
    const decimals = Math.abs(millions) >= 100 ? 0 : Math.abs(millions) >= 10 ? 1 : 2;
    const text = formatNumber(millions, decimals).replace(/(,\d*?)0+$/, "$1").replace(/,$/, "");
    // Review of #109, R-10: never «unos 1 millones»
    return text === "1" ? "alrededor de 1 millón de €" : `unos ${text} millones de €`;
  }
  return `unos ${formatEuros(rounded)}`;
}

/** inversores.ficha.* of pitch/textos_web.md */
export const SHEET_TEXT = {
  eyebrow: (district: string) => `Barrio de Madrid · distrito de ${district}`,
  income: "Renta neta media de los hogares",
  householdSize: "Personas por hogar (media)",
  onePerson: "Hogares de una persona",
  fivePlus: "Hogares de 5 personas o más",
  over65: "Personas de 65 años o más",
  under15: "Menores de 15 años",
  population: "Población",
  demandNote:
    "Cada cifra es de la zona más pequeña que la publica: el barrio, su distrito o toda la ciudad. Lo dice su fuente.",
  sale: "Precio de venta estimado",
  saleNote: "Es una estimación del precio de la vivienda usada, no el de un anuncio ni el de una venta.",
  premium: "Prima de la vivienda nueva",
  saleNew: "Precio de venta de vivienda nueva",
  rent: "Alquiler de un contrato nuevo",
  gapsIntro: (district: string) =>
    `Lo que falta se calcula por distrito, no por barrio: estas son las filas de ${district}, comparado con los municipios de su tipo.`,
  gapsLevel: (district: string) => `Dato del distrito de ${district}`,
  gapsMore: (district: string) => `Ver «Qué falta» en ${district}, con sus cifras y fuentes`,
  commerce: "Comercio de proximidad",
  landIntro:
    "Contexto urbanístico, no qué se puede construir: los m² edificables son los que publica la fuente, y la normativa de cada parcela manda. No los pasamos a viviendas.",
  // D-246: a zone without parcels never says «0 parcelas»
  parcels: (n: number) =>
    n === 0 ? "Parcelas públicas para vivienda" : n === 1 ? "1 parcela pública para vivienda" : `${n} parcelas públicas para vivienda`,
  noParcels: "El Portal del Suelo no ofrece ahora ninguna parcela residencial en este barrio.",
  parcelsUnknown: "Aún sin dato de las parcelas públicas de este barrio.",
  remaining: "Edificabilidad residencial que queda en los ámbitos del Plan General",
  remainingUnknown: "Aún sin dato para este barrio.",
  noRemaining: "Ningún ámbito del barrio tiene edificabilidad residencial disponible.",
  vacant: "Suelo vacante (Catastro)",
  viewer: "Ver en el visor de la Comunidad",
  record: "Ver la ficha oficial",
  notPilot: "Ese barrio no está en el piloto (Madrid capital dentro de la M-40).",
  version: (version: string | null) =>
    version ? `Datos calculados el ${isoInWords(version)}. Método: viabilidad v0 (D-248).` : "Método: viabilidad v0 (D-248).",
  datasets: (n: number) => `Los ${n} conjuntos de datos de esta ficha`,
  open: "Ver la fuente",
  pemDataset:
    "Comunidad de Madrid: Visados, superficie y presupuesto de dirección de obra de edificios (Ministerio de Vivienda)",
} as const;

/** Line A's commerce figures (D-247), by their feature id. */
export const COMMERCE_LABEL: Record<string, string> = {
  comercio_proximidad_1000hab: "Comercio de proximidad abierto por cada 1.000 habitantes",
  locales_abiertos_1000hab: "Locales abiertos por cada 1.000 habitantes",
  locales_cerrados_pct: "Locales cerrados",
  unidades_comerciales_1000hab: "Inmuebles comerciales del Catastro por cada 1.000 habitantes",
};

/** Each dataset once, by its id, in the order given. */
export function uniqueDatasets<T extends Pick<DatasetRef, "dataset_id">>(datasets: T[]): T[] {
  const seen = new Set<string>();
  return datasets.filter((d) => !seen.has(d.dataset_id) && Boolean(seen.add(d.dataset_id)));
}

/**
 * What an empty list of land says. A null figure is data not loaded yet (e.g. right after a deploy,
 * before the sync): «sin dato», never «ninguna». A 0 with an empty list is a real «ninguna».
 */
export function emptyLandText(value: number | null | undefined, kind: "parcelas" | "ambitos"): string {
  const unknown = value === null || value === undefined;
  if (kind === "parcelas") return unknown ? SHEET_TEXT.parcelsUnknown : SHEET_TEXT.noParcels;
  return unknown ? SHEET_TEXT.remainingUnknown : SHEET_TEXT.noRemaining;
}
