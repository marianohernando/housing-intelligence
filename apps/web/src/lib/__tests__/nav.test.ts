import { describe, expect, it } from "vitest";

import { activeTab, TABS } from "../nav";

describe("header tabs", () => {
  it("uses the plain-language names of the brief, in order", () => {
    expect(TABS.map((t) => t.label)).toEqual(["Mapa", "Qué falta", "Cómo lo calculamos"]);
  });

  it("marks Mapa on the home page and inside a zone", () => {
    expect(activeTab("/")).toBe("/");
    expect(activeTab("/zona/distrito/2807905")).toBe("/");
  });

  it("marks the other tabs by their path, including subpaths", () => {
    expect(activeTab("/que-falta")).toBe("/que-falta");
    expect(activeTab("/que-falta/municipio/28079")).toBe("/que-falta");
    expect(activeTab("/como-lo-calculamos")).toBe("/como-lo-calculamos");
  });

  it("marks nothing outside the product pages", () => {
    expect(activeTab("/map")).toBeNull();
    expect(activeTab("/que-faltaba")).toBeNull();
  });
});
