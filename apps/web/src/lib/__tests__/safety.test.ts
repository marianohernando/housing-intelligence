import { describe, expect, it } from "vitest";

import type { FeatureValueRow } from "../features";
import { perceivedSafety, perceivedSafetyText, type SafetyRows } from "../safety";

// Test fixture: rows shaped as GET /features/{id}/values gives them (D-226 §1), values from 12 nov
function row(code: string, value: number | null, period = "2025-01-01"): FeatureValueRow {
  return { territory_code: code, admin_unit_id: null, name: null, period_start: period, value, null_reason: value === null ? "SOURCE_MISSING" : null, confidence: 0.9 };
}

const rows: SafetyRows = {
  night: [row("2807901", 6.5), row("2807905", 7.0), row("2807905", 5.0, "2023-01-01")],
  day: [row("2807901", 7.9), row("2807905", 8.0)],
  nightCity: [row("28079", 6.4), row("28110", null)],
  dayCity: [row("28079", 7.8), row("28110", null)],
};

describe("perceivedSafety (DATA-020, D-226 §1)", () => {
  it("takes the district's latest night and day ratings, with the city's of the same year", () => {
    expect(perceivedSafety("2807905", rows)).toEqual({ night: 7, day: 8, city: { night: 6.4, day: 7.8 }, year: "2025" });
  });

  it("says nothing without a rating: never 0, never another district's", () => {
    expect(perceivedSafety("2807921", rows)).toBeNull();
    expect(perceivedSafety("2807901", { ...rows, day: [] })).toBeNull();
  });

  it("leaves the city out when the API does not give it, and never mixes years", () => {
    expect(perceivedSafety("2807901", { ...rows, nightCity: [] })?.city).toBeNull();
    expect(perceivedSafety("2807901", { ...rows, dayCity: [row("28079", 7.5, "2024-01-01")] })?.city).toBeNull();
    expect(perceivedSafety("2807901", { ...rows, day: [row("2807901", 7.9, "2024-01-01")] })).toBeNull();
  });
});

describe("perceivedSafetyText (zona.seguridad_vecinos)", () => {
  it("says it is the neighbours' rating, with the city's, the year and the survey", () => {
    const text = perceivedSafetyText({ night: 7, day: 8, city: { night: 6.4, day: 7.8 }, year: "2025" });
    expect(text.rating).toBe("Así valoran sus vecinos la seguridad de su barrio: 7,0 de noche y 8,0 de día, de 0 a 10 (en todo Madrid, 6,4 y 7,8).");
    expect(text.source).toBe("Encuesta de calidad de vida del Ayuntamiento de Madrid, 2025, unas 400 personas por distrito.");
    // Never an alarm word (D-205, D-226)
    expect(`${text.rating} ${text.source}`).not.toMatch(/peligros|insegur/i);
  });

  it("drops the city's part when there is none", () => {
    expect(perceivedSafetyText({ night: 4.9, day: 7.1, city: null, year: "2025" }).rating).toBe(
      "Así valoran sus vecinos la seguridad de su barrio: 4,9 de noche y 7,1 de día, de 0 a 10.",
    );
  });
});
