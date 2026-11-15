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
  FEW_OFFICE_DAYS,
  FLOOR_AREA_RANGE,
  floorArea,
  floorAreaOptions,
  HOUSEHOLD_FLOOR_AREA_M2,
  HOME_LABEL,
  isOlderHousehold,
  OFFICE_DAYS,
  officeDays,
  officeDaysOptions,
  OLDER_PRIORITIES,
  OLDER_TRIP,
  olderPlace,
  LEISURE_KEYS,
  leisureConfig,
  nearbyServices,
  peopleAtHome,
  placeOf,
  QUICK_BUDGETS,
  removeNearby,
  retiredExampleScenario,
  SCOPES,
  scopeOf,
  setAdults,
  setBudgetAmount,
  setBudgetKind,
  setFloorArea,
  setLeisureMinutes,
  setLeisureRequired,
  setMinors,
  setNearbyMinutes,
  setNearbyRequired,
  setNoBudgetLimit,
  setOlderHousehold,
  setOlderPlace,
  setOlderPlaceKind,
  setPlace,
  setPlaceMaxMinutes,
  setScope,
  setSeniors,
  setTypedBudget,
  setWorkDays,
  setWorkMaxMinutes,
  setWorkPlace,
  toggleLeisureGroup,
  togglePriority,
  typedBudget,
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

