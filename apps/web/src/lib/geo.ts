/** Helpers for the canonical geography map (pure functions, unit tested). */

export type AdminLevel = "municipio" | "distrito" | "barrio" | "seccion_censal";

export interface AdminUnitProperties {
  admin_unit_id: string;
  level: AdminLevel;
  code: string;
  name: string | null;
  parent: string | null;
  area_km2: number;
}

export interface Lineage {
  version_label?: string;
  parser_version?: string;
  attribution_text?: string;
  license_name?: string;
}

export const DEFAULT_API_URL = "http://localhost:8010";

export const LEVEL_LABEL: Record<AdminLevel, string> = {
  municipio: "Municipio",
  distrito: "Distrito",
  barrio: "Barrio",
  seccion_censal: "Sección censal",
};

/** `parent` keeps only the direct children of that admin_unit_id (e.g. Madrid's 21 districts). */
export function adminUnitsUrl(base: string, level: AdminLevel, simplifyMeters: number, parent?: string): string {
  const url = new URL("/api/v1/geo/admin-units", base);
  url.searchParams.set("level", level);
  url.searchParams.set("simplify_m", String(simplifyMeters));
  if (parent) url.searchParams.set("parent", parent);
  return url.toString();
}

export function describeUnit(props: AdminUnitProperties): { title: string; rows: [string, string][] } {
  const title = props.name ?? `${LEVEL_LABEL[props.level]} ${props.code}`;
  const rows: [string, string][] = [
    ["Nivel", LEVEL_LABEL[props.level]],
    ["Código INE", props.code],
    ["Superficie", `${props.area_km2.toLocaleString("es-ES", { maximumFractionDigits: 2 })} km²`],
  ];
  if (props.name === null) {
    rows.push(["Nombre", "Sin nombre en la fuente"]);
  }
  return { title, rows };
}

export function describeLineage(lineage: Lineage): string {
  const parts = [lineage.attribution_text, lineage.version_label && `versión ${lineage.version_label}`];
  return parts.filter(Boolean).join(" · ");
}
