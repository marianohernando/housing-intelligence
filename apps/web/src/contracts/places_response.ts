/**
 * Generated from data/schemas/api/places_response.schema.json by scripts/gen-contracts.mjs. Do not edit:
 * change the Pydantic contract in packages/contracts, run `make schemas`, then
 * `npm run -w apps/web contracts`.
 */

export type ContractVersion = string;
/**
 * [lon, lat], WGS84
 *
 * @minItems 2
 * @maxItems 2
 */
export type Coordinates = [unknown, unknown, ...unknown[]];
export type Type = "Point";
export type Id = string;
export type DatasetId = string;
/**
 * Hospitals (D-218, D-239): public network or private, as `dependency` of the place; mutuas count as private
 */
export type Dependency = ("publica" | "privada") | null;
/**
 * Hospitals (D-218): the register's type (general, especializado, ...)
 */
export type Kind = string | null;
export type Unit = string;
export type Value = number;
export type PlaceCategory =
  | "education"
  | "health"
  | "pharmacy"
  | "social"
  | "transport"
  | "commerce"
  | "culture"
  | "sport"
  | "administration"
  | "green"
  | "other";
/**
 * 1 for the register's own coordinates
 */
export type Confidence = number;
/**
 * 'geocoded' when the register's coordinates were missing or wrong (D-216)
 */
export type Coordinates1 = "source" | "geocoded";
/**
 * Health places (D-239): 'publica' for the network of the Servicio Madrileño de Salud (the CM register's dependencia funcional, or a network hospital a private company runs), 'privada' for the rest; mutuas count as private (None elsewhere)
 */
export type Dependency1 = ("publica" | "privada") | null;
/**
 * Rows of the per-zone list of what is missing (GAP-001, D-194).
 */
export type GapRowKey =
  "escuela_infantil" | "colegio" | "centro_salud" | "mayores" | "farmacia" | "vivienda";
/**
 * Rows of the list of what is missing that count this place (same filters)
 */
export type GapRows = GapRowKey[];
/**
 * Hospitals (D-239): who runs it. 'privada' for a private hospital and for a hospital of the public network run by a private company by concession or concierto singular (a versioned list with its official source), 'publica' for the rest of the public ones (None elsewhere)
 */
export type Management = ("publica" | "privada") | null;
export type Municipio = string | null;
/**
 * Institutional name; '<type> (<municipio>)' when no official one is known
 */
export type Name = string;
/**
 * Educational centres only: titularidad of the register (None elsewhere)
 */
export type Ownership = ("publica" | "concertada" | "privada") | null;
export type Seccion = string | null;
export type Subcategory = string;
export type Type1 = "Feature";
export type Features = PlaceFeature[];
export type Page = number;
export type Pages = number;
export type Total = number;
export type Type2 = "FeatureCollection";
export type ApiVersion = string;
export type DataVersion = string | null;
export type GeneratedAt = string;
export type MethodologyVersion = string | null;
export type RequestId = string;
export type Warnings = string[];

/**
 * GET /api/v1/places
 */
export interface PlacesResponse {
  data: PlaceCollection;
  meta?: Meta;
  warnings?: Warnings;
}
export interface PlaceCollection {
  contract_version?: ContractVersion;
  features: Features;
  page: Page;
  pages: Pages;
  total: Total;
  type?: Type2;
}
export interface PlaceFeature {
  geometry: PointGeometry;
  id: Id;
  properties: PlaceProperties;
  type?: Type1;
}
export interface PointGeometry {
  coordinates: Coordinates;
  type?: Type;
}
export interface PlaceProperties {
  capacity?: PlaceCapacity | null;
  category: PlaceCategory;
  confidence: Confidence;
  coordinates?: Coordinates1;
  dependency?: Dependency1;
  gap_rows?: GapRows;
  management?: Management;
  municipio?: Municipio;
  name: Name;
  ownership?: Ownership;
  seccion?: Seccion;
  subcategory: Subcategory;
}
/**
 * How much the place can serve, as its source publishes it (never estimated).
 */
export interface PlaceCapacity {
  dataset_id: DatasetId;
  dependency?: Dependency;
  kind?: Kind;
  unit: Unit;
  value: Value;
}
export interface Meta {
  api_version?: ApiVersion;
  data_version?: DataVersion;
  generated_at?: GeneratedAt;
  methodology_version?: MethodologyVersion;
  request_id?: RequestId;
}
