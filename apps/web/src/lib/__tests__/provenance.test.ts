import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { DatasetList, DatasetRef } from "../../contracts/dataset_list_response";
import {
  CARTOCIUDAD_ATTRIBUTION,
  counterText,
  datasetLines,
  mapAttribution,
  MINISTRY_ATTRIBUTION,
  ministryAttribution,
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

describe("ministryAttribution (pie.sanidad)", () => {
  // Test fixture published by line A with the contract (data/fixtures/contracts), not demo data.
  const url = new URL("../../../../../data/fixtures/contracts/dataset_list.all.fixture.json", import.meta.url);
  const { datasets } = JSON.parse(readFileSync(url, "utf8")) as DatasetList;

  it("cites both catalogues with their update date, read from the API, as line D wrote it", () => {
    expect(ministryAttribution(datasets)).toBe(MINISTRY_ATTRIBUTION);
  });

  it("follows the API when a catalogue changes, and keeps D's text until it answers", () => {
    const hospitals = datasets.find((d) => d.dataset_id === "ms_catalogo_nacional_hospitales");
    if (!hospitals) throw new Error("fixture without the hospital catalogue");
    const next = { ...hospitals, name: "Catálogo Nacional de Hospitales 2026 (actualizado a 31 de diciembre de 2025)" };
    expect(ministryAttribution([next])).toBe("Fuente: Ministerio de Sanidad — Catálogo Nacional de Hospitales 2026 (actualizado a 31/12/2025).");
    expect(ministryAttribution(null)).toBe(MINISTRY_ATTRIBUTION);
    expect(ministryAttribution([metro, osm])).toBe(MINISTRY_ATTRIBUTION);
  });
});

describe("mapAttribution (mapa.atribucion: the screens with a map have no footer)", () => {
  const url = new URL("../../../../../data/fixtures/contracts/dataset_list.all.fixture.json", import.meta.url);
  const { datasets } = JSON.parse(readFileSync(url, "utf8")) as DatasetList;
  const text = (html: string) => html.replace(/<[^>]+>/g, "");

  it("cites the CM, the Ayuntamiento, CRTM, the Ministry with its catalogues' dates from /datasets and CartoCiudad as the IGN asks", () => {
    const html = mapAttribution(datasets);
    expect(text(html)).toBe(
      "Comunidad de Madrid · Ayuntamiento de Madrid · Powered by CRTM · Ministerio de Sanidad (catálogos a 31/12/2024 y 31/12/2025) · © Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es",
    );
    expect(html).toContain('<a href="https://datos.madrid.es" target="_blank" rel="noopener noreferrer">Ayuntamiento de Madrid</a>');
    expect(CARTOCIUDAD_ATTRIBUTION).toBe("© Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es");
  });

  it("follows the API's dates, and keeps line D's text while /datasets has not answered", () => {
    expect(text(mapAttribution(null))).toBe(text(mapAttribution(datasets)));
    const hospitals = datasets.find((d) => d.dataset_id === "ms_catalogo_nacional_hospitales");
    if (!hospitals) throw new Error("fixture without the hospital catalogue");
    const next = { ...hospitals, name: "Catálogo Nacional de Hospitales 2026 (actualizado a 31 de diciembre de 2025)" };
    expect(text(mapAttribution([next]))).toContain("Ministerio de Sanidad (catálogo a 31/12/2025)");
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