describe("«¿Dónde?» (scope, D-238)", () => {
  it("offers the whole region first, then Madrid capital, its surroundings and the villages", () => {
    expect(SCOPES).toEqual(["all", "madrid", "alrededores", "pueblos"]);
  });

  it("sends a part of the region and leaves `scope` out for «Toda la Comunidad», as before", () => {
    const madrid = setScope(defaultScenario(), "madrid");
    expect(madrid.scope).toBe("madrid");
    expect(scopeOf(madrid)).toBe("madrid");
    const all = setScope(madrid, "all");
    expect("scope" in all).toBe(false);
    expect(scopeOf(all)).toBe("all");
    expect(all).toEqual(defaultScenario());
  });

  it("treats the API's explicit `all` like no scope", () => {
    expect(scopeOf({ scope: "all" })).toBe("all");
    expect("scope" in setScope({ ...defaultScenario(), scope: "all" }, "all")).toBe(false);
  });

  it("keeps the example without a scope: its figures are the pitch's", () => {
    expect("scope" in exampleScenario()).toBe(false);
  });

  it("round-trips a shared link with a scope and rejects an unknown one", () => {
    const s = setScope(defaultScenario(), "alrededores");
    expect(decodeScenario(encodeScenario(s))).toEqual(s);
    expect(decodeScenario(encodeScenario({ ...defaultScenario(), scope: "sierra" } as unknown as ScenarioState))).toBeNull();
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

  it("marked, it is a priority with bars and restaurants at 10 min that ranks and never filters", () => {
    const s = ocio();
    expect(s.priorities).toEqual(["ocio"]);
    expect(s.nearby).toEqual([
      { need: "bares", max_walk_minutes: 10, required: false },
      { need: "restaurantes", max_walk_minutes: 10, required: false },
    ]);
    expect(leisureConfig(s)).toEqual({ groups: ["bares", "restaurantes"], minutes: 10, required: false });
  });

  it("sends each ticked group as a nearby need, in the order of the boxes", () => {
    let s = toggleLeisureGroup(ocio(), "cultura");
    s = toggleLeisureGroup(s, "gimnasios");
    s = toggleLeisureGroup(s, "restaurantes");
    expect(s.nearby?.map((n) => n.need)).toEqual(["bares", "gimnasios", "cultura"]);
    expect(LEISURE_KEYS).toEqual(["bares", "restaurantes", "gimnasios", "cultura"]);
  });

  it("the minutes (5, 10 or 15) and «Imprescindible» are one choice for every group, new ones too", () => {
    let s = setLeisureRequired(setLeisureMinutes(ocio(), 15), true);
    s = toggleLeisureGroup(s, "gimnasios");
    expect(s.nearby).toEqual([
      { need: "bares", max_walk_minutes: 15, required: true },
      { need: "restaurantes", max_walk_minutes: 15, required: true },
      { need: "gimnasios", max_walk_minutes: 15, required: true },
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
    expect(leisureConfig(s)).toEqual({ groups: [], minutes: 10, required: false });
  });

  it("travels in a shared link", () => {
    const s = toggleLeisureGroup(ocio(), "cultura");
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

describe("«¿Cuántos días vas a la oficina?» (trabajo.dias, D-240)", () => {
  const withWork = () => setWorkPlace(defaultScenario(), { label: "Nuevos Ministerios (metro)", lat: 40.446, lon: -3.692 });

  it("offers 5 to 1 days and Teletrabajo total (0), and starts at the contract's 5 without sending them", () => {
    expect(OFFICE_DAYS).toEqual([5, 4, 3, 2, 1, 0]);
    const anchor = workPlace(withWork());
    expect(anchor && "days_per_week" in anchor).toBe(false);
    expect(anchor && officeDays(anchor)).toBe(5);
  });

  it("sends the chosen days as days_per_week of the work anchor and keeps its limit", () => {
    const limited = setWorkMaxMinutes(withWork(), 45);
    expect(setWorkDays(limited, 2).anchors).toEqual([
      { kind: "work", label: "Nuevos Ministerios (metro)", lat: 40.446, lon: -3.692, max_minutes: 45, days_per_week: 2 },
    ]);
    expect(setWorkDays(setWorkDays(limited, 2), 5).anchors?.[0]).toMatchObject({ days_per_week: 5, max_minutes: 45 });
  });

  it("sends Teletrabajo total as 0 days and keeps the limit, which still applies", () => {
    const telework = setWorkDays(setWorkMaxMinutes(withWork(), 45), 0);
    expect(telework.anchors?.[0]).toMatchObject({ label: "Nuevos Ministerios (metro)", days_per_week: 0, max_minutes: 45 });
    expect(setWorkMaxMinutes(telework, 30).anchors?.[0]).toMatchObject({ days_per_week: 0, max_minutes: 30 });
  });

  it("keeps the days inside the contract's 0 to 7 and does nothing without a work place", () => {
    expect(setWorkDays(withWork(), 9).anchors?.[0]?.days_per_week).toBe(7);
    expect(setWorkDays(withWork(), -1).anchors?.[0]?.days_per_week).toBe(0);
    expect(setWorkDays(defaultScenario(), 2).anchors).toEqual([]);
  });

  it("only touches the work place: family or friends have no days", () => {
    const both = setPlace(withWork(), "family", { label: "Getafe", lat: 40.31, lon: -3.73 });
    expect(setWorkDays(both, 1).anchors?.map((a) => [a.kind, a.days_per_week])).toEqual([
      ["work", 1],
      ["family", undefined],
    ]);
  });

  it("offers the days of a shared link outside the list, and says which ones weigh half", () => {
    expect(officeDaysOptions(5)).toEqual([5, 4, 3, 2, 1, 0]);
    expect(officeDaysOptions(7)).toEqual([7, 5, 4, 3, 2, 1, 0]);
    expect(FEW_OFFICE_DAYS).toBe(2);
  });
});

describe("«Cerca de mi familia o amigos» (familia.*, a second place)", () => {
  const AZCA = { label: "Nuevos Ministerios (metro)", lat: 40.446, lon: -3.692 };
  const GETAFE = { label: "Getafe Central (Cercanías)", lat: 40.31, lon: -3.73 };

  it("sends a family anchor without a limit, after the work place whatever the order they are picked in", () => {
    const familyFirst = setWorkPlace(setPlace(defaultScenario(), "family", GETAFE), AZCA);
    const workFirst = setPlace(setWorkPlace(defaultScenario(), AZCA), "family", GETAFE);
    expect(familyFirst).toEqual(workFirst);
    expect(workFirst.anchors).toEqual([
      { kind: "work", ...AZCA, max_minutes: null },
      { kind: "family", ...GETAFE, max_minutes: null },
    ]);
    expect(placeOf(workFirst, "family")?.label).toBe(GETAFE.label);
  });

  it("goes alone when there is no work place, and removing it leaves the work place as it was", () => {
    expect(setPlace(defaultScenario(), "family", GETAFE).anchors).toEqual([{ kind: "family", ...GETAFE, max_minutes: null }]);
    const work = setWorkDays(setWorkMaxMinutes(setWorkPlace(defaultScenario(), AZCA), 45), 3);
    expect(setPlace(setPlace(work, "family", GETAFE), "family", null)).toEqual(work);
  });

  it("sends its own limit as max_minutes of the family anchor, apart from the work one", () => {
    const both = setPlace(setWorkMaxMinutes(setWorkPlace(defaultScenario(), AZCA), 45), "family", GETAFE);
    expect(setPlaceMaxMinutes(both, "family", 30).anchors?.map((a) => [a.kind, a.max_minutes])).toEqual([
      ["work", 45],
      ["family", 30],
    ]);
    expect(setWorkMaxMinutes(setPlaceMaxMinutes(both, "family", 30), null).anchors?.map((a) => a.max_minutes)).toEqual([null, 30]);
    expect(setPlaceMaxMinutes(both, "family", 500).anchors?.[1]?.max_minutes).toBe(120);
  });

  it("keeps a place of another kind from a shared link, after the two the web edits", () => {
    const study: ScenarioState = { ...defaultScenario(), anchors: [{ kind: "study", label: "Universidad", lat: 40.4, lon: -3.7 }] };
    const all = setWorkPlace(setPlace(study, "family", GETAFE), AZCA);
    expect(all.anchors?.map((a) => a.kind)).toEqual(["work", "family", "study"]);
  });
});

describe("demo case (portada.ejemplo.boton)", () => {
  it("is line A's golden profile, with the work place without a limit (the pitch's figures)", () => {
    const golden = JSON.parse(readFileSync(GOLDEN, "utf8")) as ScenarioState;
    const asReference = { ...golden, anchors: golden.anchors?.map((a) => ({ ...a, max_minutes: null })) };
    expect(exampleScenario()).toEqual(asReference);
    expect(exampleScenario().anchors?.every((a) => a.max_minutes === null)).toBe(true);
  });

  it("goes to the office 4 days a week: from 3 days the trip weighs as always (D-240)", () => {
    const work = workPlace(exampleScenario());
    expect(work && officeDays(work)).toBe(4);
    expect(work && officeDays(work) > FEW_OFFICE_DAYS).toBe(true);
  });

  it("is a new object every time, so editing it never changes the next example", () => {
    expect(exampleScenario()).not.toBe(exampleScenario());
  });
});

describe("m² of the home («Para unos 68 m² (cámbialo)»)", () => {
  it("is the household's usual unless the person picks it: the table the API uses (D-214)", () => {
    const python = readFileSync(new URL("../../../../../packages/domain/src/hi_domain/affordability.py", import.meta.url), "utf8");
    const table = /MEDIAN_FLOOR_AREA_M2: dict\[int, int\] = (\{[^}]+\})/.exec(python)?.[1];
    expect(table && JSON.parse(table.replace(/(\d+):/g, '"$1":'))).toEqual(HOUSEHOLD_FLOOR_AREA_M2);
    expect(floorArea(defaultScenario())).toEqual({ m2: 61, household: true });
    expect(floorArea(setAdults(defaultScenario(), 2))).toEqual({ m2: 68, household: true });
    expect(floorArea(exampleScenario())).toEqual({ m2: 77, household: true });
    // 5 or more people count as 5
    expect(floorArea(setSeniors(setMinors(setAdults(defaultScenario(), 2), 8), 4)).m2).toBe(77);
  });

  it("sends the m² picked, and null again with «Lo normal para tu hogar»", () => {
    const picked = setFloorArea(defaultScenario(), 82.4);
    expect(picked.min_floor_area_m2).toBe(82);
    expect(floorArea(picked)).toEqual({ m2: 82, household: false });
    const back = setFloorArea(picked, null);
    expect(back.min_floor_area_m2).toBeNull();
    // Back to the usual is the same search as before (no «Has cambiado tu búsqueda»)
    expect(back).toEqual(defaultScenario());
    // Inside the contract range (15–400 m²)
    expect(setFloorArea(defaultScenario(), 5).min_floor_area_m2).toBe(15);
    expect(setFloorArea(defaultScenario(), 900).min_floor_area_m2).toBe(400);
  });

  it("keeps the m² picked when the household changes: only «Lo normal para tu hogar» follows it", () => {
    const withChildren = setMinors(setFloorArea(defaultScenario(), 60), 2);
    expect(withChildren.min_floor_area_m2).toBe(60);
    expect(floorArea(withChildren)).toEqual({ m2: 60, household: false });
    expect(floorArea(setMinors(defaultScenario(), 2))).toEqual({ m2: 71, household: true });
  });

  it("offers 40 to 150 m² by 5, and a value from a shared link outside them too", () => {
    const options = floorAreaOptions(null);
    expect([options[0], options.at(-1), options.length]).toEqual([FLOOR_AREA_RANGE.min, FLOOR_AREA_RANGE.max, 23]);
    expect(floorAreaOptions(62)).toContain(62);
    expect(floorAreaOptions(60)).toHaveLength(23);
  });

  it("leaves the example of the pitch with min_floor_area_m2: null", () => {
    expect(exampleScenario().min_floor_area_m2).toBeNull();
  });
});

describe("«Somos mayores» (D-244)", () => {
  it("says who the adults are and adds no one: the same people and the same m²", () => {
    const couple = setAdults(defaultScenario(), 2);
    const older = setOlderHousehold(couple, true);
    expect(isOlderHousehold(older)).toBe(true);
    expect(older.household?.seniors).toBe(true);
    expect(peopleAtHome(older)).toBe(peopleAtHome(couple));
    expect(floorArea(older)).toEqual(floorArea(couple));
  });

  it("marks the health centre, step-free stations and transport, after what was marked, once each, and each can go", () => {
    const older = setOlderHousehold({ ...defaultScenario(), priorities: ["transporte"] }, true);
    expect(OLDER_PRIORITIES).toEqual(["salud", "sin_escaleras", "transporte"]);
    expect(older.priorities).toEqual(["transporte", "salud", "sin_escaleras"]);
    expect(setOlderHousehold(defaultScenario(), true).priorities).toEqual(["salud", "sin_escaleras", "transporte"]);
    expect(togglePriority(older, "salud").priorities).toEqual(["transporte", "sin_escaleras"]);
  });

  it("starts in Madrid capital when the whole region has no place to go, and never overrides a choice", () => {
    expect(setOlderHousehold(defaultScenario(), true).scope).toBe("madrid");
    expect(setOlderHousehold(setScope(defaultScenario(), "alrededores"), true).scope).toBe("alrededores");
    const withPlace = setPlace(defaultScenario(), "family", { label: "Getafe Central (Cercanías)", lon: -3.71, lat: 40.31 });
    expect("scope" in setOlderHousehold(withPlace, true)).toBe(false);
    // The person can go back to the whole region
    expect("scope" in setScope(setOlderHousehold(defaultScenario(), true), "all")).toBe(false);
  });

  it("unmarked, leaves the household as it was before the field, and keeps what it marked in view", () => {
    const back = setOlderHousehold(setOlderHousehold(defaultScenario(), true), false);
    expect("seniors" in (back.household ?? {})).toBe(false);
    expect(back.household).toEqual(defaultScenario().household);
    expect(back.priorities).toEqual(["salud", "sin_escaleras", "transporte"]);
    expect(back.scope).toBe("madrid");
    expect(isOlderHousehold(defaultScenario())).toBe(false);
  });

  // Review H1 of PR #79: no field shows «Donde vivimos ahora» without «Somos mayores», so it must not filter unseen
  it("unmarked, takes «Donde vivimos ahora» away and keeps a family place and a work place, which other fields show", () => {
    const station = { label: "Ciudad Lineal (metro)", lon: -3.63816, lat: 40.43805 };
    const home = setOlderPlace(setOlderHousehold(setAdults(defaultScenario(), 2), true), "other", station);
    expect(setOlderHousehold(home, false).anchors).toEqual([]);
    const family = setOlderPlace(setOlderHousehold(defaultScenario(), true), "family", station);
    expect(setOlderHousehold(family, false).anchors?.map((a) => a.kind)).toEqual(["family"]);
    const working = setPlace(home, "work", station);
    expect(setOlderHousehold(working, false).anchors?.map((a) => a.kind)).toEqual(["work"]);
  });

  it("asks where they want to live: where they live now (never its own name) or near their family, 30 min and 3 days", () => {
    const station = { label: "Ciudad Lineal (metro)", lon: -3.63816, lat: 40.43805 };
    const home = setOlderPlace(defaultScenario(), "other", station);
    expect(olderPlace(home)).toEqual({ kind: "other", anchor: { kind: "other", label: HOME_LABEL, lon: station.lon, lat: station.lat, max_minutes: 30, days_per_week: 3 } });
    // Lower case: the API says it inside a sentence («… hasta donde vivimos ahora, llegando a las 9:00»)
    expect(HOME_LABEL).toBe("donde vivimos ahora");
    const family = setOlderPlace(home, "family", station);
    expect(family.anchors).toEqual([{ kind: "family", label: "Ciudad Lineal (metro)", lon: station.lon, lat: station.lat, ...OLDER_TRIP }]);
    // One place: the other kind takes the same point, and keeps a limit the person changed
    const limited = setPlaceMaxMinutes(family, "family", 45);
    const moved = setOlderPlaceKind(limited, "other", "Ciudad Lineal (metro)");
    expect(moved.anchors).toEqual([{ kind: "other", label: HOME_LABEL, lon: station.lon, lat: station.lat, max_minutes: 45, days_per_week: 3 }]);
    expect(setOlderPlaceKind(moved, "family", "Ciudad Lineal (metro)").anchors?.[0]?.label).toBe("Ciudad Lineal (metro)");
    expect(setOlderPlace(moved, "other", null).anchors).toEqual([]);
    // A work place stays, before the place to live near
    const working = setOlderPlace(setPlace(defaultScenario(), "work", station), "other", station);
    expect(working.anchors?.map((a) => a.kind)).toEqual(["work", "other"]);
  });

  it("is the second example: a retired couple renting up to 1.200 € near their family in Ciudad Lineal", () => {
    const retired = retiredExampleScenario();
    expect(retired).toMatchObject({
      scope: "madrid",
      budget: { kind: "rent", amount_eur: 1_200 },
      household: { adults: 2, minors: 0, seniors: true },
      priorities: ["salud", "sin_escaleras", "transporte"],
    });
    // The Ciudad Lineal metro station of GET /api/v1/places: a public place, never a home address
    expect(retired.anchors).toEqual([{ kind: "family", label: "Ciudad Lineal (metro)", lon: -3.63816, lat: 40.43805, max_minutes: 30, days_per_week: 3 }]);
    expect(olderPlace(retired)?.kind).toBe("family");
    expect(peopleAtHome(retired)).toBe(2);
    expect(floorArea(retired)).toEqual({ m2: 68, household: true });
    expect(decodeScenario(encodeScenario(retired))).toEqual(retired);
  });
});

describe("quick amounts and «Otra cantidad» (UX mobile audit, A1)", () => {
  it("offers amounts inside the slider, on its steps, and starts each kind on one of them", () => {
    for (const kind of ["rent", "buy"] as const) {
      const { min, max, step, initial } = BUDGET_RANGE[kind];
      expect(QUICK_BUDGETS[kind]).toContain(initial);
      for (const amount of QUICK_BUDGETS[kind]) {
        expect(amount).toBeGreaterThanOrEqual(min);
        expect(amount).toBeLessThanOrEqual(max);
        expect(amount % step).toBe(0);
      }
    }
    expect(QUICK_BUDGETS.rent).toEqual([600, 900, 1_200, 1_500]);
    expect(QUICK_BUDGETS.buy).toEqual([150_000, 250_000, 400_000, 600_000]);
    expect(setBudgetKind(defaultScenario(), "buy").budget?.amount_eur).toBe(250_000);
  });

  it("reads the euros as people type them, inside the slider's range", () => {
    expect(typedBudget("900", "rent")).toBe(900);
    expect(typedBudget("1.250", "rent")).toBe(1_250);
    expect(typedBudget(" 1 250 € ", "rent")).toBe(1_250);
    expect(typedBudget("320.000", "buy")).toBe(320_000);
    expect(typedBudget("", "rent")).toBeNull();
    expect(typedBudget("900,50", "rent")).toBeNull();
    expect(typedBudget("mil", "rent")).toBeNull();
    expect(typedBudget(String(BUDGET_RANGE.rent.min - 1), "rent")).toBeNull();
    expect(typedBudget(String(BUDGET_RANGE.rent.max + 1), "rent")).toBeNull();
    expect(typedBudget("900", "buy")).toBeNull();
  });

  it("keeps a typed amount as typed, not on the slider's step", () => {
    expect(setTypedBudget(defaultScenario(), 875).budget).toEqual({ kind: "rent", amount_eur: 875 });
    expect(setTypedBudget(setBudgetKind(defaultScenario(), "buy"), 312_500).budget).toEqual({ kind: "buy", amount_eur: 312_500 });
  });
});
