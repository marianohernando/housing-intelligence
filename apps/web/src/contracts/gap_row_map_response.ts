/**
 * Generated from data/schemas/api/gap_row_map_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

export type Cubierto = number;
export type Falta = number;
export type Justo = number;
export type SinDatos = number;
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
export type Datasets = DatasetRef[];
export type Direction = "higher_is_better" | "lower_is_better";
/**
 * Plain-language name of the indicator
 */
export type IndicatorLabel = string;
export type Label = string;
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
export type ProxyNote = string | null;
/**
 * Same indicator for the whole region (each zone carries its own)
 */
export type Reference1 = number | null;
export type ReferenceLabel = string;
/**
 * Rows of the per-zone list of what is missing (GAP-001, D-194).
 */
export type GapRowKey =
  "escuela_infantil" | "colegio" | "centro_salud" | "mayores" | "farmacia" | "vivienda";
export type Unit = string;
/**
 * promoteId of /api/v1/geo/admin-units
 */
export type AdminUnitId = string;
export type Code = string;
export type Confidence = number;
export type Name1 = string;
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
/**
 * Oriented so that above 1 is better than the reference
 */
export type RatioToReference = number | null;
/**
 * What the zone is compared with: municipios of its type
 */
export type Reference2 = number | null;
export type ReferenceLabel1 = string | null;
/**
 * False when the zone is too small for this row: the count expected at the reference rate is under the 95 % bound of a zero count (3,7), so not even having none would be a significant shortfall. The status is then never FALTA; show it as «poco fiable» (D-213). True also when the test does not apply (no counts)
 */
export type Reliable = boolean;
export type GapStatus = "FALTA" | "JUSTO" | "CUBIERTO" | "SIN_DATOS";
export type Value = number | null;
export type Zones = ZoneGapStatus[];
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings = string[];

/**
 * GET /api/v1/gaps?level=&row=
 */
export interface GapRowMapResponse {
  data: GapRowMap;
  meta?: Meta;
  warnings?: Warnings;
}
/**
 * One row of the list for every zone of a level (GET /api/v1/gaps?level=&row=): the map.
 *
 * Same value, reference and cut-offs as the row in each zone's list. A row not computed at
 * this level comes with no zones and a warning in the envelope.
 */
export interface GapRowMap {
  counts: GapStatusCounts;
  datasets: Datasets;
  direction: Direction;
  indicator_label: IndicatorLabel;
  label: Label;
  level: TerritoryLevel;
  method: GapMethod;
  proxy_note?: ProxyNote;
  reference: Reference1;
  reference_label: ReferenceLabel;
  row: GapRowKey;
  unit: Unit;
  zones: Zones;
}
export interface GapStatusCounts {
  cubierto: Cubierto;
  falta: Falta;
  justo: Justo;
  sin_datos: SinDatos;
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
/**
 * One zone of a row map: the status that colours it and the value behind it.
 */
export interface ZoneGapStatus {
  admin_unit_id: AdminUnitId;
  code: Code;
  confidence: Confidence;
  name: Name1;
  null_reason?: NullReason | null;
  ratio_to_reference?: RatioToReference;
  reference?: Reference2;
  reference_label?: ReferenceLabel1;
  reliable?: Reliable;
  status: GapStatus;
  value: Value;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
