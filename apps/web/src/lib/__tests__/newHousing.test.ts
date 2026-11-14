import { describe, expect, it } from "vitest";

import type { FeatureValueDetail, FeatureValueRow } from "../features";
import {
  areasSentences,
  dateInWords,
  listInWords,
  newHousingLines,
  newHousingRequests,
  type NewHousingRows,
  phaseInWords,
  planViveSentence,
  quarterInWords,
  salesSentence,
  valueSentence,
} from "../newHousing";

// Test fixture: rows shaped as GET /features/{id}/values gives them (D-241), values of 14 nov
function row(code: string, value: number | null, period: string, detail?: FeatureValueDetail): FeatureValueRow {
  return { territory_code: code, admin_unit_id: null, name: null, period_start: period, value, null_reason: value === null ? "SOURCE_MISSING" : null, confidence: 1, detail };
}

const sales = [
  row("28065", 28.126, "2025-07-01", { numerator: 650, denominator: 2311, period_end: "2026-06-30", provisional: true }),
  row("28079", 3.772, "2025-07-01", { numerator: 1512, denominator: 40086, period_end: "2026-06-30", provisional: false }),
  row("28001", null, "2025-07-01", { numerator: 0, denominator: 0, period_end: "2026-06-30", provisional: true }),
];
const newValue = [row("28115", 5431.7, "2025-01-01"), row("28079", 5458.5, "2025-01-01"), row("28007", 2859.9, "2025-01-01"), row("28106", null, "2025-01-01")];
const usedValue = [row("28115", 4787.9, "2025-01-01"), row("28079", 4987.9, "2025-01-01"), row("28007", 3077.1, "2025-01-01"), row("28106", 2096.9, "2025-01-01")];
const shared = "La Comunidad no publica cuántas de estas viviendas hay en cada uno de los dos sitios.";
const planVive = [
  row("28006", 756, "2026-11-14", { items: [{ code: "alcobendas", name: "avda. Olímpica y avda. Camilo José Cela", stage: "Construcción", value: 756 }] }),
  row("28065", 0, "2026-11-14", { items: [] }),
];
const planViveDistricts = [
  row("2807919", 1616, "2026-11-14", { items: [{ code: "madrid", name: "Valdebebas y Los Ahijones", stage: "Entrega y construcción", value: 1616, note: shared }] }),
  row("2807913", 0, "2026-11-14", { items: [] }),
];
const areas = [
  row("2807919", 4, "2026-07-01", {
    items: [
      { code: "UZPp.02.04-RP", name: "Los Berrocales", stage: "obras", value: 7810077 },
      { code: "UZPp.02.03-RP", name: "Los Ahijones", stage: "obras", value: 5507172 },
      { code: "X", name: "C/ Peyre", stage: "tramitacion", value: 2997 },
      { code: "Y", name: "Muralla", stage: "sin_empezar", value: 25582 },
    ],
  }),
  row("2807913", 0, "2026-07-01", { items: [] }),
];
const rows: NewHousingRows = { sales, newValue, usedValue, planVive, areas };

describe("newHousingRequests (D-241)", () => {
  it("asks a district for the city's sales and appraisals, and for its own Plan Vive and planning areas", () => {
    expect(newHousingRequests("municipio").map((r) => `${r.key}@${r.level}`)).toEqual(["sales@municipio", "newValue@municipio", "usedValue@municipio", "planVive@municipio"]);
    expect(newHousingRequests("distrito").map((r) => `${r.key}@${r.level}`)).toEqual(["sales@municipio", "newValue@municipio", "usedValue@municipio", "planVive@distrito", "areas@distrito"]);
  });
});

describe("words", () => {
  it("writes dates, quarters and lists the Spanish way", () => {
    expect(dateInWords("2026-11-14")).toBe("14 de noviembre de 2026");
    expect(quarterInWords("2025-07-01")).toBe("3.er trimestre de 2025");
    expect(quarterInWords("2026-06-30")).toBe("2.º trimestre de 2026");
    expect(listInWords(["A"])).toBe("A");
    expect(listInWords(["A", "B", "C"])).toBe("A, B y C");
    expect(listInWords(["A", "B", "C", "D", "E", "F"])).toBe("A, B, C, D y 2 más");
  });

  it("says the Plan Vive phases in plain words", () => {
    expect(phaseInWords("Construcción")).toBe("en obras");
    expect(phaseInWords("Entrega y construcción")).toBe("en entrega y en obras");
    expect(phaseInWords("Entrega, comercialización y construcción")).toBe("en entrega, en comercialización y en obras");
    expect(phaseInWords("Adjudicación")).toBe("en fase de adjudicación");
  });
});

