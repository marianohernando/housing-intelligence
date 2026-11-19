/**
 * Generated from data/schemas/api/investor_zone_list_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

/**
 * What the licence asks to show next to the data (source, date, geocoder)
 */
export type AttributionText = string | null;
export type DatasetId = string;
/**
 * Published in the Comunidad de Madrid open data portal (counts for DATAMAD)
 */
export type IsCmOpenData = boolean;
export type License = string | null;
export type Name = string;
export type Publisher = string;
/**
 * Where it is published, to name where `url` opens (the CM portal, the Ayuntamiento's, OpenStreetMap, the Ministerio de Sanidad, the Agencia Tributaria…)
 */
export type SourceName = string | null;
/**
 * Portal page (CM portal when it exists)
 */
export type Url = string | null;
/**
 * dataset_version label used
 */
export type Version = string | null;
export type Datasets = DatasetRef[];
export type Pilot = string;
/**
 * Open local shops per 1.000 inhabitants (line A); null until loaded
 */
export type CommercePer1000 = number | null;
/**
 * geo_admin_unit id for /api/v1/geo/admin-units; None for H3 cells
 */
export type AdminUnitId = string | null;
export type CenterLat = number | null;
export type CenterLon = number | null;
export type Code = string;
/**
 * Territorial units observations can refer to (superset of AdminLevel).
 */
export type TerritoryLevel =
  | "ccaa"
  | "municipio"
  | "distrito"
  | "barrio"
  | "seccion_censal"
  | "codigo_postal"
  | "zona_estadistica"
  | "h3_r8"
  | "h3_r9";
export type MunicipioIne = string | null;
export type MunicipioName = string | null;
export type Name1 = string;
export type Falta = number;
export type Justo = number;
/**
 * Labels of the FALTA rows, then the JUSTO ones
 */
export type Rows = string[];
/**
 * Public parcels for housing; null if unknown
 */
export type Parcels = number | null;
export type ParcelsM2 = number | null;
/**
 * Residential buildable area left in its planning areas (line A); null until loaded. An area that also covers other barrios counts whole here
 */
export type RemainingM2 = number | null;
/**
 * How many of those areas also cover other barrios
 */
export type RemainingSharedAreas = number | null;
export type RentM2Month = number | null;
export type SalePriceM2 = number | null;
export type Zones = InvestorZoneSummary[];
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings = string[];

/**
 * GET /api/v1/investors/zones (D-248)
 */
export interface InvestorZoneListResponse {
  data: InvestorZoneList;
  meta?: Meta;
  warnings?: Warnings;
}
export interface InvestorZoneList {
  datasets: Datasets;
  pilot: Pilot;
  zones: Zones;
}
/**
 * Provenance of a result: the dataset, who publishes it and where to open it.
 */
export interface DatasetRef {
  attribution_text?: AttributionText;
  dataset_id: DatasetId;
  is_cm_open_data: IsCmOpenData;
  license?: License;
  name: Name;
  publisher: Publisher;
  source_name?: SourceName;
  url?: Url;
  version?: Version;
}
/**
 * A pilot barrio in the list: what it lacks (its district's rows), its land and prices.
 */
export interface InvestorZoneSummary {
  commerce_per_1000: CommercePer1000;
  district: ZoneRef;
  /**
   * Its district's «Qué falta»; null if not computed
   */
  gaps: GapCount | null;
  parcels: Parcels;
  parcels_m2: ParcelsM2;
  remaining_m2: RemainingM2;
  remaining_shared_areas?: RemainingSharedAreas;
  rent_m2_month: RentM2Month;
  sale_price_m2: SalePriceM2;
  zone: ZoneRef;
}
/**
 * A zone the product talks about. `code` is the INE code (municipio, sección) or H3 index.
 */
export interface ZoneRef {
  admin_unit_id?: AdminUnitId;
  center_lat?: CenterLat;
  center_lon?: CenterLon;
  code: Code;
  level: TerritoryLevel;
  municipio_ine?: MunicipioIne;
  municipio_name?: MunicipioName;
  name: Name1;
}
export interface GapCount {
  falta: Falta;
  justo: Justo;
  rows: Rows;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
