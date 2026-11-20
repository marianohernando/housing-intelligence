/**
 * «Busca tu parcela» (D-250): texts, formats and checks of the search by parcel of the investor
 * version. Copy from pitch/textos_web.md, section 11 (inversores.parcela.*). Every figure comes
 * from the API (GET /api/v1/investors/parcels); this module never adds a number of its own.
 */
import type {
  AmbitStatus,
  Buildability,
  LandItem,
  ParcelBlock,
  ParcelSheet,
  PlanningBlock,
  PlanUseFigure,
  PowerEstimate,
  ProtectedBuilding,
  SourcedValue,
  UseClass,
  UseFigure,
  UseOwnership,
} from "@/contracts/parcel_sheet_response";
import { formatNumber } from "@/lib/format";
import { AREA_STAGE_TEXT, isoInWords, landCaution, REGIME_TEXT } from "@/lib/investors";
import { INVESTOR_METHOD } from "@/lib/investorMethod";
import { titleCase } from "@/lib/names";

const HOME_M2 = INVESTOR_METHOD.homeM2;

/** A parcel near a point on the street (a 404's `details.nearest`; not in a response schema). */
export interface NearbyParcel {
  rc14: string;
  address: string | null;
  distance_m: number | null;
}

/** The four demo parcels (the API keeps their sheets for when a source fails). */
export const DEMO_PARCELS: readonly { rc14: string; label: string; why: string }[] = [
  { rc14: "2122202VK4722A", label: "Méndez Álvaro 47–49", why: "sin edificar, con edificabilidad oficial y del plan por uso" },
  { rc14: "3959601VK4735H", label: "Almería 1", why: "suelo público en un ámbito sin empezar" },
  { rc14: "0390314VK4709A", label: "Luis Misson 2", why: "sin edificar y sin coeficiente: pones tú los m²" },
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
    services: "4. Servicios y suministros",
    demand: (district: boolean) => `5. Quién vive en el ${district ? "distrito" : "barrio"}`,
    prices: (district: boolean) => `6. Precios en el ${district ? "distrito" : "barrio"}`,
    gaps: "7. Qué falta",
    land: (district: boolean) => `8. Suelo en el ${district ? "distrito" : "barrio"}`,
    viability: "9. ¿Sale la promoción?",
    study: "Lo que añade un estudio completo",
    sources: "Fuentes y avisos",
  },
  area: "Superficie de la parcela",
  use: "Uso actual",
  built: "Construido hoy",
  builtNote: "Es lo que hay, no lo que se puede construir.",
  year: "Año de construcción",
  vacant: "¿Está sin edificar? (según su uso en el Catastro)",
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
  officialTitle: "Lo que publica cada fuente para esta parcela catastral",
  planUsesTitle: (urbanParcel: string | null | undefined) =>
    urbanParcel ? `Según el plan, la parcela urbanística ${urbanParcel} tiene:` : "Según el plan, la parcela urbanística tiene:",
  planUsesNone: "El plan no publica la edificabilidad por uso de esta parcela.",
  /** D-252c: table 4 has the urban parcel with its principal use but no figure */
  planUsesWithoutFigure: (use: string) =>
    use.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim() === "sin uso pormenorizado"
      ? "El plan no fija uso pormenorizado ni cifra de edificabilidad para esta parcela urbanística."
      : `El plan fija su uso principal (${use.toLocaleLowerCase("es-ES")}), pero sin cifra de edificabilidad.`,
  planUsesCaveats:
    "La parcela urbanística del plan puede no coincidir con la catastral, y es lo que el plan permite en total, no lo que queda por construir. Salvo excepciones, los usos asociados y complementarios no pueden pasar del 50 % de lo edificado, ni del 25 % en una parcela dotacional (Normas Urbanísticas, art. 7.2.8).",
  /** D-252c: from the snapshot of tables 4 and 5, with its date (DD/MM/AAAA) */
  planUsesSource: (day: string | null) =>
    `Ayuntamiento de Madrid, Urbanismo (usos del suelo: uso cualificado principal y otros usos cualificados)${day ? `, del plan a fecha ${day}` : ""}. Información urbanística sin valor jurídico.`,
  planUsesDown: "No hemos podido leer ahora la edificabilidad por uso del plan; el resto de la ficha sí. Vuelve a intentarlo en un rato.",
  ambit: "Estado del ámbito",
  ambitUntracked: "El Ayuntamiento no publica su estado.",
  ambitAsOf: (code: string, day: string) => `${code}, según el Ayuntamiento a ${day}`,
  publicLand: "Suelo público",
  catalog: "Catálogo de edificios protegidos",
  // Review of #110, R-02: the layer is read at the parcel's reference point only
  catalogNone: "No aparece en el catálogo en el punto de referencia de la parcela",
  catalogUnread: "No lo hemos podido leer ahora",
  catalogDown: "No hemos podido leer ahora el catálogo de edificios protegidos; el resto de la ficha sí. Vuelve a intentarlo en un rato.",
  // D-253 (audit D6): what this sheet is, and what it is not
  firstFilter:
    "Esto es un primer filtro de minutos, gratis y con fuentes. No sustituye al estudio de viabilidad que hace una consultora o un arquitecto.",
  takeIt: "Llévate esta ficha (PDF) a tu consultora: ahorra parte de la recopilación de datos públicos.",
  studyItems: [
    "La nota simple del Registro, con sus cargas.",
    "El informe urbanístico del Ayuntamiento.",
    "La consulta a la distribuidora eléctrica y a Canal de Isabel II.",
    "El levantamiento topográfico y el estudio geotécnico.",
    "Un estudio de mercado con testigos de venta.",
    "Un plan de negocio con plazos y financiación.",
    "Si hubo industria, el estudio de suelos contaminados (Real Decreto 9/2005).",
    "Si la zona lo pide, el estudio arqueológico.",
  ],
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
  return parcel.is_vacant ? "Sí" : "No";
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
  if (degraded.includes("plan_uses")) lines.push(SHEET_TEXT.planUsesDown);
  if (degraded.includes("catalog")) lines.push(SHEET_TEXT.catalogDown);
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

