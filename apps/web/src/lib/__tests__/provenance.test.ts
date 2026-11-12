import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { DatasetList, DatasetRef } from "../../contracts/dataset_list_response";
import {
  attributions,
  ATTRIBUTIONS_FALLBACK,
  attributionsOrFallback,
  counterText,
  datasetLines,
  mapAttribution,
  sortDatasets,
} from "../provenance";

const metro: DatasetRef = {
  dataset_id: "crtm_metro",
  name: "Oferta planificada de la Red de Metro",
  publisher: "Consorcio Regional de Transportes de Madrid",
  is_cm_open_data: true,
  license: "CRTM Licencia de datos abiertos (LDA)",
  url: "https://datos.comunidad.madrid/dataset/red_de_metro",
  version: "2026-11-10-cccabfd6f025",
};
const osm: DatasetRef = {
  dataset_id: "osm_red_peatonal",
  name: "Red peatonal de OpenStreetMap",
  publisher: "OpenStreetMap contributors",
  is_cm_open_data: false,
  license: null,
  url: null,
  version: null,
};

describe("counterText (pie.contador)", () => {
  it("counts the CM portal datasets and names the other publishers", () => {
    expect(counterText(23)).toBe(
      "Datos: 23 conjuntos de la Comunidad de Madrid (con los del CRTM) + Ayuntamiento de Madrid + Ministerio de Sanidad",
    );
  });
});

describe("attributions (attribution_text of /datasets, from the source catalogue)", () => {
  // Test fixture published by line A with the contract (data/fixtures/contracts), not demo data.
  const url = new URL("../../../../../data/fixtures/contracts/dataset_list.all.fixture.json", import.meta.url);
  const { datasets } = JSON.parse(readFileSync(url, "utf8")) as DatasetList;

  it("cites every source once, as the catalogue writes it, with CartoCiudad on its own", () => {
    const cited = attributions(datasets).map((a) => a.text);
    for (const ref of datasets) {
      const text = ref.attribution_text ?? "";
      // Each dataset's citation is made of the lines shown, in order
      expect(cited.some((c) => text === c || text.startsWith(`${c} `))).toBe(true);
    }
    expect(new Set(cited).size).toBe(cited.length);
    expect(cited.some((c) => c.includes("Ministerio de Sanidad") && c.includes("actualizado a 31/12/2024"))).toBe(true);
    expect(cited.filter((c) => c.includes("CartoCiudad"))).toHaveLength(1);
    expect(cited.filter((c) => c.includes("Comunidad de Madrid"))).toHaveLength(1);
  });

  it("keeps the fallback faithful: what the API's fixture gives today", () => {
    expect(attributions(datasets)).toEqual(ATTRIBUTIONS_FALLBACK);
  });

  it("shows the fallback only while /datasets has not answered, or answers without citations", () => {
    expect(attributionsOrFallback(null)).toBe(ATTRIBUTIONS_FALLBACK);
    expect(attributionsOrFallback([{ ...metro, attribution_text: null }])).toBe(ATTRIBUTIONS_FALLBACK);
    const next = { ...metro, attribution_text: "Powered by CRTM (texto nuevo del catálogo)." };
    expect(attributionsOrFallback([next])).toEqual([{ text: "Powered by CRTM (texto nuevo del catálogo).", href: "https://www.crtm.es" }]);
  });
});

describe("mapAttribution (the screens with a map have no footer)", () => {
  const url = new URL("../../../../../data/fixtures/contracts/dataset_list.all.fixture.json", import.meta.url);
  const { datasets } = JSON.parse(readFileSync(url, "utf8")) as DatasetList;
  const text = (html: string) => html.replace(/<[^>]+>/g, "");

  it("carries every citation of the footer, linked, in a new tab", () => {
    const html = mapAttribution(datasets);
    expect(text(html)).toBe(attributions(datasets).map((a) => a.text).join(" · "));
    expect(html).toContain('<a href="https://datos.madrid.es" target="_blank" rel="noopener noreferrer">Fuente: Ayuntamiento de Madrid');
    expect(text(mapAttribution(null))).toBe(text(html));
  });
});

describe("datasetLines (fuente.*)", () => {
  it("says who publishes it, the CM portal, version, licence and how to open it", () => {
    expect(datasetLines(metro)).toEqual({
      title: "Oferta planificada de la Red de Metro — Consorcio Regional de Transportes de Madrid",
      portal: "Portal de Datos Abiertos de la Comunidad de Madrid",
      version: "Versión de los datos: 2026-11-10-cccabfd6f025",
      license: "Licencia: CRTM Licencia de datos abiertos (LDA)",
      url: "https://datos.comunidad.madrid/dataset/red_de_metro",
      openHint: "en el portal de datos (se abre en una pestaña nueva)",
    });
  });

  it("leaves out what the API does not give, instead of inventing it", () => {
    expect(datasetLines(osm)).toMatchObject({ portal: null, version: null, license: null, url: null });
  });
});

describe("sortDatasets", () => {
  it("puts the CM portal datasets first, each group by name", () => {
    const rent = { ...metro, dataset_id: "alquiler", name: "Alquiler medio" };
    expect(sortDatasets([osm, metro, rent]).map((d) => d.dataset_id)).toEqual(["alquiler", "crtm_metro", "osm_red_peatonal"]);
  });
});
