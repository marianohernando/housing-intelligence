import { describe, expect, it } from "vitest";

import { type PlaceFeature, pickKeyPoints, placesInZone } from "../map/places";

function place(name: string, category: string, subcategory: string, lon: number, lat: number, seccion = "ES.28.SEC.2807905001", municipio = "28079"): PlaceFeature {
  return {
    type: "Feature",
    id: `${name}-${lon}-${lat}`,
    geometry: { type: "Point", coordinates: [lon, lat] },
    properties: { name, category, subcategory, municipio, seccion },
  };
}

describe("placesInZone", () => {
  const inside = place("CONCHA ESPINA", "transport", "metro", -3.677, 40.451);
  const otherDistrict = place("SOL", "transport", "metro", -3.703, 40.417, "ES.28.SEC.2807901001");
  const otherMunicipio = place("MOSTOLES CENTRAL", "transport", "cercanias", -3.86, 40.32, "ES.28.SEC.2809201001", "28092");
  const noSection = place("SIN SECCION", "transport", "metro", -3.68, 40.45, "", "28079");

  it("keeps a district's places by the census section they fall in", () => {
    expect(placesInZone([inside, otherDistrict, otherMunicipio, noSection], { level: "distrito", code: "2807905" })).toEqual([inside]);
  });

  it("keeps a municipio's places by their municipio code", () => {
    expect(placesInZone([inside, otherMunicipio], { level: "municipio", code: "28092" })).toEqual([otherMunicipio]);
  });
});

describe("pickKeyPoints", () => {
  const center: [number, number] = [-3.68, 40.46];
  const places = [
    place("CONCHA ESPINA", "transport", "metro", -3.677, 40.451),
    place("Chamartín", "transport", "metro", -3.682, 40.472),
    place("Chamartín", "transport", "metro", -3.6821, 40.4721),
    place("Madrid-Chamartín-Clara Campoamor", "transport", "cercanias", -3.682, 40.472),
    place("Paseo De La Habana - Veracruz", "transport", "emt", -3.68, 40.46),
    place("Farmacia · CALLE de Mateo Inurria 9", "health", "Farmacia", -3.68, 40.461),
    place("Centro de salud (Madrid)", "health", "Centro de salud", -3.67, 40.445),
    place("Hospital general (Madrid)", "health", "Hospital general", -3.69, 40.47),
    place("PATRIARCA OBISPO EIJO GARAY", "education", "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", -3.675, 40.455),
    place("WILLOUGHBY COLLEGE", "education", "CENTRO PRIVADO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA", -3.68, 40.46),
  ];
  const points = pickKeyPoints(places, center);

  it("shows at most two stations, one health centre and one public school", () => {
    expect(points.map((p) => p.kind)).toEqual(["transporte", "transporte", "salud", "colegio"]);
  });

  it("prefers commuter rail, then spreads the rest away from what is already shown", () => {
    expect(points[0]?.name).toBe("Madrid-Chamartín-Clara Campoamor");
    expect(points[1]?.name).toBe("Concha Espina");
  });

  it("never picks bus stops, pharmacies or private schools as key points", () => {
    const names = points.map((p) => p.name);
    expect(names).not.toContain("Paseo De La Habana - Veracruz");
    expect(points.some((p) => p.label === "Farmacia")).toBe(false);
    expect(names).not.toContain("Willoughby College");
  });

  it("labels each point in plain words, without the generic «(Madrid)» suffix", () => {
    expect(points.map((p) => [p.label, p.name])).toEqual([
      ["Estación", "Madrid-Chamartín-Clara Campoamor"],
      ["Metro", "Concha Espina"],
      ["Centro de salud", null],
      ["Colegio", "Patriarca Obispo Eijo Garay"],
    ]);
  });

  it("returns nothing for a zone without places", () => {
    expect(pickKeyPoints([], center)).toEqual([]);
  });
});

describe("pickKeyPoints spreads labels across kinds", () => {
  it("picks the public school farthest from the points already shown", () => {
    const center: [number, number] = [-3.68, 40.46];
    const points = pickKeyPoints(
      [
        place("Madrid-Chamartín-Clara Campoamor", "transport", "cercanias", -3.682, 40.472),
        place("Centro de salud (Madrid)", "health", "Centro de salud", -3.68, 40.46),
        place("CERCA DEL CENTRO", "education", "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", -3.6801, 40.4601),
        place("LEJOS SUR", "education", "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", -3.675, 40.44),
      ],
      center,
    );
    expect(points.find((p) => p.kind === "colegio")?.name).toBe("Lejos Sur");
  });
});

describe("pickKeyPoints only labels places in view", () => {
  const center: [number, number] = [-3.68, 40.46];
  const places = [
    place("Madrid-Chamartín-Clara Campoamor", "transport", "cercanias", -3.682, 40.472),
    place("CONCHA ESPINA", "transport", "metro", -3.677, 40.451),
    place("Centro de salud (Madrid)", "health", "Centro de salud", -3.69, 40.47),
    place("Hospital general (Madrid)", "health", "Hospital general", -3.672, 40.455),
    place("PATRIARCA OBISPO EIJO GARAY", "education", "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", -3.675, 40.455),
  ];
  // In view: everything east of -3.68 (the rest would sit under the side cards)
  const eastOnly = (lon: number) => lon > -3.68;

  it("skips places out of view, falling back to the next class of the same kind", () => {
    const points = pickKeyPoints(places, center, { inView: eastOnly });
    expect(points.map((p) => [p.label, p.name])).toEqual([
      ["Metro", "Concha Espina"],
      ["Hospital", null],
      ["Colegio", "Patriarca Obispo Eijo Garay"],
    ]);
  });

  it("leaves a kind out rather than labelling it off-screen", () => {
    expect(pickKeyPoints(places, center, { inView: (lon) => lon > -3.674 }).map((p) => p.kind)).toEqual(["salud"]);
    expect(pickKeyPoints(places, center, { inView: () => false })).toEqual([]);
  });

  it("passes longitude and latitude to the visibility check", () => {
    const seen: [number, number][] = [];
    pickKeyPoints(places.slice(0, 1), center, {
      inView: (lon, lat) => {
        seen.push([lon, lat]);
        return true;
      },
    });
    expect(seen).toEqual([[-3.682, 40.472]]);
  });
});

describe("pickKeyPoints keeps labels apart", () => {
  const center: [number, number] = [-3.68, 40.46];
  const places = [
    place("Madrid-Chamartín-Clara Campoamor", "transport", "cercanias", -3.682, 40.472),
    place("PEGADA A LA ESTACION", "transport", "metro", -3.6821, 40.4721),
    place("Centro de salud (Madrid)", "health", "Centro de salud", -3.6822, 40.4719),
    place("PATRIARCA OBISPO EIJO GARAY", "education", "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", -3.675, 40.455),
  ];
  // Two labels collide when their pins are less than 0.001° apart (a stand-in for screen space)
  const apart = (a: { lon: number; lat: number }, b: { lon: number; lat: number }) =>
    Math.hypot(a.lon - b.lon, a.lat - b.lat) >= 0.001;

  it("drops a point whose label would cover one already shown", () => {
    const points = pickKeyPoints(places, center, { apart });
    expect(points.map((p) => p.name)).toEqual(["Madrid-Chamartín-Clara Campoamor", "Patriarca Obispo Eijo Garay"]);
  });

  it("keeps every point when nothing collides", () => {
    expect(pickKeyPoints(places, center).map((p) => p.kind)).toEqual(["transporte", "transporte", "salud", "colegio"]);
  });
});
