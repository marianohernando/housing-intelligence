/**
 * Generated from data/schemas/api/zone_gap_list_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

export type DatasetId = string;
/**
 * Published in the Comunidad de Madrid open data portal (counts for DATAMAD)
 */
export type IsCmOpenData = boolean;
export type License = string | null;
export type Name = string;
export type Publisher = string;
/**
 * Portal page (CM portal when it exists)
 */
export type Url = string | null;
/**
 * dataset_version label used
 */
export type Version = string | null;
/**
 * Union of the rows' datasets
 */
export type Datasets = DatasetRef[];
/**
 * FALTA also needs a significant shortfall: the exact Poisson upper bound of the zone's count at this level below the count expected at the reference rate. None: the ratio alone decides
 */
export type ConfidenceLevel = number | null;
/**
 * ratio at or above this -> CUBIERTO
 */
export type CubiertoFrom = number;
/**
 * ratio to reference below this -> FALTA
 */
export type FaltaBelow = number;
export type Reference = string;
export type Version1 = string;
export type Datasets1 = DatasetRef[];
export type Direction = "higher_is_better" | "lower_is_better";
export type Explanation = string;
export type Confidence = number;
/**
 * dataset_id values
 */
export type Datasets2 = string[];
export type FeatureId = string;
/**
 * Plain-language name
 */
export type Label = string;
/**
 * Level the value was computed at
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
export type NullReason =
  | "NOT_APPLICABLE"
  | "SOURCE_NO_COVERAGE"
  | "SOURCE_MISSING"
  | "TEMPORARILY_UNAVAILABLE"
  | "STALE"
  | "PARSE_ERROR"
  | "ENTITY_NOT_RESOLVED"
  | "ESTIMATION_NOT_ALLOWED"
  | "UNKNOWN";
export type Unit = string;
export type Value = number | null;
/**
 * e.g. walking minutes (CORE-005)
 */
export type ExtraIndicators = IndicatorValue[];
export type Label1 = string;
export type ProxyNote = string | null;
/**
 * Oriented so that above 1 is better than the reference
 */
export type RatioToReference = number | null;
/**
 * Same indicator for the zones the row is compared with (D-213: the municipios of its type in the region)
 */
export type Reference1 = number | null;
export type ReferenceLabel = string;
/**
 * Same indicator for the whole Comunidad de Madrid (context)
 */
export type RegionalReference = number | null;
/**
 * False when the zone is too small for this row: the count expected at the reference rate is under the 95 % bound of a zero count (3,7), so not even having none would be a significant shortfall. The status is then never FALTA; show it as «poco fiable» (D-213). True also when the test does not apply (no counts)
 */
export type Reliable = boolean;
/**
 * Rows of the per-zone list of what is missing (GAP-001, D-194).
 */
export type GapRowKey =
  "escuela_infantil" | "colegio" | "centro_salud" | "mayores" | "farmacia" | "vivienda";
export type GapStatus = "FALTA" | "JUSTO" | "CUBIERTO" | "SIN_DATOS";
export type Rows = GapRow[];
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
export type TerritoryLevel1 =
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
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings = string[];

/**
 * GET /api/v1/gaps/{level}/{code}
 */
export interface ZoneGapListResponse {
  data: ZoneGapList;
  meta?: Meta;
  warnings?: Warnings;
}
export interface ZoneGapList {
  datasets: Datasets;
  method: GapMethod;
  rows: Rows;
  zone: ZoneRef;
}
/**
 * Provenance of a result: the dataset, who publishes it and where to open it.
 */
export interface DatasetRef {
  dataset_id: DatasetId;
  is_cm_open_data: IsCmOpenData;
  license?: License;
  name: Name;
  publisher: Publisher;
  url?: Url;
  version?: Version;
}
/**
 * How rows are classified: value / regional reference against declared cut-offs.
 */
export interface GapMethod {
  confidence_level?: ConfidenceLevel;
  cubierto_from: CubiertoFrom;
  falta_below: FaltaBelow;
  reference: Reference;
  version: Version1;
}
export interface GapRow {
  datasets: Datasets1;
  direction: Direction;
  explanation: Explanation;
  extra_indicators?: ExtraIndicators;
  indicator: IndicatorValue;
  label: Label1;
  proxy_note?: ProxyNote;
  ratio_to_reference?: RatioToReference;
  reference: Reference1;
  reference_label: ReferenceLabel;
  regional_reference?: RegionalReference;
  reliable?: Reliable;
  row: GapRowKey;
  status: GapStatus;
}
/**
 * One measured value with its unit, confidence and the reason when it is missing.
 */
export interface IndicatorValue {
  confidence: Confidence;
  datasets?: Datasets2;
  feature_id: FeatureId;
  label: Label;
  level: TerritoryLevel;
  /**
   * Why value is missing; never 0 for unknown
   */
  null_reason?: NullReason | null;
  unit: Unit;
  value: Value;
}
/**
 * A zone the product talks about. `code` is the INE code (municipio, sección) or H3 index.
 */
export interface ZoneRef {
  admin_unit_id?: AdminUnitId;
  center_lat?: CenterLat;
  center_lon?: CenterLon;
  code: Code;
  level: TerritoryLevel1;
  municipio_ine?: MunicipioIne;
  municipio_name?: MunicipioName;
  name: Name1;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
