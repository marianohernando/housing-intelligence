import { describe, expect, it } from "vitest";

import type { PlaceCategory } from "../../contracts/places_response";
import { facilityQueries, groupFacilities } from "../map/facilities";
import { keyPointQueries, type PlaceFeature, pickKeyPoints } from "../map/places";
import { askedFor, FACILITY_CATEGORIES, KEY_POINT_CATEGORIES, zonePlaceQueries } from "../map/zonePlaces";

function place(id: string, category: PlaceCategory, subcategory: string, lon: number, lat: number): PlaceFeature {
  return {
    type: "Feature",
    id,
    geometry: { type: "Point", coordinates: [lon, lat] },
    properties: { name: `Lugar ${id}`, category, subcategory, municipio: "28079", seccion: "ES.28.SEC.2807905001", confidence: 1 },
  };
}

describe("zonePlaceQueries", () => {
  it("asks once per category for «Todos los centros» and the key points together (EMAXCONNSESSION)", () => {
    const queries = zonePlaceQueries();
    expect([...queries.keys()]).toEqual(["education", "health", "pharmacy", "social", "green", "commerce", "sport", "culture", "transport"]);
    expect(FACILITY_CATEGORIES).toEqual(["education", "health", "pharmacy", "social", "green", "commerce", "sport", "culture"]);
    expect(KEY_POINT_CATEGORIES).toEqual(["transport", "health", "education"]);
    // Every subcategory either side asks for, once
    for (const { category, subcategories } of [...facilityQueries(), ...keyPointQueries()]) {
      expect(queries.get(category)).toEqual(expect.arrayContaining(subcategories));
    }
    for (const list of queries.values()) expect(new Set(list).size).toBe(list.length);
  });

  it("adds nothing to what «Todos los centros» already asked: the key points of health and education are among them", () => {
    const queries = zonePlaceQueries();
    for (const { category, subcategories } of facilityQueries()) expect(queries.get(category)).toEqual(subcategories);
  });

  it("gives the same key points and facilities as asking each side apart", () => {
    const keyOnly = [
      place("m1", "transport", "metro", -3.677, 40.451),
      place("c1", "health", "Centro de salud", -3.68, 40.46),
      place("e1", "education", "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", -3.69, 40.47),
    ];
    // What only «Todos los centros» wanted, in the same answers
    const shared = [
      ...keyOnly,
      place("h1", "health", "Hospital especializado", -3.6801, 40.4601),
      place("e2", "education", "CENTRO PRIVADO DE EDUCACIÓN INFANTIL Y PRIMARIA", -3.6901, 40.4701),
      place("f1", "pharmacy", "Farmacia", -3.67, 40.45),
    ];
    expect(pickKeyPoints(shared, [-3.68, 40.46])).toEqual(pickKeyPoints(keyOnly, [-3.68, 40.46]));
    expect(groupFacilities(shared).centro_salud).toEqual(groupFacilities(keyOnly).centro_salud);
  });

  it("keeps from the combined answer only the category and subcategory pairs asked for (M2)", () => {
    const queries = zonePlaceQueries();
    expect(askedFor(queries, place("c1", "health", "Centro de salud", -3.68, 40.46))).toBe(true);
    expect(askedFor(queries, place("f1", "pharmacy", "Farmacia", -3.67, 40.45))).toBe(true);
    // A subcategory asked for health, in a place of another category the request also asked for
    expect(askedFor(queries, place("x1", "social", "Centro de salud", -3.68, 40.46))).toBe(false);
    expect(askedFor(queries, place("x2", "pharmacy", "Hospital general", -3.68, 40.46))).toBe(false);
    // A subcategory nobody asked for, and a category outside the request
    expect(askedFor(queries, place("x3", "health", "Clínica dental", -3.68, 40.46))).toBe(false);
    expect(askedFor(queries, place("x4", "administration", "Ayuntamiento", -3.68, 40.46))).toBe(false);
  });

  it("key points never take a place of another category with the same subcategory", () => {
    const misplaced = place("x", "social", "Centro de salud", -3.68, 40.46);
    expect(pickKeyPoints([misplaced], [-3.68, 40.46])).toEqual([]);
  });
});