/** One source's figure with its use: «Industrial: 3.465 m² edificables». */
export function byUseText(figure: UseFigure): string {
  return `${landUseLabel(figure.use_class)}: ${m2(figure.value_m2)} edificables`;
}

/** «Uso en la fuente: industrial · VEDA Madrid (…)». */
export function byUseSource(figure: UseFigure): string {
  return `Uso en la fuente: ${lowerFirst(sentence(figure.use) ?? figure.use)} · ${figure.source}`;
}

/** «Residencial: 60.231 m²», or with a coefficient «Terciario: 19.920 m² (1,2 m²/m² × 16.600 m² de la parcela urbanística: supuesto)». */
export function planUseText(figure: PlanUseFigure, urbanArea: number | null | undefined): string {
  const label = landUseLabel(figure.use_class, figure.use_ownership);
  const coefficient = figure.coefficient;
  if (coefficient === null || coefficient === undefined) {
    return `${label}: ${figure.value_m2 === null || figure.value_m2 === undefined ? "sin cifra" : m2(figure.value_m2)}`;
  }
  const per = `${formatNumber(coefficient, 2).replace(/,?0+$/, "")} m²/m²`;
  if (figure.value_m2 === null || figure.value_m2 === undefined || !urbanArea) return `${label}: ${per}`;
  return `${label}: ${m2(figure.value_m2)} (${per} × ${m2(urbanArea)} de la parcela urbanística: supuesto)`;
}

/** «Uso principal: residencial vivienda colectiva» / «Otro uso: servicios terciarios». */
export function planUseSource(figure: PlanUseFigure): string {
  return `${figure.principal ? "Uso principal" : "Otro uso"}: ${lowerFirst(sentence(figure.use) ?? figure.use)}`;
}

/** «Planeamiento: finalizado · Gestión: sin iniciar · …», and VEDA's situation. */
export function ambitText(ambit: AmbitStatus): string {
  if (!ambit.tracked) return SHEET_TEXT.ambitUntracked;
  const phases = (ambit.phases ?? []).map((p) => `${p.label}: ${p.state.toLowerCase()}`);
  const stage = ambit.veda_stage ? AREA_STAGE_TEXT[ambit.veda_stage] : null;
  return [...phases, stage ? `VEDA: ${lowerFirst(stage)}` : null].filter(Boolean).join(" · ");
}

