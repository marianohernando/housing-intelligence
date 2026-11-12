/**
 * Provenance in plain words (pure, unit tested): the footer counter, the citations the licences
 * ask for (attribution_text) and the dataset lines of pitch/textos_web.md (pie.contador and
 * fuente.*), from GET /api/v1/datasets.
 */
import type { DatasetRef } from "@/contracts/dataset_list_response";

export const PORTAL_CM = "Portal de Datos Abiertos de la Comunidad de Madrid";

/** `n` is cm_open_data_count, the CRTM's included (D-196): the other publishers are named, not counted. */
export function counterText(n: number): string {
  return `Datos: ${n.toLocaleString("es-ES")} conjuntos de la Comunidad de Madrid (con los del CRTM) + Ayuntamiento de Madrid + Ministerio de Sanidad`;
}

const MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
const UPDATED = /actualizado a (\d{1,2}) de ([a-z]+) de (\d{4})/;

/** «31 de diciembre de 2024» from «… actualizado a 31 de diciembre de 2024)», or null. */
export function updatedInWords(name: string): string | null {
  const [, day, month, year] = UPDATED.exec(name) ?? [];
  return day && month && MONTHS.includes(month) ? `${day} de ${month} de ${year}` : null;
}

/** A citation a licence asks for: the catalogue's text (DatasetRef.attribution_text), and where it links. */
export interface Attribution {
  text: string;
  href: string | null;
}

/** Where each source's citation links: navigation only, the text is always the catalogue's. */
const ATTRIBUTION_LINKS: [RegExp, string][] = [
  [/CartoCiudad/, "https://www.cartociudad.es"],
  [/Ministerio de Sanidad/, "https://www.sanidad.gob.es/estadEstudios/estadisticas/sisInfSanSNS/ofertaRecursos/hospitales/home.htm"],
  // fit-0.6 (D-228): rent of the leases signed in 2024; the licence asks to cite the source and its date
  [/Agencia Tributaria/, "https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfvivienda/2024/home.html"],
  [/CRTM/, "https://www.crtm.es"],
  [/Ayuntamiento de Madrid/, "https://datos.madrid.es"],
  [/Comunidad de Madrid/, "https://datos.comunidad.madrid"],
  [/OpenStreetMap/, "https://www.openstreetmap.org/copyright"],
];

/** «A B», where A is another source's citation: A, then what follows it (the geocoder's, D-216). */
function splitCitation(text: string, all: readonly string[]): string[] {
  const base = all.filter((other) => other !== text && text.startsWith(`${other} `)).sort((a, b) => b.length - a.length)[0];
  return base ? [base, ...splitCitation(text.slice(base.length + 1), all)] : [text];
}

/**
 * Every citation the licences ask for, once, from the `attribution_text` of /datasets (taken by
 * the API from the source catalogue). A dataset with places located by the geocoder carries its
 * source's citation and then CartoCiudad's: each shows on its own.
 */
export function attributions(refs: readonly DatasetRef[]): Attribution[] {
  const texts = [...new Set(sortDatasets(refs).flatMap((ref) => ref.attribution_text?.trim() || []))];
  const cited: string[] = [];
  for (const text of texts) for (const part of splitCitation(text, texts)) if (!cited.includes(part)) cited.push(part);
  return cited.map((text) => ({ text, href: ATTRIBUTION_LINKS.find(([pattern]) => pattern.test(text))?.[1] ?? null }));
}

/**
 * What `attributions` gives for the catalogue today, shown only while /datasets has not answered
 * or failed. A test keeps it equal to the API's contract fixture, so it never drifts from it.
 */
export const ATTRIBUTIONS_FALLBACK: readonly Attribution[] = [
  { text: "Fuente: Comunidad de Madrid — Portal de Datos Abiertos (datos.comunidad.madrid), CC BY 4.0.", href: "https://datos.comunidad.madrid" },
  { text: "Geocodificación: © Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es.", href: "https://www.cartociudad.es" },
  { text: "Powered by CRTM — datos del Consorcio Regional de Transportes de Madrid (www.crtm.es). En bruto: los nombres de las estaciones. Explotados: los minutos hasta las paradas, hasta las estaciones accesibles y en transporte público, que calcula Vida Fácil con sus paradas, horarios y grados de accesibilidad.", href: "https://www.crtm.es" },
  { text: "Catálogo Nacional de Hospitales 2025 (actualizado a 31/12/2024) y Catálogo de Centros de Atención Primaria del SNS 2026 (actualizado a 31/12/2025). Ministerio de Sanidad.", href: "https://www.sanidad.gob.es/estadEstudios/estadisticas/sisInfSanSNS/ofertaRecursos/hospitales/home.htm" },
  { text: "Fuente: Ayuntamiento de Madrid — datos.madrid.es (CC BY 4.0).", href: "https://datos.madrid.es" },
  { text: "© OpenStreetMap contributors, ODbL.", href: "https://www.openstreetmap.org/copyright" },
];

/** The citations to show: the API's, or the fallback while it has not answered. */
export function attributionsOrFallback(refs: readonly DatasetRef[] | null): readonly Attribution[] {
  const cited = refs ? attributions(refs) : [];
  return cited.length ? cited : ATTRIBUTIONS_FALLBACK;
}

/**
 * mapa.atribucion.movil of pitch/textos_web.md: the two citations whose licences want them seen
 * without touching anything (the OSMF attribution guidelines, and the CRTM licence §2.2), always
 * beside the map's (i), each with its link, whatever /datasets answers.
 */
export const MAP_CREDITS: readonly { text: string; href: string }[] = [
  { text: "© OpenStreetMap", href: "https://www.openstreetmap.org/copyright" },
  { text: "Powered by CRTM", href: "https://www.crtm.es" },
];

const escapeHtml = (text: string) => text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

/**
 * The map's attribution (HTML for MapLibre): the screens with a map have no footer, so every
 * citation the licences ask for goes here, as the footer shows them.
 */
export function mapAttribution(refs: readonly DatasetRef[] | null): string {
  return attributionsOrFallback(refs)
    .map(({ text, href }) =>
      href ? `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(text)}</a>` : escapeHtml(text),
    )
    .join(" · ");
}

export interface DatasetLines {
  title: string;
  /** Tag for the datasets that count for DATAMAD (published in the CM portal) */
  portal: string | null;
  version: string | null;
  license: string | null;
  url: string | null;
  /** Said after the dataset's name in its link, hidden on screen: the name starts with the visible text (WCAG 2.5.3) */
  openHint: string;
}

export function datasetLines(ref: DatasetRef): DatasetLines {
  return {
    title: `${ref.name} — ${ref.publisher}`,
    portal: ref.is_cm_open_data ? PORTAL_CM : null,
    version: ref.version ? `Versión de los datos: ${ref.version}` : null,
    license: ref.license ? `Licencia: ${ref.license}` : null,
    url: ref.url ?? null,
    openHint: "en el portal de datos (se abre en una pestaña nueva)",
  };
}

/** CM portal datasets first, then the rest; each group by name. */
export function sortDatasets(refs: readonly DatasetRef[]): DatasetRef[] {
  return [...refs].sort(
    (a, b) => Number(b.is_cm_open_data) - Number(a.is_cm_open_data) || a.name.localeCompare(b.name, "es"),
  );
}
