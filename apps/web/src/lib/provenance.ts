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
  const cited = (refs ?? [])
    .filter((ref) => ref.publisher === MINISTRY)
    .sort((a, b) => b.name.localeCompare(a.name, "es"))
    .map((ref) => citedName(ref.name));
  if (cited.length === 0) return MINISTRY_ATTRIBUTION;
  const list = cited.length === 1 ? cited[0] : `${cited.slice(0, -1).join(", ")} y ${cited.at(-1)}`;
  return `Fuente: ${MINISTRY} — ${list}.`;
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
