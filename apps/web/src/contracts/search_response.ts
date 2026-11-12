/**
 * Generated from data/schemas/api/search_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

export type FailedConstraints = string[];
/**
 * None = unknown
 */
export type MatchPct = number | null;
export type PassesAll = boolean;
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
/**
 * Every evaluated zone, for the map
 */
export type AllZones = ZoneMatch[];
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
/**
 * Every dataset behind this result
 */
export type Datasets = DatasetRef[];
export type MethodologyVersion = string;
export type Confidence = number;
export type Confidence1 = number;
export type ConstraintId = string;
export type Explanation = string;
export type Label = string;
export type ConstraintStatus = "PASS" | "FAIL" | "UNKNOWN";
export type Threshold = number | null;
export type Unit = string | null;
export type Value = number | null;
export type Constraints = ConstraintCheck[];
/**
 * Monthly rent or purchase price for the needed area
 */
export type EstimatedCostEur = number | null;
export type Confidence2 = number;
export type Confidence3 = number;
/**
 * dataset_id values
 */
export type Datasets1 = string[];
export type FeatureId = string;
/**
 * Plain-language name
 */
export type Label1 = string;
/**
 * Level the value was computed at
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
export type Unit1 = string;
export type Value1 = number | null;
export type FactKind = "strength" | "weakness" | "unknown";
export type Text = string;
/**
 * Which icon the web shows next to a fact.
 */
export type FactTopic =
  | "coste"
  | "transporte"
  | "salud"
  | "colegios"
  | "zonas_verdes"
  | "seguridad"
  | "accesibilidad"
  | "trayecto"
  | "otro";
/**
 * Up to 5 tangible facts, most important to the person first; unknown last
 *
 * @maxItems 5
 */
export type Facts = Fact[];
/**
 * constraint_id values with FAIL (near misses)
 */
export type FailedConstraints1 = string[];
export type Label2 = string;
/**
 * Rows of the per-zone list of what is missing (GAP-001, D-194).
 */
export type GapRowKey =
  "escuela_infantil" | "colegio" | "centro_salud" | "mayores" | "farmacia" | "vivienda";
export type GapStatus = "FALTA" | "JUSTO" | "CUBIERTO" | "SIN_DATOS";
/**
 * @maxItems 3
 */
export type GapHighlights = GapHighlight[];
/**
 * % of fit with the search, not a grade
 */
export type MatchPct1 = number;
export type Rank = number;
/**
 * Explicit alternatives failing one condition
 */
export type NearMisses = RankedZone[];
/**
 * constraint_id that removes the most zones
 */
export type BindingConstraint = string | null;
export type AddedZones = number;
export type ConstraintId1 = string;
export type Label3 = string;
export type DaysPerWeek = number;
export type AnchorKind = "work" | "study" | "family" | "other";
export type Label4 = string;
export type Lat = number;
export type Lon = number;
/**
 * Hard limit for the trip; None = preference only
 */
export type MaxMinutes = number | null;
/**
 * @maxItems 3
 */
export type Anchors = Anchor[];
/**
 * €/month when kind=rent, € when kind=buy
 */
export type AmountEur = number;
export type BudgetKind = "rent" | "buy";
export type Adults = number;
/**
 * 0-17, optional
 */
export type MinorAges = number[];
export type Minors = number;
/**
 * People aged 65+ cared for
 */
export type SeniorsInCare = number;
/**
 * None = derived from the household size
 */
export type MinFloorAreaM2 = number | null;
export type MaxWalkMinutes = number;
/**
 * Everyday services the search and the per-zone list both talk about.
 */
export type NeedKey =
  "escuela_infantil" | "colegio" | "centro_salud" | "farmacia" | "mayores" | "transporte";
/**
 * True = hard constraint (PASS/FAIL/UNKNOWN)
 */
export type Required = boolean;
/**
 * @maxItems 6
 */
export type Nearby = NearbyNeed[];
/**
 * «Me importa» chips. Seguridad only counts when chosen; sin escaleras is optional.
 */
export type PriorityKey =
  "transporte" | "salud" | "colegios" | "zonas_verdes" | "seguridad" | "sin_escaleras";
/**
 * Most important first
 *
 * @maxItems 6
 */
export type Priorities = PriorityKey[];
export type SchemaVersion = 2;
export type ZonesIfRelaxed = number;
/**
 * Sorted by added_zones, largest first
 */
export type Relaxations = Relaxation[];
export type ZonesEvaluated = number;
/**
 * Every constraint PASS
 */
export type ZonesPassing = number;
/**
 * No FAIL but some UNKNOWN: not counted as passing
 */
