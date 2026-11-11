/**
 * Provenance in plain words (pure, unit tested): the footer counter and the dataset lines of
 * pitch/textos_web.md (pie.contador and fuente.*), from GET /api/v1/datasets.
 */
import type { DatasetRef } from "@/contracts/dataset_list_response";

export const PORTAL_CM = "Portal de Datos Abiertos de la Comunidad de Madrid";

/** `n` is cm_open_data_count: the other publishers are named, not counted. */
export function counterText(n: number): string {
  return `Datos: ${n.toLocaleString("es-ES")} conjuntos de la Comunidad de Madrid + Ayuntamiento de Madrid + CRTM`;
}

export interface DatasetLines {
  title: string;
  /** Tag for the datasets that count for DATAMAD (published in the CM portal) */
  portal: string | null;
  version: string | null;
  license: string | null;
  url: string | null;
  openLabel: string;
}

export function datasetLines(ref: DatasetRef): DatasetLines {
  return {
    title: `${ref.name} — ${ref.publisher}`,
    portal: ref.is_cm_open_data ? PORTAL_CM : null,
    version: ref.version ? `Versión de los datos: ${ref.version}` : null,
    license: ref.license ? `Licencia: ${ref.license}` : null,
    url: ref.url ?? null,
    openLabel: `Abrir ${ref.name} en el portal de datos (se abre en una pestaña nueva)`,
  };
}

/** CM portal datasets first, then the rest; each group by name. */
export function sortDatasets(refs: readonly DatasetRef[]): DatasetRef[] {
  return [...refs].sort(
    (a, b) => Number(b.is_cm_open_data) - Number(a.is_cm_open_data) || a.name.localeCompare(b.name, "es"),
  );
}