/** D-252: the parcel as public land of the Portal del Suelo, with its owner, regime and urbanization. */
export function publicLandText(item: LandItem): string {
  const regime = item.regime ? (REGIME_TEXT[item.regime] ?? null) : null;
  const stage = item.stage === "sin_urbanizar" ? "sin urbanizar" : item.stage === "urbanizado" ? "urbanizada según el Portal" : null;
  const facts = [regime, item.manager ? `la ofrece ${item.manager}` : null, stage].filter(Boolean).join(", ");
  const caution = landCaution(item);
  return `Parcela del Portal del Suelo de la Comunidad de Madrid${facts ? `: ${facts}` : ""}.${caution ? ` ${caution}` : ""}`;
}

/** «2026-11-20» → «20/11/2026». */
export function dayMonthYear(iso: string | null | undefined): string | null {
  const match = iso ? /^(\d{4})-(\d{2})-(\d{2})/.exec(iso) : null;
  return match ? `${match[3]}/${match[2]}/${match[1]}` : null;
}

/** «Protección parcial, nº 02933 (nivel 3 de 3)», from the Plan General's catalogue (D-253). */
export function catalogText(building: ProtectedBuilding | null | undefined, unread = false): string {
  if (unread) return SHEET_TEXT.catalogUnread;
  if (!building) return SHEET_TEXT.catalogNone;
  const status = (building.protection ?? "").normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
  if (status === "descatalogado" || status === "demolicion total") {
    // The layer also gives these: never said as a protection
    return `${sentence(building.protection) ?? ""}${building.number ? `, nº ${building.number}` : ""}`;
  }
  const protection = building.protection ? `Protección ${building.protection.toLowerCase()}` : "Catalogado";
  const number = building.number ? `, nº ${building.number}` : "";
  const level = building.level ? ` (nivel ${building.level} de 3)` : "";
  return `${protection}${number}${level}`;
}

// The finished states of an area's works: the domain's (hi_domain.parcels.DONE_PHASES), generated
const DONE_WORKS = new Set<string>(INVESTOR_METHOD.doneWorks);

