import { describe, expect, it } from "vitest";

import { displayName, titleCase } from "../names";

describe("displayName (same cases as tests/unit/geo/test_names.py)", () => {
  it.each([
    ["MADRID", "Madrid"],
    ["ROZAS DE MADRID, LAS", "Las Rozas de Madrid"],
    ["ALAMO, EL", "El Alamo"],
    ["SAN SEBASTIAN DE LOS REYES", "San Sebastian de los Reyes"],
    ["VILLANUEVA DE LA CAÑADA", "Villanueva de la Cañada"],
    ["  TORREJON   DE ARDOZ ", "Torrejon de Ardoz"],
    ["Fuencarral-El Pardo", "Fuencarral-El Pardo"],
    ["Chamartín", "Chamartín"],
  ])("%s -> %s", (official, readable) => {
    expect(displayName(official)).toBe(readable);
  });
});

describe("titleCase (place names in upper case, e.g. metro stations)", () => {
  it("capitalises words and keeps Spanish particles in lower case", () => {
    expect(titleCase("CONCHA ESPINA")).toBe("Concha Espina");
    expect(titleCase("PATRIARCA OBISPO EIJO GARAY")).toBe("Patriarca Obispo Eijo Garay");
    expect(titleCase("PLAZA DE CASTILLA")).toBe("Plaza de Castilla");
  });

  it("leaves mixed-case names alone", () => {
    expect(titleCase("Madrid-Chamartín-Clara Campoamor")).toBe("Madrid-Chamartín-Clara Campoamor");
  });
});
