import { describe, expect, it } from "vitest";

import { GAP_STATUS, rowsPending, topRows } from "../gaps";

describe("gap statuses (pitch/textos_web.md, estado.*)", () => {
  it("has a text label for every status, never colour alone", () => {
    expect(Object.keys(GAP_STATUS).sort()).toEqual(["CUBIERTO", "FALTA", "JUSTO", "SIN_DATOS"]);
    expect(GAP_STATUS.SIN_DATOS.label).toBe("SIN DATOS");
    for (const meta of Object.values(GAP_STATUS)) expect(meta.help.length).toBeGreaterThan(10);
  });
});

describe("rowsPending", () => {
  it("detects the API warning about rows not computed yet at this level", () => {
    expect(rowsPending(["No indicators computed at this level yet"])).toBe(true);
    expect(rowsPending(["colegio: cannot classify against a zero reference"])).toBe(false);
    expect(rowsPending([])).toBe(false);
    expect(rowsPending(undefined)).toBe(false);
  });
});

describe("topRows", () => {
  it("puts what is missing first and keeps at most three rows for the zone card", () => {
    const rows = [
      { row: "farmacia", status: "CUBIERTO" },
      { row: "colegio", status: "FALTA" },
      { row: "mayores", status: "SIN_DATOS" },
      { row: "centro_salud", status: "JUSTO" },
    ] as const;
    expect(topRows([...rows]).map((r) => r.row)).toEqual(["colegio", "centro_salud", "farmacia"]);
  });
});
