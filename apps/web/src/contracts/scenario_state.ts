/**
 * Generated from data/schemas/api/scenario_state.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
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
 * Everyday services the search and the per-zone list both talk about, and the leisure
 * groups of «Ocio» (D-236), which only the search knows: they are never rows of the list.
 */
export type NeedKey =
  | "escuela_infantil"
  | "colegio"
  | "centro_salud"
  | "farmacia"
  | "mayores"
  | "transporte"
  | "bares"
  | "restaurantes"
  | "gimnasios"
  | "cultura";
/**
 * True = hard constraint (PASS/FAIL/UNKNOWN)
 */
export type Required = boolean;
/**
 * @maxItems 10
 */
export type Nearby = NearbyNeed[];
/**
 * «Me importa» chips. Seguridad only counts when chosen; sin escaleras is optional. Ocio
 * (D-236) scores the leisure groups of `nearby` (LEISURE_NEEDS); without any, nothing.
 */
export type PriorityKey =
  "transporte" | "salud" | "colegios" | "zonas_verdes" | "seguridad" | "sin_escaleras" | "ocio";
/**
 * Most important first
 *
 * @maxItems 7
 */
export type Priorities = PriorityKey[];
export type SchemaVersion = 2;

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
