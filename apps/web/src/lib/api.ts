/**
 * Typed client of the PUBLIC API (docs/04_technical_architecture/31_public_api_routes.md).
 * Response types are generated from the JSON Schemas (src/contracts), never written by hand.
 */
import type { DatasetListResponse } from "@/contracts/dataset_list_response";
import type { GapRowMapResponse } from "@/contracts/gap_row_map_response";
import type { PlaceCategory as ContractPlaceCategory, PlacesResponse } from "@/contracts/places_response";
import type { ScenarioState } from "@/contracts/scenario_state";
import type { SearchResponse } from "@/contracts/search_response";
import type { GapRowKey, ZoneGapListResponse } from "@/contracts/zone_gap_list_response";
import type { Envelope } from "@/lib/envelope";
import { type AdminLevel, adminUnitsUrl, DEFAULT_API_URL, type Lineage } from "@/lib/geo";
import type { PlaceFeature } from "@/lib/map/places";
import type { AdminFeature } from "@/lib/map/zones";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL;

/** Levels with a «Qué falta» list: municipios, Madrid's 21 districts and census sections. */
export type GapLevel = "municipio" | "distrito" | "seccion_censal";

/** Place categories of /api/v1/places (places-1). */
export type PlaceCategory = ContractPlaceCategory;

/** Routes that predate the PUBLIC contracts: their shapes live in lib/geo.ts and lib/map. */
export type AdminUnitsResponse = Envelope<{ type: "FeatureCollection"; features: AdminFeature[]; lineage: Lineage }>;


/**
 * Places of one category. The map always asks by zone, never for a whole layer; without a zone,
 * only a few subcategories (the stations for «Trabajo en»).
 */
export interface PlacesQuery {
  category: PlaceCategory;
  adminUnitId?: string;
  subcategories?: readonly string[];
}

function placesPath({ category, adminUnitId, subcategories = [] }: PlacesQuery, page: number): string {
  const params = new URLSearchParams({ category });
  if (adminUnitId) params.set("admin_unit_id", adminUnitId);
  for (const subcategory of subcategories) params.append("subcategory", subcategory);
  if (page > 1) params.set("page", String(page));
  return `/api/v1/places?${params.toString()}`;
}

export type FetchLike = (input: string, init?: RequestInit) => Promise<Response>;

/**
 * A failed call. `code` comes from the API (`ErrorCode`), or is NETWORK when the API cannot be
 * reached, ABORTED when the caller cancelled it, VALIDATION for a rejected request and
 * HTTP_<status> when the body says nothing.
 */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface ErrorBody {
  detail?: { code?: string; message?: string } | unknown[];
}

async function toApiError(response: Response): Promise<ApiError> {
  const body = (await response.json().catch(() => null)) as ErrorBody | null;
  const detail = body?.detail;
  if (Array.isArray(detail)) return new ApiError(response.status, "VALIDATION", "Petición no válida");
  if (detail?.code) return new ApiError(response.status, detail.code, detail.message ?? detail.code);
  return new ApiError(response.status, `HTTP_${response.status}`, `HTTP ${response.status}`);
}

export function createApi(base: string = API_URL, fetchImpl: FetchLike = fetch) {
  async function call<T>(path: string, init?: RequestInit): Promise<T> {
    let response: Response;
    try {
      response = await fetchImpl(new URL(path, base).toString(), init);
    } catch (exc) {
      const aborted = init?.signal?.aborted || (exc as Error).name === "AbortError";
      throw new ApiError(0, aborted ? "ABORTED" : "NETWORK", (exc as Error).message);
    }
    if (!response.ok) throw await toApiError(response);
    return (await response.json()) as T;
  }

  /** GET /api/v1/places: a zone's facilities of one category as points, following every page. */
  async function places(query: PlacesQuery): Promise<PlaceFeature[]> {
    const first = await call<PlacesResponse>(placesPath(query, 1));
    const rest = await Promise.all(
      Array.from({ length: first.data.pages - 1 }, (_, i) => call<PlacesResponse>(placesPath(query, i + 2))),
    );
    // The schema types the point as a tuple of unknowns (tuple[float, float] in Pydantic): it is GeoJSON [lon, lat]
    return [first, ...rest].flatMap((body) => body.data.features) as unknown as PlaceFeature[];
  }

  return {
    /** GET /api/v1/gaps/{level}/{code}: what a zone is missing against the region. */
    zoneGaps(level: GapLevel, code: string) {
      return call<ZoneGapListResponse>(`/api/v1/gaps/${level}/${encodeURIComponent(code)}`);
    },
    /** GET /api/v1/gaps?level=&row=: one row of «Qué falta» for every zone of a level (the map). */
    gapRowMap(level: "municipio" | "distrito", row: GapRowKey) {
      return call<GapRowMapResponse>(`/api/v1/gaps?${new URLSearchParams({ level, row }).toString()}`);
    },
    /** GET /api/v1/datasets: every dataset behind the product (footer counter and provenance). */
    datasets({ cmOnly = false }: { cmOnly?: boolean } = {}) {
      return call<DatasetListResponse>(`/api/v1/datasets${cmOnly ? "?cm_only=true" : ""}`);
    },
    /** GET /api/v1/geo/admin-units: zone outlines, simplified by `simplifyM` metres, optionally one unit's children. */
    adminUnits(level: AdminLevel, simplifyM: number, parent?: string) {
      return call<AdminUnitsResponse>(adminUnitsUrl(base, level, simplifyM, parent));
    },
    places,
    /** POST /api/v1/search: ranked zones, the choropleth and the Reality Check; `signal` cancels it. */
    search(scenario: ScenarioState, { signal }: { signal?: AbortSignal } = {}) {
      return call<SearchResponse>("/api/v1/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(scenario),
        signal,
      });
    },
  };
}

export type Api = ReturnType<typeof createApi>;
