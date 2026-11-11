import { describe, expect, it } from "vitest";

import type { ScenarioState } from "../../contracts/scenario_state";
import {
  BUDGET_RANGE,
  decodeScenario,
  defaultScenario,
  encodeScenario,
  peopleAtHome,
  setAdults,
  setBudgetAmount,
  setBudgetKind,
  setMinors,
  setSeniors,
  togglePriority,
} from "../scenario";

describe("scenario defaults", () => {
  it("starts as one adult, renting, with no priorities", () => {
    const s = defaultScenario();
    expect(s).toMatchObject({ schema_version: 2, household: { adults: 1, minors: 0, seniors_in_care: 0 }, priorities: [] });
    expect(s.budget).toEqual({ kind: "rent", amount_eur: BUDGET_RANGE.rent.initial });
  });
});

describe("household", () => {
  it("counts everyone at home", () => {
    const s = setSeniors(setMinors(setAdults(defaultScenario(), 2), 2), 1);
    expect(peopleAtHome(s)).toBe(5);
  });

  it("keeps the counters inside the contract limits", () => {
    expect(setMinors(defaultScenario(), 12).household?.minors).toBe(8);
    expect(setSeniors(defaultScenario(), 9).household?.seniors_in_care).toBe(4);
    expect(setMinors(defaultScenario(), -1).household?.minors).toBe(0);
  });

  it("drops the children's ages when the number of children changes", () => {
    const withAges: ScenarioState = { ...defaultScenario(), household: { adults: 2, minors: 1, minor_ages: [4], seniors_in_care: 0 } };
    expect(setMinors(withAges, 2).household?.minor_ages).toEqual([]);
  });
});

describe("priorities («Me importa»)", () => {
  it("keeps the order in which they were marked: the first counts most", () => {
    let s = togglePriority(defaultScenario(), "colegios");
    s = togglePriority(s, "transporte");
    expect(s.priorities).toEqual(["colegios", "transporte"]);
  });

  it("unmarks a priority that was already marked", () => {
    const s = togglePriority(togglePriority(defaultScenario(), "salud"), "salud");
    expect(s.priorities).toEqual([]);
  });
});

describe("budget", () => {
  it("switches between rent and purchase with a sensible starting amount", () => {
    const buy = setBudgetKind(defaultScenario(), "buy");
    expect(buy.budget).toEqual({ kind: "buy", amount_eur: BUDGET_RANGE.buy.initial });
    expect(setBudgetKind(buy, "rent").budget?.kind).toBe("rent");
  });

  it("clamps and rounds the amount to the slider steps", () => {
    const rent = defaultScenario();
    expect(setBudgetAmount(rent, 10).budget?.amount_eur).toBe(BUDGET_RANGE.rent.min);
    expect(setBudgetAmount(rent, 1234).budget?.amount_eur).toBe(1250);
    expect(setBudgetAmount(rent, 99_999).budget?.amount_eur).toBe(BUDGET_RANGE.rent.max);
  });

  it("keeps the slider ranges inside the contract ranges (100–20.000 €/mes, 10.000–5.000.000 €)", () => {
    expect(BUDGET_RANGE.rent.min).toBeGreaterThanOrEqual(100);
    expect(BUDGET_RANGE.rent.max).toBeLessThanOrEqual(20_000);
    expect(BUDGET_RANGE.buy.min).toBeGreaterThanOrEqual(10_000);
    expect(BUDGET_RANGE.buy.max).toBeLessThanOrEqual(5_000_000);
  });
});

describe("encode / decode (link to share a search)", () => {
  it("round-trips a scenario, accents included", () => {
    const s: ScenarioState = {
      ...togglePriority(setMinors(setAdults(defaultScenario(), 2), 2), "colegios"),
      anchors: [{ kind: "work", label: "Paseo de la Castellana (Azca)", lon: -3.69, lat: 40.45, days_per_week: 5, max_minutes: null }],
    };
    expect(decodeScenario(encodeScenario(s))).toEqual(s);
  });

  it("produces URL-safe text", () => {
    expect(encodeScenario(defaultScenario())).toMatch(/^[A-Za-z0-9_-]+$/);
  });

  it("rejects text that is not a valid scenario", () => {
    expect(decodeScenario("not-base64!")).toBeNull();
    expect(decodeScenario(encodeScenario({ ...defaultScenario(), schema_version: 1 } as unknown as ScenarioState))).toBeNull();
    expect(decodeScenario(encodeScenario({ ...defaultScenario(), priorities: ["piscina"] } as unknown as ScenarioState))).toBeNull();
  });
});