export type ZonesUnknown = number;
/**
 * Zones passing every constraint, best first
 */
export type Results = RankedZone[];
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion1 = string | null;
export type RequestId = string;
export type Warnings = string[];

/**
 * POST /api/v1/search
 */
export interface SearchResponse {
  data: SearchResult;
  meta?: Meta;
  warnings?: Warnings;
}
export interface SearchResult {
  all_zones: AllZones;
  datasets: Datasets;
  methodology_version: MethodologyVersion;
  near_misses?: NearMisses;
  reality_check: RealityCheck;
  results: Results;
  scenario: ScenarioState;
}
/**
 * Every evaluated zone, for the choropleth («Encaje con tu búsqueda»).
 */
export interface ZoneMatch {
  failed_constraints?: FailedConstraints;
  match_pct?: MatchPct;
  passes_all: PassesAll;
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
  name: Name;
}
/**
 * Provenance of a result: the dataset, who publishes it and where to open it.
 */
export interface DatasetRef {
  attribution_text?: AttributionText;
  dataset_id: DatasetId;
  is_cm_open_data: IsCmOpenData;
  license?: License;
  name: Name1;
  publisher: Publisher;
  source_name?: SourceName;
  url?: Url;
  version?: Version;
}
export interface RankedZone {
  confidence: Confidence;
  constraints: Constraints;
  estimated_cost_eur?: EstimatedCostEur;
  facts: Facts;
  failed_constraints?: FailedConstraints1;
  gap_highlights?: GapHighlights;
  match_pct: MatchPct1;
  rank: Rank;
  zone: ZoneRef;
}
/**
 * One hard condition of the scenario evaluated on one zone.
 */
export interface ConstraintCheck {
  confidence: Confidence1;
  constraint_id: ConstraintId;
  explanation: Explanation;
  label: Label;
  status: ConstraintStatus;
  threshold?: Threshold;
  unit?: Unit;
  value?: Value;
}
/**
 * A tangible, plain-language fact («Colegio público a 6 min andando») with its confidence,
 * always traceable to an indicator and its datasets.
 */
export interface Fact {
  confidence: Confidence2;
  indicator?: IndicatorValue | null;
  kind: FactKind;
  text: Text;
  topic: FactTopic;
}
/**
 * One measured value with its unit, confidence and the reason when it is missing.
 */
export interface IndicatorValue {
  confidence: Confidence3;
  datasets?: Datasets1;
  feature_id: FeatureId;
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
 * One row of «Qué falta aquí» for the zone card; the full list is GET /gaps.
 */
export interface GapHighlight {
  label: Label2;
  row: GapRowKey;
  status: GapStatus;
}
export interface RealityCheck {
  binding_constraint?: BindingConstraint;
  relaxations: Relaxations;
  zones_evaluated: ZonesEvaluated;
  zones_passing: ZonesPassing;
  zones_unknown: ZonesUnknown;
}
/**
 * How many more zones appear when one condition is relaxed and the rest stay.
 *
 * `relaxed_scenario` is the scenario with that change applied: the web sends it back to
 * POST /search when the person taps the option.
 */
export interface Relaxation {
  added_zones: AddedZones;
  constraint_id: ConstraintId1;
  label: Label3;
  relaxed_scenario: ScenarioState;
  zones_if_relaxed: ZonesIfRelaxed;
}
export interface ScenarioState {
  anchors?: Anchors;
  /**
   * None = no budget limit
   */
  budget?: Budget | null;
  household?: Household;
  min_floor_area_m2?: MinFloorAreaM2;
  nearby?: Nearby;
  priorities?: Priorities;
  schema_version?: SchemaVersion;
}
/**
 * A place the household travels to often («Trabajo en»).
 */
export interface Anchor {
  days_per_week?: DaysPerWeek;
  kind?: AnchorKind;
  label: Label4;
  lat: Lat;
  lon: Lon;
  max_minutes?: MaxMinutes;
}
/**
 * Rent in €/month or purchase price in €; the purchase result is always «orientativo».
 */
export interface Budget {
  amount_eur: AmountEur;
  kind: BudgetKind;
}
/**
 * «Tu hogar»: adults, children and older people they look after (all live together).
 */
export interface Household {
  adults?: Adults;
  minor_ages?: MinorAges;
  minors?: Minors;
  seniors_in_care?: SeniorsInCare;
}
/**
 * A service the household wants within walking distance (e.g. «colegio cerca»).
 */
export interface NearbyNeed {
  max_walk_minutes?: MaxWalkMinutes;
  need: NeedKey;
  required?: Required;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion1;
  request_id?: RequestId;
}
