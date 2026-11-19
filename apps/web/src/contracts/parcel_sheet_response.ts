/**
 * Generated from data/schemas/api/parcel_sheet_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

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
export type Name = string;
export type Article = string | null;
export type ArticleUrl = string | null;
/**
 * The norm's assumption when an official figure wins
 */
export type AssumedM2 = number | null;
export type DatasetId = string;
/**
 * Whether the calculator can use it (housing only)
 */
export type Residential = boolean;
export type Source = string;
/**
 * As the source writes it
 */
export type Use = string;
/**
 * D-252: a use as the person reads it, from the planning's or a source's words.
 */
export type UseClass =
  | "residencial"
  | "terciario"
  | "industrial"
  | "dotacional"
  | "zona_verde"
  | "infraestructura"
  | "sin_uso"
  | "otro";
export type ValueM2 = number;
/**
 * D-252: every official figure of the parcel with its use and source
 */
export type ByUse = UseFigure[];
/**
 * m² per m² of parcel
 */
export type Coefficient = number | null;
export type DatasetIds = string[];
export type Editable = true;
export type Formula = string | null;
export type BuildabilityKind = "oficial" | "supuesto" | "sin_dato";
/**
 * What to keep in mind about the figure
 */
export type Note = string | null;
/**
 * In words, with its date or its article
 */
export type Source1 = string;
export type ValueM21 = number | null;
/**
 * D-252: what keeps the sheet's figures from passing for free housing ready to build.
 */
export type ParcelCautionKey =
  "otro_uso" | "ambito_pendiente" | "vivienda_protegida" | "unifamiliar";
export type Text = string;
/**
 * D-252: shown before the figures
 */
export type Cautions = ParcelCaution[];
export type InPilot = boolean;
export type Note1 = string | null;
/**
 * What the licence asks to show next to the data (source, date, geocoder)
 */
export type AttributionText = string | null;
export type DatasetId1 = string;
/**
 * Published in the Comunidad de Madrid open data portal (counts for DATAMAD)
 */
export type IsCmOpenData = boolean;
export type License = string | null;
export type Name1 = string;
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
export type DatasetIds1 = string[];
export type Period = string | null;
/**
 * In words, with its date
 */
export type Text1 = string;
/**
 * Where to open the source
 */
export type Url1 = string | null;
export type Unit = string;
export type Value = number | null;
export type Key = string;
export type Label = string;
export type Pct = number;
export type Source2 = string;
export type CostParts = AssumptionPart[];
export type SalesCostParts = AssumptionPart[];
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
 * Oriented so that above 1 is better than the reference
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
export type GapStatus = "FALTA" | "JUSTO" | "CUBIERTO" | "SIN_DATOS";
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
export type Note2 = string | null;
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
export type Use1 = string | null;
export type Parcels = LandItem[];
export type Remaining = LandItem[];
export type Notices = string[];
/**
 * The parts that could not be read now
 */
export type Degraded = ("catastro" | "planning" | "buildability" | "context" | "plan_uses")[];
/**
 * Served from the saved demo sheet because a source failed
 */
export type Fallback = "demo_snapshot" | null;
/**
 * How the parcel was asked for: its cadastral reference, a point on the map or an address.
 */
export type ParcelInput = "rc" | "point" | "address";
export type Notices1 = string[];
export type Address = string | null;
/**
 * Surface of the parcel (land)
 */
export type AreaM2 = number | null;
/**
 * Built today: context, not buildability
 */
export type BuiltM2 = number | null;
export type CurrentUse = string | null;
export type HorizontalDivision = boolean;
/**
 * A plot with nothing built (solar); null unknown
 */
export type IsVacant = boolean | null;
export type Lat = number | null;
export type Lon = number | null;
/**
 * When the Catastro was asked
 */
export type ObservedAt = string;
/**
 * The parcel in the Sede Electrónica del Catastro, as its service returns it
 */
export type OfficialUrl = string | null;
export type PostalCode = string | null;
export type Rc14 = string;
/**
 * Rustic land: a reduced sheet, no buildability
 */
export type Rustic = boolean | null;
export type BuiltM21 = number | null;
export type Count1 = number;
export type Use2 = string;
export type ByUse1 = UnitUse[];
export type Total = number;
export type YearBuilt = number | null;
export type AsOf = string;
/**
 * The code in the Ayuntamiento's list
 */
export type Code2 = string;
/**
 * Planning, management or urbanization not finished
 */
export type Pending = boolean;
export type Label4 = string;
export type State = string;
export type Phases = AmbitPhase[];
/**
 * False: the Ayuntamiento does not publish its state
 */
