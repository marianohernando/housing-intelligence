/**
 * «Busca tu parcela» (D-250): texts, formats and checks of the search by parcel of the investor
 * version. Copy from pitch/textos_web.md, section 11 (inversores.parcela.*). Every figure comes
 * from the API (GET /api/v1/investors/parcels); this module never adds a number of its own.
 */
import type {
  Buildability,
  ParcelBlock,
  ParcelSheet,
  PlanningBlock,
  SourcedValue,
  UseClass,
  UseFigure,
  UseOwnership,
} from "@/contracts/parcel_sheet_response";
import { formatNumber } from "@/lib/format";
import { isoInWords } from "@/lib/investors";
import { titleCase } from "@/lib/names";

/** A parcel near a point on the street (a 404's `details.nearest`; not in a response schema). */
export interface NearbyParcel {
  rc14: string;
  address: string | null;
  distance_m: number | null;
}

/** The four demo parcels (the API keeps their sheets for when a source fails). */
export const DEMO_PARCELS: readonly { rc14: string; label: string; why: string }[] = [
  { rc14: "2122202VK4722A", label: "Méndez Álvaro 47–49", why: "solar con edificabilidad oficial" },
  { rc14: "3959601VK4735H", label: "Almería 1", why: "suelo público de Metro de Madrid" },
  { rc14: "0390314VK4709A", label: "Luis Misson 2", why: "solar sin coeficiente: pones tú los m²" },
  { rc14: "9943003VK3794D", label: "Mayor 61", why: "edificio en división horizontal" },
];

export const SEARCH_TEXT = {
  title: "Busca tu parcela",
  intro:
    "Para inversores y promotores: cómo es la parcela, qué dice el planeamiento, cuánto se puede construir y si una promoción sale, con la fuente de cada cifra.",
  coverage: "Toda Madrid capital. Dentro de la M-40 (el piloto), con todo el contexto del barrio.",
  rcTitle: "Por referencia catastral",
  rcLabel: "Referencia catastral",
  rcHelp: "Los 14 primeros caracteres (por ejemplo, 2122202VK4722A). La de 20 también vale.",
  rcButton: "Buscar la parcela",
  rcInvalid: "Una referencia catastral tiene 14, 18 o 20 letras y números.",
  addressTitle: "Por dirección",
  addressLabel: "Calle y número",
  addressHelp: "En Madrid capital. Elige tu portal en la lista: nunca lo elegimos por ti.",
  addressShort: "Escribe al menos 4 letras.",
  addressSearching: "Buscando portales…",
  addressNone: "No encontramos ningún portal de Madrid capital con esa dirección.",
  addressNeedsNumber: "Encontramos la calle: añade el número del portal.",
  addressDown: "El buscador de direcciones no responde ahora. Usa la referencia catastral o el mapa.",
  addressList: "Portales que coinciden",
  addressCount: (n: number) => (n === 1 ? "1 portal coincide." : `${n} portales coinciden.`),
  mapTitle: "En el mapa",
  mapHelp: "Acerca el mapa y pincha en la parcela.",
  mapAria: "Mapa de Madrid capital: pincha en una parcela para buscarla",
  mapFinding: "Buscando la parcela de ese punto…",
  mapStreet: "Ese punto cae en la calle. ¿Era una de estas?",
  mapNone: "En ese punto no hay ninguna parcela.",
  mapOut: "Ese punto está fuera de Madrid capital.",
  mapNoWebgl: "Tu navegador no puede mostrar el mapa: usa la referencia catastral o la dirección.",
  mapCredits: "Mapa: © OpenStreetMap · OpenFreeMap",
  demosTitle: "O prueba con una de estas",
} as const;