/** D-253 (audit D1): services and supplies. Legal texts read at their source (BOE, BOCM, CNMC, Comunidad de Madrid). */
export const SERVICES_TEXT = {
  solar:
    "Para ser solar, la parcela tiene que estar completamente urbanizada: calzadas pavimentadas, aceras, y agua, saneamiento, electricidad y alumbrado público conectados a las redes públicas (Ley 9/2001 del Suelo de la Comunidad de Madrid, art. 14.1.a). Ningún dato abierto dice si esta parcela los tiene.",
  zonal:
    "Norma zonal: suelo urbano común o consolidado, ordenado de modo directo por el Plan General (Normas Urbanísticas, arts. 3.1.4 y 3.2.2). Aun así, la acometida y la potencia hay que pedirlas a cada compañía.",
  works: (code: string, state: string) => `Obras de urbanización del ${code}: ${state.toLowerCase()}, según el Ayuntamiento.`,
  worksPending:
    "Mientras no estén terminadas, la parcela no es solar. La ley permite pedir licencia con la urbanización a la vez y una garantía que cubra su coste (Ley 9/2001, arts. 19.3, 20.3 y 23.1).",
  untracked: "El Ayuntamiento no publica el estado de este ámbito: no sabemos si su urbanización está terminada.",
  portal: (stage: string): string | null =>
    stage === "urbanizado"
      ? "El Portal del Suelo dice que esta parcela está urbanizada."
      : stage === "sin_urbanizar"
        ? "El Portal del Suelo dice que esta parcela está sin urbanizar."
        : null,
  electricity: "Electricidad",
  power: (p: PowerEstimate) =>
    `Con unas ${formatNumber(p.homes, 0)} viviendas (los m² edificables de partida entre ${formatNumber(HOME_M2, 0)} m², la vivienda tipo), la previsión de potencia es de al menos ${formatNumber(p.kw, 1)} kW: ${formatNumber(p.kw_per_home, 2)} kW por vivienda (electrificación básica) por el coeficiente de simultaneidad de la ITC-BT-10 del Reglamento de Baja Tensión (${formatNumber(p.simultaneity, 1)} para ${formatNumber(p.homes, 0)} viviendas). Sin servicios comunes ni garaje, que se suman aparte.`,
  powerNone: "Sin m² edificables de partida no estimamos la potencia.",
  transformer:
    "Por encima de 100 kW, el edificio tiene que reservar un local para un centro de transformación de la distribuidora (RD 1048/2013, art. 26.1). Y la extensión de red la paga quien pide el suministro (art. 25.2): solo hasta 100 kW en baja tensión, en suelo urbanizado, la hace la distribuidora y cobra los derechos de extensión (art. 25.1).",
  belowTransformer:
    "Hasta 100 kW en baja tensión, en suelo urbanizado, la extensión de red la hace la distribuidora y cobra los derechos de extensión (RD 1048/2013, art. 25.1).",
  capacity:
    "Aunque haya red en la calle, la subestación puede no tener capacidad. Antes de comprar, pregunta a la distribuidora (en Madrid, i-DE o UFD) por el punto de suministro (CUPS) de la parcela y por la potencia que te puede dar.",
  cnmc: "La CNMC publica cada mes un mapa de la capacidad de las redes para nuevos consumos: es informativo y sus cifras no se pueden sumar.",
  cnmcLink: "Ver el mapa de capacidad de demanda de la CNMC",
  cnmcUrl: "https://experience.arcgis.com/experience/c7dc433cb2e44d53a908a8a467523f5a",
  water: "Agua",
  canal:
    "El agua la da Canal de Isabel II, que no publica datos de su red. Antes de comprar, pregúntale si hay una red adecuada: para una acometida nueva se compromete a 10 días laborables, «siempre que exista una red adecuada» y tenga los permisos.",
  canalLink: "Ver los compromisos de Canal de Isabel II (Comunidad de Madrid)",
  canalUrl: "https://www.comunidad.madrid/consumo/informacion-completa-agua",
  wordsTitle: "Palabras y plazos de los suministros",
  words: [
    {
      term: "CUPS",
      text: "El código que identifica un punto de suministro (una vivienda, un local), no a la persona que lo contrata (guía «El CUPS» de la CNMC). La distribuidora lo guarda en su base de datos de puntos de suministro (Reglamento del RD 88/2026, art. 8). Si la parcela no tiene, es que no ha tenido suministro: no quiere decir que no pueda tenerlo.",
    },
    { term: "Acometida", text: "La conexión entre la red de la calle y el edificio." },
    {
      term: "Derechos de acometida",
      text: "Lo que se paga a la distribuidora por un suministro nuevo: los de extensión, de acceso y de supervisión de instalaciones cedidas (RD 1048/2013, art. 24.2). El enganche y la verificación se cobran aparte (art. 29.1).",
    },
    {
      term: "Quién paga la red",
      text: "Hasta 100 kW en baja tensión (250 kW en alta), en suelo urbanizado con sus servicios, la hace la distribuidora y cobra los derechos de extensión (RD 1048/2013, art. 25.1). En el resto, la paga quien pide el suministro (art. 25.2) y, si la van a usar más consumidores, la cede a la distribuidora (art. 25.5). La ley del suelo pone a cargo de quien urbaniza la conexión con las redes generales y su ampliación (texto refundido de la Ley de Suelo, art. 18.1.c).",
    },
    {
      term: "Centro de transformación",
      text: "Por encima de 100 kW, el edificio reserva un local cerrado, con acceso desde la calle, para la distribuidora (RD 1048/2013, art. 26.1).",
    },
    {
      term: "Plazos de la norma",
      text: "La distribuidora contesta a una solicitud de acceso en 15 días hábiles en baja tensión (5 hasta 15 kW si no hay que extender la red) y en 30 entre 1 y 36 kV (RD 1183/2020, art. 13). Con centro de transformación, el presupuesto en 20 días hábiles; y, si la obra la hace la distribuidora, 60 días hábiles desde que se pagan los derechos, que no empiezan a contar hasta que se firma la cesión del local, y sin contar los permisos (RD 1955/2000, art. 103).",
    },
  ],
} as const;

/** The planning's signal about services: a norma zonal, the area's works, or nothing said. */
export function servicesSignal(planning: PlanningBlock | null | undefined): string[] {
  if (!planning) return [];
  if (planning.norma_zonal || planning.kind === "norma_zonal") return [SERVICES_TEXT.zonal];
  const ambit = planning.ambit;
  if (!ambit) return [];
  if (!ambit.tracked) return [SERVICES_TEXT.untracked];
  const works = (ambit.phases ?? []).find((p) => p.label === "Obras de urbanización");
  if (!works) return [];
  const done = DONE_WORKS.has(works.state.toLowerCase());
  return done ? [SERVICES_TEXT.works(ambit.code, works.state)] : [SERVICES_TEXT.works(ambit.code, works.state), SERVICES_TEXT.worksPending];
}
