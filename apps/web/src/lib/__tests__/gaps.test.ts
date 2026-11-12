import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { GapRowKey, GapStatus, IndicatorValue, ZoneGapList } from "@/contracts/zone_gap_list_response";

import {
  comparisonText,
  fitsButShortText,
  GAP_STATUS,
  gapFigures,
  gapSummary,
  GROUP,
  groupText,
  hospitalText,
  hospitalWalking,
  inGroup,
  isSmallZone,
  listNames,
  referenceLabel,
  SMALL_ZONE,
  gapsHref,
  NULL_REASON,
  parseZoneParam,
  pendingRows,
  peopleAffectedText,
  ROW_IN_LIST,
  ROW_MEASURE,
  ROW_NAME,
  rowComparison,
  sortRows,
  topRows,
  walking,
  walkingText,
} from "../gaps";

const ROW_KEYS = ["centro_salud", "colegio", "escuela_infantil", "farmacia", "mayores", "vivienda"];

describe("gap statuses (pitch/textos_web.md, estado.*)", () => {
  it("has a text label for every status, never colour alone", () => {
    expect(Object.keys(GAP_STATUS).sort()).toEqual(["CUBIERTO", "FALTA", "JUSTO", "SIN_DATOS"]);
    expect(GAP_STATUS.SIN_DATOS.label).toBe("SIN DATOS");
    for (const meta of Object.values(GAP_STATUS)) expect(meta.help.length).toBeGreaterThan(10);
  });
});

describe("rows", () => {
  it("names and measures the six rows of /gaps", () => {
    expect(Object.keys(ROW_NAME).sort()).toEqual(ROW_KEYS);
    expect(Object.keys(ROW_MEASURE).sort()).toEqual(ROW_KEYS);
    // gap-0.3 (D-217): capacity within 15 min on foot, shared among those who have it that close
    for (const key of ROW_KEYS.filter((k) => k !== "vivienda")) {
      expect(ROW_MEASURE[key as keyof typeof ROW_MEASURE]).toMatch(/a 15 min andando .*repartid[oa]s entre todos los que l[oa]s tienen cerca$/);
    }
    expect(ROW_MEASURE.centro_salud).toMatch(/^Centros de salud del SERMAS/);
    expect(ROW_MEASURE.vivienda).not.toMatch(/andando/);
  });

  it("explains every reason for a missing value in plain words (falta, null_reason)", () => {
    expect(Object.keys(NULL_REASON)).toHaveLength(9);
    expect(NULL_REASON.SOURCE_MISSING).toBe("La fuente oficial no trae este dato.");
  });
});

describe("pendingRows", () => {
  it("reads the rows /gaps has not computed at this level yet, in row order", () => {
    const warnings = [
      "INSUFFICIENT_DATA: row vivienda not computed at distrito level yet",
      "INSUFFICIENT_DATA: row escuela_infantil not computed at distrito level yet",
    ];
    expect(pendingRows(warnings)).toEqual(["escuela_infantil", "vivienda"]);
  });

  it("reads the exact warnings the API emits (tests/unit/api/test_gaps_warnings.py)", () => {
    const python = readFileSync(new URL("../../../../../tests/unit/api/test_gaps_warnings.py", import.meta.url), "utf8");
    const warnings = [...python.matchAll(/"(INSUFFICIENT_DATA: row [^"]+)"/g)].map((m) => m[1] ?? "");
    expect(warnings.length).toBeGreaterThan(0);
    expect(pendingRows(warnings)).toHaveLength(warnings.length);
  });

  it("ignores other warnings, unknown rows and a missing list", () => {
    expect(pendingRows(["colegio: no regional reference"])).toEqual([]);
    expect(pendingRows(["INSUFFICIENT_DATA: row parques not computed at municipio level yet"])).toEqual([]);
    expect(pendingRows([])).toEqual([]);
    expect(pendingRows(undefined)).toEqual([]);
  });
});

describe("small zones (gap-0.2, D-213, fila.zona_pequena)", () => {
  it("flags only `reliable: false`; answers without the field are comparable", () => {
    expect(isSmallZone({ reliable: false })).toBe(true);
    expect(isSmallZone({ reliable: true })).toBe(false);
    expect(isSmallZone({})).toBe(false);
    expect(SMALL_ZONE.label).toBe("Zona pequeña para comparar");
  });
});