export const SHEET_TEXT = {
  loading: "Buscando la parcela…",
  back: "‹ Buscar otra parcela",
  rcLine: (rc: string) => `Referencia catastral ${rc}`,
  eyebrow: (barrio: string | null, district: string | null) =>
    barrio && district ? `Parcela de Madrid · barrio de ${barrio}, distrito de ${district}` : "Parcela de Madrid capital",
  sections: {
    parcel: "1. Datos de la parcela",
    planning: "2. Planeamiento",
    buildability: "3. Edificabilidad",
    demand: (district: boolean) => `4. Quién vive en el ${district ? "distrito" : "barrio"}`,
    prices: (district: boolean) => `5. Precios en el ${district ? "distrito" : "barrio"}`,
    gaps: "6. Qué falta",
    land: (district: boolean) => `7. Suelo en el ${district ? "distrito" : "barrio"}`,
    viability: "8. ¿Sale la promoción?",
    sources: "Fuentes y avisos",
  },
  area: "Superficie de la parcela",
  use: "Uso actual",
  built: "Construido hoy",
  builtNote: "Es lo que hay, no lo que se puede construir.",
  year: "Año de construcción",
  vacant: "¿Es un solar?",
  division: "División horizontal",
  catastroLink: "Ver la parcela en la Sede Electrónica del Catastro",
  qualification: "Calificación",
  planningUse: "Uso pormenorizado",
  urbanParcel: "Parcela urbanística",
  instrument: "Planeamiento en vigor",
  viewer: "Ver en el visor del Geoportal del Ayuntamiento",
  recordLink: "Ver la ficha oficial del expediente",
  /** «Artículo 8.4.9 de las Normas Urbanísticas» → «Ver el artículo 8.4.9 de las Normas Urbanísticas» */
  sheetLink: (label: string | null | undefined) =>
    label ? `Ver el ${label.charAt(0).toLowerCase()}${label.slice(1)}` : "Ver la ficha oficial",
  planningDown: "El Ayuntamiento no responde ahora; el resto de la ficha sí. Vuelve a intentarlo en un rato.",
  planningNone: "El Ayuntamiento no tiene calificación para el punto de esta parcela.",
  buildable: "Edificabilidad de partida",
  buildableEditable: "Siempre la puedes cambiar en la calculadora.",
  byUseTitle: "Edificabilidad publicada, por uso",
  byUseNote: "Cada fuente publica una sola cifra por parcela, con un solo uso: la enseñamos tal cual, sin repartirla entre usos.",
  byUseNone:
    "Ninguna fuente publica la edificabilidad de esta parcela: ni el visor de edificabilidad (VEDA) del Ayuntamiento ni el Portal del Suelo de la Comunidad de Madrid.",
  notHousing: "No es vivienda: no entra en la calculadora.",
  housingOnly:
    "La calculadora calcula solo vivienda: parte de la edificabilidad residencial, porque sus precios y alquileres son de vivienda. Una cifra de otro uso (terciario, industrial) la enseñamos como referencia y no la usamos.",
  /** A norm's assumption on a parcel the plan gives another use (NZ 9, actividades económicas) */
  assumedOtherUse: (use: string) =>
    `El planeamiento da a esta parcela uso ${use}, no de vivienda. La calculadora parte de estos m² como si fueran de vivienda: comprueba en la ficha oficial si la parcela la admite.`,
  article: (n: string) => `Ver el artículo ${n} de las Normas Urbanísticas`,
  contextDown: "No hemos podido leer el barrio ahora; el resto de la ficha sí. La calculadora empieza sin los precios del barrio.",
  instrumentDown:
    "El Ayuntamiento no nos ha dado ahora el planeamiento en vigor de la parcela; el resto de la ficha sí. Vuelve a intentarlo en un rato.",
  zDown:
    "No hemos podido leer ahora el plano de condiciones de la edificación de la norma zonal 1: la edificabilidad queda sin dato. Vuelve a intentarlo en un rato.",
  noBarrio: "Esta parcela no cae en ningún barrio de Madrid que tengamos.",
  fallback: (day: string) =>
    `El Catastro o el Ayuntamiento no responden ahora: te enseñamos los datos guardados el ${day} de esta parcela de demostración.`,
  sourcesTitle: (n: number) => `Las ${n} fuentes de la parcela`,
  barrioDatasets: (n: number) => `Los ${n} conjuntos de datos del barrio`,
  open: "Ver la fuente",
  retry: "Reintentar",
  calculatorFrom: (kind: Buildability["kind"]) =>
    kind === "oficial"
      ? "La que publica la fuente oficial para esta parcela"
      : kind === "supuesto"
        ? "Supuesta con la norma: compruébala en la ficha"
        : "Ponla tú: la norma no fija una cifra para esta parcela",
} as const;

/** What a failed lookup says, by the API's code. */
export const LOOKUP_ERROR: Record<string, string> = {
  NOT_FOUND: "No existe ninguna parcela con esa referencia catastral.",
  OUT_OF_COVERAGE: "Esa referencia no es de una parcela de Madrid capital, o no está bien escrita.",
  SOURCE_DEGRADED: "El Catastro no responde ahora y esta parcela no es de las de demostración. Vuelve a intentarlo en unos minutos.",
  RATE_LIMITED: "Has buscado muchas parcelas nuevas en poco tiempo. Espera un minuto y vuelve a intentarlo.",
  AMBIGUOUS_INPUT: "Esa dirección coincide con varios portales: elige el tuyo en la lista.",
};

