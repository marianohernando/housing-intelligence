import { describe, expect, it } from "vitest";

import type { LandItem, SourcedValue, ViabilityDefaults } from "@/contracts/investor_zone_response";

import {
  adminUnitId,
  defaultLand,
  figure,
  gapsLine,
  initialFields,
  isoInWords,
  landName,
  missingFields,
  money,
  parcelsLine,
  parseNumber,
  rentRange,
  viabilityRequest,
  withoutMark,
} from "../investors";

// Test fixture: figures shaped as GET /api/v1/investors/zones/{id} gives them (Pinar del Rey, 19 nov)
function value(v: number | null, unit: string, mark: SourcedValue["mark"] = "dato"): SourcedValue {
  return { value: v, unit, mark, source: { text: "Fuente de prueba", dataset_ids: [] }, null_reason: v === null ? "SOURCE_NO_COVERAGE" : null };
}

const defaults: ViabilityDefaults = {
  sale_price_m2: value(4846.67, "€/m²"),
  new_build_premium_pct: value(9.3, "%"),
  rent_m2_month: value(15.94, "€/m²/mes"),
  pem_m2: value(644, "€/m²"),
  cost_coefficient: value(1.36, "×", "supuesto"),
  cost_parts: [],
  sales_costs_pct: value(8, "% de las ventas", "supuesto"),
  sales_cost_parts: [],
  target_margin_pct: value(20, "%", "supuesto"),
  adjust_floor_pct: value(10, "%", "supuesto"),
  household_income: value(41018, "€/hogar/año"),
  home_m2: value(80, "m²", "supuesto"),
  ltv_pct: value(80, "%", "supuesto"),
  loan_years: value(30, "años", "supuesto"),
  loan_rate_pct: value(3, "%", "supuesto"),
  effort_threshold_pct: value(30, "%", "supuesto"),
};

const parcel = (code: string, m2: number | null): LandItem => ({ kind: "parcela", code, name: `Calle ${code}`, parcel: null, buildable_m2: m2 });

describe("figures in words", () => {
  it("says the unknown as such, never 0", () => {
    expect(figure(value(null, "%"))).toBe("Sin dato");
    expect(figure(value(0, "%"))).toBe("0 %");
  });

  it("writes euros, rents and shares the Spanish way", () => {
    expect(figure(value(41018, "€/hogar/año"))).toBe("41.018 € al año");
    expect(figure(value(15.94, "€/m²/mes"), 2)).toBe("15,94 €/m² al mes");
    expect(figure(value(9.3, "%"), 1)).toBe("9,3 %");
    expect(money(850_000)).toBe("850.000 €");
    expect(money(35_823_698)).toBe("35,82 millones de €");
  });

  it("gives the rent range only when the source has one", () => {
    expect(rentRange({ ...value(15.94, "€/m²/mes"), low: 13.03, high: 17.82 })).toBe("La mitad de los contratos, entre 13,0 y 17,8 €/m² al mes.");
    expect(rentRange(value(15.94, "€/m²/mes"))).toBeNull();
  });

  it("dates the data in words", () => {
    expect(isoInWords("2026-11-18")).toBe("18 de noviembre de 2026");
    expect(isoInWords("ayer")).toBe("ayer");
  });

  it("drops the «supuesto:» the tag already says", () => {
    expect(withoutMark("supuesto: un piso de 2 o 3 dormitorios")).toBe("Un piso de 2 o 3 dormitorios");
    expect(withoutMark("Ley 12/2023")).toBe("Ley 12/2023");
  });
});

describe("the list of barrios", () => {
  it("says what the district lacks, FALTA before JUSTO, naming the district", () => {
    const district = { name: "Carabanchel" };
    expect(gapsLine({ district, gaps: { falta: 1, justo: 2, rows: ["Colegios", "Centros de salud", "Farmacias"] } })).toBe(
      "Falta en el distrito de Carabanchel: colegios; justo: centros de salud, farmacias.",
    );
    expect(gapsLine({ district, gaps: { falta: 0, justo: 1, rows: ["Centros de mayores"] } })).toBe(
      "Justo en el distrito de Carabanchel: centros de mayores.",
    );
    expect(gapsLine({ district, gaps: { falta: 0, justo: 0, rows: [] } })).toBe("En el distrito de Carabanchel no falta nada de lo que medimos.");
    expect(gapsLine({ district, gaps: null })).toBe("Sin datos de lo que falta en el distrito de Carabanchel.");
  });

  it("counts public land, and says nothing without it", () => {
    expect(parcelsLine(4, 19796.18)).toBe("4 parcelas públicas, 19.796 m² edificables");
    expect(parcelsLine(1, null)).toBe("1 parcela pública");
    expect(parcelsLine(0, 0)).toBeNull();
    expect(parcelsLine(null, null)).toBeNull();
  });

  it("takes only Madrid barrio codes from the address", () => {
    expect(adminUnitId("28079164")).toBe("ES.28.BAR.28079164");
    expect(adminUnitId("2807916")).toBeNull();
    expect(adminUnitId("28005001")).toBeNull();
  });
});

describe("the calculator", () => {
  it("starts on the largest parcel with a published area", () => {
    const land = defaultLand([parcel("a", 328), parcel("b", null), parcel("c", 12192)], []);
    expect(land?.code).toBe("c");
    expect(defaultLand([parcel("b", null)], [])).toBeNull();
    expect(landName({ ...parcel("x", 1), name: null })).toBe("Referencia x");
  });

  it("shows the defaults with Spanish decimals and reads them back", () => {
    const fields = initialFields(defaults, parcel("c", 12192));
    expect(fields.buildable_m2).toBe("12192");
    expect(fields.new_build_premium_pct).toBe("9,3");
    expect(fields.cost_coefficient).toBe("1,36");
    expect(parseNumber("9,3")).toBe(9.3);
    expect(parseNumber("1.36")).toBe(1.36);
    expect(parseNumber("12.192")).toBe(12192);
    expect(parseNumber("1.234.567,5")).toBe(1234567.5);
    expect(parseNumber("")).toBeNull();
    expect(parseNumber("abc")).toBeNull();
  });

  it("builds the request with the land as total or per m², and the demand check", () => {
    const fields = { ...initialFields(defaults, parcel("c", 12192)), land: "3200", land_unit: "m2" as const };
    const request = viabilityRequest(fields);
    expect(request).toMatchObject({
      buildable_m2: 12192,
      sale_price_m2: 4847,
      new_build_premium_pct: 9.3,
      pem_m2: 644,
      cost_coefficient: 1.36,
      land_eur_m2: 3200,
      demand: { household_income: 41018, home_m2: 80, ltv_pct: 80, loan_years: 30, loan_rate_pct: 3 },
    });
    expect(request).not.toHaveProperty("land_eur");
    const total = viabilityRequest({ ...fields, land_unit: "total" });
    expect(total).toMatchObject({ land_eur: 3200 });
    expect(viabilityRequest({ ...fields, land: "" })).not.toHaveProperty("land_eur_m2");
  });

  it("waits for the area, the price and the PEM", () => {
    const fields = initialFields(defaults, null);
    expect(missingFields(fields)).toEqual(["buildable_m2"]);
    expect(viabilityRequest(fields)).toBeNull();
    expect(viabilityRequest({ ...fields, buildable_m2: "0" })).toBeNull();
  });
});
