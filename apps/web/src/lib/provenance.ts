/**
 * Provenance in plain words (pure, unit tested): the footer counter and the dataset lines of
 * pitch/textos_web.md (pie.contador and fuente.*), from GET /api/v1/datasets.
 */
import type { DatasetRef } from "@/contracts/dataset_list_response";

export const PORTAL_CM = "Portal de Datos Abiertos de la Comunidad de Madrid";

/** `n` is cm_open_data_count, the CRTM's included (D-196): the other publishers are named, not counted. */
export function counterText(n: number): string {
  return `Datos: ${n.toLocaleString("es-ES")} conjuntos de la Comunidad de Madrid (con los del CRTM) + Ayuntamiento de Madrid + Ministerio de Sanidad`;
}

const MINISTRY = "Ministerio de Sanidad";

/** pie.sanidad as line D wrote it (pitch/textos_web.md §10), while /datasets has not answered. */
export const MINISTRY_ATTRIBUTION =
  "Fuente: Ministerio de Sanidad — Catálogo Nacional de Hospitales 2025 (actualizado a 31/12/2024) y Catálogo de Centros de Atención Primaria del SNS 2026 (actualizado a 31/12/2025).";

const MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"];
const UPDATED = /actualizado a (\d{1,2}) de ([a-z]+) de (\d{4})/;

/** «Catálogo Nacional de Hospitales 2025 (directorio…, actualizado a 31 de diciembre de 2024)» -> «… 2025 (actualizado a 31/12/2024)». */
function citedName(name: string): string {
  const title = name.split(" (")[0] ?? name;
  const [, day = "", monthName = "", year = ""] = UPDATED.exec(name) ?? [];
  const month = MONTHS.indexOf(monthName) + 1;
  if (!day || month === 0) return title;
  return `${title} (actualizado a ${day.padStart(2, "0")}/${String(month).padStart(2, "0")}/${year})`;
}

/**
 * pie.sanidad: the Ministry's legal notice asks to cite the source and its update date (D-218),
 * both read from the names /datasets gives its catalogues (hospitals first, as D wrote it).
 */
export function ministryAttribution(refs: readonly DatasetRef[] | null): string {
  const citation = ministryCitation(refs);
  return citation ? `Fuente: ${citation}.` : MINISTRY_ATTRIBUTION;
}

function ministryRefs(refs: readonly DatasetRef[] | null): DatasetRef[] {
  return (refs ?? []).filter((ref) => ref.publisher === MINISTRY).sort((a, b) => b.name.localeCompare(a.name, "es"));
}

/** «Ministerio de Sanidad — Catálogo … 2025 (actualizado a 31/12/2024) y …», or null while /datasets has not named them. */
function ministryCitation(refs: readonly DatasetRef[] | null): string | null {
  const cited = ministryRefs(refs).map((ref) => citedName(ref.name));
  if (cited.length === 0) return null;
  const list = cited.length === 1 ? cited[0] : `${cited.slice(0, -1).join(", ")} y ${cited.at(-1)}`;
  return `${MINISTRY} — ${list}`;
}

/** CartoCiudad, as the IGN asks to be cited (CC BY 4.0 scne.es), in the footer and on the map. */
export const CARTOCIUDAD_ATTRIBUTION = "© Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es";

const MINISTRY_URL = "https://www.sanidad.gob.es/estadEstudios/estadisticas/sisInfSanSNS/ofertaRecursos/hospitales/home.htm";

/** «31/12/2024» from «… actualizado a 31 de diciembre de 2024)», or null. */
function updatedDate(name: string): string | null {
  const [, day = "", monthName = "", year = ""] = UPDATED.exec(name) ?? [];
  const month = MONTHS.indexOf(monthName) + 1;
  return day && month > 0 ? `${day.padStart(2, "0")}/${String(month).padStart(2, "0")}/${year}` : null;
}

/** «31 de diciembre de 2024» from «… actualizado a 31 de diciembre de 2024)», or null. */
export function updatedInWords(name: string): string | null {
  return UPDATED.exec(name)?.slice(1, 4).join(" de ") ?? null;
}

/** mapa.atribucion of line D while /datasets has not answered. */
const MINISTRY_ON_MAP = "Ministerio de Sanidad (catálogos a 31/12/2024 y 31/12/2025)";

/** «Ministerio de Sanidad (catálogos a 31/12/2024 y 31/12/2025)», the dates from /datasets. */
function ministryOnMap(refs: readonly DatasetRef[] | null): string {
  const dates = ministryRefs(refs).flatMap((ref) => updatedDate(ref.name) ?? []);
  if (dates.length === 0) return MINISTRY_ON_MAP;
  const list = dates.length === 1 ? dates[0] : `${dates.slice(0, -1).join(", ")} y ${dates.at(-1)}`;
  return `${MINISTRY} (${dates.length === 1 ? "catálogo" : "catálogos"} a ${list})`;
}

const escapeHtml = (text: string) => text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function link(href: string, text: string): string {
  return `<a href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">${escapeHtml(text)}</a>`;
}

/**
 * mapa.atribucion (HTML for MapLibre): the screens with a map have no footer, so the sources whose
 * licences ask to be cited where their data shows go here, the Ministry with the update dates its
 * legal notice asks for (from /datasets; line D's text until it answers).
 */
export function mapAttribution(refs: readonly DatasetRef[] | null): string {
  const ministryUrl = ministryRefs(refs).find((ref) => ref.url)?.url ?? MINISTRY_URL;
  return [
    "Comunidad de Madrid",
    link("https://datos.madrid.es", "Ayuntamiento de Madrid"),
    // CRTM asks for «Powered by CRTM» with a link (data/catalog/sources/crtm_open_data.yaml)
    link("https://www.crtm.es", "Powered by CRTM"),
    link(ministryUrl, ministryOnMap(refs)),
    link("https://www.cartociudad.es", CARTOCIUDAD_ATTRIBUTION),
  ].join(" · ");
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