describe("comparison groups (gap-0.3, D-217)", () => {
  // Test fixture published by line A with the contract (data/fixtures/contracts), not demo data.
  const FIXTURE = new URL("../../../../../data/fixtures/contracts/zone_gap_list.el_alamo.fixture.json", import.meta.url);
  const alamo = JSON.parse(readFileSync(FIXTURE, "utf8")) as ZoneGapList;
  const row = (key: string) => alamo.rows.find((r) => r.row === key);

  it("reads the group only when the API sends one", () => {
    expect(inGroup(row("centro_salud") ?? {})?.names[0]).toBe("El Álamo");
    expect(inGroup(row("farmacia") ?? {})).toBeNull();
    expect(inGroup({})).toBeNull();
    expect(GROUP.help).toMatch(/^Comparado con municipios parecidos de la zona/);
  });

  it("names the neighbours and the group's share in plain words, like the API explanation", () => {
    const health = row("centro_salud");
    const group = health?.comparison_group;
    if (!health || !group) throw new Error("the fixture must carry El Álamo's health row with its group");
    const text = groupText("El Álamo", group);
    expect(text).toMatch(/^Comparado con municipios parecidos de la zona\./);
    expect(text).toContain("sus 5 vecinos más cercanos del mismo tipo: Navalcarnero, Arroyomolinos, Serranillos del Valle, Moraleja de Enmedio y Móstoles.");
    // the API: «…, tiene el 105 % de lo esperado»
    expect(health.explanation).toContain(`tiene el ${Math.round(100 * group.ratio_to_reference)} % de lo esperado`);
    expect(text).toContain(`Juntos tienen el ${Math.round(100 * group.ratio_to_reference)} % de lo que tienen de media los municipios de su tipo`);
  });

  it("uses the singular with one neighbour", () => {
    const text = groupText("El Álamo", { codes: ["28004", "28096"], names: ["El Álamo", "Navalcarnero"], ratio_to_reference: 1.0815 });
    expect(text).toContain("lo juntamos con su vecino más cercano del mismo tipo: Navalcarnero.");
    expect(text).toContain("Juntos tienen el 108 %");
  });
});

describe("sortRows and topRows", () => {
  const rows = [
    { row: "farmacia", status: "CUBIERTO" },
    { row: "colegio", status: "FALTA" },
    { row: "mayores", status: "SIN_DATOS" },
    { row: "centro_salud", status: "JUSTO" },
    { row: "vivienda", status: "FALTA" },
  ] as const;

  it("puts what is missing first and keeps the API order within a status", () => {
    expect(sortRows([...rows]).map((r) => r.row)).toEqual(["colegio", "vivienda", "centro_salud", "farmacia", "mayores"]);
  });

  it("puts a small zone after a comparable one with the same status", () => {
    const mixed = [
      { row: "farmacia", status: "CUBIERTO" },
      { row: "colegio", status: "JUSTO", reliable: false },
      { row: "mayores", status: "JUSTO" },
    ] as const;
    expect(sortRows([...mixed]).map((r) => r.row)).toEqual(["mayores", "colegio", "farmacia"]);
    const small = [{ row: "colegio", status: "JUSTO", reliable: false }, { row: "mayores", status: "FALTA" }] as const;
    expect(sortRows([...small]).map((r) => r.row)).toEqual(["mayores", "colegio"]);
  });

  it("keeps at most three rows for the zone card", () => {
    expect(topRows([...rows]).map((r) => r.row)).toEqual(["colegio", "vivienda", "centro_salud"]);
  });
});

describe("fitsButShortText (encaje.aviso_*: a zone that fits, short of something)", () => {
  type Row = { row: GapRowKey; status: GapStatus; reliable?: boolean };
  const row = (key: GapRowKey, status: GapStatus, reliable = true): Row => ({ row: key, status, reliable });

  it("names the rows that are JUSTO (Fuencarral-El Pardo, 12 nov)", () => {
    expect(fitsButShortText([row("escuela_infantil", "JUSTO"), row("colegio", "JUSTO"), row("centro_salud", "JUSTO")])).toBe(
      "Encaja con lo que pides. Aun así, frente a municipios parecidos, aquí van justos de escuelas infantiles, colegios y centros de salud.",
    );
  });

  it("says what is missing, and then what is tight", () => {
    expect(fitsButShortText([row("escuela_infantil", "FALTA")])).toBe(
      "Encaja con lo que pides. Aun así, frente a municipios parecidos, aquí faltan escuelas infantiles.",
    );
    expect(fitsButShortText([row("centro_salud", "FALTA"), row("colegio", "JUSTO"), row("farmacia", "CUBIERTO")])).toBe(
      "Encaja con lo que pides. Aun así, frente a municipios parecidos, aquí faltan centros de salud y van justos de colegios.",
    );
  });

  it("names every FALTA and JUSTO row of the API, also beyond the three the card shows", () => {
    const rows = [
      row("escuela_infantil", "JUSTO"),
      row("colegio", "JUSTO"),
      row("centro_salud", "FALTA"),
      row("farmacia", "JUSTO"),
      row("mayores", "CUBIERTO"),
      row("vivienda", "JUSTO"),
    ];
    expect(topRows(rows)).toHaveLength(3);
    expect(fitsButShortText(rows)).toBe(
      "Encaja con lo que pides. Aun así, frente a municipios parecidos, aquí faltan centros de salud y van justos de escuelas infantiles, colegios, farmacias y viviendas grandes para familias.",
    );
  });

  it("says nothing when no row is FALTA or JUSTO, and leaves out rows too small to compare", () => {
    expect(fitsButShortText([row("colegio", "CUBIERTO"), row("farmacia", "SIN_DATOS")])).toBeNull();
    expect(fitsButShortText([row("farmacia", "JUSTO", false)])).toBeNull();
    expect(fitsButShortText([])).toBeNull();
  });
});

