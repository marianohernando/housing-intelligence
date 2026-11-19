import { describe, expect, it } from "vitest";

import { activeTab, overviewHref, overviewZoneKey, type Tab, tabHref, TABS } from "../nav";

describe("header tabs", () => {
  it("uses the plain-language names of the brief, in order, and «Inversores» last (D-251)", () => {
    expect(TABS.map((t) => t.label)).toEqual(["Mapa", "Qué falta", "Cómo lo calculamos", "Inversores"]);
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

  it("marks «Inversores» on the search, a barrio's sheet and a parcel's sheet", () => {
    expect(activeTab("/inversores")).toBe("/inversores");
    expect(activeTab("/inversores/28079164")).toBe("/inversores");
    expect(activeTab("/inversores/parcela/2122202VK4722A")).toBe("/inversores");
    expect(activeTab("/inversores/")).toBe("/inversores");
    expect(activeTab("/inversoresx")).toBeNull();
    expect(activeTab("/desarrolladores")).toBeNull();
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
  const [mapa, falta, como, inversores] = [tab("/"), tab("/que-falta"), tab("/como-lo-calculamos"), tab("/inversores")];

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
    expect(tabHref(inversores, "/zona/distrito/2807905")).toBe("/inversores");
  });
});

describe("the zone picked on the overview, in its address (second delivery of the UX mobile audit)", () => {
  it("opens a zone of the map from ?zona=, and nothing else", () => {
    expect(overviewZoneKey("distrito/2807913")).toBe("distrito/2807913");
    expect(overviewZoneKey("municipio/28049")).toBe("municipio/28049");
    expect(overviewZoneKey("barrio/28079211")).toBe("barrio/28079211");
    expect(overviewZoneKey("seccion_censal/2807901001")).toBeNull();
    expect(overviewZoneKey("distrito/")).toBeNull();
    expect(overviewZoneKey("distrito/28<script>")).toBeNull();
    expect(overviewZoneKey(null)).toBeNull();
  });

  it("writes the list without a zone and the card with it", () => {
    expect(overviewHref(null)).toBe("/");
    expect(overviewHref("distrito/2807913")).toBe("/?zona=distrito/2807913");
    expect(overviewZoneKey(new URLSearchParams(overviewHref("barrio/28079211").slice(2)).get("zona"))).toBe("barrio/28079211");
  });
});
