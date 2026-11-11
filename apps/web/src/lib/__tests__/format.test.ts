import { describe, expect, it } from "vitest";

import { formatEuros } from "../format";

describe("formatEuros", () => {
  it("groups thousands with a dot, also for 4-digit amounts", () => {
    expect(formatEuros(1200)).toBe("1.200 €");
    expect(formatEuros(300000)).toBe("300.000 €");
    expect(formatEuros(950)).toBe("950 €");
  });
});