describe("gapFigures", () => {
  // Pairs from GET /gaps (11 nov) and the decimals of their API `explanation`
  it("formats value and reference like the API explanation", () => {
    expect(gapFigures(5.011, 4.714)).toMatchObject({ value: "5,0", reference: "4,7" });
    expect(gapFigures(0.469, 0.5918)).toMatchObject({ value: "0,47", reference: "0,59" });
    expect(gapFigures(0, 0.3895)).toMatchObject({ value: "0,00", reference: "0,39" });
    expect(gapFigures(142.9, 0.5918)).toMatchObject({ value: "142,9", reference: "0,6" });
    expect(gapFigures(10700, 177.6)).toMatchObject({ value: "10.700,0", reference: "177,6" });
  });

  it("never turns a missing value or reference into a number", () => {
    expect(gapFigures(null, 177.6)).toEqual({ value: null, reference: "177,6", regional: null });
    expect(gapFigures(1.2, null)).toEqual({ value: "1,2", reference: null, regional: null });
  });

  it("gives the whole region with the decimals of the value and its reference (gap-0.2 explanation)", () => {
    // «0,47 …; en los demás municipios urbanos …, 0,56 (en toda la Comunidad, 0,59)»
    expect(gapFigures(0.469, 0.5553, 0.5918)).toEqual({ value: "0,47", reference: "0,56", regional: "0,59" });
    // «142,9 …; en los demás municipios rurales …, 6,8 (en toda la Comunidad, 0,6)»
    expect(gapFigures(142.9, 6.799, 0.5918)).toEqual({ value: "142,9", reference: "6,8", regional: "0,6" });
  });
});

function extra(featureId: string, value: number | null, nullReason: IndicatorValue["null_reason"] = null): IndicatorValue {
  return { feature_id: featureId, label: "", unit: "min", level: "distrito", confidence: value === null ? 0 : 1, value, null_reason: nullReason };
}

describe("walking minutes (extra_indicators)", () => {
  it("picks the walking extra among the others", () => {
    const extras = [extra("plazas_residencia_por_100_mayores", 3.7), extra("min_a_pie_mayores", 10.01)];
    expect(walking(extras)?.feature_id).toBe("min_a_pie_mayores");
    expect(walking([extra("tamano_medio_hogar", 2.4)])).toBeUndefined();
    expect(walking(undefined)).toBeUndefined();
  });

  it("picks the row's own minutes, never the hospital's (D-217)", () => {
    const health = [extra("centros_salud_por_10000_hab", 0.9), extra("min_a_pie_hospital", 234.3), extra("min_a_pie_centro_salud", 12.7)];
    expect(walking(health, "centro_salud")?.feature_id).toBe("min_a_pie_centro_salud");
    expect(walking(health)?.feature_id).toBe("min_a_pie_centro_salud");
    expect(walking([extra("min_a_pie_hospital", 34.2)], "centro_salud")).toBeUndefined();
    expect(hospitalWalking(health)?.value).toBe(234.3);
    expect(hospitalWalking([extra("min_a_pie_colegio", 5.8)])).toBeUndefined();
    expect(walkingText(hospitalWalking(health) ?? extra("x", null))).toBe("más de 60 min");
  });

  it("rounds to whole minutes and caps the text above 60", () => {
    expect(walkingText(extra("min_a_pie_colegio", 5.815))).toBe("6 min");
    expect(walkingText(extra("min_a_pie_centro_salud", 9.466))).toBe("9 min");
    expect(walkingText(extra("min_a_pie_colegio", 60))).toBe("60 min");
    expect(walkingText(extra("min_a_pie_colegio", 60.4))).toBe("más de 60 min");
    expect(walkingText(extra("min_a_pie_colegio", 207.3))).toBe("más de 60 min");
    expect(walkingText(extra("min_a_pie_farmacia", 0.3))).toBe("menos de 1 min");
  });

  it("says «Sin datos» when the value is missing, never 0 (a_pie.min)", () => {
    expect(walkingText(extra("min_a_pie_colegio", null, "SOURCE_NO_COVERAGE"))).toBe("Sin datos");
  });
});

