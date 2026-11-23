/**
 * Generated from data/schemas/api/investor_zone_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
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
export type Confidence = number | null;
/**
 * The Feature Store figure behind it, when it is data
 */
export type FeatureId = string | null;
export type High = number | null;
export type Low = number | null;
export type ValueMark = "dato" | "supuesto" | "usuario";
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
export type DatasetIds = string[];
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
export type Period = string | null;
/**
 * In words, with its date
 */
export type Text = string;
/**
 * Where to open the source
 */
export type Url1 = string | null;
export type Unit = string;
export type Value = number | null;
export type Key = string;
export type Label = string;
export type Pct = number;
export type Source = string;
export type CostParts = AssumptionPart[];
export type SalesCostParts = AssumptionPart[];
/**
 * geo_admin_unit id for /api/v1/geo/admin-units; None for H3 cells
 */
export type AdminUnitId = string | null;
export type CenterLat = number | null;
export type CenterLon = number | null;
export type Code = string;
export type MunicipioIne = string | null;
export type MunicipioName = string | null;
export type Name1 = string;
export type Commerce = SourcedValue[];
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
export type Datasets1 = DatasetRef[];
export type Direction = "higher_is_better" | "lower_is_better";
export type Explanation = string;
export type Confidence1 = number;
/**
 * dataset_id values
 */
export type Datasets2 = string[];
export type FeatureId1 = string;
/**
 * Plain-language name
 */
export type Label1 = string;
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
export type Unit1 = string;
export type Value1 = number | null;
/**
 * e.g. walking minutes (CORE-005)
 */
export type ExtraIndicators = IndicatorValue[];
export type Label2 = string;
export type Count = number;
export type Label3 = string;
export type ProxyNote = string | null;
/**
 * Oriented so that above 1 is better than the reference; None when the value is unknown, and always in a context row (gap-0.4)
 */
export type RatioToReference1 = number | null;
/**
 * Same indicator for the zones the row is compared with (D-213: the municipios of its type in the region)
 */
export type Reference = number | null;
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
export type GapStatus = "FALTA" | "JUSTO" | "CUBIERTO" | "SIN_DATOS" | "CONTEXTO";
export type Rows = GapRow[];
export type Warnings = string[];
export type ZoneName = string;
/**
 * null when the source does not publish it
 */
export type BuildableM2 = number | null;
export type Code1 = string | null;
/**
 * parcela | ambito
 */
export type Kind = string;
export type Manager = string | null;
export type Name2 = string | null;
/**
 * A caveat that travels with the item: an area that also covers other barrios says which share of it is here (it counts whole in this barrio)
 */
export type Note = string | null;
export type Parcel = string | null;
/**
 * venta | concesion
 */
export type Regime = string | null;
export type Stage = string | null;
/**
 * The official viewer or record
 */
export type Url2 = string | null;
/**
 * Line A's planning areas: their use, as the source writes it
 */
export type Use = string | null;
export type Parcels = LandItem[];
export type Remaining = LandItem[];
export type Notices = string[];
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings1 = string[];

/**
 * GET /api/v1/investors/zones/{admin_unit_id} (D-248)
 */
export interface InvestorZoneResponse {
  data: InvestorZone;
  meta?: Meta;
  warnings?: Warnings1;
}
/**
 * GET /api/v1/investors/zones/{admin_unit_id}: the sheet of one pilot barrio.
 */
