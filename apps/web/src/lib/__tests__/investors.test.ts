import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import type { LandItem, SourcedValue, ViabilityDefaults } from "@/contracts/investor_zone_response";

import {
  breakEvenFreeText,
  roughMoney,
  breakEvenText,
  breakEvenValue,
  CALCULATOR_TEXT,
  costNowValue,
  adminUnitId,
  areaFacts,
  defaultLand,
  emptyLandText,
  FIELD_LIMITS,
  fieldErrors,
  LAND_LIMITS,
  landCaution,
  remainingLine,
  SHEET_TEXT,
  uniqueDatasets,
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
  residualText,
  viabilityRequest,
  withoutMark,
} from "../investors";
import { INVESTOR_METHOD as M } from "@/lib/investorMethod";

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

  it("names the method by the version the API serves, never «viabilidad v0 (D-248)» (F14)", () => {
    expect(SHEET_TEXT.version("2026-11-19", "viability-0.2")).toBe("Datos calculados el 19 de noviembre de 2026. Método: viability-0.2.");
    expect(SHEET_TEXT.version(null, "parcels-0.1")).toBe("Método: parcels-0.1.");
    expect(SHEET_TEXT.version("2026-11-19", null)).toBe("Datos calculados el 19 de noviembre de 2026.");
    expect(SHEET_TEXT.version(null, null)).toBe("");
    expect(CALCULATOR_TEXT.method("viability-0.2")).toBe("Método de la cuenta: viability-0.2.");
    expect(JSON.stringify(SHEET_TEXT.version("2026-11-19", "viability-0.2"))).not.toContain("D-248");
  });

  it("says the zone the vacant land figure is of: 13.813 is all of Madrid, not the barrio (F14)", () => {
    expect(SHEET_TEXT.vacant("municipio")).toBe("Suelo vacante de toda la ciudad (Catastro)");
    expect(SHEET_TEXT.vacant("distrito")).toBe("Suelo vacante del distrito (Catastro)");
    expect(SHEET_TEXT.vacant("barrio")).toBe("Suelo vacante del barrio (Catastro)");
    expect(SHEET_TEXT.vacant(null)).toBe("Suelo vacante (Catastro)");
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

  it("says a planning area's situation and type of home in words", () => {
    const area = { kind: "ambito", code: "APR.16.04", name: "UVA de Hortaleza", buildable_m2: 26322, stage: "edificacion", use: "colectiva" };
    // D-252 (audit B10): never «se puede construir ya»
    expect(areaFacts(area)).toEqual([
      "En fase de edificación, según el Ayuntamiento: no quiere decir que se pueda construir ya (hace falta licencia)",
      "vivienda colectiva",
    ]);
    expect(areaFacts({ ...area, stage: "otra", use: null })).toEqual([]);
    expect(areaFacts(parcel("x", 1))).toEqual([]);
  });

  it("says when a planning area also covers other barrios", () => {
    expect(remainingLine(15000, 0)).toBe("15.000 m² edificables en ámbitos del Plan General");
    expect(remainingLine(15000, 2)).toBe("15.000 m² edificables en ámbitos del Plan General (alguno ocupa también otros barrios y cuenta entero aquí)");
    expect(remainingLine(null, null)).toBeNull();
    expect(remainingLine(0, 0)).toBeNull();
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

  it("checks each field against the same range and step as the API", () => {
    const fields = initialFields(defaults, parcel("c", 12192));
    expect(fieldErrors(fields)).toEqual({});
    expect(fieldErrors({ ...fields, buildable_m2: "40" })).toEqual({ buildable_m2: "Pon un número entre 50 y 500.000." });
    expect(fieldErrors({ ...fields, loan_years: "30,5" })).toEqual({ loan_years: "Pon un número entero entre 5 y 40." });
    expect(fieldErrors({ ...fields, sale_price_m2: "mucho" })).toHaveProperty("sale_price_m2");
    // A target under 10 % is fine: the floor of «ajustar» comes down to it (never a 422)
    expect(fieldErrors({ ...fields, target_margin_pct: "5" })).toEqual({});
    // The land's range follows its unit
    expect(fieldErrors({ ...fields, land: "40000", land_unit: "m2" })).toHaveProperty("land");
    expect(fieldErrors({ ...fields, land: "40000", land_unit: "total" })).toEqual({});
    expect(viabilityRequest({ ...fields, loan_years: "30,5" })).toBeNull();
  });

  it("uses the ranges of the API's JSON Schema", () => {
    const path = fileURLToPath(new URL("../../../../../data/schemas/api/viability_request.schema.json", import.meta.url));
    const schema = JSON.parse(readFileSync(path, "utf8"));
    const demand = schema.$defs.DemandRequest.properties;
    const bounds = (prop: { minimum?: number; maximum?: number; anyOf?: { minimum?: number; maximum?: number }[] }) => {
      const own = prop.anyOf?.[0] ?? prop;
      return { min: own.minimum, max: own.maximum };
    };
    for (const [name, limit] of Object.entries(FIELD_LIMITS)) {
      const prop = schema.properties[name] ?? demand[name];
      expect(prop, name).toBeDefined();
      expect({ min: limit.min, max: limit.max }, name).toEqual(bounds(prop));
      expect(Boolean(limit.integer), name).toBe(prop.type === "integer");
    }
    expect(LAND_LIMITS.total).toEqual(bounds(schema.properties.land_eur));
    expect(LAND_LIMITS.m2).toEqual(bounds(schema.properties.land_eur_m2));
  });

  it("warns that free prices do not hold for protected housing or a concession", () => {
    const avs = { ...parcel("a", 12192), manager: "AVS- Agencia de Vivienda Social (antes, IVIMA)" };
    expect(landCaution(avs)).toMatch(/^Es de la Agencia de Vivienda Social: suele ir a vivienda protegida/);
    const concession = { ...parcel("b", 1000), regime: "concesion", manager: "Ayuntamiento de Alcobendas" };
    expect(landCaution(concession)).toMatch(/^Se ofrece en concesión.*no valen para vivienda protegida ni para una concesión/);
    expect(landCaution({ ...parcel("c", 328), regime: "venta", manager: "Ayuntamiento de Madrid" })).toBeNull();
    expect(landCaution(null)).toBeNull();
  });

  it("never says «0 parcelas» (D-246)", () => {
    expect(SHEET_TEXT.parcels(0)).toBe("Parcelas públicas para vivienda");
    expect(SHEET_TEXT.parcels(1)).toBe("1 parcela pública para vivienda");
    expect(SHEET_TEXT.parcels(4)).toBe("4 parcelas públicas para vivienda");
  });

  it("says «sin dato» for land not loaded yet, and «ninguna» only for a real 0", () => {
    // null: the feature is not in the database yet (after a deploy, before the sync)
    expect(emptyLandText(null, "parcelas")).toBe("Aún sin dato de las parcelas públicas de este barrio.");
    expect(emptyLandText(undefined, "parcelas")).toBe("Aún sin dato de las parcelas públicas de este barrio.");
    expect(emptyLandText(0, "parcelas")).toBe("El Portal del Suelo no ofrece ahora ninguna parcela residencial en este barrio.");
    expect(emptyLandText(null, "ambitos")).toBe("Aún sin dato para este barrio.");
    expect(emptyLandText(0, "ambitos")).toBe("Ningún ámbito del barrio tiene edificabilidad residencial disponible.");
  });

  it("lists each dataset once", () => {
    expect(uniqueDatasets([{ dataset_id: "a" }, { dataset_id: "b" }, { dataset_id: "a" }])).toEqual([{ dataset_id: "a" }, { dataset_id: "b" }]);
  });

  it("waits for the area, the price and the PEM", () => {
    const fields = initialFields(defaults, null);
    expect(missingFields(fields)).toEqual(["buildable_m2"]);
    expect(viabilityRequest(fields)).toBeNull();
    expect(viabilityRequest({ ...fields, buildable_m2: "0" })).toBeNull();
  });
});

describe("the cost and its break-even (D-252)", () => {
  const free = { construction_m2: 2800, pem_m2: 1866.67, coefficient: 4.6667, current_construction_m2: 875.84, land_counted: false, reachable: true };

  it("says up to what construction cost the target margin holds, as PEM and as coefficient", () => {
    expect(breakEvenText(free)).toBe(
      "Sin pagar nada por el suelo, la promoción llega al margen objetivo mientras la construcción cueste menos de 2.800 €/m² construido (PEM × coeficiente). Es un PEM de hasta 1.867 €/m² con tu coeficiente, o un coeficiente de hasta 4,67 sobre tu PEM.",
    );
    const withLand = { ...free, construction_m2: 600, pem_m2: 400, coefficient: 1, land_counted: true };
    expect(breakEvenText(withLand)).toMatch(/^Con el precio del suelo que has puesto, la promoción llega al margen objetivo mientras la construcción cueste menos de 600 €\/m² construido/);
    expect(breakEvenFreeText(free)).toBe("Con el suelo gratis, hasta 2.800 €/m² construido.");
    expect(costNowValue(free)).toBe("876 €/m² construido (PEM × coeficiente)");
  });

  it("says when not even free construction reaches the target margin", () => {
    const none = { ...free, construction_m2: -1200, land_counted: true, reachable: false };
    expect(breakEvenValue(none)).toBe("Ni gratis");
    expect(breakEvenText(none)).toBe("Con el precio del suelo que has puesto, ni con la construcción gratis llega la promoción al margen objetivo.");
    expect(breakEvenFreeText({ ...none, land_counted: false })).toBe("Ni con el suelo gratis llega al margen objetivo.");
    // Review of #109, R-04: never «un coeficiente de hasta 0,8»
    const tight = { ...free, construction_m2: 700, pem_m2: 515.65, coefficient: 0.79, land_counted: true };
    expect(breakEvenText(tight)).toMatch(/\(PEM × coeficiente\)\. Con tu PEM, ni con el PEM solo \(coeficiente 1\) llega\.$/);
  });

  it("says what the cost counts and what it leaves out, and that the calculator is for housing", () => {
    expect(CALCULATOR_TEXT.intro).toMatch(/^Calcula solo vivienda/);
    expect(CALCULATOR_TEXT.costIncludes(["honorarios"])).toContain("con el coeficiente, honorarios.");
    for (const left of ["El suelo", "La urbanización", "El derribo", "Los sótanos", "La financiación", "El IVA", "imprevistos"]) {
      expect(CALCULATOR_TEXT.costExcludes.some((line) => line.includes(left))).toBe(true);
    }
  });

  it("says the residual with three figures, never cents on assumptions (D-252, D7)", () => {
    expect(roughMoney(66_958_000)).toBe("unos 67 millones de €");
    expect(roughMoney(140_490_000)).toBe("unos 140 millones de €");
    expect(roughMoney(1_234_567)).toBe("unos 1,23 millones de €");
    expect(roughMoney(900_091)).toBe("unos 900.000 €");
    expect(roughMoney(4297.4)).toBe("unos 4.300 €");
    expect(roughMoney(1_002_000)).toBe("alrededor de 1 millón de €"); // review of #109, R-10
  });

  it("says the residual per m² buildable and as a share of the sales, and what the account leaves out (F14)", () => {
    // Méndez Álvaro as the jury read it: 61,2 M€ on 13.121 m² and 109,4 M€ of sales
    const mendez = { residual_land_value: 61_234_000, residual_land_value_m2: 4_666.9, revenue: 109_400_000 };
    expect(residualText(mendez)).toBe("unos 61,2 millones de € (unos 4.670 € por m² edificable; el 56 % de los ingresos por ventas)");
    // Not even free land reaches the target margin: no share of a negative figure
    const none = { residual_land_value: -200_000, residual_land_value_m2: -150, revenue: 1_000_000 };
    expect(residualText(none)).toBe("unos -200.000 € (unos -150 € por m² edificable)");
    // The four parts it names are not in the cost: the PEM goes on the buildable m² above ground, and the coefficient's and
    // the sales costs' parts are others
    expect(CALCULATOR_TEXT.residualLeavesOut).toBe("La cuenta no incluye sótanos, urbanización, financiación ni IVA.");
    const parts = [...M.costParts, ...M.salesCostParts].map((p) => p.label.toLowerCase()).join(" · ");
    for (const left of ["sótano", "urbaniza", "financia", "iva"]) expect(parts).not.toContain(left);
  });

  it("gives the semaphore and the scenarios from the code's figures (D-252, D8)", () => {
    expect(CALCULATOR_TEXT.thresholds).toContain(`«Ajustar» entre el ${M.adjustFloorPct} % y el objetivo`);
    expect(CALCULATOR_TEXT.thresholds).toContain("pesimista: −10 % y +15 %");
    expect(CALCULATOR_TEXT.thresholds).toContain("Orden ECO/805/2003, disposición adicional sexta");
    expect(CALCULATOR_TEXT.thresholds).toContain(`al menos un ${M.appraisalMinMarginPct} %`);
  });

  it("says where the cost comes from and how much it varies, without «mínimo oficial» (D-252, D4)", () => {
    const [permits, crg, st] = CALCULATOR_TEXT.costReferences();
    expect(permits?.text).toContain(`${M.pem.eurM2} €/m²`);
    expect(crg?.text).toContain("bloque abierto, 871–1.064 €/m²");
    expect(crg?.text).toContain(`punto medio del bloque abierto: ${M.costReferences.crg.defaultPem} €/m² (supuesto)`);
    expect(st?.text).toContain("1.360 €/m²");
    expect(st?.text).toContain("según la prensa");
    expect(st?.text).toContain("No sabemos si incluye gastos generales y beneficio"); // R-03
    expect(JSON.stringify(CALCULATOR_TEXT)).not.toContain("Mínimo oficial");
    // The permits' PEM as the API reads it from the CM dataset, with its source
    const [fromApi] = CALCULATOR_TEXT.costReferences(value(644, "€/m²"));
    expect(fromApi?.text).toContain("(2025): 644 €/m²");
    expect(fromApi?.text).toContain("Fuente: Fuente de prueba.");
    expect(fromApi?.mark).toBe("dato");
  });
});
