import { describe, expect, it } from "vitest";

import type { ParcelBlock, PlanningBlock } from "@/contracts/parcel_sheet_response";
import { ApiError, createApi, parcelPath } from "@/lib/api";
import {
  areaText,
  buildabilityMark,
  buildableText,
  DEMO_PARCELS,
  degradedLines,
  divisionText,
  instrumentText,
  parcelHref,
  parcelRc,
  qualificationText,
  SEARCH_TEXT,
  SHEET_TEXT,
  sentence,
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
    expect(vacantText({ ...PARCEL, is_vacant: true })).toBe("Sí, sin edificar");
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