describe("zone links of «Qué falta»", () => {
  it("round-trips a zone through the ?zona= parameter", () => {
    expect(gapsHref("distrito", "2807905")).toBe("/que-falta?zona=distrito/2807905");
    expect(parseZoneParam("distrito/2807905")).toEqual({ level: "distrito", code: "2807905" });
    expect(parseZoneParam("municipio/28092")).toEqual({ level: "municipio", code: "28092" });
  });

  it("rejects levels without a map zone and malformed values", () => {
    expect(parseZoneParam(undefined)).toBeNull();
    expect(parseZoneParam("")).toBeNull();
    expect(parseZoneParam("seccion_censal/2807905001")).toBeNull();
    expect(parseZoneParam("distrito")).toBeNull();
    expect(parseZoneParam("distrito/28 07")).toBeNull();
    expect(parseZoneParam(["distrito/2807905", "municipio/28092"])).toBeNull();
  });
});

describe("each row in plain words (D-229 §6, falta.fila.comparacion)", () => {
  // Test fixtures published by line A with the contract (data/fixtures/contracts), not demo data.
  const load = (name: string) =>
    JSON.parse(readFileSync(new URL(`../../../../../data/fixtures/contracts/${name}`, import.meta.url), "utf8")) as ZoneGapList;
  const centro = load("zone_gap_list.centro.fixture.json");
  const alamo = load("zone_gap_list.el_alamo.fixture.json");
  const row = (list: ZoneGapList, key: string) => {
    const found = list.rows.find((r) => r.row === key);
    if (!found) throw new Error(`no row ${key}`);
    return found;
  };

  it("gives n = round(100 × ratio), also above 100 and with Spanish thousands", () => {
    expect(comparisonText(0.571, false)).toBe("Aquí hay 57 por cada 100 que hay en municipios parecidos.");
    expect(comparisonText(2.498, false)).toBe("Aquí hay 250 por cada 100 que hay en municipios parecidos.");
    expect(comparisonText(60.2, false)).toBe("Aquí hay 6.020 por cada 100 que hay en municipios parecidos.");
  });

  it("uses the zone's own ratio, or its group's when it is compared with its neighbours", () => {
    const nursery = row(centro, "escuela_infantil");
    expect(rowComparison(nursery)).toBe(`Aquí hay ${Math.round(100 * (nursery.ratio_to_reference ?? NaN))} por cada 100 que hay en municipios parecidos.`);
    // El Álamo has no health centre within 15 min (ratio 0), but its group has 104 per 100: CUBIERTO
    const health = row(alamo, "centro_salud");
    expect(health.ratio_to_reference).toBe(0);
    expect(rowComparison(health)).toBe(
      `Junto con sus vecinos, hay ${Math.round(100 * (health.comparison_group?.ratio_to_reference ?? NaN))} por cada 100 que hay en municipios parecidos.`,
    );
  });

  it("says nothing when there is no ratio (SIN DATOS) or the zone is too small to compare even with its neighbours", () => {
    expect(rowComparison(row(centro, "vivienda"))).toBeNull();
    expect(rowComparison({ status: "JUSTO" })).toBeNull();
    expect(rowComparison({ status: "JUSTO", reliable: false, ratio_to_reference: 0 })).toBeNull();
    const group = { codes: ["28004", "28096"] as [string, string], names: ["El Álamo", "Navalcarnero"] as [string, string], ratio_to_reference: 0.6 };
    expect(rowComparison({ status: "JUSTO", reliable: false, ratio_to_reference: 0, comparison_group: group })).toMatch(/^Junto con sus vecinos, hay 60 /);
  });

  it("names the people a FALTA row leaves short, and only for FALTA", () => {
    expect(peopleAffectedText({ status: "FALTA", people: { count: 9433, label: "niños de 0 a 4 años" } })).toBe("Afecta a 9.433 niños de 0 a 4 años.");
    expect(peopleAffectedText(row(centro, "escuela_infantil"))).toBeNull(); // JUSTO
    expect(peopleAffectedText({ status: "FALTA", people: null })).toBeNull();
  });

  it("has a name inside a sentence for every row (fila.lista.*)", () => {
    expect(Object.keys(ROW_IN_LIST).sort()).toEqual(ROW_KEYS);
    expect(ROW_IN_LIST.vivienda).toBe("viviendas grandes para familias");
  });
});