const RC = /^([0-9A-Z]{14})(?:[0-9]{4}(?:[A-Z]{2})?)?$/;

/** The parcel's reference (14) from what was typed, as the API reads it; null if it cannot be one. */
export function parcelRc(typed: string): string | null {
  const match = RC.exec(typed.replace(/[\s.-]/g, "").toUpperCase());
  return match ? (match[1] as string) : null;
}

export function parcelHref(rc14: string): string {
  return `/inversores/parcela/${rc14}`;
}

const m2 = (value: number) => `${formatNumber(value, value >= 100 || Number.isInteger(value) ? 0 : 1)} m²`;

/** «2.843 m²», or «Sin dato» (never 0 for unknown). */
export function areaText(value: number | null | undefined): string {
  return value === null || value === undefined ? "Sin dato" : m2(value);
}

export function vacantText(parcel: ParcelBlock): string {
  if (parcel.is_vacant === null || parcel.is_vacant === undefined) return "Sin dato";
  return parcel.is_vacant ? "Sí, sin edificar" : "No";
}

/** «Sí: 6 inmuebles (5 residencial, 314 m²; 1 comercial, 62 m²)». Never one unit by one. */
export function divisionText(parcel: ParcelBlock): string {
  if (!parcel.horizontal_division) return "No";
  const units = parcel.units;
  if (!units) return "Sí";
  const uses = units.by_use
    .map((u) => `${u.count} ${u.use.toLowerCase()}${u.built_m2 !== null && u.built_m2 !== undefined ? `, ${m2(u.built_m2)}` : ""}`)
    .join("; ");
  return `Sí: ${units.total === 1 ? "1 inmueble" : `${units.total} inmuebles`} (${uses})`;
}

/** An official text in capitals, as a sentence: «RESIDENCIAL VIVIENDA COLECTIVA» → «Residencial vivienda colectiva». */
export function sentence(text: string | null | undefined): string | null {
  if (!text) return null;
  if (text !== text.toUpperCase()) return text;
  const lower = text.toLocaleLowerCase("es-ES");
  return lower.charAt(0).toLocaleUpperCase("es-ES") + lower.slice(1);
}

export const PLANNING_KIND_TEXT: Record<PlanningBlock["kind"], string> = {
  norma_zonal: "Norma zonal",
  API: "Área de planeamiento incorporado",
  APE: "Área de planeamiento específico",
  APR: "Área de planeamiento remitido",
  APD: "Área de planeamiento diferenciado",
  UZI: "Suelo urbanizable incorporado",
  UZP: "Suelo urbanizable programado",
  UNP: "Suelo urbanizable no programado",
  NUP: "Suelo no urbanizable de protección",
  AOE: "Área de ordenación especial",
  otro: "Otra calificación",
};

/** «Norma zonal 8, grado 3º, nivel a» or «Área de planeamiento remitido APR.02.06: Méndez Álvaro Norte I». */
export function qualificationText(planning: PlanningBlock): string {
  const nz = planning.norma_zonal;
  if (nz) {
    const parts = [`Norma zonal ${nz.nz}`, nz.grado ? `grado ${nz.grado}º` : null, nz.nivel ? `nivel ${nz.nivel}` : null];
    return parts.filter(Boolean).join(", ");
  }
  const name = planning.name ? titleCase(planning.name) : null;
  return `${PLANNING_KIND_TEXT[planning.kind]} ${planning.code}${name ? `: ${name}` : ""}`;
}

export function instrumentText(planning: PlanningBlock): string | null {
  const i = planning.instrument;
  if (!i) return null;
  return [i.figure, i.name, i.file_number ? `expediente ${i.file_number}` : null].filter(Boolean).join(" · ") || null;
}

/** The buildability's tag: official is data; the rest say what they are (never a colour alone). */
export function buildabilityMark(kind: Buildability["kind"]): SourcedValue["mark"] | "sin_dato" {
  return kind === "oficial" ? "dato" : kind === "supuesto" ? "supuesto" : "sin_dato";
}

export function buildableText(b: Buildability): string {
  return b.value_m2 === null || b.value_m2 === undefined ? "Sin dato" : `${m2(b.value_m2)} edificables`;
}