describe("sentences (zona.vivienda_nueva.*)", () => {
  it("says how many sales were new homes, with the zero cases in words", () => {
    expect(salesSentence(650, 2311, 28.126)).toBe("650 de las 2.311 compraventas de vivienda del último año fueron de obra nueva (28 %).");
    expect(salesSentence(1512, 40086, 3.772)).toBe("1.512 de las 40.086 compraventas de vivienda del último año fueron de obra nueva (3,8 %).");
    expect(salesSentence(0, 12, 0)).toBe("Ninguna de las 12 compraventas de vivienda del último año fue de obra nueva.");
    expect(salesSentence(0, 0, null)).toBe("No hubo compraventas de vivienda en el último año.");
    expect(salesSentence(1, 1, 100)).toBe("La única compraventa de vivienda del último año fue de obra nueva.");
    expect(salesSentence(1, 9, 11.1)).toContain("del último año fue de obra nueva");
  });

  it("compares the appraisal of a new home with a used one, up or down", () => {
    expect(valueSentence(5431.7, 4787.9)).toBe("Una vivienda de menos de 5 años se tasa a 5.432 €/m², un 13 % más que la usada.");
    expect(valueSentence(2859.9, 3077.1)).toBe("Una vivienda de menos de 5 años se tasa a 2.860 €/m², un 7 % menos que la usada.");
    expect(valueSentence(2568.8, 2565.1)).toBe("Una vivienda de menos de 5 años se tasa a 2.569 €/m², casi lo mismo que la usada.");
  });

  it("names Plan Vive with its homes, phase and place", () => {
    expect(planViveSentence({ name: "avda. Olímpica y avda. Camilo José Cela", stage: "Construcción", value: 756 })).toBe(
      "Lo que viene: Plan Vive, 756 viviendas de alquiler asequible en obras (avda. Olímpica y avda. Camilo José Cela).",
    );
    expect(planViveSentence({ name: "x", stage: "Construcción", value: 0 })).toBeNull();
  });

  it("groups the planning areas by stage, the works first", () => {
    expect(areasSentences(areas[0]?.detail?.items ?? []).map((s) => s.text)).toEqual([
      "En desarrollo: Los Berrocales y Los Ahijones (urbanización en obras).",
      "En tramitación: C/ Peyre (planeamiento, gestión o proyecto en marcha).",
      "Previstos: Muralla (aún sin empezar).",
    ]);
  });
});

describe("newHousingLines", () => {
  it("in a municipio: sales, appraisal and Plan Vive, each with its source and date", () => {
    const lines = newHousingLines({ level: "municipio", code: "28065" }, rows);
    expect(lines.map((l) => l.key)).toEqual(["sales"]);
    expect(lines[0]?.text).toBe("650 de las 2.311 compraventas de vivienda del último año fueron de obra nueva (28 %). Incluye datos aún provisionales.");
    expect(lines[0]?.source).toContain("del 3.er trimestre de 2025 al 2.º trimestre de 2026");
    const alcobendas = newHousingLines({ level: "municipio", code: "28006" }, rows);
    expect(alcobendas.map((l) => l.key)).toEqual(["plan-vive-alcobendas"]);
    expect(alcobendas[0]?.source).toBe("Página del Plan Vive de la Comunidad de Madrid, consultada el 14 de noviembre de 2026.");
    const pozuelo = newHousingLines({ level: "municipio", code: "28115" }, rows);
    expect(pozuelo.map((l) => l.key)).toEqual(["value"]);
    expect(pozuelo[0]?.source).toContain("de 2025");
  });

  it("never a 0 where the source publishes nothing: Parla has no new-home appraisal, so no line", () => {
    expect(newHousingLines({ level: "municipio", code: "28106" }, rows)).toEqual([]);
    expect(newHousingLines({ level: "municipio", code: "28001" }, rows)[0]?.text).toBe("No hubo compraventas de vivienda en el último año. Incluye datos aún provisionales.");
  });

  it("in a district: the city's figures said as such, its Plan Vive with the shared note, and its areas", () => {
    const lines = newHousingLines({ level: "distrito", code: "2807919" }, { ...rows, planVive: planViveDistricts });
    expect(lines.map((l) => l.key)).toEqual(["sales", "value", "plan-vive-madrid", "areas-obras", "areas-tramitacion", "areas-sin_empezar"]);
    expect(lines[0]?.text.startsWith("En toda la ciudad de Madrid, 1.512 de las 40.086")).toBe(true);
    expect(lines[0]?.note).toBe("La fuente no lo da por distritos.");
    expect(lines[1]?.text).toBe("En toda la ciudad de Madrid, una vivienda de menos de 5 años se tasa a 5.459 €/m², un 9 % más que la usada.");
    expect(lines[2]?.note).toBe(shared);
    expect(lines[3]?.source).toContain("a 1 de julio de 2026");
  });

  it("says a district has no area left, and leaves out what the API does not have", () => {
    const lines = newHousingLines({ level: "distrito", code: "2807913" }, { areas: [...areas], planVive: planViveDistricts });
    expect(lines.map((l) => l.text)).toEqual(["En este distrito no queda ningún ámbito de vivienda del Plan General por terminar."]);
    expect(newHousingLines({ level: "distrito", code: "2807913" }, {})).toEqual([]);
  });

  it("an API without the detail (before D-241 is deployed) gives no sales or Plan Vive line", () => {
    const bare = sales.map((r) => ({ ...r, detail: undefined }));
    expect(newHousingLines({ level: "municipio", code: "28065" }, { sales: bare })).toEqual([]);
  });

  it("never uses alarm or ranking words", () => {
    const text = newHousingLines({ level: "distrito", code: "2807919" }, { ...rows, planVive: planViveDistricts })
      .map((l) => `${l.text} ${l.note ?? ""} ${l.source}`)
      .join(" ")
      .toLowerCase();
    for (const word of ["mejor", "peor", "riesgo", "alerta", "cuidado", "caro", "barato"]) expect(text).not.toContain(word);
  });
});
