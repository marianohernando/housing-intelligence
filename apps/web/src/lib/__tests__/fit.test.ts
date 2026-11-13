import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { RankedZone, RealityCheck, SearchResult, ZoneMatch } from "@/contracts/search_response";

import {
  constraintLabels,
  countFit,
  failedLabels,
  fewZones,
  fitClass,
  hasWalkingFact,
  optionText,
  paintFit,
  passingText,
  rankText,
  relaxOptions,
  unknownText,
  WALK_MINUTES_FEATURE_PREFIX,
  zoneFit,
  zoneKeyOf,
} from "../fit";
import type { ZoneCollection, ZoneFeature, ZoneLevel } from "../map/zones";

// Test fixture published by line A with the contract (data/fixtures/contracts), not demo data.
const FIXTURE = new URL("../../../../../data/fixtures/contracts/search_result.familia_presupuesto.fixture.json", import.meta.url);
const fixture = JSON.parse(readFileSync(FIXTURE, "utf8")) as SearchResult;

function zone(level: ZoneLevel, code: string): ZoneFeature {
  return {
    type: "Feature",
    id: code,
    geometry: { type: "Polygon", coordinates: [] },
    properties: { admin_unit_id: code, level, code, name: code, municipio_name: "", zone_key: `${level}/${code}` },
  };
}

function match(level: ZoneLevel, code: string, pct: number | null, passes: boolean, failed: string[] = []): ZoneMatch {
  return { zone: { level, code, name: code }, match_pct: pct, passes_all: passes, failed_constraints: failed };
}

function ranked(code: string, rank: number, constraints: [string, string, "PASS" | "FAIL"][], failed: string[] = []): RankedZone {
  return {
    zone: { level: "municipio", code, name: code },
    match_pct: 90,
    rank,
    confidence: 0.9,
    facts: [],
    failed_constraints: failed,
    constraints: constraints.map(([id, label, status]) => ({ constraint_id: id, label, status, confidence: 1, explanation: "" })),
  };
}

const rc = (passing: number, relaxations: [string, number, number][] = []): RealityCheck => ({
  zones_evaluated: 199,
  zones_passing: passing,
  zones_unknown: 0,
  relaxations: relaxations.map(([id, added, total]) => ({
    constraint_id: id,
    label: id,
    added_zones: added,
    zones_if_relaxed: total,
    relaxed_scenario: { schema_version: 2 },
  })),
});

describe("fitClass", () => {
  it("never paints an unknown % as a fit, and keeps a zone that fails apart even with its %", () => {
    expect(fitClass({ match_pct: null, passes_all: false })).toBe("SIN_DATOS");
    expect(fitClass({ match_pct: 93, passes_all: false })).toBe("NO_CUMPLE");
    expect(fitClass({ match_pct: 0, passes_all: true })).toBe("ENCAJA");
  });
});

describe("paintFit and countFit", () => {
  const map: ZoneCollection = {
    type: "FeatureCollection",
    features: [zone("distrito", "2807915"), zone("municipio", "28006"), zone("municipio", "28001"), zone("municipio", "28002")],
  };
  const all = [
    match("distrito", "2807915", 99, true),
    match("municipio", "28006", 84, false, ["near:colegio"]),
    match("municipio", "28001", null, false),
  ];

  it("joins the API zones to the map by level and code, with the % only when known", () => {
    const painted = paintFit(map, all);
    expect(painted.features.map((f) => [f.properties.fit, f.properties.fit_pct])).toEqual([
      ["ENCAJA", 99],
      ["NO_CUMPLE", 84],
      ["SIN_DATOS", undefined],
      [undefined, undefined],
    ]);
    expect(painted.features[2]?.properties).not.toHaveProperty("fit_pct");
    expect(map.features[0]?.properties).not.toHaveProperty("fit");
  });

  it("counts each class; a zone the search did not carry is pending, not SIN DATOS", () => {
    expect(countFit(paintFit(map, all))).toEqual({ ENCAJA: 1, NO_CUMPLE: 1, SIN_DATOS: 1, pending: 1 });
  });

  it("on line A's search fixture, paints as many zones that fit as the API says pass", () => {
    const zones: ZoneCollection = {
      type: "FeatureCollection",
      features: fixture.all_zones.map((z) => zone(z.zone.level as ZoneLevel, z.zone.code)),
    };
    const counts = countFit(paintFit(zones, fixture.all_zones));
    expect(counts.ENCAJA).toBe(fixture.reality_check.zones_passing);
    expect(counts.SIN_DATOS).toBe(fixture.all_zones.filter((z) => z.match_pct == null).length);
    expect(counts.pending).toBe(0);
  });
});

