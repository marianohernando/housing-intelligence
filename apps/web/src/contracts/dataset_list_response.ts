/**
 * Generated from data/schemas/api/dataset_list_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

/**
 * Published in the CM open data portal
 */
export type CmOpenDataCount = number;
export type DatasetId = string;
/**
 * Published in the Comunidad de Madrid open data portal (counts for DATAMAD)
 */
export type IsCmOpenData = boolean;
export type License = string | null;
export type Name = string;
export type Publisher = string;
/**
 * Portal page (CM portal when it exists)
 */
export type Url = string | null;
/**
 * dataset_version label used
 */
export type Version = string | null;
export type Datasets = DatasetRef[];
export type Total = number;
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings = string[];

/**
 * GET /api/v1/datasets
 */
export interface DatasetListResponse {
  data: DatasetList;
  meta?: Meta;
  warnings?: Warnings;
}
/**
 * Datasets behind the product (GET /api/v1/datasets): the footer counter and provenance.
 */
export interface DatasetList {
  cm_open_data_count: CmOpenDataCount;
  datasets: Datasets;
  total: Total;
}
/**
 * Provenance of a result: the dataset, who publishes it and where to open it.
 */
export interface DatasetRef {
  dataset_id: DatasetId;
  is_cm_open_data: IsCmOpenData;
  license?: License;
  name: Name;
  publisher: Publisher;
  url?: Url;
  version?: Version;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
