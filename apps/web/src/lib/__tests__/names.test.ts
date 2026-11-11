import { describe, expect, it } from "vitest";

import { titleCase } from "../names";

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
