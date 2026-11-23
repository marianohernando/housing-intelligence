import { describe, expect, it } from "vitest";

import type { ParcelBlock, PlanningBlock, UseFigure, VedaStage } from "@/contracts/parcel_sheet_response";
import { ApiError, createApi, parcelPath } from "@/lib/api";
import { INVESTOR_METHOD } from "@/lib/investorMethod";
import {
  ambitText,
  areaText,
  buildabilityMark,
  buildableText,
  byUseSource,
  calculatorStart,
  catalogText,
  byUseText,
  dayMonthYear,
  DEMO_PARCELS,
  degradedLines,
  divisionText,
  instrumentText,
  isCatalogued,
  parcelHref,
  parcelRc,
  planUseSource,
  planUseText,
  publicLandText,
  qualificationText,
  SEARCH_TEXT,
  SHEET_TEXT,
  sentence,
  SERVICES_TEXT,
  servicesSignal,
  USE_TEXT,
  landUseLabel,
  landUseNote,
  vacantText,
} from "@/lib/parcels";

const PARCEL: ParcelBlock = {
  rc14: "1111111VK1111A",
  address: "Calle de Prueba 1, 28001 Madrid",
  area_m2: 68,
  rustic: false,
  is_vacant: false,
  horizontal_division: true,
  units: {
    total: 6,
    by_use: [
      { use: "Residencial", count: 5, built_m2: 314 },
      { use: "Comercial", count: 1, built_m2: 62 },
    ],
  },
  built_m2: 376,
  current_use: "Residencial",
  official_url: null,
  observed_at: "2026-11-19",
};

function planning(extra: Partial<PlanningBlock>): PlanningBlock {
  return {
    code: "8.3.a",
    name: "ZONA 8 GRADO 3º - NIVEL a",
    kind: "norma_zonal",
    norma_zonal: { nz: 8, grado: 3, nivel: "a" },
    use: "RESIDENCIAL VIVIENDA UNIFAMILIAR",
    urban_parcel: null,
    instrument: null,
    sheet_url: null,
    sheet_label: null,
    viewer_url: "https://geoportal.madrid.es/",
    notice: "Información urbanística sin valor jurídico (Ayuntamiento de Madrid). Consulte la ficha oficial.",
    observed_at: "2026-11-19",
    ...extra,
  };
}