export type Tracked = boolean;
export type Url3 = string;
export type VedaStage =
  | ("pendiente_sectorizacion" | "pendiente_planeamiento" | "gestion_urbanizacion" | "edificacion")
  | null;
export type Code3 = string;
export type Figure = string | null;
export type FileNumber = string | null;
export type Name3 = string | null;
export type Url4 = string | null;
/**
 * What the planning code is: a norma zonal or a planning area (ámbito) of the PGOUM.
 */
export type PlanningKind =
  "norma_zonal" | "API" | "APE" | "APR" | "APD" | "UZI" | "UZP" | "UNP" | "NUP" | "AOE" | "otro";
export type Name4 = string | null;
export type Grado = number | null;
/**
 * The zone's name in the Normas Urbanísticas (art. 8.0.5)
 */
export type Name5 = string | null;
export type Nivel = string | null;
export type Nz = number;
export type Notice = string;
export type ObservedAt1 = string;
/**
 * D-252: what the plan allows by use on the urban parcel; [] when it publishes nothing, null when it could not be read
 */
export type PlanUses = PlanUseFigure[] | null;
/**
 * value_m2 computed from the coefficient
 */
export type Assumed = boolean;
/**
 * m²/m² when the plan gives it so
 */
export type Coefficient1 = number | null;
/**
 * Table 4, «uso cualificado principal»; else table 5
 */
export type Principal = boolean;
export type Use3 = string;
export type UseOwnership = "publico" | "privado";
/**
 * m²; with a coefficient, coefficient × urban parcel area
 */
export type ValueM22 = number | null;
export type SheetLabel = string | null;
/**
 * The official record: the instrument's, or the article of the Normas Urbanísticas for a norma zonal
 */
export type SheetUrl = string | null;
export type UrbanParcel = string | null;
/**
 * D-252: the area of the urban parcel's polygon in the plan
 */
export type UrbanParcelAreaM2 = number | null;
export type Use4 = string | null;
/**
 * The Geoportal viewer, centred on the parcel
 */
export type ViewerUrl = string;
export type AccessedAt = string | null;
export type Attribution = string;
export type License1 = string;
export type LicenseUrl = string | null;
export type Name6 = string;
export type Publisher1 = string;
export type SourceId = string;
export type Url5 = string | null;
export type Sources = ParcelSource[];
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings1 = string[];

/**
 * GET /api/v1/investors/parcels (D-250)
 */
export interface ParcelSheetResponse {
  data: ParcelSheet;
  meta?: Meta;
  warnings?: Warnings1;
}
/**
 * GET /api/v1/investors/parcels: one parcel of Madrid capital for whoever builds.
 */
export interface ParcelSheet {
  barrio: ZoneRef | null;
  buildability: Buildability;
  cautions?: Cautions;
  /**
   * null when the barrio is unknown
   */
  context: ParcelContext | null;
  defaults: ViabilityDefaults;
  degraded?: Degraded;
  district: ZoneRef | null;
  fallback?: Fallback;
  input: ParcelInput;
  notices: Notices1;
  parcel: ParcelBlock;
  /**
   * null when the Ayuntamiento fails
   */
  planning: PlanningBlock | null;
  /**
   * D-252: the parcel as public land of the Portal del Suelo in its barrio (owner, regime, urbanization), when the barrio's sheet lists it
   */
  public_land?: LandItem | null;
  sources: Sources;
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
  name: Name;
}
/**
 * The buildable m² the calculator starts from: official, assumed or unknown. Always
 * editable.
 */
export interface Buildability {
  article?: Article;
  article_url?: ArticleUrl;
  assumed_m2?: AssumedM2;
  by_use?: ByUse;
  coefficient?: Coefficient;
  dataset_ids?: DatasetIds;
  editable?: Editable;
  formula?: Formula;
  kind: BuildabilityKind;
  note?: Note;
  source: Source1;
  value_m2: ValueM21;
}
/**
 * One source's buildable m² for a parcel, with the use that source gives it. A source that
 * gives one figure is never split by use.
 */
export interface UseFigure {
  dataset_id: DatasetId;
  residential: Residential;
  source: Source;
  use: Use;
  use_class: UseClass;
  value_m2: ValueM2;
}
export interface ParcelCaution {
  key: ParcelCautionKey;
  text: Text;
}
/**
 * The barrio around the parcel: the whole investor sheet in a pilot barrio (D-248); outside
 * the pilot, its district's figures, and it says so.
 */
