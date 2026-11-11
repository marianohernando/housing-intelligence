/**
 * Typed client of the PUBLIC API (docs/04_technical_architecture/31_public_api_routes.md).
 * Response types are generated from the JSON Schemas (src/contracts), never written by hand.
 */
import type { DatasetListResponse } from "@/contracts/dataset_list_response";
import type { ScenarioState } from "@/contracts/scenario_state";
import type { SearchResponse } from "@/contracts/search_response";
import type { ZoneGapListResponse } from "@/contracts/zone_gap_list_response";
import type { Envelope } from "@/lib/envelope";
import { type AdminLevel, adminUnitsUrl, DEFAULT_API_URL, type Lineage } from "@/lib/geo";
import type { PlaceFeature } from "@/lib/map/places";
import type { AdminFeature } from "@/lib/map/zones";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL;

/** Levels with a «Qué falta» list: municipios, Madrid's 21 districts and census sections. */
export type GapLevel = "municipio" | "distrito" | "seccion_censal";

/** Place categories the map uses for a zone's key points (PlaceCategory in the API). */
export type PlaceCategory = "transport" | "health" | "education" | "social";

/** Routes that predate the PUBLIC contracts: their shapes live in lib/geo.ts and lib/map. */
export type AdminUnitsResponse = Envelope<{ type: "FeatureCollection"; features: AdminFeature[]; lineage: Lineage }>;
export type PlacesResponse = Envelope<{ type: "FeatureCollection"; features: PlaceFeature[] }>;

export type FetchLike = (input: string, init?: RequestInit) => Promise<Response>;

/**
 * A failed call. `code` comes from the API (`ErrorCode`), or is NETWORK when the API cannot be
 * reached, VALIDATION for a rejected request and HTTP_<status> when the body says nothing.
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
      throw new ApiError(0, "NETWORK", (exc as Error).message);
    }
    if (!response.ok) throw await toApiError(response);
    return (await response.json()) as T;
  }

  return {
    /** GET /api/v1/gaps/{level}/{code}: what a zone is missing against the region. */
    zoneGaps(level: GapLevel, code: string) {
      return call<ZoneGapListResponse>(`/api/v1/gaps/${level}/${encodeURIComponent(code)}`);
    },
    /** GET /api/v1/datasets: every dataset behind the product (footer counter and provenance). */
    datasets({ cmOnly = false }: { cmOnly?: boolean } = {}) {
      return call<DatasetListResponse>(`/api/v1/datasets${cmOnly ? "?cm_only=true" : ""}`);
    },
    /** GET /api/v1/geo/admin-units: zone outlines, simplified by `simplifyM` metres. */
    adminUnits(level: AdminLevel, simplifyM: number) {
      return call<AdminUnitsResponse>(adminUnitsUrl(base, level, simplifyM));
    },
    /** GET /api/v1/places: facilities of one category as points. */
    places(category: PlaceCategory) {
      return call<PlacesResponse>(`/api/v1/places?category=${category}`);
    },
    /** POST /api/v1/search: ranked zones, the choropleth and the Reality Check. */
    search(scenario: ScenarioState) {
      return call<SearchResponse>("/api/v1/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(scenario),
      });
    },
  };
}

export type Api = ReturnType<typeof createApi>;