/** The parts of the sheet that could not be read now, in words, in the sheet's order. */
export function degradedLines(sheet: Pick<ParcelSheet, "degraded" | "fallback" | "parcel" | "planning">): string[] {
  const lines: string[] = [];
  const degraded = sheet.degraded ?? [];
  if (sheet.fallback === "demo_snapshot") lines.push(SHEET_TEXT.fallback(isoInWords(sheet.parcel.observed_at)));
  // Without any planning its own section says so; with it, a layer of it is missing
  if (degraded.includes("planning") && sheet.planning) lines.push(SHEET_TEXT.instrumentDown);
  if (degraded.includes("buildability")) lines.push(SHEET_TEXT.zDown);
  if (degraded.includes("context")) lines.push(SHEET_TEXT.contextDown);
  return lines;
}

/** What each use is, in one plain line (D-252): the parcel's sheet and «Cómo lo calculamos». */
export const USE_TEXT: Record<UseClass, { label: string; plain: string }> = {
  residencial: { label: "Residencial", plain: "Vivienda, en pisos o en casas, libre o con protección pública." },
  terciario: { label: "Terciario", plain: "Oficinas, comercios, hoteles y otros servicios privados." },
  industrial: { label: "Industrial", plain: "Fábricas, talleres, almacenes y otras actividades productivas." },
  dotacional: {
    label: "Dotacional",
    plain:
      "Equipamientos como colegios, centros de salud o instalaciones deportivas, culturales o sociales; público si es de una administración, privado si es de una empresa o una entidad privada.",
  },
  zona_verde: { label: "Zona verde", plain: "Parques y jardines, suelo dotacional para el uso de todos y no para edificar." },
  infraestructura: {
    label: "Vía pública, transporte e infraestructuras",
    plain: "Calles, vías del tren o del metro e instalaciones de agua, gas o electricidad; también es suelo dotacional.",
  },
  sin_uso: {
    label: "Sin uso pormenorizado",
    plain: "El plan aún no le ha fijado un uso concreto; lo fija el plan propio de su ámbito.",
  },
  otro: { label: "Otros usos", plain: "Un uso que la fuente no clasifica en los anteriores (en el Portal del Suelo, «Otros»)." },
};

/** «Dotacional privado», «Zona verde, de titularidad pública», «Industrial». */
export function landUseLabel(kind: UseClass, owner?: UseOwnership | null): string {
  const label = USE_TEXT[kind].label;
  if (!owner) return label;
  if (kind === "dotacional") return `${label} ${owner === "publico" ? "público" : "privado"}`;
  return `${label}, de titularidad ${owner === "publico" ? "pública" : "privada"}`;
}

const lowerFirst = (text: string) => text.charAt(0).toLowerCase() + text.slice(1);

const folded = (text: string) => text.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();

/**
 * Under the plan's use: what it means, and that the calculator is for housing when it is not. The
 * class goes first when the use's words do not already say it («Dotacional privado: …»).
 */
export function landUseNote(planning: Pick<PlanningBlock, "use" | "use_class" | "use_ownership">): string | null {
  const kind = planning.use_class;
  if (!kind) return null;
  const plain = USE_TEXT[kind].plain;
  const said = !planning.use_ownership && folded(planning.use ?? "").startsWith(folded(USE_TEXT[kind].label));
  const meaning = said ? plain : `${landUseLabel(kind, planning.use_ownership)}: ${lowerFirst(plain)}`;
  return kind === "residencial" ? meaning : `${meaning} La calculadora calcula solo vivienda.`;
}

/** The plan's use when it is not housing nor undecided, for the caution on a norm's assumption. */
export function otherPlanningUse(planning: Pick<PlanningBlock, "use_class" | "use_ownership"> | null | undefined): string | null {
  const kind = planning?.use_class;
  if (!kind || kind === "residencial" || kind === "sin_uso" || kind === "otro") return null;
  return landUseLabel(kind, planning.use_ownership).toLowerCase();
}

/** One source's figure with its use: «Industrial: 3.465 m² edificables». */
export function byUseText(figure: UseFigure): string {
  return `${landUseLabel(figure.use_class)}: ${m2(figure.value_m2)} edificables`;
}

/** «Uso en la fuente: industrial · VEDA Madrid (…)». */
export function byUseSource(figure: UseFigure): string {
  return `Uso en la fuente: ${lowerFirst(sentence(figure.use) ?? figure.use)} · ${figure.source}`;
}
