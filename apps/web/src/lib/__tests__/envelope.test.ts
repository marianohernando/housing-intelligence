import { describe, expect, it } from "vitest";

import { API_VERSION, buildMeta, envelope } from "../envelope";

describe("envelope", () => {
  it("builds deterministic meta when inputs are fixed", () => {
    const meta = buildMeta(new Date("2026-10-20T10:00:00Z"), "req-1");
    expect(meta).toEqual({
      request_id: "req-1",
      generated_at: "2026-10-20T10:00:00.000Z",
      api_version: API_VERSION,
      methodology_version: null,
      data_version: null,
    });
  });

  it("wraps data with unique request ids and empty warnings", () => {
    const a = envelope({ status: "ok" });
    const b = envelope({ status: "ok" });
    expect(a.data).toEqual({ status: "ok" });
    expect(a.warnings).toEqual([]);
    expect(a.meta.request_id).not.toBe(b.meta.request_id);
  });
});
