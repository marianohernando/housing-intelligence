/**
 * Generated from data/schemas/api/viability_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

export type DownPayment = number;
export type DownPaymentYears = number;
export type HomePrice = number;
export type Lines = string[];
export type Loan = number;
export type MonthlyPayment = number;
export type MonthlyRent = number | null;
export type PurchaseEffortPct = number;
export type PurchaseWithin = boolean;
export type RentEffortPct = number | null;
export type RentWithin = boolean | null;
export type ThresholdPct = number;
export type LandKnown = boolean;
export type Notices = string[];
/**
 * The sale price with the new-build premium
 */
export type SalePriceM2New = number;
export type AnnualRent = number | null;
export type Construction = number;
export type CostFactor = number;
export type Headline = string;
export type Key = string;
export type Label = string;
export type Land = number | null;
export type MarginPct = number | null;
export type PriceFactor = number;
export type Profit = number | null;
/**
 * Annual rent over construction plus land; null without rent or when not even free land reaches the target margin
 */
export type RentalYieldPct = number | null;
export type ResidualLandValue = number;
export type ResidualLandValueM2 = number;
export type Revenue = number;
export type SalesCosts = number;
/**
 * null without a land price
 */
export type TotalCost = number | null;
export type Verdict = "sale" | "ajustar" | "no_sale";
/**
 * The land the yield counts: the price given, or without one the residual land value (paying the most the target margin allows); never no land
 */
export type YieldLand = ("precio" | "valor_residual") | null;
export type Scenarios = ScenarioOutcome[];
export type Version = string;
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings = string[];

/**
 * POST /api/v1/investors/viability (D-248)
 */
export interface ViabilityResponse {
  data: ViabilityResult;
  meta?: Meta;
  warnings?: Warnings;
}
export interface ViabilityResult {
  demand: DemandOutcome | null;
  land_known: LandKnown;
  notices: Notices;
  sale_price_m2_new: SalePriceM2New;
  scenarios: Scenarios;
  version: Version;
}
export interface DemandOutcome {
  down_payment: DownPayment;
  down_payment_years: DownPaymentYears;
  home_price: HomePrice;
  lines: Lines;
  loan: Loan;
  monthly_payment: MonthlyPayment;
  monthly_rent: MonthlyRent;
  purchase_effort_pct: PurchaseEffortPct;
  purchase_within: PurchaseWithin;
  rent_effort_pct: RentEffortPct;
  rent_within: RentWithin;
  threshold_pct: ThresholdPct;
}
export interface ScenarioOutcome {
  annual_rent: AnnualRent;
  construction: Construction;
  cost_factor: CostFactor;
  headline: Headline;
  key: Key;
  label: Label;
  land: Land;
  margin_pct: MarginPct;
  price_factor: PriceFactor;
  profit: Profit;
  rental_yield_pct: RentalYieldPct;
  residual_land_value: ResidualLandValue;
  residual_land_value_m2: ResidualLandValueM2;
  revenue: Revenue;
  sales_costs: SalesCosts;
  total_cost: TotalCost;
  /**
   * Only with a land price; without it, null: the headline is the residual land value
   */
  verdict: Verdict | null;
  yield_land: YieldLand;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
