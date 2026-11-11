import { describe, expect, it } from "vitest";

import type { SearchResponse } from "@/contracts/search_response";

import { flagOn, runSearch, SEARCH_ENABLED } from "../capabilities";
import { defaultScenario } from "../scenario";

function fakeApi() {
  const calls: unknown[] = [];
  const answer = { data: {} } as SearchResponse;
  return { calls, api: { search: async (scenario: unknown) => (calls.push(scenario), answer) }, answer };
}

describe("capability flags", () => {
  it("turns a flag on only with true or 1", () => {
    expect(flagOn("true")).toBe(true);
    expect(flagOn("1")).toBe(true);
    expect(flagOn(undefined)).toBe(false);
    expect(flagOn("")).toBe(false);
    expect(flagOn("false")).toBe(false);
  });

  it("keeps the search off by default (POST /search is not published yet)", () => {
    expect(SEARCH_ENABLED).toBe(false);
  });
});

describe("runSearch", () => {
  it("off: never calls the API", async () => {
    const { calls, api } = fakeApi();
    expect(await runSearch(api, defaultScenario(), false)).toBeNull();
    expect(calls).toHaveLength(0);
  });

  it("on: posts the scenario once and returns the answer", async () => {
    const { calls, api, answer } = fakeApi();
    expect(await runSearch(api, defaultScenario(), true)).toBe(answer);
    expect(calls).toHaveLength(1);
  });
});
