/**
 * Generated from data/schemas/api/viability_request.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

export type AdjustFloorPct = number;
export type BuildableM2 = number;
export type CostCoefficient = number;
export type EffortThresholdPct = number;
export type HomeM2 = number;
/**
 * € net a year
 */
export type HouseholdIncome = number;
export type LoanRatePct = number;
export type LoanYears = number;
export type LtvPct = number;
export type LandEur = number | null;
/**
 * € per m² buildable
 */
export type LandEurM2 = number | null;
export type NewBuildPremiumPct = number;
export type PemM2 = number;
export type RentM2Month = number | null;
/**
 * €/m², before the premium
 */
export type SalePriceM2 = number;
export type SalesCostsPct = number;
export type TargetMarginPct = number;

/**
 * POST /api/v1/investors/viability. Per built m² and in euros; percentages as 20 = 20 %.
 * Land as a total or per m² buildable, not both; without it, the result is the residual land
 * value (the most the land can cost).
 */
export interface ViabilityRequest {
  adjust_floor_pct?: AdjustFloorPct;
  buildable_m2: BuildableM2;
  cost_coefficient?: CostCoefficient;
  demand?: DemandRequest | null;
  land_eur?: LandEur;
  land_eur_m2?: LandEurM2;
  new_build_premium_pct?: NewBuildPremiumPct;
  pem_m2: PemM2;
  rent_m2_month?: RentM2Month;
  sale_price_m2: SalePriceM2;
  sales_costs_pct?: SalesCostsPct;
  target_margin_pct?: TargetMarginPct;
}
/**
 * The demand check: a typical new home against the barrio's mean household income.
 */
export interface DemandRequest {
  effort_threshold_pct?: EffortThresholdPct;
  home_m2?: HomeM2;
  household_income: HouseholdIncome;
  loan_rate_pct?: LoanRatePct;
  loan_years?: LoanYears;
  ltv_pct?: LtvPct;
}
