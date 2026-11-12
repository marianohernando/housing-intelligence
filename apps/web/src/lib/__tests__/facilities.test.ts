import { describe, expect, it } from "vitest";

import {
  CONTRACT_QUERIES,
  type Facility,
  FACILITY_TYPES,
  facilitiesGeoJSON,
  facilityCountText,
  facilityQueries,
  groupFacilities,
} from "../map/facilities";
import type { PlaceFeature } from "../map/places";

function place(
  id: string,
  category: string,
  subcategory: string,
  name: string,
  lon = -3.68,
  lat = 40.45,
  extra: Partial<PlaceFeature["properties"]> = {},
): PlaceFeature {
  return {
    type: "Feature",
    id,
    geometry: { type: "Point", coordinates: [lon, lat] },
    properties: { name, category, subcategory, municipio: "28079", seccion: "ES.28.SEC.2807905001", ...extra },
  };
}

const CATALOG_COLEGIO = [
  "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA",
  "COLEGIO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA",
  "COLEGIO DE EDUCACIÓN PRIMARIA",
  "CENTRO PRIVADO DE EDUCACIÓN INFANTIL Y PRIMARIA",
  "CENTRO PRIVADO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA",
  "CENTRO PRIVADO DE EDUCACIÓN PRIMARIA",
  "CENTRO PRIVADO DE EDUCACIÓN PRIMARIA Y SECUNDARIA",
];

describe("facility types", () => {
  it("count the same places as the rows of «Qué falta» (data/catalog/features)", () => {
    const sub = (key: string) => FACILITY_TYPES.find((t) => t.key === key)?.classes.map((c) => c.subcategory);
    expect(sub("colegio")).toEqual(CATALOG_COLEGIO);
    expect(sub("escuela_infantil")).toEqual(["ESCUELA INFANTIL", "ESCUELA  INFANTIL-CASA DE NIÑOS", "ESCUELA INFANTIL PRIVADA", "CENTRO PRIVADO DE EDUCACIÓN INFANTIL"]);
    expect(sub("centro_salud")).toEqual(["Centro de salud", "Consultorio de atención primaria"]);
    expect(sub("farmacia")).toEqual(["Farmacia"]);
  });

  it("ask /places once per category, by zone and subcategory, never a whole layer", () => {
    const queries = facilityQueries();
    expect(queries.map((q) => q.category)).toEqual(["education", "health", "social"]);
    const health = queries.find((q) => q.category === "health");
    expect(health?.subcategories).toContain("Hospital general");
    // Pharmacies: in health before places-1; their own category after it (D-216), asked only then
    expect(health?.subcategories).toContain("Farmacia");
    expect(CONTRACT_QUERIES["places-1"]).toEqual([{ category: "pharmacy", subcategories: ["Farmacia"] }]);
    // The «Centro Polivalente» of health are the social records repeated (FASE_PRUEBAS, T1): left out
    expect(health?.subcategories).not.toContain("Centro Polivalente");
    for (const q of queries) expect(q.subcategories.length).toBeGreaterThan(0);
  });
});

