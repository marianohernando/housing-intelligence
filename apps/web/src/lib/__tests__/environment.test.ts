import { describe, expect, it } from "vitest";

import { airText, ENVIRONMENT_FEATURES, environmentFacts, noiseText, parkAndRideText, parkingText } from "../environment";
import type { FeatureValueRow } from "../features";
import type { Facility } from "../map/facilities";

// Test fixture: rows shaped as GET /features/{id}/values gives them (D-237), figures from 14 nov
function row(code: string, value: number | null, detail: FeatureValueRow["detail"] = null, period = "2025-01-01"): FeatureValueRow {
  return { territory_code: code, admin_unit_id: null, name: null, period_start: period, value, null_reason: value === null ? "SOURCE_NO_COVERAGE" : null, confidence: 0.9, detail };
}

function park(id: string, name: string, spaces: number | null, fee: Facility["fee"]): Facility {
  return { id, type: "aparcamiento", label: "Aparcamiento disuasorio", name, detail: null, source: null, dependency: null, lon: 0, lat: 0, spaces, fee };
}

const ALARM = /peligr|alarm|grave|malo|tóxic|nociv|insalubre/i;

describe("noiseText (zona.entorno.ruido)", () => {
  it("says the share of street above the limits by day and by night, with the map", () => {
    expect(noiseText(row("2807901", 38.14), row("2807901", 48.1))).toBe(
      "Calles con ruido alto: 38 % de día, 48 % de noche (Mapa Estratégico de Ruido 2021, Ayuntamiento de Madrid)",
    );
  });

  it("outside Madrid, or with half the figure, says there is no published figure: never 0", () => {
    expect(noiseText(null, null)).toBe("Calles con ruido alto: sin dato publicado");
    expect(noiseText(row("28065", null), row("28065", null))).toBe("Calles con ruido alto: sin dato publicado");
    expect(noiseText(row("2807901", 38), null)).toBe("Calles con ruido alto: sin dato publicado");
  });
});

describe("airText (zona.entorno.aire)", () => {
  it("names the zone's own station and the EU limit for 2030", () => {
    const getafe = row("28065", 25.6, { station: "Getafe", station_code: "28065014", own: true, distance_km: 1 });
    expect(airText(getafe)).toBe("Aire: NO₂ medio 2025, 25,6 µg/m³ en la estación de Getafe (límite UE 2030: 20)");
  });

  it("says when the station is another zone's, and how far", () => {
    const boadilla = row("28022", 14.63, { station: "Majadahonda", station_code: "28080003", own: false, distance_km: 3.5 });
    expect(airText(boadilla)).toBe(
      "Aire: NO₂ medio 2025, 14,6 µg/m³ en la estación de Majadahonda, la más cercana de su zona de calidad del aire, a 3,5 km (límite UE 2030: 20)",
    );
  });

  it("never gives a figure without its station", () => {
    expect(airText(row("28065", 25.6))).toBe("Aire: sin dato publicado");
    expect(airText(null)).toBe("Aire: sin dato publicado");
  });
});

describe("parkingText and parkAndRideText (zona.entorno.aparcamiento)", () => {
  it("says the minutes to the nearest public car park, and nothing near past 30", () => {
    expect(parkingText(row("2807901", 4.7))).toBe("Aparcamiento público a unos 5 min andando");
    expect(parkingText(row("28120", 423.5))).toBe("Ningún aparcamiento público de los publicados en abierto a menos de 30 min andando");
    expect(parkingText(null)).toBeNull();
  });

  it("names one park-and-ride with its spaces and fee, and sums several", () => {
    expect(parkAndRideText([park("a", "Aparcamiento disuasorio Doce de Octubre", 210, "free")], "Usera")).toBe(
      "Aparcamiento disuasorio gratuito (210 plazas) en Usera: Doce de Octubre",
    );
    const getafe = [park("a", "Aparcamiento disuasorio Getafe - Sector 3", 996, "free"), park("b", "Aparcamiento disuasorio Getafe - Industrial", 27, "free")];
    expect(parkAndRideText(getafe, "Getafe")).toBe("2 aparcamientos disuasorios en Getafe, con 1.023 plazas (todos gratuitos)");
  });

  it("leaves out the spaces when one does not say them, and the zones without any", () => {
    const mixed = [park("a", "Aparcamiento disuasorio X", 100, "free"), park("b", "Aparcamiento disuasorio Aviación Española", null, null)];
    expect(parkAndRideText(mixed, "Latina")).toBe("2 aparcamientos disuasorios en Latina (1 gratuito)");
    expect(parkAndRideText([], "Pinto")).toBeNull();
  });
});

describe("environmentFacts", () => {
  const rows = {
    [ENVIRONMENT_FEATURES.noiseDay]: [row("2807901", 38.1), row("28065", null)],
    [ENVIRONMENT_FEATURES.noiseNight]: [row("2807901", 48.1), row("28065", null)],
    [ENVIRONMENT_FEATURES.air]: [row("28065", 25.6, { station: "Getafe", own: true, distance_km: 1 })],
    [ENVIRONMENT_FEATURES.parking]: [row("28065", 23.2)],
  };

  it("brings every line of a municipio: noise without a figure, air and car parks", () => {
    const facts = environmentFacts("28065", rows, [], "Getafe");
    expect(facts).toMatchObject({ noiseKnown: false, parking: "Aparcamiento público a unos 23 min andando", parkAndRide: null });
    expect(facts?.air).toContain("Getafe");
  });

  it("shows nothing for a zone the API says nothing about, and never an alarm word", () => {
    expect(environmentFacts("28999", rows, [], "Ninguno")).toBeNull();
    const facts = environmentFacts("2807901", rows, [], "Centro");
    expect(Object.values(facts ?? {}).join(" ")).not.toMatch(ALARM);
  });
});