describe("«Busca tu parcela» (D-250)", () => {
  it("reads a reference as the API does: 14, 18 or 20 characters give the parcel", () => {
    expect(parcelRc("2122202vk4722a")).toBe("2122202VK4722A");
    expect(parcelRc(" 9943003 VK3794D ")).toBe("9943003VK3794D");
    expect(parcelRc("9943003VK3794D0001ZO")).toBe("9943003VK3794D");
    expect(parcelRc("9943003-VK3794D-0001")).toBe("9943003VK3794D");
    for (const wrong of ["", "12345", "2122202VK4722A0", "calle mayor 61"]) expect(parcelRc(wrong)).toBeNull();
    expect(parcelHref("2122202VK4722A")).toBe("/inversores/parcela/2122202VK4722A");
  });

  it("offers the four demo parcels, each a valid reference", () => {
    expect(DEMO_PARCELS.map((d) => d.rc14)).toEqual(["2122202VK4722A", "3959601VK4735H", "0390314VK4709A", "9943003VK3794D"]);
    for (const demo of DEMO_PARCELS) expect(parcelRc(demo.rc14)).toBe(demo.rc14);
  });

  it("asks the API with exactly one way in", () => {
    expect(parcelPath({ rc: "2122202VK4722A" })).toBe("/api/v1/investors/parcels?rc=2122202VK4722A");
    expect(parcelPath({ lat: 40.4, lon: -3.7 })).toBe("/api/v1/investors/parcels?lat=40.400000&lon=-3.700000");
    expect(parcelPath({ address: "calle de prueba 1" })).toBe("/api/v1/investors/parcels?address=calle+de+prueba+1");
  });

  it("keeps an error's details (an address's candidates, the parcels near a point)", async () => {
    const body = { detail: { code: "NOT_FOUND", message: "street", details: { nearest: [{ rc14: "1111111VK1111A" }] } } };
    const fetchImpl = async () => new Response(JSON.stringify(body), { status: 404, headers: { "content-type": "application/json" } });
    const error = await createApi("http://api.test", fetchImpl)
      .parcel({ lat: 40.4, lon: -3.7 })
      .catch((exc: unknown) => exc);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).code).toBe("NOT_FOUND");
    expect((error as ApiError).details.nearest).toEqual([{ rc14: "1111111VK1111A" }]);
  });

  it("says the parcel in words, never 0 for unknown and never a unit by its floor", () => {
    expect(areaText(2843)).toBe("2.843 m²");
    expect(areaText(null)).toBe("Sin dato");
    // D-252 (audit B3): «solar» is a legal condition with services; this is only «sin edificar»
    expect(SHEET_TEXT.vacant).toBe("¿Está sin edificar? (según su uso en el Catastro)");
    expect(vacantText({ ...PARCEL, is_vacant: true })).toBe("Sí");
    expect(vacantText({ ...PARCEL, is_vacant: null })).toBe("Sin dato");
    expect(divisionText(PARCEL)).toBe("Sí: 6 inmuebles (5 residencial, 314 m²; 1 comercial, 62 m²)");
    expect(divisionText({ ...PARCEL, horizontal_division: false, units: null })).toBe("No");
  });

  it("says the planning: the norma zonal with its grado, or the area with its name", () => {
    expect(qualificationText(planning({}))).toBe("Norma zonal 8, grado 3º, nivel a");
    expect(qualificationText(planning({ code: "4", norma_zonal: { nz: 4 }, name: "NZ 4" }))).toBe("Norma zonal 4");
    const area = planning({ code: "APR.02.06", kind: "APR", norma_zonal: null, name: "MÉNDEZ ÁLVARO NORTE I" });
    expect(qualificationText(area)).toBe("Área de planeamiento remitido APR.02.06: Méndez Álvaro Norte I");
    expect(sentence("RESIDENCIAL VIVIENDA COLECTIVA")).toBe("Residencial vivienda colectiva");
    expect(sentence("Ya en minúsculas")).toBe("Ya en minúsculas");
    const instrument = planning({ instrument: { figure: "MPR.02.391", name: "Tercera Modificación", file_number: "711/2014/11518", url: null } });
    expect(instrumentText(instrument)).toBe("MPR.02.391 · Tercera Modificación · expediente 711/2014/11518");
    expect(instrumentText(planning({}))).toBeNull();
  });

  it("marks the buildability with a word: official is data, the rest say what they are", () => {
    expect(buildabilityMark("oficial")).toBe("dato");
    expect(buildabilityMark("supuesto")).toBe("supuesto");
    expect(buildabilityMark("sin_dato")).toBe("sin_dato");
    const base = { kind: "supuesto" as const, source: "x", editable: true as const };
    expect(buildableText({ ...base, value_m2: 351.4 })).toBe("351 m² edificables");
    expect(buildableText({ ...base, value_m2: 68.5 })).toBe("68,5 m² edificables");
    expect(buildableText({ ...base, value_m2: 13121 })).toBe("13.121 m² edificables");
    expect(buildableText({ ...base, value_m2: null })).toBe("Sin dato");
  });

  it("says what could not be read now and that the rest of the sheet is there", () => {
    expect(degradedLines({ parcel: PARCEL, degraded: [], fallback: null, planning: null })).toEqual([]);
    const lines = degradedLines({ parcel: PARCEL, degraded: ["context"], fallback: "demo_snapshot", planning: null });
    expect(lines[0]).toContain("19 de noviembre de 2026");
    expect(lines[1]).toBe(SHEET_TEXT.contextDown);
    expect(SHEET_TEXT.planningDown).toContain("el resto de la ficha sí");
    // No planning at all: its own section says so; a layer of it missing: a line up top (R-03)
    expect(degradedLines({ parcel: PARCEL, degraded: ["planning"], fallback: null, planning: null })).toEqual([]);
    const partial = degradedLines({ parcel: PARCEL, degraded: ["planning", "buildability"], fallback: null, planning: planning({}) });
    expect(partial).toEqual([SHEET_TEXT.instrumentDown, SHEET_TEXT.zDown]);
  });

  it("never calls our data «información catastral» and never under its own name", () => {
    const all = JSON.stringify({ SEARCH_TEXT, SHEET: Object.values(SHEET_TEXT).filter((v) => typeof v === "string") });
    expect(all.toLowerCase()).not.toMatch(/(información|ficha|cartografía) catastral/);
  });
});

