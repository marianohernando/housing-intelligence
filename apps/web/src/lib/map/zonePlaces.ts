/**
 * What the zone screen asks /api/v1/places for (pure, unit tested). «Todos los centros» and the
 * key points of the 3D view want places of the same categories, so the zone is asked once, with every
 * category and the subcategories of both (/places takes several categories since 12 nov), and each
 * side keeps its own: every request can hold a database connection, and the pooler admits 15 clients
 * (incident EMAXCONNSESSION, 12 nov).
 */
import type { PlaceCategory } from "@/lib/api";

import { facilityQueries } from "./facilities";
import { keyPointQueries, type PlaceFeature } from "./places";

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

/**
 * A place one of the queries asked for: its category with one of that category's subcategories.
 * The combined request filters categories and subcategories apart, so a subcategory asked for one
 * category also brings the places of another category that share its name (review of PR #19, M2).
 */
export function askedFor(queries: ReadonlyMap<PlaceCategory, readonly string[]>, place: PlaceFeature): boolean {
  const { category, subcategory } = place.properties;
  return queries.get(category)?.includes(subcategory) ?? false;
}

const categories = (queries: { category: PlaceCategory }[]) => [...new Set(queries.map((q) => q.category))];

/** Categories of «Todos los centros» and of the key points. */
export const FACILITY_CATEGORIES: readonly PlaceCategory[] = categories(facilityQueries());
export const KEY_POINT_CATEGORIES: readonly PlaceCategory[] = categories(keyPointQueries());
