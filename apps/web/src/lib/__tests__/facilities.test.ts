import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { PlaceCategory } from "../../contracts/places_response";
import {
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
  category: PlaceCategory,
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
    properties: { name, category, subcategory, municipio: "28079", seccion: "ES.28.SEC.2807905001", confidence: 1, ...extra },
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
    expect(sub("mayores")).toEqual(["CENTROS DE DÍA: OTROS", "HOGARES Y CLUBES"]);
  });

  it("ask /places once per category, by zone and subcategory, never a whole layer", () => {
    const queries = facilityQueries();
    expect(queries.map((q) => q.category)).toEqual(["education", "health", "pharmacy", "social"]);
    const health = queries.find((q) => q.category === "health");
    expect(health?.subcategories).toContain("Hospital general");
    // Pharmacies have their own category since D-216
    expect(health?.subcategories).not.toContain("Farmacia");
    expect(queries.find((q) => q.category === "pharmacy")?.subcategories).toEqual(["Farmacia"]);
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
    place("6", "pharmacy", "Farmacia", "Farmacia · AVDA de Alberto Alcocer 22"),
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
    // Residences are not in the row of «Centros de mayores» (hogares, clubes y centros de día)
    expect(groups.mayores.map((f) => f.id)).toEqual(["9"]);
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
    expect(one(groups.mayores, "9")).toMatchObject({ label: "Centro de día", name: "Juan Pablo II Ayuntamiento de Madrid" });
    expect(one(groups.centro_salud, "10")).toMatchObject({ label: "Consultorio", name: null });
  });

  it("leaves the capacity empty until the API gives it: no figure is made up", () => {
    for (const f of Object.values(groups).flat()) expect(f.detail).toBeNull();
  });

  it("counts what the row of «Qué falta» counts (gap_rows), not every school of the subcategory", () => {
    const rows = groupFacilities([
      place("in", "education", "CENTRO PRIVADO DE EDUCACIÓN INFANTIL Y PRIMARIA", "CONCERTADO", -3.68, 40.45, { gap_rows: ["colegio"], ownership: "concertada" }),
      place("out", "education", "CENTRO PRIVADO DE EDUCACIÓN INFANTIL Y PRIMARIA", "PRIVADO", -3.68, 40.45, { gap_rows: [], ownership: "privada" }),
    ]);
    expect(rows.colegio.map((f) => f.id)).toEqual(["in"]);
  });

  it("says when a place was placed by its address (places-1, D-216)", () => {
    const geo = groupFacilities([
      place("g", "health", "Centro de salud", "Centro de salud (Madrid)", -3.68, 40.45, { coordinates: "geocoded", confidence: 0.7 }),
      place("m", "social", "HOGARES Y CLUBES", "ZURBANO", -3.68, 40.45, {
        coordinates: "geocoded",
        capacity: { value: 120, unit: "plazas autorizadas", dataset_id: "cm_centros_atencion_social" },
      }),
    ]);
    expect(geo.centro_salud[0]?.detail).toBe("ubicación aproximada");
    expect(geo.mayores[0]?.detail).toBe("120 plazas autorizadas · ubicación aproximada");
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

  it("names hospitals and their beds from the Catálogo Nacional de Hospitales, «gestión privada» never «privado» (D-218)", () => {
    // Test fixture published by line A with the contract (data/fixtures/contracts), not demo data.
    const url = new URL("../../../../../data/fixtures/contracts/places.hospitales_madrid.fixture.json", import.meta.url);
    const { features } = JSON.parse(readFileSync(url, "utf8")) as { features: PlaceFeature[] };
    const hospitals = groupFacilities(features).hospital;
    const doce = hospitals.find((f) => f.name === "Hospital Universitario 12 de Octubre");
    expect(doce).toMatchObject({ detail: "1.161 camas instaladas · gestión pública", source: "ms_catalogo_nacional_hospitales" });
    const jd = hospitals.find((f) => f.name === "Hospital Universitario Fundacion Jimenez Diaz");
    expect(jd?.detail).toBe("651 camas instaladas · gestión privada");
    for (const f of hospitals) expect(f.detail ?? "").not.toMatch(/privado|(^|· )privada/);
    // Beds only with their source, and never a made-up name: the generic «Hospital general (Madrid)» stays unnamed
    expect(hospitals.some((f) => f.name === null)).toBe(true);
    for (const f of hospitals) expect(f.source !== null).toBe(/camas/.test(f.detail ?? ""));
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
    expect(facilityCountText("mayores", 2, "Tres Cantos")).toBe("2 centros de mayores en Tres Cantos");
    // The list has the consultorios too (pitch/textos_web.md, 12 nov)
    expect(facilityCountText("centro_salud", 7, "Chamartín")).toBe("7 centros de salud y consultorios en Chamartín");
    expect(facilityCountText("centro_salud", 1, "La Acebeda")).toBe("1 centro de salud o consultorio en La Acebeda");
    expect(facilityCountText("centro_salud", 0, "X")).toBe("Ningún centro de salud ni consultorio en X");
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
