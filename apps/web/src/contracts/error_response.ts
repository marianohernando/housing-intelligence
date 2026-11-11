/**
 * Generated from data/schemas/api/error_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

export type ErrorCode =
  | "INSUFFICIENT_DATA"
  | "INVALID_PROFILE"
  | "OUT_OF_COVERAGE"
  | "SOURCE_DEGRADED"
  | "MODEL_UNAVAILABLE"
  | "CONSENT_REQUIRED"
  | "RATE_LIMITED"
  | "NOT_FOUND";
export type Message = string;

export interface ErrorEnvelope {
  error: ErrorBody;
}
export interface ErrorBody {
  code: ErrorCode;
  details?: Details;
  message: Message;
}
export interface Details {
  [k: string]: unknown | undefined;
}