describe("groupFacilities", () => {
  const places = [
    place("1", "education", "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", "PADRE POVEDA"),
    place("2", "education", "CENTRO PRIVADO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA", "CIUDAD JARDIN"),
    place("3", "education", "INSTITUTO DE EDUCACIÓN SECUNDARIA", "RAMIRO DE MAEZTU"),
    place("4", "health", "Hospital general", "Hospital general (Madrid)"),
    place("5", "health", "Hospital especializado", "Hospital especializado (Madrid)"),
    place("6", "health", "Farmacia", "Farmacia · AVDA de Alberto Alcocer 22"),
    place("7", "health", "Centro Polivalente", "Centro Polivalente (Madrid)"),
    place("8", "social", "RESIDENCIAS DE PERSONAS MAYORES MIXTA", "SANITAS RESIDENCIAL EL VISO, RESIDENCIA DE PERSONAS MAYORES"),
    place("9", "social", "CENTROS DE DÍA: OTROS", "JUAN PABLO II AYUNTAMIENTO DE MADRID, CENTRO DE DIA"),
    place("10", "health", "Consultorio de atención primaria", "Consultorio de atención primaria (Madrid)"),
  ];
  const groups = groupFacilities(places);

  it("puts each place in its type, and leaves out what no type counts", () => {
    expect(groups.colegio.map((f) => f.id)).toEqual(["2", "1"]);
    expect(groups.hospital).toHaveLength(2);
    expect(groups.farmacia).toHaveLength(1);
    expect(groups.mayores).toHaveLength(2);
    expect(groups.centro_salud).toHaveLength(1);
    expect(groups.escuela_infantil).toHaveLength(0);
    const all = Object.values(groups).flat();
    expect(all.map((f) => f.id)).not.toContain("3");
    expect(all.map((f) => f.id)).not.toContain("7");
  });

  it("names each place in plain words, and never invents a name the source does not give", () => {
    const one = (list: Facility[], id: string) => list.find((f) => f.id === id);
    expect(one(groups.colegio, "1")).toMatchObject({ label: "Colegio público", name: "Padre Poveda" });
    expect(one(groups.colegio, "2")).toMatchObject({ label: "Colegio privado o concertado", name: "Ciudad Jardin" });
    expect(one(groups.hospital, "4")).toMatchObject({ label: "Hospital", name: null });
    expect(one(groups.hospital, "5")).toMatchObject({ label: "Hospital especializado", name: null });
    expect(one(groups.farmacia, "6")).toMatchObject({ label: "Farmacia", name: "Avenida de Alberto Alcocer 22" });
    expect(one(groups.mayores, "8")).toMatchObject({ label: "Residencia", name: "Sanitas Residencial el Viso" });
    expect(one(groups.mayores, "9")).toMatchObject({ label: "Centro de día", name: "Juan Pablo II Ayuntamiento de Madrid" });
    expect(one(groups.centro_salud, "10")).toMatchObject({ label: "Consultorio", name: null });
  });

  it("leaves the capacity empty until the API gives it: no figure is made up", () => {
    for (const f of Object.values(groups).flat()) expect(f.detail).toBeNull();
  });

  it("shows the capacity and the ownership when the API gives them (places-1, line A)", () => {
    // Test fixture: the figures are made up for the test only
    const typed = groupFacilities([
      place("h", "health", "Hospital general", "HOSPITAL UNIVERSITARIO LA PAZ", -3.69, 40.48, {
        capacity: { value: 1300, unit: "camas", dataset_id: "cm_hospitales" },
      }),
      place("c", "education", "CENTRO PRIVADO DE EDUCACIÓN INFANTIL Y PRIMARIA", "AMOROS", -3.68, 40.45, { ownership: "concertada" }),
      place("p", "education", "CENTRO PRIVADO DE EDUCACIÓN PRIMARIA", "OTRO", -3.68, 40.45, { ownership: "privada" }),
      place("f", "pharmacy", "Farmacia", "Farmacia · CALLE de Serrano 1"),
    ]);
    expect(typed.hospital[0]).toMatchObject({ name: "Hospital Universitario la Paz", detail: "1.300 camas" });
    expect(typed.colegio.map((f) => f.label)).toEqual(["Colegio concertado", "Colegio privado"]);
    expect(typed.farmacia[0]).toMatchObject({ name: "Calle de Serrano 1" });
  });

  it("sorts named places by name, after them the ones without a name", () => {
    const sorted = groupFacilities([
      place("a", "health", "Hospital general", "Hospital general (Madrid)"),
      place("b", "social", "HOGARES Y CLUBES", "ZURBANO"),
      place("c", "social", "HOGARES Y CLUBES", "ÁLAMOS"),
    ]);
    expect(sorted.mayores.map((f) => f.name)).toEqual(["Álamos", "Zurbano"]);
  });
});

describe("facilityCountText", () => {
  it("says how many there are, in singular, plural and none", () => {
    expect(facilityCountText("colegio", 23, "Chamartín")).toBe("23 colegios con primaria en Chamartín");
    expect(facilityCountText("colegio", 1, "Chamartín")).toBe("1 colegio con primaria en Chamartín");
    expect(facilityCountText("hospital", 0, "La Acebeda")).toBe("Ningún hospital en La Acebeda");
    expect(facilityCountText("farmacia", 0, "La Acebeda")).toBe("Ninguna farmacia en La Acebeda");
    expect(facilityCountText("escuela_infantil", 1234, "Madrid")).toBe("1.234 escuelas infantiles en Madrid");
    expect(facilityCountText("mayores", 2, "Tres Cantos")).toBe("2 residencias y centros de mayores en Tres Cantos");
  });
});

describe("facilitiesGeoJSON", () => {
  it("makes points for the clustered layer, with what the map label shows", () => {
    const { colegio } = groupFacilities([place("1", "education", "COLEGIO DE EDUCACIÓN PRIMARIA", "LUIS BELLO", -3.67, 40.46)]);
    const geo = facilitiesGeoJSON(colegio);
    expect(geo.features).toHaveLength(1);
    expect(geo.features[0]).toMatchObject({
      type: "Feature",
      id: "1",
      geometry: { type: "Point", coordinates: [-3.67, 40.46] },
      properties: { id: "1", type: "colegio" },
    });
  });
});
