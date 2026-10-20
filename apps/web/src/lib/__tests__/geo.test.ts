import { describe, expect, it } from "vitest";

import { adminUnitsUrl, describeLineage, describeUnit } from "../geo";

describe("geo helpers", () => {
  it("builds the API url with level and simplification", () => {
    expect(adminUnitsUrl("http://localhost:8010", "barrio", 10)).toBe(
      "http://localhost:8010/api/v1/geo/admin-units?level=barrio&simplify_m=10",
    );
  });

  it("describes named and unnamed units without inventing names", () => {
    const named = describeUnit({
      admin_unit_id: "ES.28.BAR.28079016",
      level: "barrio",
      code: "28079016",
      name: "Sol",
      parent: "ES.28.DIS.2807901",
      area_km2: 0.4512,
    });
    expect(named.title).toBe("Sol");
    const unnamed = describeUnit({ ...{ admin_unit_id: "x", level: "barrio", code: "28079183", parent: null, area_km2: 1 }, name: null });
    expect(unnamed.title).toBe("Barrio 28079183");
    expect(unnamed.rows).toContainEqual(["Nombre", "Sin nombre en la fuente"]);
  });

  it("joins lineage pieces that exist", () => {
    expect(describeLineage({ attribution_text: "Fuente: CM", version_label: "v1" })).toBe("Fuente: CM · versión v1");
    expect(describeLineage({})).toBe("");
  });
});
