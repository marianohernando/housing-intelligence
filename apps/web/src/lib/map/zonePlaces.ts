/**
 * What the zone screen asks /api/v1/places for (pure, unit tested). «Todos los centros» and the
 * key points of the 3D view want places of the same categories, so each category is asked once per
 * zone with the subcategories of both, and each side keeps its own: every request can hold a
 * database connection, and the pooler admits 15 clients (incident EMAXCONNSESSION, 12 nov).
 */
import type { PlaceCategory } from "@/lib/api";

import { facilityQueries } from "./facilities";
import { keyPointQueries } from "./places";

/** The subcategories asked for each category: those of «Todos los centros», then the key points'. */
export function zonePlaceQueries(): ReadonlyMap<PlaceCategory, readonly string[]> {
  const merged = new Map<PlaceCategory, string[]>();
  for (const { category, subcategories } of [...facilityQueries(), ...keyPointQueries()]) {
    const list = merged.get(category) ?? [];
    for (const subcategory of subcategories) if (!list.includes(subcategory)) list.push(subcategory);
    merged.set(category, list);
  }
  return merged;
}

const categories = (queries: { category: PlaceCategory }[]) => [...new Set(queries.map((q) => q.category))];

/** Categories of «Todos los centros» and of the key points. */
export const FACILITY_CATEGORIES: readonly PlaceCategory[] = categories(facilityQueries());
export const KEY_POINT_CATEGORIES: readonly PlaceCategory[] = categories(keyPointQueries());