describe("Edificabilidad por uso (D-252)", () => {
  const industrial: UseFigure = {
    use_class: "industrial",
    use: "INDUSTRIAL",
    value_m2: 3465.3,
    source: "VEDA Madrid (Ayuntamiento de Madrid), julio de 2026: edificabilidad de la parcela",
    dataset_id: "ayto_edificabilidad_remanente_ambitos",
    residential: false,
  };

  it("names each use in plain words, with público or privado when the plan says it", () => {
    expect(landUseLabel("dotacional", "privado")).toBe("Dotacional privado");
    expect(landUseLabel("dotacional", "publico")).toBe("Dotacional público");
    expect(landUseLabel("zona_verde", "publico")).toBe("Zona verde, de titularidad pública");
    expect(landUseLabel("industrial")).toBe("Industrial");
    for (const { label, plain } of Object.values(USE_TEXT)) {
      expect(label.length).toBeGreaterThan(0);
      expect(plain.endsWith(".")).toBe(true);
    }
  });

  it("says under the plan's use what it means, and that the calculator is for housing", () => {
    // The use's words already say the class: only what it means
    expect(landUseNote(planning({ use_class: "residencial" }))).toBe("Vivienda, en pisos o en casas, libre o con protección pública.");
    expect(landUseNote(planning({ use: "SIN USO PORMENORIZADO", use_class: "sin_uso" }))).toBe(
      "El plan aún no le ha fijado un uso concreto; lo fija el plan propio de su ámbito. La calculadora calcula solo vivienda.",
    );
    expect(landUseNote(planning({ use: "SERVICIOS TERCIARIOS OFICINAS", use_class: "terciario" }))).toMatch(/^Terciario: oficinas/);
    const note = landUseNote(planning({ use: "DOTACIONAL EQUIPAMIENTO PRIVADO EDUCATIVO", use_class: "dotacional", use_ownership: "privado" }));
    expect(note).toMatch(/^Dotacional privado: equipamientos como colegios/);
    expect(note).toMatch(/La calculadora calcula solo vivienda\.$/);
    expect(landUseNote(planning({}))).toBeNull();
  });

  it("gives the plan's m² by use on the urban parcel, a coefficient times its area as an assumption", () => {
    const housing = { use: "RESIDENCIAL VIVIENDA COLECTIVA", use_class: "residencial" as const, principal: true, value_m2: 60230.88 };
    expect(planUseText(housing, 16600.2)).toBe("Residencial: 60.231 m²");
    expect(planUseSource(housing)).toBe("Uso principal: residencial vivienda colectiva");
    const offices = { use: "SERVICIOS TERCIARIOS", use_class: "terciario" as const, principal: false, value_m2: 1200, coefficient: 1.2, assumed: true };
    expect(planUseText(offices, 1000)).toBe("Terciario: 1.200 m² (1,2 m²/m² × 1.000 m² de la parcela urbanística: supuesto)");
    expect(planUseSource(offices)).toBe("Otro uso: servicios terciarios");
    expect(SHEET_TEXT.planUsesTitle("MANZANA B")).toBe("Según el plan, la parcela urbanística MANZANA B tiene:");
    // D-252c: the snapshot's date, and a use without a figure said as such
    expect(dayMonthYear("2026-11-20")).toBe("20/11/2026");
    expect(SHEET_TEXT.planUsesSource("20/11/2026")).toContain(", del plan a fecha 20/11/2026.");
    expect(SHEET_TEXT.planUsesWithoutFigure("SIN USO PORMENORIZADO")).toBe(
      "El plan no fija uso pormenorizado ni cifra de edificabilidad para esta parcela urbanística.",
    );
    expect(SHEET_TEXT.planUsesWithoutFigure("RESIDENCIAL VIVIENDA COLECTIVA")).toBe(
      "El plan fija su uso principal (residencial vivienda colectiva), pero sin cifra de edificabilidad.",
    );
    expect(SHEET_TEXT.planUsesWithoutFigure("DOTACIONAL VÍA PÚBLICA PRINCIPAL")).toContain("(dotacional vía pública principal)");
    expect(SHEET_TEXT.planUsesCaveats).toContain("no lo que queda por construir");
    expect(SHEET_TEXT.planUsesCaveats).toContain("art. 7.2.8");
  });

  it("says the state of the planning area, or that the Ayuntamiento does not publish it", () => {
    const base = { code: "APR.04.09", tracked: true, pending: true, as_of: "2026-07-01", url: "https://datos.madrid.es/" };
    const phases = ["Planeamiento", "Gestión", "Proyecto de urbanización", "Obras de urbanización"].map((label) => ({ label, state: "Sin Iniciar" }));
    expect(ambitText({ ...base, phases, veda_stage: "pendiente_planeamiento" })).toBe(
      "Planeamiento: sin iniciar · Gestión: sin iniciar · Proyecto de urbanización: sin iniciar · Obras de urbanización: sin iniciar · VEDA: pendiente de planeamiento de desarrollo",
    );
    expect(ambitText({ ...base, tracked: false, pending: false, phases: [] })).toBe("El Ayuntamiento no publica su estado.");
  });

  it("says who offers public land and how, with the cautions of D-248", () => {
    const land = { kind: "parcela" as const, code: "00000002M", name: "Depósito 2", buildable_m2: 32697, regime: "venta", manager: "Metro de Madrid", stage: "sin_urbanizar" };
    expect(publicLandText(land)).toBe("Parcela del Portal del Suelo de la Comunidad de Madrid: En venta, la ofrece Metro de Madrid, sin urbanizar.");
    expect(publicLandText({ ...land, regime: "concesion", manager: null, stage: null })).toMatch(/^Parcela del Portal del Suelo de la Comunidad de Madrid: En concesión, derecho de superficie o alquiler\. Se ofrece en concesión/);
  });

  it("gives each source's figure with its own use and source, never split", () => {
    expect(byUseText(industrial)).toBe("Industrial: 3.465 m² edificables");
    expect(byUseSource(industrial)).toBe(`Uso en la fuente: industrial · ${industrial.source}`);
    expect(byUseSource({ ...industrial, use: "Residencial", use_class: "residencial" })).toMatch(/^Uso en la fuente: residencial · /);
    expect(SHEET_TEXT.byUseNote).toContain("sin repartirla entre usos");
    expect(SHEET_TEXT.housingOnly).toMatch(/^La calculadora calcula solo vivienda/);
  });
});

