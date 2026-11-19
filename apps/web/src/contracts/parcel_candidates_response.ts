/**
 * Generated from data/schemas/api/parcel_candidates_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

export type Address = string;
export type Lat = number | null;
export type Lon = number | null;
export type PostalCode = string | null;
export type Rc14 = string;
export type Candidates = ParcelCandidate[];
/**
 * The text matches streets but no portal: add the number
 */
export type NeedsNumber = boolean;
export type AccessedAt = string | null;
export type Attribution = string;
export type License = string;
export type LicenseUrl = string | null;
export type Name = string;
export type Publisher = string;
export type SourceId = string;
export type Url = string | null;
export type Sources = ParcelSource[];
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings = string[];

/**
 * GET /api/v1/investors/parcels/candidates (D-250)
 */
export interface ParcelCandidatesResponse {
  data: ParcelCandidates;
  meta?: Meta;
  warnings?: Warnings;
}
/**
 * GET /api/v1/investors/parcels/candidates: portals of Madrid capital with their parcel.
 */
export interface ParcelCandidates {
  candidates: Candidates;
  needs_number: NeedsNumber;
  sources: Sources;
}
/**
 * An address that matches what was typed, with its parcel. Shown for the person to pick:
 * never picked for them.
 */
export interface ParcelCandidate {
  address: Address;
  lat?: Lat;
  lon?: Lon;
  postal_code?: PostalCode;
  rc14: Rc14;
}
/**
 * Who the sheet's data comes from, its licence and how it asks to be cited.
 */
export interface ParcelSource {
  accessed_at?: AccessedAt;
  attribution: Attribution;
  license: License;
  license_url?: LicenseUrl;
  name: Name;
  publisher: Publisher;
  source_id: SourceId;
  url?: Url;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
