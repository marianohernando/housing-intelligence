import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { MatchBand, RankedZone, SearchResult, ZoneMatch } from "@/contracts/search_response";

import { bandRanges, matchBand, matchText, tiedNames, tiedWith, tieText } from "../match";

// Test fixture published by line A with the contract (data/fixtures/contracts), not demo data.
const FIXTURE = new URL("../../../../../data/fixtures/contracts/search_result.familia_presupuesto.fixture.json", import.meta.url);
const fixture = JSON.parse(readFileSync(FIXTURE, "utf8")) as SearchResult;

const zone = (name: string, pct: number | null, passes = true): ZoneMatch => ({
  zone: { level: "distrito", code: name, name },
  match_pct: pct,
  passes_all: passes,
});

const row = (name: string, pct: number, rank: number): RankedZone => ({
  zone: { level: "distrito", code: name, name },
  match_pct: pct,
  rank,
  confidence: 0.9,
  facts: [],
  constraints: [],
});

describe("the band of the % (F5 of fit-0.9)", () => {
  it("derives it from the % with the API's thresholds: 90, 75 and 60", () => {
    const bands = [100, 90, 89, 75, 74, 60, 59, 0].map((pct) => matchBand({ match_pct: pct }));
    expect(bands).toEqual(["muy_bien", "muy_bien", "bien", "bien", "regular", "regular", "poco", "poco"]);
  });

  it("takes the band the API sends (fit-0.9) over its own reading of the %", () => {
    expect(matchBand({ match_pct: 92, match_band: "bien" })).toBe("bien");
    expect(matchBand({ match_pct: 92, match_band: null })).toBe("muy_bien");
  });

  it("gives none to a zone that fails some condition, neither the API's nor from its % (D-243 §4)", () => {
    // Chamartín in «Casi encajan» at 92 %: it reads by what it lacks, never «muy bien»
    expect(matchBand({ match_pct: 92, match_band: null, passes_all: false })).toBeNull();
    expect(matchBand({ match_pct: 92, passes_all: false })).toBeNull();
    expect(matchBand({ match_pct: 92, match_band: "muy_bien", passes_all: false })).toBeNull();
    expect(matchText({ match_pct: 92, passes_all: false })).toBeNull();
    expect(matchBand({ match_pct: 92, match_band: null, passes_all: true })).toBe("muy_bien");
  });

  it("ignores a band it does not know, and gives none without a % (unknown is never «poco»)", () => {
    // The contract's types are not checked at run time
    expect(matchBand({ match_pct: 70, match_band: "excelente" as unknown as MatchBand })).toBe("regular");
    expect(matchBand({ match_pct: null, match_band: "poco" })).toBeNull();
    expect(matchBand({ match_pct: null })).toBeNull();
    expect(matchText({ match_pct: null })).toBeNull();
  });

  it("says it with the figure: «Muy buena opción · 94 %» (resultados.banda.*)", () => {
    expect(matchText({ match_pct: 94 })).toEqual({ band: "Muy buena opción", pct: "94\u00a0%", text: "Muy buena opción · 94\u00a0%" });
    expect([80, 65, 40].map((pct) => matchText({ match_pct: pct })?.text)).toEqual(["Buena opción · 80\u00a0%", "Opción regular · 65\u00a0%", "Poco recomendable · 40\u00a0%"]);
  });

  it("writes the table of «Cómo lo calculamos» from the same thresholds and words", () => {
    expect(bandRanges()).toEqual([
      ["90\u00a0% o más", "Muy buena opción"],
      ["De 75 a 89\u00a0%", "Buena opción"],
      ["De 60 a 74\u00a0%", "Opción regular"],
      ["Menos del 60\u00a0%", "Poco recomendable"],
    ]);
  });

  it("reads line A's fixture: the band it sends for every zone that passes all, none for the rest", () => {
    expect(fixture.results.every((z) => z.match_band != null && matchBand(z) === z.match_band)).toBe(true);
    expect(fixture.near_misses?.every((z) => z.match_band === null)).toBe(true);
    expect(fixture.all_zones.filter((z) => !z.passes_all).every((z) => matchBand(z) === null)).toBe(true);
    expect(fixture.all_zones.filter((z) => z.passes_all).every((z) => matchBand(z) === z.match_band)).toBe(true);
  });

  it("derives the same bands from an API before fit-0.9, which sends no match_band", () => {
    const before = fixture.results.map((zone) => ({ ...zone, match_band: undefined }));
    expect(before.map((z) => matchBand(z))).toEqual(fixture.results.map((z) => z.match_band));
  });
});

describe("zones tied at the same shown % (F5 of fit-0.9)", () => {
  const all = [zone("Puente de Vallecas", 94), zone("Latina", 94), zone("Usera", 93), zone("Moratalaz", 93), zone("Tetuán", 92), zone("Chamartín", 94, false), zone("Getafe", null, false)];

  it("ties a zone with the others that meet everything at its %, never with one that fails or has none", () => {
    expect(tiedWith(all[0]!, all).map((z) => z.zone.name)).toEqual(["Latina"]);
    expect(tiedWith(all[4]!, all)).toEqual([]);
    expect(tiedWith(all[6]!, all)).toEqual([]);
  });

  it("names them in the order of the ranking, then in the order of all_zones beyond it (review R-10)", () => {
    const four = [zone("Puente de Vallecas", 98), zone("Latina", 98), zone("Moratalaz", 98), zone("Ciudad Lineal", 98)];
    const ranking = [row("Latina", 98, 1), row("Moratalaz", 98, 2), row("Ciudad Lineal", 98, 3)];
    expect(tiedNames(four[1]!, four, "zona", ranking)).toBe("Moratalaz, Ciudad Lineal y Puente de Vallecas");
    expect(tieText(four[0]!, four, "zona", ranking)).toBe("Igual de buena que Latina, Moratalaz y Ciudad Lineal (98\u00a0%).");
    // Without the ranking, the order of all_zones
    expect(tiedNames(four[1]!, four)).toBe("Puente de Vallecas, Moratalaz y Ciudad Lineal");
  });

  it("names up to three, then counts them in the scope's word (zona.empate)", () => {
    expect(tieText(all[1]!, all)).toBe("Igual de buena que Puente de Vallecas (94\u00a0%).");
    expect(tieText(all[4]!, all)).toBeNull();
    const four = ["A", "B", "C", "D"].map((n) => zone(n, 100));
    expect(tiedNames(four[0]!, four)).toBe("B, C y D");
    const many = Array.from({ length: 13 }, (_, i) => zone(`B${i}`, 100));
    expect(tieText(many[0]!, many, "barrio")).toBe("Igual de bueno que 12 barrios más (100\u00a0%).");
  });
});
