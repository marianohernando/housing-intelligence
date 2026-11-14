import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { ScenarioState } from "../../contracts/scenario_state";
import {
  addNearby,
  BUDGET_RANGE,
  COMMUTE_MINUTES,
  commuteMinutesOptions,
  decodeScenario,
  defaultScenario,
  encodeScenario,
  exampleScenario,
  LEISURE_KEYS,
  leisureConfig,
  nearbyServices,
  peopleAtHome,
  removeNearby,
  setAdults,
  setBudgetAmount,
  setBudgetKind,
  setLeisureMinutes,
  setLeisureRequired,
  setMinors,
  setNearbyMinutes,
  setNearbyRequired,
  setNoBudgetLimit,
  setSeniors,
  setWorkMaxMinutes,
  setWorkPlace,
  toggleLeisureGroup,
  togglePriority,
  walkMinutesOptions,
  workPlace,
} from "../scenario";

// Line A's golden profile for the demo (data/fixtures/contracts), the body of POST /search.
const GOLDEN = new URL("../../../../../data/fixtures/contracts/scenario_state.familia_castellana.fixture.json", import.meta.url);

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

describe("budget without a limit (presupuesto.sin_limite)", () => {
  it("sends budget null and comes back as renting", () => {
    const none = setNoBudgetLimit(setBudgetKind(defaultScenario(), "buy"), true);
    expect(none.budget).toBeNull();
    expect(setNoBudgetLimit(none, false).budget).toEqual({ kind: "rent", amount_eur: BUDGET_RANGE.rent.initial });
    const rent = setBudgetAmount(defaultScenario(), 1500);
    expect(setNoBudgetLimit(rent, false)).toBe(rent);
  });
});

describe("«Lo quiero a un paseo» (nearby)", () => {
  it("adds a service once, at 10 min and as a must (the contract defaults)", () => {
    const s = addNearby(addNearby(defaultScenario(), "colegio"), "colegio");
    expect(s.nearby).toEqual([{ need: "colegio", max_walk_minutes: 10, required: true }]);
  });

  it("changes the minutes inside 1–60 and whether it is a must, and removes it", () => {
    let s = addNearby(addNearby(defaultScenario(), "colegio"), "farmacia");
    s = setNearbyMinutes(s, "colegio", 90);
    s = setNearbyRequired(s, "farmacia", false);
    expect(s.nearby).toEqual([
      { need: "colegio", max_walk_minutes: 60, required: true },
      { need: "farmacia", max_walk_minutes: 10, required: false },
    ]);
    expect(removeNearby(s, "colegio").nearby?.map((n) => n.need)).toEqual(["farmacia"]);
  });

  it("offers the minutes a relaxed search brings even when they are not in the usual list", () => {
    expect(walkMinutesOptions(15)).toEqual([5, 10, 15, 20, 30]);
    expect(walkMinutesOptions(12)).toEqual([5, 10, 12, 15, 20, 30]);
  });
});

describe("«Ocio» (importa.ocio.*, D-236): what the configurator sends", () => {
  const ocio = () => togglePriority(defaultScenario(), "ocio");

  it("marked, it is a priority with bars and restaurants at 10 min as a must", () => {
    const s = ocio();
    expect(s.priorities).toEqual(["ocio"]);
    expect(s.nearby).toEqual([
      { need: "bares", max_walk_minutes: 10, required: true },
      { need: "restaurantes", max_walk_minutes: 10, required: true },
    ]);
    expect(leisureConfig(s)).toEqual({ groups: ["bares", "restaurantes"], minutes: 10, required: true });
  });

  it("sends each ticked group as a nearby need, in the order of the boxes", () => {
    let s = toggleLeisureGroup(ocio(), "cines_teatros");
    s = toggleLeisureGroup(s, "gimnasios");
    s = toggleLeisureGroup(s, "restaurantes");
    expect(s.nearby?.map((n) => n.need)).toEqual(["bares", "gimnasios", "cines_teatros"]);
    expect(LEISURE_KEYS).toEqual(["bares", "restaurantes", "gimnasios", "cines_teatros"]);
  });

  it("the minutes (5, 10 or 15) and «Imprescindible» are one choice for every group, new ones too", () => {
    let s = setLeisureRequired(setLeisureMinutes(ocio(), 15), false);
    s = toggleLeisureGroup(s, "gimnasios");
    expect(s.nearby).toEqual([
      { need: "bares", max_walk_minutes: 15, required: false },
      { need: "restaurantes", max_walk_minutes: 15, required: false },
      { need: "gimnasios", max_walk_minutes: 15, required: false },
    ]);
    expect(walkMinutesOptions(leisureConfig(s).minutes, [5, 10, 15])).toEqual([5, 10, 15]);
  });

  it("keeps the other services and priorities as they were, and leaves with all its groups", () => {
    let s = togglePriority(addNearby(defaultScenario(), "colegio"), "colegios");
    s = toggleLeisureGroup(togglePriority(s, "ocio"), "gimnasios");
    s = addNearby(s, "farmacia");
    expect(s.priorities).toEqual(["colegios", "ocio"]);
    expect(nearbyServices(s).map((n) => n.need)).toEqual(["colegio", "farmacia"]);
    const off = togglePriority(s, "ocio");
    expect(off.priorities).toEqual(["colegios"]);
    expect(off.nearby).toEqual([
      { need: "colegio", max_walk_minutes: 10, required: true },
      { need: "farmacia", max_walk_minutes: 10, required: true },
    ]);
  });

  it("with every box unticked sends the priority alone, which the API does not score", () => {
    const s = toggleLeisureGroup(toggleLeisureGroup(ocio(), "bares"), "restaurantes");
    expect(s.priorities).toEqual(["ocio"]);
    expect(s.nearby).toEqual([]);
    expect(leisureConfig(s)).toEqual({ groups: [], minutes: 10, required: true });
  });

  it("travels in a shared link", () => {
    const s = toggleLeisureGroup(ocio(), "cines_teatros");
    expect(decodeScenario(encodeScenario(s))).toEqual(s);
  });

  it("is not part of a search that never marked it: the example of the pitch has no leisure", () => {
    const example = exampleScenario();
    expect(example.priorities).not.toContain("ocio");
    expect(example.nearby?.map((n) => n.need)).toEqual(["colegio"]);
    expect(leisureConfig(example).groups).toEqual([]);
  });
});