describe("zoneFit and the names of the conditions", () => {
  const result = {
    ...fixture,
    all_zones: [match("municipio", "1", 95, true), match("municipio", "2", 80, false, ["budget"])],
    results: [ranked("1", 1, [["budget", "Alquiler hasta 1.500 €/mes para 77 m²", "PASS"]])],
    near_misses: [ranked("2", 1, [["near:colegio", "Colegio a 10 min andando como mucho", "PASS"], ["budget", "Alquiler hasta 1.500 €/mes para 77 m²", "FAIL"]], ["budget"])],
  } satisfies SearchResult;

  it("finds the zone's match and its ranked entry, in the results or among the near misses", () => {
    expect(zoneFit(result, "municipio/1").ranked?.rank).toBe(1);
    expect(zoneFit(result, "municipio/2").ranked?.failed_constraints).toEqual(["budget"]);
    expect(zoneFit(result, "municipio/3")).toEqual({ match: null, ranked: null });
  });

  it("names the conditions a zone fails, leaving out the unnamed ones", () => {
    const labels = constraintLabels(result);
    expect(labels.get("near:colegio")).toBe("Colegio a 10 min andando como mucho");
    expect(failedLabels(["budget", "commute:0"], labels)).toEqual(["Alquiler hasta 1.500 €/mes para 77 m²"]);
    expect(failedLabels(undefined, labels)).toEqual([]);
  });

  it("keys zones like the map does", () => {
    expect(zoneKeyOf({ level: "distrito", code: "2807905" })).toBe("distrito/2807905");
  });
});

describe("«¿Y si cambias algo?»", () => {
  it("offers only the options that add zones, in the API order", () => {
    const options = relaxOptions(rc(0, [["budget", 48, 48], ["near:colegio", 0, 0]]));
    expect(options.map((r) => r.constraint_id)).toEqual(["budget"]);
  });

  it("opens unfolded with few zones or none", () => {
    expect(fewZones(rc(0))).toBe(true);
    expect(fewZones(rc(5))).toBe(true);
    expect(fewZones(rc(32))).toBe(false);
  });

  it("says how many zones there are, in plain words (rc.ninguna, rc.una, rc.varias)", () => {
    expect(passingText(0)).toBe("Con tu búsqueda tal cual no sale ninguna zona.");
    expect(passingText(1)).toBe("Con tu búsqueda tal cual sale 1 zona.");
    expect(passingText(32)).toBe("Con tu búsqueda tal cual salen 32 zonas.");
    expect(passingText(49, true)).toBe("Con este cambio salen 49 zonas.");
    expect(passingText(1, true)).toBe("Con este cambio sale 1 zona.");
  });

  it("says in how many zones something could not be checked, in singular with one (rc.sin_dato)", () => {
    expect(unknownText(3)).toBe("En 3 zonas no podemos comprobarlo todo por falta de datos. No las contamos como buenas.");
    expect(unknownText(1)).toBe("En 1 zona no podemos comprobarlo todo por falta de datos. No la contamos como buena.");
  });

  it("tells each option with the API's figures, never recomputed", () => {
    const option = { label: "+5 min a pie hasta colegio con primaria", zones_if_relaxed: 49, added_zones: 17 };
    expect(optionText(option)).toEqual({ label: option.label, count: "saldrían 49 zonas, 17 más" });
    // Singular with 1 zone (rc.opcion.cuenta, pitch/textos_web.md 8c49e33)
    expect(optionText({ ...option, zones_if_relaxed: 1, added_zones: 1 }).count).toBe("saldría 1 zona, 1 más");
  });

  it("writes the place in the ranking (zona.puesto)", () => {
    expect(rankText(8)).toBe("La 8.ª que más encaja");
  });
});

describe("facts in plain words (a_pie.mediana)", () => {
  it("says the walking median once, when a fact is a walk, and the facts no longer say it (D-229 follow-up of A)", () => {
    const facts = fixture.results.flatMap((r) => r.facts);
    const walks = facts.filter((f) => f.indicator?.feature_id.startsWith(WALK_MINUTES_FEATURE_PREFIX));
    expect(walks.length).toBeGreaterThan(0);
    for (const f of walks) {
      expect(f.text).toContain("andando");
      expect(f.text).not.toMatch(/mitad de sus calles/);
    }
    expect(hasWalkingFact(walks)).toBe(true);
    // The contract: the walks are told by the indicator, not by the words of the text
    expect(hasWalkingFact([{ indicator: { feature_id: "alquiler_m2_mensual" } }, { indicator: null }])).toBe(false);
    // A park out of range says «sin parque… a un paseo»: no minutes, no indicator, no median note
    expect(hasWalkingFact([{ indicator: null }])).toBe(false);
    expect(hasWalkingFact([{ indicator: { feature_id: "centros_salud_a_pie_por_10000_hab" } }])).toBe(false);
  });
});
