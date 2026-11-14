import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { BarrioSearchResult } from "@/contracts/barrio_search_response";

import { barrioRows, barriosText, FACTS_PER_BARRIO } from "../barrios";

// Test fixture published by line A with the contract (data/fixtures/contracts), not demo data:
// San Blas-Canillejas with the demo case, fit-0.7 (D-232)
const FIXTURE = new URL("../../../../../data/fixtures/contracts/barrio_search_result.san_blas.fixture.json", import.meta.url);
const sanBlas = JSON.parse(readFileSync(FIXTURE, "utf8")) as BarrioSearchResult;

describe("barrioRows (D-232)", () => {
  it("keeps the API's order of the barrios that fit, with their outline id, % and first facts", () => {
    const { fits } = barrioRows(sanBlas);
    expect(fits.map((b) => [b.name, b.pct])).toEqual([
      ["Canillejas", 97],
      ["Arcos", 97],
      ["Simancas", 97],
      ["Rosas", 96],
      ["Amposta", 96],
      ["El Salvador", 95],
      ["Hellín", 93],
    ]);
    expect(fits[2]).toMatchObject({ id: "ES.28.BAR.28079201", code: "28079201", fails: null });
    expect(fits[0]?.facts).toEqual(["Colegio con primaria a unos 7 min andando", "Parada de transporte público a unos 3 min andando"]);
    expect(fits.every((b) => b.facts.length <= FACTS_PER_BARRIO)).toBe(true);
  });

  it("names the condition a near miss fails, from the API's labels", () => {
    const { near } = barrioRows(sanBlas);
    expect(near).toHaveLength(1);
    expect(near[0]).toMatchObject({ name: "Rejas", pct: 55, fails: ["Colegio con primaria a 10 min andando como mucho"] });
  });

  it("leaves out a failed condition without a name, and works without near misses", () => {
    const [rejas] = sanBlas.near_misses ?? [];
    if (!rejas) throw new Error("fixture without near misses");
    const unnamed = { ...rejas, failed_constraints: ["no_label"], constraints: [] };
    expect(barrioRows({ results: [], near_misses: [unnamed] }).near[0]?.fails).toEqual([]);
    expect(barrioRows({ results: sanBlas.results }).near).toEqual([]);
  });

  it("has no outline to show when the API gives no admin unit", () => {
    const [first] = sanBlas.results;
    if (!first) throw new Error("fixture without results");
    const row = barrioRows({ results: [{ ...first, zone: { ...first.zone, admin_unit_id: null } }] }).fits[0];
    expect(row?.id).toBeNull();
  });
});

describe("barriosText (barrios.encajan.resumen)", () => {
  it("says how many of the district's barrios fit", () => {
    expect(barriosText(sanBlas.reality_check)).toBe("7 de sus 8 barrios encajan con tu búsqueda.");
    expect(barriosText({ zones_passing: 1, zones_evaluated: 8 })).toBe("1 de sus 8 barrios encaja con tu búsqueda.");
    expect(barriosText({ zones_passing: 6, zones_evaluated: 6 })).toBe("Sus 6 barrios encajan con tu búsqueda.");
    expect(barriosText({ zones_passing: 0, zones_evaluated: 6 })).toBe("Ninguno de sus 6 barrios cumple todo lo que pides.");
  });
});

describe("the price of each barrio (D-234)", () => {
  it("goes beside its %, as a purchase price when buying and a monthly rent otherwise", () => {
    const first = sanBlas.results[0]!;
    const cost = first.estimated_cost_eur ?? 0;
    const amount = new Intl.NumberFormat("es-ES", { useGrouping: "always" }).format(cost);
    expect(barrioRows(sanBlas).fits[0]?.price?.short).toBe(`≈ ${amount} €/mes`);
    const buying = { ...sanBlas, scenario: { ...sanBlas.scenario, budget: { kind: "buy" as const, amount_eur: 400_000 } } };
    const estimate = { ...first, estimated_cost_eur: 348_000, estimated_cost_confidence: 0.5 };
    const row = barrioRows({ ...buying, results: [estimate] }).fits[0];
    expect([row?.price?.short, row?.price?.confidence?.label]).toEqual(["≈ 348.000 €", "Dato aproximado"]);
    expect(barrioRows({ results: [{ ...first, estimated_cost_eur: null }] }).fits[0]?.price).toBeNull();
  });
});