describe("«Trabajo en» (work place)", () => {
  it("goes as a reference without a minutes limit (D-215) and replaces the previous one", () => {
    let s = setWorkPlace(defaultScenario(), { label: "Nuevos Ministerios (metro)", lat: 40.446, lon: -3.692 });
    s = setWorkPlace(s, { label: "Alcobendas", lat: 40.54, lon: -3.64 });
    expect(s.anchors).toEqual([{ kind: "work", label: "Alcobendas", lat: 40.54, lon: -3.64, max_minutes: null }]);
    expect(workPlace(s)?.label).toBe("Alcobendas");
    expect(setWorkPlace(s, null).anchors).toEqual([]);
  });

  it("keeps other kinds of places and cuts the name to the contract's 80 characters", () => {
    const study: ScenarioState = { ...defaultScenario(), anchors: [{ kind: "study", label: "Universidad", lat: 40.4, lon: -3.7 }] };
    const s = setWorkPlace(study, { label: "x".repeat(100), lat: 40.45, lon: -3.69 });
    expect(s.anchors?.map((a) => [a.kind, a.label.length])).toEqual([
      ["work", 80],
      ["study", 11],
    ]);
  });
});

describe("«Tardar como mucho» (work commute limit)", () => {
  const withWork = () => setWorkPlace(defaultScenario(), { label: "Nuevos Ministerios (metro)", lat: 40.446, lon: -3.692 });

  it("offers Sin límite first (null) and 30, 45, 60 and 90 min", () => {
    expect(COMMUTE_MINUTES).toEqual([30, 45, 60, 90]);
    expect(withWork().anchors?.[0]?.max_minutes).toBeNull();
  });

  it("sends the chosen minutes as max_minutes of the work anchor, and Sin límite sends null again", () => {
    const limited = setWorkMaxMinutes(withWork(), 45);
    expect(limited.anchors).toEqual([{ kind: "work", label: "Nuevos Ministerios (metro)", lat: 40.446, lon: -3.692, max_minutes: 45 }]);
    expect(setWorkMaxMinutes(limited, null).anchors?.[0]?.max_minutes).toBeNull();
  });

  it("keeps the limit inside the contract's 5 to 120 minutes", () => {
    expect(setWorkMaxMinutes(withWork(), 1).anchors?.[0]?.max_minutes).toBe(5);
    expect(setWorkMaxMinutes(withWork(), 500).anchors?.[0]?.max_minutes).toBe(120);
  });

  it("changes the scenario, so the search is stale until it runs again", () => {
    expect(encodeScenario(setWorkMaxMinutes(withWork(), 60))).not.toBe(encodeScenario(withWork()));
  });

  it("leaves other places alone and does nothing without a work place", () => {
    const study: ScenarioState = { ...defaultScenario(), anchors: [{ kind: "study", label: "Universidad", lat: 40.4, lon: -3.7 }] };
    expect(setWorkMaxMinutes(study, 30)).toEqual(study);
    expect(setWorkMaxMinutes(defaultScenario(), 30).anchors).toEqual([]);
  });

  it("offers a limit that came in a shared link even when it is not in the usual list", () => {
    expect(commuteMinutesOptions(null)).toEqual([30, 45, 60, 90]);
    expect(commuteMinutesOptions(45)).toEqual([30, 45, 60, 90]);
    expect(commuteMinutesOptions(75)).toEqual([30, 45, 60, 75, 90]);
  });
});

describe("demo case (portada.ejemplo.boton)", () => {
  it("is line A's golden profile, with the work place without a limit (the pitch's figures)", () => {
    const golden = JSON.parse(readFileSync(GOLDEN, "utf8")) as ScenarioState;
    const asReference = { ...golden, anchors: golden.anchors?.map((a) => ({ ...a, max_minutes: null })) };
    expect(exampleScenario()).toEqual(asReference);
    expect(exampleScenario().anchors?.every((a) => a.max_minutes === null)).toBe(true);
  });

  it("is a new object every time, so editing it never changes the next example", () => {
    expect(exampleScenario()).not.toBe(exampleScenario());
  });
});
