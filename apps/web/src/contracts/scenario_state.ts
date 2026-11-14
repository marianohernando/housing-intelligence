/**
 * Generated from data/schemas/api/scenario_state.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

/**
 * Days they go there in a week: 1-2 halve the weight of the trip; 0 = never (full telework), the trip is not scored but its max_minutes still applies (D-240)
 */
export type DaysPerWeek = number;
export type AnchorKind = "work" | "study" | "family" | "other";
export type Label = string;
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
/**
 * Where to search; Madrid capital is ranked by barrio instead of by district
 */
export type SearchScope = "all" | "madrid" | "alrededores" | "pueblos";

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
  scope?: SearchScope;
}
/**
 * A place the household travels to often: where they work, or family and friends.
 */
export interface Anchor {
  days_per_week?: DaysPerWeek;
  kind?: AnchorKind;
  label: Label;
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