describe("the summary over the rows (falta.resumen.*)", () => {
  type Row = { row: GapRowKey; status: GapStatus; reliable?: boolean; comparison_group?: { codes: [string, string]; names: [string, string]; ratio_to_reference: number } };
  const row = (key: GapRowKey, status: GapStatus, extra: Partial<Row> = {}): Row => ({ row: key, status, reliable: true, ...extra });
  const group = { codes: ["28004", "28096"] as [string, string], names: ["El Álamo", "Navalcarnero"] as [string, string], ratio_to_reference: 0.6 };

  it("starts with what is missing, then what is tight and what has no data (Puente de Vallecas)", () => {
    const rows = [row("escuela_infantil", "FALTA"), row("colegio", "CUBIERTO"), row("centro_salud", "CUBIERTO"), row("vivienda", "SIN_DATOS")];
    expect(gapSummary(rows)).toEqual({ lead: "Aquí falta: escuelas infantiles.", rest: ["Sin datos: viviendas grandes para familias."] });
  });

  it("says nothing is clearly missing when only some are tight (Fuencarral-El Pardo)", () => {
    const rows = [row("escuela_infantil", "JUSTO"), row("colegio", "JUSTO"), row("centro_salud", "JUSTO"), row("farmacia", "CUBIERTO")];
    expect(gapSummary(rows)).toEqual({ lead: "Aquí no falta nada claro.", rest: ["Van justos: escuelas infantiles, colegios y centros de salud."] });
  });

  it("says nothing is missing when every comparable row is CUBIERTO", () => {
    expect(gapSummary([row("colegio", "CUBIERTO"), row("farmacia", "CUBIERTO")])).toEqual({ lead: "Aquí no falta nada frente a municipios parecidos.", rest: [] });
  });

  it("keeps rows too small to compare apart, but not those compared with their neighbours", () => {
    const rows = [row("farmacia", "JUSTO", { reliable: false }), row("colegio", "FALTA", { comparison_group: group }), row("mayores", "CUBIERTO")];
    expect(gapSummary(rows)).toEqual({ lead: "Aquí falta: colegios.", rest: ["Zona muy pequeña para comparar: farmacias."] });
  });

  it("has no verdict in bold when no row can be compared", () => {
    expect(gapSummary([row("vivienda", "SIN_DATOS")])).toEqual({ lead: null, rest: ["Sin datos: viviendas grandes para familias."] });
    expect(gapSummary([row("farmacia", "JUSTO", { reliable: false })])).toEqual({ lead: null, rest: ["Zona muy pequeña para comparar: farmacias."] });
    expect(gapSummary([])).toEqual({ lead: null, rest: [] });
  });

  it("joins names with commas and «y»", () => {
    expect(listNames(["a"])).toBe("a");
    expect(listNames(["a", "b"])).toBe("a y b");
    expect(listNames(["a", "b", "c"])).toBe("a, b y c");
  });
});

describe("who a zone is compared with (falta.fila.referencia.distrito)", () => {
  it("says a district is compared with the urban municipios without Madrid", () => {
    expect(referenceLabel("Otros municipios urbanos de la Comunidad de Madrid", "distrito")).toBe(
      "Municipios urbanos de la Comunidad, sin contar Madrid (como Getafe o Alcalá de Henares)",
    );
    expect(referenceLabel("Otros municipios rurales de la Comunidad de Madrid", "municipio")).toBe("Otros municipios rurales de la Comunidad de Madrid");
  });
});

describe("the nearest hospital (hospital.distancia)", () => {
  it("gives minutes up to 30, and the distance at 4 km/h beyond", () => {
    expect(hospitalText({ value: 12.4 })).toBe("a 12 min andando");
    expect(hospitalText({ value: 30 })).toBe("a 30 min andando");
    expect(hospitalText({ value: 51.32 })).toBe("a unos 3,4 km");
    expect(hospitalText({ value: 95 })).toBe("a unos 6,3 km");
    expect(hospitalText({ value: null })).toBe("Sin datos");
  });
});
