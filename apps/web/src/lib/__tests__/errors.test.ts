import { describe, expect, it } from "vitest";

import { errorMessage } from "../errors";

describe("errorMessage", () => {
  it("tells a network failure apart from a server failure", () => {
    expect(errorMessage({ code: "NETWORK" })).toMatch(/conexión/);
    expect(errorMessage({ code: "HTTP_502" })).toMatch(/por nuestra parte/);
  });

  it("uses the API error codes when it knows them", () => {
    expect(errorMessage({ code: "NOT_FOUND" })).toMatch(/No encontramos esa zona/);
    expect(errorMessage({ code: "VALIDATION" })).toMatch(/Revisa/);
  });

  it("never uses English or technical words", () => {
    for (const code of ["NETWORK", "VALIDATION", "NOT_FOUND", "HTTP_500", "SOURCE_DEGRADED"]) {
      expect(errorMessage({ code })).not.toMatch(/error|HTTP|API|dataset/i);
    }
  });
});
