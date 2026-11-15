import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { RankedZone, SearchResult, ZoneMatch } from "@/contracts/search_response";

import { matchBand, matchText, rankingRows, tiedNames, tiedWith, tieText } from "../match";

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

  it("ignores a band it does not know, and gives none without a % (unknown is never «poco»)", () => {
    expect(matchBand({ match_pct: 70, match_band: "excelente" })).toBe("regular");
    expect(matchBand({ match_pct: null, match_band: "poco" })).toBeNull();
    expect(matchBand({ match_pct: null })).toBeNull();
    expect(matchText({ match_pct: null })).toBeNull();
  });

  it("says it with the figure: «Encaja muy bien · 94 %» (resultados.banda.*)", () => {
    expect(matchText({ match_pct: 94 })).toEqual({ band: "Encaja muy bien", pct: "94 %", text: "Encaja muy bien · 94 %" });
    expect([80, 65, 40].map((pct) => matchText({ match_pct: pct })?.text)).toEqual(["Encaja bien · 80 %", "Encaja regular · 65 %", "Encaja poco · 40 %"]);
  });

  it("gives every zone that fits in line A's fixture a band, from the API deployed before fit-0.9", () => {
    expect(fixture.results.every((z) => matchText(z) !== null)).toBe(true);
  });
});

describe("zones tied at the same shown % (F5 of fit-0.9)", () => {
  const all = [zone("Puente de Vallecas", 94), zone("Latina", 94), zone("Usera", 93), zone("Moratalaz", 93), zone("Tetuán", 92), zone("Chamartín", 94, false), zone("Getafe", null, false)];

  it("ties a zone with the others that meet everything at its %, never with one that fails or has none", () => {
    expect(tiedWith(all[0]!, all).map((z) => z.zone.name)).toEqual(["Latina"]);
    expect(tiedWith(all[4]!, all)).toEqual([]);
    expect(tiedWith(all[6]!, all)).toEqual([]);
  });

  it("names up to three, then counts them in the scope's word (zona.empate)", () => {
    expect(tieText(all[1]!, all)).toBe("Empata al 94 % con Puente de Vallecas.");
    expect(tieText(all[4]!, all)).toBeNull();
    const four = ["A", "B", "C", "D"].map((n) => zone(n, 100));
    expect(tiedNames(four[0]!, four)).toBe("B, C y D");
    const many = Array.from({ length: 13 }, (_, i) => zone(`B${i}`, 100));
    expect(tieText(many[0]!, many, "barrio")).toBe("Empata al 100 % con 12 barrios más.");
  });

  it("marks the runs of rows in view with the same %, headed «Empatan al 94 %»", () => {
    const shown = [row("Puente de Vallecas", 94, 1), row("Latina", 94, 2), row("Usera", 93, 3), row("Moratalaz", 93, 4), row("Tetuán", 92, 5)];
    const rows = rankingRows(shown, all);
    expect(rows.map((r) => r.tie)).toEqual([
      { first: true, last: false, label: "Empatan al 94 %" },
      { first: false, last: true, label: "Empatan al 94 %" },
      { first: true, last: false, label: "Empatan al 93 %" },
      { first: false, last: true, label: "Empatan al 93 %" },
      null,
    ]);
  });

  it("counts every tied zone when the run goes on beyond the rows in view", () => {
    const crowd = Array.from({ length: 45 }, (_, i) => zone(`Z${i}`, 100));
    const shown = crowd.slice(0, 5).map((z, i) => row(z.zone.name, 100, i + 1));
    expect(rankingRows(shown, crowd)[0]?.tie?.label).toBe("Empatan al 100 % (45 zonas)");
    // A single row in view tied with zones beyond the list has no run: its card says it
    expect(rankingRows([row("Z0", 100, 1)], crowd)[0]?.tie).toBeNull();
  });
});
