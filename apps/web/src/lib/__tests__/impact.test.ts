import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { GapImpact } from "@/contracts/gap_impact_response";

import { impactContext, impactFigure, impactSentence, moreZonesText, rankedZone, splitImpactRows } from "../impact";

// Test fixture published by line A with the contract (data/fixtures/contracts), not demo data.
const FIXTURE = new URL("../../../../../data/fixtures/contracts/gap_impact.comunidad.fixture.json", import.meta.url);
const impact = JSON.parse(readFileSync(FIXTURE, "utf8")) as GapImpact;
const row = (key: string) => {
  const found = impact.rows.find((r) => r.row === key);
  if (!found) throw new Error(`no row ${key} in the fixture`);
  return found;
};

describe("where to invest first (D-229)", () => {
  it("says the region-wide figure of a row in one sentence, with the API's numbers", () => {
    const nursery = row("escuela_infantil");
    expect(`${impactFigure(nursery)} ${impactSentence(nursery)}`).toBe(
      `${nursery.people_in_falta.toLocaleString("es-ES", { useGrouping: "always" })} niños de 0 a 4 años viven donde faltan escuelas infantiles`,
    );
    expect(impactSentence(row("vivienda"))).toBe("hogares de 4 o más personas viven donde faltan viviendas grandes para familias");
  });

  it("matches the API summary: same people, same share and same number of zones", () => {
    for (const r of impact.rows.filter((x) => x.people_in_falta > 0)) {
      expect(r.summary).toContain(impactFigure(r));
      const share = impactContext(r).match(/^El ([\d,]+) %/)?.[1];
      expect(r.summary).toContain(`(el ${share} %)`);
      expect(impactContext(r)).toContain(`en ${r.zones_in_falta} zona`);
    }
  });

  it("uses the singular for a single zone", () => {
    expect(impactContext({ share_in_falta: 0.012, zones_in_falta: 1 })).toBe("El 1,2 % de toda la Comunidad, en 1 zona.");
    expect(moreZonesText(1)).toBe("Ver 1 zona más");
    expect(moreZonesText(22)).toBe("Ver 22 zonas más");
  });

  it("keeps the API order and puts apart the rows where no zone is clearly short", () => {
    const { affected, clear } = splitImpactRows(impact.rows);
    expect(affected.map((r) => r.row)).toEqual(impact.rows.filter((r) => r.people_in_falta > 0).map((r) => r.row));
    expect(clear.every((r) => r.people_in_falta === 0 && r.ranking.length === 0)).toBe(true);
    expect(affected.length + clear.length).toBe(impact.rows.length);
  });

  it("links each zone of the ranking to its «Qué falta» list, with its people and its ratio in words", () => {
    const nursery = row("escuela_infantil");
    const [top] = nursery.ranking;
    if (!top) throw new Error("no zones");
    const zone = rankedZone(top, nursery.people_label);
    expect(zone.href).toBe(`/que-falta?zona=${top.level}/${top.code}`);
    expect(zone.people).toMatch(/^[\d.]+ niños de 0 a 4 años$/);
    expect(zone.comparison).toBe(`Aquí hay ${Math.round(100 * top.ratio_to_reference)} por cada 100 que hay en municipios parecidos.`);
    // Same number as the API's own sentence for the zone
    expect(top.explanation).toContain(`Tienen ${Math.round(100 * top.ratio_to_reference)} por cada 100`);
  });

  it("says when a zone is compared together with its neighbours, with the group's ratio", () => {
    const elders = row("mayores");
    const grouped = elders.ranking.find((z) => z.comparison_group);
    if (!grouped) throw new Error("no grouped zone in the fixture");
    const zone = rankedZone(grouped, elders.people_label);
    expect(zone.comparison).toMatch(/^Junto con sus vecinos, hay \d+ por cada 100/);
    expect(grouped.explanation).toContain(`Junto con sus vecinos tienen ${Math.round(100 * grouped.ratio_to_reference)} por cada 100`);
  });

  it("has no link for a level the web has no list of", () => {
    const [top] = row("escuela_infantil").ranking;
    if (!top) throw new Error("no zones");
    expect(rankedZone({ ...top, level: "seccion_censal" }, "personas").href).toBeNull();
  });
});
