import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { ConstraintCheck, Fact, RankedZone, ScenarioState, SearchResult } from "@/contracts/search_response";

import {
  askedLines,
  cityOf,
  comparableFineText,
  householdGaps,
  markedRows,
  nothingMissingText,
  pertinentRows,
  rowPlace,
  unknownRowsText,
} from "../essentials";

// Test fixture published by line A with the contract (data/fixtures/contracts), not demo data.
const FIXTURE = new URL("../../../../../data/fixtures/contracts/search_result.familia_presupuesto.fixture.json", import.meta.url);
const fixture = JSON.parse(readFileSync(FIXTURE, "utf8")) as SearchResult;

const fact = (topic: Fact["topic"], text: string, featureId?: string, kind: Fact["kind"] = "strength"): Fact => ({
  topic,
  text,
  kind,
  confidence: 0.9,
  indicator: featureId ? { feature_id: featureId, label: text, level: "distrito", unit: "min", value: 5, confidence: 0.9 } : null,
});

const check = (constraint_id: string, label: string, value: number, status: ConstraintCheck["status"] = "PASS"): ConstraintCheck => ({
  constraint_id,
  label,
  value,
  status,
  explanation: "",
  confidence: 0.9,
});

// The retired couple of the portada (D-244): «Somos mayores», the family in Ciudad Lineal, 30 min, three priorities
const retired: Pick<ScenarioState, "priorities" | "nearby" | "anchors"> = {
  priorities: ["salud", "sin_escaleras", "transporte"],
  nearby: [],
  anchors: [{ kind: "family", label: "Ciudad Lineal (metro)", lon: -3.63816, lat: 40.43805, max_minutes: 30, days_per_week: 3 }],
};

// Casco Histórico de Barajas for them (POST /search with the local API, 15 nov), as the API sends it
const barajas: Pick<RankedZone, "facts" | "constraints"> = {
  constraints: [check("budget", "Alquiler hasta 1.200 €/mes para 68 m²", 1038), check("commute:0", "Trayecto a Ciudad Lineal (metro) de 30 min como mucho", 27.1)],
  facts: [
    fact("salud", "Centro de salud a unos 9 min andando", "min_a_pie_centro_salud"),
    fact("accesibilidad", "Estación de metro o tren accesible (sin escaleras) a unos 9 min andando", "min_a_pie_estacion_sin_escaleras"),
    fact("transporte", "Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 9 min", "min_a_pie_transporte"),
    fact("trayecto", "27 min en transporte público hasta Ciudad Lineal (metro)"),
    fact("coste", "Alquiler ≈ 1.038 €/mes por 68 m² (15,3 €/m², contratos firmados en 2024; un anuncio de hoy puede pedir más)", "alquiler_m2_mensual"),
  ],
};

