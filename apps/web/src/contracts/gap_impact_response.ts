/**
 * Generated from data/schemas/api/gap_impact_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
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
 * Portal page (CM portal when it exists)
 */
export type Url = string | null;
/**
 * dataset_version label used
 */
export type Version = string | null;
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
export type Label = string;
/**
 * Madrid capital counted by its 21 districts, or as one municipio when the row has no district values
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
export type PeopleInFalta = number;
export type PeopleLabel = string;
/**
 * The row's target population in the region
 */
export type PeopleTotal = number;
export type AdminUnitId = string;
export type Code = string;
/**
 * The zone first, then its neighbours
 *
 * @minItems 2
 */
export type Codes = [string, string, ...string[]];
/**
 * @minItems 2
 */
export type Names = [string, string, ...string[]];
/**
 * Group total over its expected total
 */
export type RatioToReference = number;
export type Explanation = string;
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
export type Name1 = string;
/**
 * One-sided exact Poisson probability that a zone at the reference rate has this little or less; FALTA needs it below 0,025 (D-213). None when the row keeps no counts to test and the ratio alone decided
 */
export type PValue = number | null;
/**
 * The row's target population living in the zone
 */
export type People = number;
/**
 * Supply over the reference (the group's when compared with neighbours)
 */
export type RatioToReference1 = number;
/**
 * Where to invest first: zones in FALTA, most people affected first
 */
export type Ranking = GapImpactZone[];
/**
 * Rows of the per-zone list of what is missing (GAP-001, D-194).
 */
export type GapRowKey =
  "escuela_infantil" | "colegio" | "centro_salud" | "mayores" | "farmacia" | "vivienda";
export type ShareInFalta = number;
export type Summary = string;
/**
 * Zones counted, whatever their status (SIN_DATOS too)
 */
export type Zones = number;
export type ZonesInFalta = number;
export type Rows = GapImpactRow[];
export type Version2 = string;
/**
 * Which zones are counted: the municipios and Madrid capital's districts
 */
export type ZonesNote = string;
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings = string[];

/**
 * GET /api/v1/gaps/impact
 */
export interface GapImpactResponse {
  data: GapImpact;
  meta?: Meta;
  warnings?: Warnings;
}
/**
 * GET /api/v1/gaps/impact: the people affected by each row, region-wide (D-229).
 */
export interface GapImpact {
  datasets: Datasets;
  method: GapMethod;
  rows: Rows;
  version: Version2;
  zones_note: ZonesNote;
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
 * One row of the list: how many people live where it is missing, and where to invest.
 */
export interface GapImpactRow {
  label: Label;
  madrid_level: TerritoryLevel;
  people_in_falta: PeopleInFalta;
  people_label: PeopleLabel;
  people_total: PeopleTotal;
  ranking: Ranking;
  row: GapRowKey;
  share_in_falta: ShareInFalta;
  summary: Summary;
  zones: Zones;
  zones_in_falta: ZonesInFalta;
}
/**
 * A zone in FALTA, with the people affected and how clear the shortfall is (D-229).
 */
export interface GapImpactZone {
  admin_unit_id: AdminUnitId;
  code: Code;
  comparison_group?: ComparisonGroup | null;
  explanation: Explanation;
  level: TerritoryLevel1;
  name: Name1;
  p_value: PValue;
  people: People;
  ratio_to_reference: RatioToReference1;
}
/**
 * A zone too small to compare alone, compared with its nearest same-type neighbours.
 *
 * gap-0.3 (D-217): the nearest municipios of the same type are added until the group expects
 * 3,69 cases at the reference rate (the floor of D-213). `status` is then the group's.
 */
export interface ComparisonGroup {
  codes: Codes;
  names: Names;
  ratio_to_reference: RatioToReference;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