export interface ParcelContext {
  in_pilot: InPilot;
  level: TerritoryLevel;
  note: Note1;
  sheet: InvestorZone;
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
  dataset_id: DatasetId1;
  is_cm_open_data: IsCmOpenData;
  license?: License;
  name: Name1;
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
  pem_m2: SourcedValue;
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
  dataset_ids?: DatasetIds1;
  /**
   * The zone the figure is of: the barrio, its district or the whole city
   */
  level?: TerritoryLevel | null;
  period?: Period;
  text: Text1;
  url?: Url1;
}
/**
 * One piece of an assumed percentage (the cost coefficient, the sales costs).
 */
export interface AssumptionPart {
  key: Key;
  label: Label;
  pct: Pct;
  source: Source2;
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
  note?: Note2;
  parcel?: Parcel;
  regime?: Regime;
  stage?: Stage;
  url?: Url2;
  use?: Use1;
}
export interface PricesBlock {
  new_build_premium_pct: SourcedValue;
  new_build_sale_m2: SourcedValue;
  rent_m2_month: SourcedValue;
  sale_m2: SourcedValue;
}
/**
 * «Datos de la parcela»: our fields, worked out from the Catastro's public data. Never its
 * raw answer, never the units with their floor and door.
 */
export interface ParcelBlock {
  address: Address;
  area_m2: AreaM2;
  built_m2: BuiltM2;
  current_use: CurrentUse;
  horizontal_division: HorizontalDivision;
  is_vacant: IsVacant;
  lat?: Lat;
  lon?: Lon;
  observed_at: ObservedAt;
  official_url: OfficialUrl;
  postal_code?: PostalCode;
  rc14: Rc14;
  rustic: Rustic;
  /**
   * Only in horizontal division
   */
  units: ParcelUnits | null;
  year_built?: YearBuilt;
}
/**
 * A building in horizontal division, summarised: units by use (no list of units).
 */
export interface ParcelUnits {
  by_use: ByUse1;
  total: Total;
}
/**
 * How many units of one use a building has, and their built area: never floor and door.
 */
export interface UnitUse {
  built_m2: BuiltM21;
  count: Count1;
  use: Use2;
}
/**
 * «Planeamiento»: the Ayuntamiento's planning at the parcel's reference point.
 */
export interface PlanningBlock {
  /**
   * D-252: the state of the planning area; null for a norma zonal
   */
  ambit?: AmbitStatus | null;
  code: Code3;
  instrument: PlanningInstrument | null;
  kind: PlanningKind;
  name: Name4;
  norma_zonal: NormaZonal | null;
  notice: Notice;
  observed_at: ObservedAt1;
  plan_uses?: PlanUses;
  sheet_label: SheetLabel;
  sheet_url: SheetUrl;
  urban_parcel: UrbanParcel;
  urban_parcel_area_m2?: UrbanParcelAreaM2;
  use: Use4;
  /**
   * D-252: the use, classified
   */
  use_class?: UseClass | null;
  /**
   * D-252: dotacional público or privado, when the plan says it
   */
  use_ownership?: UseOwnership | null;
  viewer_url: ViewerUrl;
}
/**
 * D-252: the state of the planning area, as the Ayuntamiento publishes it.
 */
export interface AmbitStatus {
  as_of: AsOf;
  code: Code2;
  pending: Pending;
  phases?: Phases;
  tracked: Tracked;
  url: Url3;
  veda_stage?: VedaStage;
}
export interface AmbitPhase {
  label: Label4;
  state: State;
}
/**
 * The planning instrument in force at the point, with its official record.
 */
export interface PlanningInstrument {
  figure: Figure;
  file_number: FileNumber;
  name: Name3;
  url: Url4;
}
export interface NormaZonal {
  grado?: Grado;
  name?: Name5;
  nivel?: Nivel;
  nz: Nz;
}
/**
 * D-252: what the plan allows of one use on the urban parcel (USOS_SUELO, table 4 for the
 * principal use and table 5 for the others). The total the plan allows, not what is left; the
 * urban parcel may not be the cadastral one.
 */
export interface PlanUseFigure {
  assumed?: Assumed;
  coefficient?: Coefficient1;
  principal: Principal;
  use: Use3;
  use_class: UseClass;
  use_ownership?: UseOwnership | null;
  value_m2?: ValueM22;
}
/**
 * Who the sheet's data comes from, its licence and how it asks to be cited.
 */
export interface ParcelSource {
  accessed_at?: AccessedAt;
  attribution: Attribution;
  license: License1;
  license_url?: LicenseUrl;
  name: Name6;
  publisher: Publisher1;
  source_id: SourceId;
  url?: Url5;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