describe("what the person asked for, with its minutes (zona.esencial.pedido)", () => {
  it("says the API's facts of what was asked, in their order, without the cost", () => {
    expect(askedLines(barajas, retired).map((l) => l.text)).toEqual([
      "Centro de salud a unos 9 min andando",
      "Estación de metro o tren accesible (sin escaleras) a unos 9 min andando",
      "Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 9 min",
      "27 min en transporte público hasta Ciudad Lineal (metro)",
    ]);
  });

  it("keeps a weak fact of what was asked, with its kind (the family's 39 min to work)", () => {
    const lines = askedLines(fixture.results[0]!, fixture.scenario);
    expect(lines.map((l) => l.topic)).toEqual(["colegios", "transporte", "salud", "trayecto"]);
    expect(lines.at(-1)).toMatchObject({ kind: "weakness", text: expect.stringContaining("hasta Paseo de la Castellana (Azca)") });
  });

  it("says the limits without their % and leaves the walks nobody asked for to «Ver más»", () => {
    const zone = {
      constraints: [],
      facts: [
        fact("trayecto", "Más de 1 h de trayecto hasta Getafe: como mucho 74 %", undefined, "weakness"),
        fact("trayecto", "No llegas a Getafe a las 9:00 en transporte público: el % se queda en la mitad", undefined, "weakness"),
        fact("colegios", "Faltan colegios: como mucho 89 %", undefined, "weakness"),
        fact("salud", "Centro de salud a unos 8 min andando", "min_a_pie_centro_salud"),
        // Context the API adds when fewer than three things were asked (CONTEXT_NEEDS of hi_domain/fit.py)
        fact("salud", "Farmacia a unos 3 min andando", "min_a_pie_farmacia"),
        fact("colegios", "Colegio con primaria a unos 5 min andando", "min_a_pie_colegio"),
      ],
    };
    const lines = askedLines(zone, { priorities: ["salud"], nearby: [], anchors: [] });
    // The limits keep their sentence without the tail about the % (review R-04 of PR #81); the shortage names its rows
    expect(lines.map((l) => l.text)).toEqual([
      "Más de 1 h de trayecto hasta Getafe",
      "No llegas a Getafe a las 9:00 en transporte público",
      "Faltan colegios",
      "Centro de salud a unos 8 min andando",
    ]);
    expect(lines[2]?.rows).toEqual(["colegio"]);
    expect(lines[0]?.rows).toBeUndefined();
    // Any other figure with a «%» is not about the fit and stays
    const green = { constraints: [], facts: [fact("zonas_verdes", "Parque urbano a unos 4 min andando (el 12 % de la zona)")] };
    expect(askedLines(green, { priorities: ["zonas_verdes"], nearby: [], anchors: [] })).toHaveLength(1);
    // The same walk, asked at a walk, is the person's
    const asked = askedLines(zone, { priorities: ["salud"], nearby: [{ need: "farmacia", max_walk_minutes: 10, required: true }], anchors: [] });
    expect(asked.map((l) => l.text)).toContain("Farmacia a unos 3 min andando");
  });

  it("says a walk or a trip the zone meets when no fact says it (the API keeps five facts at most)", () => {
    const zone = {
      constraints: [
        check("near:farmacia", "Farmacia a 10 min andando como mucho", 3.2),
        check("near:mayores", "Centro de mayores a 15 min andando como mucho", 20, "FAIL"),
        check("commute:0", "Trayecto a Ciudad Lineal (metro) de 30 min como mucho", 27.1),
      ],
      facts: [fact("salud", "Centro de salud a unos 9 min andando", "min_a_pie_centro_salud")],
    };
    expect(askedLines(zone, retired).map((l) => l.text)).toEqual([
      "Centro de salud a unos 9 min andando",
      "Farmacia a unos 3 min andando",
      "27 min en transporte público hasta Ciudad Lineal (metro)",
    ]);
    // Said by a fact, never twice
    expect(askedLines(barajas, retired).filter((l) => l.topic === "trayecto")).toHaveLength(1);
    // A condition met without minutes is still said, as the API names it
    const unnamed = { constraints: [{ ...check("near:mayores", "Centro de mayores cerca", 0), value: null }], facts: [] };
    expect(askedLines(unnamed, retired).map((l) => l.text)).toEqual(["Centro de mayores cerca"]);
  });

  it("says nothing of a zone the search did not rank", () => {
    expect(askedLines(null, retired)).toEqual([]);
  });
});

// Barajas for the retired couple (GET /gaps/distrito/2807921, 15 nov)
const barajasGaps = [
  { row: "escuela_infantil", status: "CUBIERTO" },
  { row: "colegio", status: "JUSTO" },
  { row: "centro_salud", status: "CUBIERTO", reliable: false },
  { row: "mayores", status: "CUBIERTO", reliable: false },
  { row: "farmacia", status: "CUBIERTO" },
  { row: "vivienda", status: "SIN_DATOS" },
] as const;

/** A search with only a household: nothing marked */
const home = (household: object): Pick<ScenarioState, "household" | "priorities" | "nearby"> => ({ household, priorities: [], nearby: [] });

