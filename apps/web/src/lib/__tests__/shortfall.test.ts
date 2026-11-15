import { describe, expect, it } from "vitest";

import type { ConstraintCheck } from "@/contracts/search_response";

import { FAILS_UNNAMED, joinShortfalls, nearMissText, shortfallOf, shortfalls } from "../shortfall";

const check = (id: string, label: string, value: number | null, threshold: number | null, unit: string, status: "PASS" | "FAIL" = "FAIL"): ConstraintCheck => ({
  constraint_id: id,
  label,
  status,
  value,
  threshold,
  unit,
  confidence: 0.9,
  explanation: "",
});

const budgetBuy = (value: number) => check("budget", "Compra hasta 400.000 €", value, 400_000, "€");
const budgetRent = (value: number) => check("budget", "Alquiler hasta 1.500 €/mes para 77 m²", value, 1_500, "€/mes");
const commute = (value: number | null, i = 0) => check(`commute:${i}`, "Trayecto a Paseo de la Castellana (Azca) de 30 min como mucho", value, 30, "min");
const school = (value: number | null) => check("near:colegio", "Colegio con primaria a 10 min andando como mucho", value, 10, "min");

describe("what a near miss lacks (F5 of fit-0.9: «Casi encajan» without a %)", () => {
  it("says how much a zone goes over the budget, rounded so the «≈» is honest (resultados.casi.presupuesto)", () => {
    // Tetuán, buying with 400.000 €: 411.000 € (CN-compra of the formula's bench)
    expect(shortfallOf(budgetBuy(411_000))).toEqual({ text: "Se pasa ≈ 11.000 € de tu presupuesto", aria: "Se pasa unos 11.000 € de tu presupuesto" });
    expect(shortfallOf(budgetBuy(400_600)).text).toBe("Se pasa ≈ 600 € de tu presupuesto");
    // Chamartín in the example: 1.590 €/mes against 1.500
    expect(shortfallOf(budgetRent(1_590))).toEqual({ text: "Se pasa ≈ 90 €/mes de tu presupuesto", aria: "Se pasa unos 90 € al mes de tu presupuesto" });
    expect(shortfallOf(budgetRent(1_620)).text).toBe("Se pasa ≈ 120 €/mes de tu presupuesto");
    expect(shortfallOf(budgetRent(1_504)).text).toBe("Se pasa ≈ 4 €/mes de tu presupuesto");
  });

  it("says how much longer a trip takes than the limit (resultados.casi.trayecto)", () => {
    expect(shortfallOf(commute(42))).toEqual({ text: "Tarda ≈ 12 min más de lo que pides", aria: "Tarda unos 12 min más de lo que pides" });
    // 30,2 against 30 is not «0 min más»
    expect(shortfallOf(commute(30.2)).text).toBe("Tarda menos de 1 min más de lo que pides");
    // Above 2 h the API gives no minutes in its fact, nor does the web
    expect(shortfallOf(commute(150)).text).toBe("Tarda más de 2 h; pides 30 min como mucho");
  });

  it("names the place only when the search has more than one with a limit", () => {
    const anchors = [
      { kind: "work" as const, label: "Paseo de la Castellana (Azca)", lon: 0, lat: 0, max_minutes: 30 },
      { kind: "family" as const, label: "Getafe Central (Cercanías)", lon: 0, lat: 0, max_minutes: 45 },
    ];
    expect(shortfallOf(commute(50, 1), { anchors }).text).toBe("Tarda ≈ 20 min más de lo que pides hasta Getafe Central (Cercanías)");
    expect(shortfallOf(commute(50, 0), { anchors: [anchors[0]!] }).text).toBe("Tarda ≈ 20 min más de lo que pides");
  });

  it("says how much farther a service on foot is (resultados.casi.a_pie)", () => {
    expect(shortfallOf(school(14.8)).text).toBe("Colegio con primaria: ≈ 5 min más andando de lo que pides");
    expect(shortfallOf(check("near:bares", "Bares y cafeterías a 5 min andando como mucho", 5.3, 5, "min")).text).toBe(
      "Bares y cafeterías: menos de 1 min más andando de lo que pides",
    );
  });

  it("gives no minutes beyond an hour on foot, which is no walk (review R-08)", () => {
    // Up to MAX_WALK_SHOWN of the API (60 min) the minutes are still said
    expect(shortfallOf(school(55.5)).text).toBe("Colegio con primaria: ≈ 46 min más andando de lo que pides");
    expect(shortfallOf(school(75))).toEqual({
      text: "Colegio con primaria a más de 1 h andando; pides 10 min como mucho",
      aria: "Colegio con primaria a más de 1 h andando; pides 10 min como mucho",
    });
  });

  it("never makes up a figure: without value or limit, the condition by its name", () => {
    expect(shortfallOf(budgetRent(Number.NaN))).toEqual({
      text: "No cumple: Alquiler hasta 1.500 €/mes para 77 m²",
      aria: "No cumple: Alquiler hasta 1.500 €/mes para 77 m²",
      label: "Alquiler hasta 1.500 €/mes para 77 m²",
    });
    expect(shortfallOf(check("budget", "Compra hasta 400.000 €", null, 400_000, "€")).text).toBe("No cumple: Compra hasta 400.000 €");
    expect(shortfallOf(commute(null)).text).toBe("No cumple: Trayecto a Paseo de la Castellana (Azca) de 30 min como mucho");
    expect(shortfallOf(check("budget", "Compra hasta 400.000 €", 411_000, null, "€")).text).toBe("No cumple: Compra hasta 400.000 €");
    // A check that is not a FAIL, or a value within the limit, says nothing of an excess
    expect(shortfallOf(check("near:colegio", "Colegio con primaria a 10 min andando como mucho", 8, 10, "min", "PASS")).text).toBe(
      "No cumple: Colegio con primaria a 10 min andando como mucho",
    );
    expect(shortfallOf(check("otra", "Otra condición", 3, 2, "x")).text).toBe("No cumple: Otra condición");
  });

  it("gives the first condition it fails and «y otra condición» or «y 2 condiciones más» (resultados.casi.varias)", () => {
    const constraints = [budgetRent(1_620), school(14.8), commute(42)];
    expect(nearMissText({ failed_constraints: ["budget"], constraints }).text).toBe("Se pasa ≈ 120 €/mes de tu presupuesto");
    expect(nearMissText({ failed_constraints: ["budget", "commute:0"], constraints }).text).toBe("Se pasa ≈ 120 €/mes de tu presupuesto y otra condición");
    expect(nearMissText({ failed_constraints: ["budget", "near:colegio", "commute:0"], constraints }).aria).toBe(
      "Se pasa unos 120 € al mes de tu presupuesto y 2 condiciones más",
    );
    expect(nearMissText({ failed_constraints: [], constraints }).text).toBe(FAILS_UNNAMED);
  });

  it("says every condition in the zone card, by name for a zone of the map without its own checks", () => {
    const labels = new Map([["budget", "Compra hasta 400.000 €"]]);
    expect(shortfalls({ failed_constraints: ["budget", "commute:0"], constraints: [commute(42)] }, labels).map((s) => s.text)).toEqual([
      "No cumple: Compra hasta 400.000 €",
      "Tarda ≈ 12 min más de lo que pides",
    ]);
    // One line for the card: the figures first, then the names under a single «No cumple:» (review R-12)
    const both = new Map([...labels, ["near:colegio", "Colegio con primaria a 10 min andando como mucho"]]);
    const card = joinShortfalls(shortfalls({ failed_constraints: ["budget", "near:colegio", "commute:0"], constraints: [commute(42)] }, both));
    expect(card).toEqual({
      text: "Tarda ≈ 12 min más de lo que pides · No cumple: Compra hasta 400.000 € · Colegio con primaria a 10 min andando como mucho",
      aria: "Tarda unos 12 min más de lo que pides. No cumple: Compra hasta 400.000 € · Colegio con primaria a 10 min andando como mucho",
    });
    expect(joinShortfalls([])).toBeNull();
    // A condition nobody names is left out, as before
    expect(shortfalls({ failed_constraints: ["sin_nombre"] }, labels)).toEqual([]);
    expect(shortfalls({ failed_constraints: undefined })).toEqual([]);
  });
});
