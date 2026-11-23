import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

import { OPEN_DATA_FILES } from "@/lib/developers";

const PUBLIC_DIR = fileURLToPath(new URL("../../../public", import.meta.url));

describe("the open data files of «Para desarrolladores» (F14)", () => {
  it("links the catalogue and the two Smart Data Models files, once each", () => {
    expect(OPEN_DATA_FILES.map((file) => file.path)).toEqual([
      "/datos/catalogo.dcat.jsonld",
      "/datos/sdm/datasets.json",
      "/datos/sdm/farmacias.json",
    ]);
  });

  it("every link is a JSON file that public/ serves, written by scripts/export_dcat_sdm.py", () => {
    for (const file of OPEN_DATA_FILES) {
      const content = JSON.parse(readFileSync(`${PUBLIC_DIR}${file.path}`, "utf8"));
      expect(content).toBeTypeOf("object");
      expect(file.title.length).toBeGreaterThan(0);
      expect(file.text).not.toMatch(/DCAT-AP-ES/);
    }
  });
});