describe("what the zone lacks that matters to the home (zona.esencial.falta)", () => {
  it("never tells a retired couple about the colegio, and says what nobody can compare", () => {
    const gaps = householdGaps([...barajasGaps], home({ seniors: true }));
    expect(gaps.short).toEqual([]);
    // The pharmacies have enough, but two rows cannot be compared: no green «No le falta nada» (review R-01 of PR #81)
    expect(gaps.covered).toBe(true);
    expect(gaps.unknown).toEqual(["centro_salud", "mayores"]);
    expect(comparableFineText()).toBe("De lo que podemos comparar, no le falta nada.");
    expect(unknownRowsText(gaps.unknown)).toBe("No sabemos si le faltan centros de salud o centros de mayores.");
    expect(unknownRowsText([])).toBeNull();
    expect(nothingMissingText(true)).toBe("No le falta nada de lo que buscáis.");
    expect(nothingMissingText(false)).toBe("No le falta nada de lo que buscas.");
  });

  it("says it of the district for a barrio, whose rows are the district's", () => {
    expect(nothingMissingText(true, "Barajas")).toBe("En Barajas no falta nada de lo que buscáis.");
    expect(comparableFineText("Barajas")).toBe("En Barajas, de lo que podemos comparar, no falta nada.");
    expect(unknownRowsText(["centro_salud", "mayores"], "Barajas")).toBe("No sabemos si en Barajas faltan centros de salud o centros de mayores.");
  });

  it("counts what the person marks too: a couple without children who marks «Colegios» (review R-02 of PR #81)", () => {
    const couple = { household: { adults: 2 }, priorities: ["colegios" as const], nearby: [] };
    const rows = [
      { row: "colegio", status: "FALTA" },
      { row: "centro_salud", status: "CUBIERTO" },
      { row: "farmacia", status: "CUBIERTO" },
    ] as const;
    expect(householdGaps([...rows], couple).short.map((s) => s.text)).toEqual(["Colegios: hay pocas aulas para tantos niños."]);
    // Unmarked, the colegios are not theirs
    expect(householdGaps([...rows], home({ adults: 2 })).short).toEqual([]);
    expect(markedRows({ priorities: ["colegios", "transporte", "salud"], nearby: [{ need: "mayores", max_walk_minutes: 10, required: false }] })).toEqual([
      "colegio",
      "centro_salud",
      "mayores",
    ]);
    expect(pertinentRows({ household: { adults: 2 }, priorities: ["colegios"], nearby: [{ need: "escuela_infantil", max_walk_minutes: 10, required: true }] })).toEqual([
      "centro_salud",
      "farmacia",
      "colegio",
      "escuela_infantil",
    ]);
  });

  it("says what is short of the home's, FALTA first, in plain words", () => {
    const baby = { minors: 1, minor_ages: [1] };
    const rows = [
      { row: "mayores", status: "FALTA" },
      { row: "escuela_infantil", status: "JUSTO" },
      { row: "colegio", status: "CUBIERTO" },
      { row: "centro_salud", status: "FALTA" },
      { row: "farmacia", status: "CUBIERTO" },
    ] as const;
    expect(householdGaps([...rows], home(baby)).short.map((s) => s.text)).toEqual([
      "Centros de salud: hay pocos para tanta gente.",
      "Escuelas infantiles: van justas para tantos niños.",
    ]);
  });

  it("says where for a barrio, whose rows are its district's", () => {
    const rows = [{ row: "farmacia", status: "JUSTO" }] as const;
    expect(householdGaps([...rows], home({ adults: 2 }), "Barajas").short[0]?.text).toBe("Farmacias en Barajas: van justas para tanta gente.");
  });

  it("never counts a row too small to compare as short, nor as fine", () => {
    const rows = [{ row: "centro_salud", status: "JUSTO", reliable: false }] as const;
    expect(householdGaps([...rows], home({}))).toEqual({ short: [], covered: false, unknown: ["centro_salud"] });
    // Nothing of the home's to compare (no rows, or none of its rows yet): never «No le falta nada»
    expect(householdGaps([], home({ seniors: true })).covered).toBe(false);
    expect(householdGaps([{ row: "colegio", status: "CUBIERTO" }], home({ seniors: true })).covered).toBe(false);
    // Compared together with its neighbours it has a status: the group's
    const grouped = [{ row: "farmacia", status: "FALTA", reliable: false, comparison_group: { names: ["A", "B"], ratio_to_reference: 0.4 } }];
    expect(householdGaps(grouped as never, home({})).short.map((s) => s.row)).toEqual(["farmacia"]);
  });
});

describe("where the zone is", () => {
  it("names the city of a district or a barrio, nothing for a municipio", () => {
    expect(cityOf({ level: "distrito", municipio_name: "Madrid" })).toBe("Madrid");
    expect(cityOf({ level: "barrio", municipio_name: "Madrid" })).toBe("Madrid");
    expect(cityOf({ level: "municipio", municipio_name: "Coslada" })).toBeNull();
  });

  it("names it in a row of the list only when two rows would read the same", () => {
    const centro = { level: "distrito", name: "Centro", municipio_name: "Madrid" };
    expect(rowPlace(centro, ["Centro", "Latina"])).toBeNull();
    expect(rowPlace(centro, ["Centro", "Centro"])).toBe("Madrid");
    expect(rowPlace({ level: "municipio", name: "Centro", municipio_name: "Centro" }, ["Centro", "Centro"])).toBeNull();
  });
});