describe("Servicios y suministros, catálogo y primer filtro (D-253)", () => {
  it("says the planning's signal: a norma zonal, the area's works, or that it is not published", () => {
    expect(servicesSignal(planning({}))).toEqual([SERVICES_TEXT.zonal]);
    const phases = ["Planeamiento", "Gestión", "Proyecto de urbanización", "Obras de urbanización"].map((label) => ({ label, state: "Sin Iniciar" }));
    const ambit = { code: "APR.04.09", tracked: true, pending: true, phases, as_of: "2026-07-01", url: "https://datos.madrid.es/" };
    const area = planning({ code: "APR.04.09", kind: "APR", norma_zonal: null, ambit });
    // Almería 1: everything «sin iniciar», so no licence with the urbanization at once yet
    expect(servicesSignal(area)).toEqual([
      "Obras de urbanización del APR.04.09: sin iniciar, según el Ayuntamiento.",
      SERVICES_TEXT.planningFirst,
    ]);
    const done ={ ...ambit, pending: false, phases: phases.map((p) => ({ ...p, state: "Finalizado" })) };
    expect(servicesSignal(planning({ ...area, ambit: done }))).toEqual(["Obras de urbanización del APR.04.09: finalizado, según el Ayuntamiento."]);
    const unneeded = { ...done, phases: phases.map((p) => ({ ...p, state: "No necesita" })) };
    expect(servicesSignal(planning({ ...area, ambit: unneeded }))).toHaveLength(1);
    expect(servicesSignal(planning({ ...area, ambit: { ...ambit, tracked: false, phases: [] } }))).toEqual([SERVICES_TEXT.untracked]);
    expect(servicesSignal(null)).toEqual([]);
    expect(SERVICES_TEXT.portal("urbanizado")).toBe("El Portal del Suelo dice que esta parcela está urbanizada.");
    expect(SERVICES_TEXT.portal("en_gestion")).toBeNull();
  });

  it("says a licence with the urbanization at once only when planning and management are finished", () => {
    const phase = (label: string, state: string) => ({ label, state });
    const ambit = (planeamiento: string, gestion: string) => ({
      code: "APR.02.06",
      tracked: true,
      pending: true,
      phases: [
        phase("Planeamiento", planeamiento),
        phase("Gestión", gestion),
        phase("Proyecto de urbanización", "Finalizado"),
        phase("Obras de urbanización", "En Ejecución"),
      ],
      as_of: "2026-07-01",
      url: "https://datos.madrid.es/",
    });
    const area = (a: ReturnType<typeof ambit>) => planning({ code: "APR.02.06", kind: "APR", norma_zonal: null, ambit: a });
    const works = "Obras de urbanización del APR.02.06: en ejecución, según el Ayuntamiento.";
    // Only the urbanization is left: the law allows the licence with it at once
    expect(servicesSignal(area(ambit("Finalizado", "Finalizado")))).toEqual([works, SERVICES_TEXT.worksPending]);
    expect(servicesSignal(area(ambit("PGOUM-97", "No Necesita")))).toEqual([works, SERVICES_TEXT.worksPending]);
    // Planning or management not finished: first them, in plain words and without articles
    expect(servicesSignal(area(ambit("Sin Iniciar", "Finalizado")))).toEqual([works, SERVICES_TEXT.planningFirst]);
    expect(servicesSignal(area(ambit("Finalizado", "En Tramitación")))).toEqual([works, SERVICES_TEXT.planningFirst]);
    expect(SERVICES_TEXT.planningFirst).toBe("Antes de pedir licencia, el ámbito necesita su planeamiento y su gestión.");
    expect(SERVICES_TEXT.planningFirst).not.toMatch(/art\.|Ley/);
  });

  it("counts VEDA too: a pending situation there is not finished, whatever the phases say (review R-03)", () => {
    const finished = ["Planeamiento", "Gestión", "Proyecto de urbanización"].map((label) => ({ label, state: "Finalizado" }));
    const ambit = (veda_stage: VedaStage) => ({
      code: "APR.02.06",
      tracked: true,
      pending: true,
      phases: [...finished, { label: "Obras de urbanización", state: "En Ejecución" }],
      veda_stage,
      as_of: "2026-07-01",
      url: "https://datos.madrid.es/",
    });
    const signal = (veda_stage: VedaStage) =>
      servicesSignal(planning({ code: "APR.02.06", kind: "APR", norma_zonal: null, ambit: ambit(veda_stage) }))[1];
    // The domain's pending situations (AmbitState.pending), generated: the phases finished and VEDA pending → not yet
    expect([...INVESTOR_METHOD.pendingStages].sort()).toEqual(["gestion_urbanizacion", "pendiente_planeamiento", "pendiente_sectorizacion"]);
    for (const stage of INVESTOR_METHOD.pendingStages) expect(signal(stage)).toBe(SERVICES_TEXT.planningFirst);
    // The phases and VEDA finished (or VEDA silent): only the urbanization is left
    expect(signal("edificacion")).toBe(SERVICES_TEXT.worksPending);
    expect(signal(null)).toBe(SERVICES_TEXT.worksPending);
  });

  it("says the power as an assumption from the rule, and only links the CNMC's map", () => {
    const power = { homes: 164, simultaneity: 86.8, kw_per_home: 5.75, kw: 499.1, over_transformer_threshold: true };
    expect(SERVICES_TEXT.power(power)).toMatch(/^Con unas 164 viviendas .* al menos 499,1 kW: 5,75 kW por vivienda .*\(86,8 para 164 viviendas\)/);
    expect(SERVICES_TEXT.solar).toContain("art. 14.1.a");
    expect(SERVICES_TEXT.cnmcUrl).toMatch(/^https:\/\/experience\.arcgis\.com\//);
    expect(SERVICES_TEXT.words.map((w) => w.term)).toEqual(["CUPS", "Acometida", "Derechos de acometida", "Quién paga la red", "Centro de transformación", "Plazos de la norma"]);
  });

  it("names the catalogued building with its protection, number and level", () => {
    expect(catalogText({ number: "02933", name: null, protection: "Parcial", level: 3 })).toBe("Protección parcial, nº 02933 (nivel 3 de 3)");
    expect(catalogText(null)).toBe("No aparece en el catálogo en el punto de referencia de la parcela");
    expect(catalogText(null, true)).toBe("No lo hemos podido leer ahora");
    expect(catalogText({ number: "01234", name: null, protection: "Descatalogado", level: null })).toBe("Descatalogado, nº 01234");
    expect(SHEET_TEXT.firstFilter).toMatch(/^Esto es un primer filtro/);
    expect(SHEET_TEXT.studyItems).toHaveLength(8);
  });

  it("starts the calculator without a figure on a catalogued building, and says why (F14)", () => {
    // Mayor 61: catálogo nº 02933, protección parcial; the sheet's 224 m² are «supuesto»
    const buildability = { kind: "supuesto" as const, value_m2: 224.4, source: "x", editable: true as const };
    const mayor = { number: "02933", name: null, protection: "Parcial", level: 3 };
    expect(isCatalogued(mayor)).toBe(true);
    expect(calculatorStart({ buildability, planning: planning({ protected_building: mayor }) })).toEqual({
      m2: null,
      mark: "sin_dato",
      help: SHEET_TEXT.calculatorCatalogued,
      caution: "Edificio catalogado: una cuenta de obra nueva no sirve; hace falta un estudio de rehabilitación.",
    });
    // Without a catalogued building, the sheet's figure with its own mark
    const plain = { m2: 224.4, mark: "supuesto", help: SHEET_TEXT.calculatorFrom("supuesto"), caution: null };
    expect(calculatorStart({ buildability, planning: planning({}) })).toEqual(plain);
    expect(calculatorStart({ buildability, planning: null })).toEqual(plain);
    // «Descatalogado» and «Demolición total» are not a protection: the account of a new building stands
    for (const protection of ["Descatalogado", "Demolición total"]) {
      const building = { ...mayor, protection, level: null };
      expect(isCatalogued(building)).toBe(false);
      expect(calculatorStart({ buildability, planning: planning({ protected_building: building }) }).m2).toBe(224.4);
    }
    expect(isCatalogued(null)).toBe(false);
  });
});