export interface InvestorZone {
  datasets: Datasets;
  defaults: ViabilityDefaults;
  demand: DemandBlock;
  district: ZoneRef;
  gaps: InvestorGaps | null;
  land: LandBlock;
  notices: Notices;
  prices: PricesBlock;
  zone: ZoneRef;
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
 * What the calculator starts from, every value with its mark and source.
 */
export interface ViabilityDefaults {
  adjust_floor_pct: SourcedValue;
  cost_coefficient: SourcedValue;
  cost_parts: CostParts;
  effort_threshold_pct: SourcedValue;
  home_m2: SourcedValue;
  household_income: SourcedValue;
  loan_rate_pct: SourcedValue;
  loan_years: SourcedValue;
  ltv_pct: SourcedValue;
  new_build_premium_pct: SourcedValue;
  pem_m2: SourcedValue1;
  /**
   * D-252: the PEM the building permits declare (CM dataset cm_visados_presupuesto_obra, from the Feature Store): the low reference
   */
  pem_permits_m2?: SourcedValue | null;
  rent_m2_month: SourcedValue;
  sale_price_m2: SourcedValue;
  sales_cost_parts: SalesCostParts;
  sales_costs_pct: SourcedValue;
  target_margin_pct: SourcedValue;
}
/**
 * A figure with its unit, mark and source; `low` and `high` when the source gives a range.
 */
export interface SourcedValue {
  confidence?: Confidence;
  feature_id?: FeatureId;
  high?: High;
  low?: Low;
  mark: ValueMark;
  /**
   * Why value is missing; never 0 for unknown
   */
  null_reason?: NullReason | null;
  source: FieldSource;
  unit: Unit;
  value: Value;
}
/**
 * Where one figure comes from, to show next to it.
 */
export interface FieldSource {
  dataset_ids?: DatasetIds;
  /**
   * The zone the figure is of: the barrio, its district or the whole city
   */
  level?: TerritoryLevel | null;
  period?: Period;
  text: Text;
  url?: Url1;
}
/**
 * One piece of an assumed percentage (the cost coefficient, the sales costs).
 */
export interface AssumptionPart {
  key: Key;
  label: Label;
  pct: Pct;
  source: Source;
}
/**
 * A figure with its unit, mark and source; `low` and `high` when the source gives a range.
 */
export interface SourcedValue1 {
  confidence?: Confidence;
  feature_id?: FeatureId;
  high?: High;
  low?: Low;
  mark: ValueMark;
  /**
   * Why value is missing; never 0 for unknown
   */
  null_reason?: NullReason | null;
  source: FieldSource;
  unit: Unit;
  value: Value;
}
/**
 * Who lives there. Each figure at the finest level published (its `source.level`).
 */
export interface DemandBlock {
  five_plus_pct: SourcedValue;
  household_size: SourcedValue;
  income: SourcedValue;
  one_person_pct: SourcedValue;
  over_65_pct: SourcedValue;
  population: SourcedValue;
  under_15_pct: SourcedValue;
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
/**
 * «Qué falta»: the district's rows (the list is not computed by barrio) and the commerce of
 * the barrio (line A).
 */
export interface InvestorGaps {
  commerce: Commerce;
  level: TerritoryLevel;
  rows: Rows;
  warnings?: Warnings;
  zone_name: ZoneName;
}
export interface GapRow {
  /**
   * Set when the zone is compared together with its nearest neighbours of the same type because it is too small alone (gap-0.3, D-217); `status` is the group's
   */
  comparison_group?: ComparisonGroup | null;
  datasets: Datasets1;
  direction: Direction;
  explanation: Explanation;
  extra_indicators?: ExtraIndicators;
  indicator: IndicatorValue;
  label: Label2;
  /**
   * Who the row serves in this zone (children of 0 to 4, people of 65 or more, …): the denominator of its indicator. With FALTA, the people affected (D-229). None when the indicator keeps no counts
   */
  people?: PeopleCount | null;
  proxy_note?: ProxyNote;
  ratio_to_reference?: RatioToReference1;
  reference: Reference;
  reference_label: ReferenceLabel;
  regional_reference?: RegionalReference;
  reliable?: Reliable;
  row: GapRowKey;
  status: GapStatus;
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
/**
 * One measured value with its unit, confidence and the reason when it is missing.
 */
export interface IndicatorValue {
  confidence: Confidence1;
  datasets?: Datasets2;
  feature_id: FeatureId1;
  label: Label1;
  level: TerritoryLevel1;
  /**
   * Why value is missing; never 0 for unknown
   */
  null_reason?: NullReason | null;
  unit: Unit1;
  value: Value1;
}
/**
 * The population a row serves, living in the zone (D-229): its indicator's denominator.
 */
export interface PeopleCount {
  count: Count;
  label: Label3;
}
export interface LandBlock {
  parcels: Parcels;
  parcels_m2: SourcedValue;
  remaining: Remaining;
  remaining_m2: SourcedValue;
  vacant_units: SourcedValue;
}
/**
 * A public parcel (D-246) or a planning area with buildable area left (line A).
 */
export interface LandItem {
  buildable_m2: BuildableM2;
  code: Code1;
  kind: Kind;
  manager?: Manager;
  name: Name2;
  note?: Note;
  parcel?: Parcel;
  regime?: Regime;
  stage?: Stage;
  url?: Url2;
  use?: Use;
}
export interface PricesBlock {
  new_build_premium_pct: SourcedValue;
  new_build_sale_m2: SourcedValue;
  rent_m2_month: SourcedValue;
  sale_m2: SourcedValue;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
