import { describe, expect, it } from "vitest";

import { activeTab, type Tab, tabHref, TABS } from "../nav";

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

describe("tabHref", () => {
  const tab = (href: string): Tab => {
    const found = TABS.find((t) => t.href === href);
    if (!found) throw new Error(`No tab ${href}`);
    return found;
  };
  const [mapa, falta, como] = [tab("/"), tab("/que-falta"), tab("/como-lo-calculamos")];

  it("opens the zone's list in «Qué falta» from a zone screen", () => {
    expect(tabHref(falta, "/zona/distrito/2807905")).toBe("/que-falta?zona=distrito/2807905");
    expect(tabHref(falta, "/zona/municipio/28092")).toBe("/que-falta?zona=municipio/28092");
  });

  it("keeps the plain tab elsewhere and for the other tabs", () => {
    expect(tabHref(falta, "/")).toBe("/que-falta");
    expect(tabHref(falta, "/que-falta")).toBe("/que-falta");
    expect(tabHref(falta, "/zona/seccion_censal/2807905001")).toBe("/que-falta");
    expect(tabHref(mapa, "/zona/distrito/2807905")).toBe("/");
    expect(tabHref(como, "/zona/distrito/2807905")).toBe("/como-lo-calculamos");
  });
});
