/**
 * Capability flags (CLAUDE.md §17): a capability that is not ready shows as «Muy pronto» and
 * never calls the API, instead of ending in an error. They are read at build time.
 */
import type { ScenarioState } from "@/contracts/scenario_state";
import type { SearchResponse } from "@/contracts/search_response";

export function flagOn(value: string | undefined): boolean {
  return value === "true" || value === "1";
}

/**
 * The search (POST /api/v1/search, CORE-003 of line A): off until the API has it. Build with
 * NEXT_PUBLIC_FEATURE_SEARCH=true to turn it on.
 */
export const SEARCH_ENABLED = flagOn(process.env.NEXT_PUBLIC_FEATURE_SEARCH);

/** Runs the search only when the capability is on; off, the API is never called. `signal` cancels it. */
export async function runSearch(
  api: { search: (scenario: ScenarioState, init?: { signal?: AbortSignal }) => Promise<SearchResponse> },
  scenario: ScenarioState,
  enabled: boolean = SEARCH_ENABLED,
  signal?: AbortSignal,
): Promise<SearchResponse | null> {
  return enabled ? api.search(scenario, { signal }) : null;
}
