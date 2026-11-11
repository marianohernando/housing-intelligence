import { describe, expect, it } from "vitest";

import type { DatasetRef } from "../../contracts/dataset_list_response";
import { counterText, datasetLines, sortDatasets } from "../provenance";

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
    expect(counterText(21)).toBe("Datos: 21 conjuntos de la Comunidad de Madrid + Ayuntamiento de Madrid + CRTM");
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
      openLabel: "Abrir Oferta planificada de la Red de Metro en el portal de datos (se abre en una pestaña nueva)",
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
