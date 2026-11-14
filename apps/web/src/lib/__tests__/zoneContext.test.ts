import { describe, expect, it } from "vitest";

import type { FeatureValueRow } from "../features";
import { contextLines, contextRequests, type ContextRows, type ContextZone } from "../zoneContext";

// Test fixture: rows shaped as GET /features/{id}/values gives them; values of 14 nov (D-235)
function row(code: string, value: number | null, period: string): FeatureValueRow {
  return { territory_code: code, admin_unit_id: null, name: null, period_start: period, value, null_reason: value === null ? "SOURCE_MISSING" : null, confidence: 1 };
}

const getafe: ContextZone = { level: "municipio", code: "28065", name: "Getafe" };
const acebeda: ContextZone = { level: "municipio", code: "28001", name: "La Acebeda" };
const centro: ContextZone = { level: "distrito", code: "2807901", name: "Centro" };
const palacio: ContextZone = { level: "barrio", code: "28079011", name: "Palacio" };

const crime = [row("28065", 48.02, "2024-01-01"), row("28079", 68.94, "2024-01-01"), row("28079", 70.1, "2023-01-01"), row("28001", null, "2024-01-01")];
const municipio: ContextRows = {
  crime,
  age: [row("28065", 22.44, "2023-01-01"), row("28001", 24.42, "2023-01-01")],
  income: [row("28065", 19234.4, "2024-01-01"), row("28001", 17120, "2024-01-01")],
};
const madrid: ContextRows = {
  crime,
  age: [row("2807901", 1926.166667, "2025-01-01"), row("28079011", 1928, "2025-01-01")],
  income: [row("2807901", 44958, "2023-01-01"), row("28079011", 48025, "2023-01-01")],
};

const texts = (zone: ContextZone, rows: ContextRows) => contextLines(zone, rows).map((line) => line.text);

describe("contextRequests (D-235)", () => {
  it("asks a municipio for its own three figures", () => {
    expect(contextRequests("municipio")).toEqual([
      { key: "crime", featureId: "infracciones_penales_por_1000_hab", level: "municipio" },
      { key: "age", featureId: "viviendas_desde_2001_pct", level: "municipio" },
      { key: "income", featureId: "renta_per_capita", level: "municipio" },
    ]);
  });

  it("asks Madrid's districts and barrios for the city's offences and their own measures of age and income", () => {
    for (const level of ["distrito", "barrio"] as const) {
      expect(contextRequests(level)).toEqual([
        { key: "crime", featureId: "infracciones_penales_por_1000_hab", level: "municipio" },
        { key: "age", featureId: "ano_medio_construccion_residencial", level },
        { key: "income", featureId: "renta_neta_media_hogar", level },
      ]);
    }
  });
});

describe("contextLines (zona.contexto.*)", () => {
  it("gives a municipio one short line per figure, with its source and year", () => {
    expect(texts(getafe, municipio)).toEqual([
      "Infracciones penales conocidas: 48,0 por cada 1.000 habitantes (Ministerio del Interior, 2024).",
      "Viviendas construidas desde 2001: 22,4 % (censo anual de la Comunidad de Madrid, 2023).",
      "Renta disponible bruta por persona: 19.234 € al año (Instituto de Estadística de la Comunidad de Madrid, 2024).",
    ]);
  });

  it("says what the offences measure, only where there is a figure", () => {
    expect(contextLines(getafe, municipio)[0]?.note).toBe("Mide hechos conocidos por la policía; sube donde hay mucha gente de paso.");
    expect(contextLines(acebeda, municipio)[0]?.note).toBeNull();
  });

  it("says why a municipio under 20.000 inhabitants has no offences: never 0, never left out", () => {
    const expected = "Infracciones penales conocidas: sin dato. El Ministerio solo lo publica para municipios de más de 20.000 habitantes.";
    expect(texts(acebeda, municipio)[0]).toBe(expected);
    // Also without a row of its own
    expect(texts({ ...acebeda, code: "28002" }, municipio)[0]).toBe(expected);
  });

  it("shows the city's latest offences in a district, saying they are the whole city's", () => {
    expect(texts(centro, madrid)).toEqual([
      "Infracciones penales conocidas: 68,9 por cada 1.000 habitantes (Ministerio del Interior, 2024). Dato de toda la ciudad de Madrid; no se publica por distrito.",
      "Año medio de construcción de los edificios de viviendas: 1926 (Catastro, 2025).",
      "Renta media por hogar: 44.958 € al año (INE, 2023).",
    ]);
  });

  it("names the barrio picked inside a district in its own age and income", () => {
    expect(texts(palacio, madrid).slice(1)).toEqual([
      "Año medio de construcción de los edificios de viviendas en Palacio: 1928 (Catastro, 2025).",
      "Renta media por hogar en Palacio: 48.025 € al año (INE, 2023).",
    ]);
  });

  it("never puts the two measures of age or income on one scale: each level has its own label", () => {
    const [, municipioAge, municipioIncome] = texts(getafe, municipio);
    const [, districtAge, districtIncome] = texts(centro, madrid);
    expect(municipioAge).toMatch(/^Viviendas construidas desde 2001/);
    expect(districtAge).toMatch(/^Año medio de construcción/);
    expect(municipioIncome).toMatch(/^Renta disponible bruta por persona/);
    expect(districtIncome).toMatch(/^Renta media por hogar/);
  });

  it("shows no line for a feature the API does not have, and nothing at all without any", () => {
    expect(texts(getafe, { age: municipio.age })).toHaveLength(1);
    expect(contextLines(getafe, {})).toEqual([]);
    // A district without the city's figure, or without its own, says nothing about it
    expect(texts(centro, { crime: [], age: [], income: [] })).toEqual([]);
  });

  it("uses no alarm or wealth words (D-205, D-226, D-235)", () => {
    const all = [...contextLines(getafe, municipio), ...contextLines(centro, madrid), ...contextLines(acebeda, municipio)];
    const said = all.map((line) => `${line.text} ${line.note ?? ""}`).join(" ");
    expect(said).not.toMatch(/peligros|insegur|delincuen|ric[ao]s?\b|pobres?\b|humilde|exclusiv/i);
  });
});
