/** Response envelope mirrored from docs/04_technical_architecture/09_api_contract_conventions.md. */

export const API_VERSION = "v1";

export interface Meta {
  request_id: string;
  generated_at: string;
  api_version: string;
  methodology_version: string | null;
  data_version: string | null;
}

export interface Envelope<T> {
  data: T;
  meta: Meta;
  warnings: string[];
}

export function buildMeta(now: Date = new Date(), requestId: string = crypto.randomUUID()): Meta {
  return {
    request_id: requestId,
    generated_at: now.toISOString(),
    api_version: API_VERSION,
    methodology_version: null,
    data_version: null,
  };
}

export function envelope<T>(data: T, warnings: string[] = []): Envelope<T> {
  return { data, meta: buildMeta(), warnings };
}
