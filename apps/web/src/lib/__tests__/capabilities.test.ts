import { describe, expect, it } from "vitest";

import type { SearchResponse } from "@/contracts/search_response";

import { flagOn, runSearch, SEARCH_ENABLED } from "../capabilities";
import { defaultScenario } from "../scenario";

function fakeApi() {
  const calls: unknown[] = [];
  const answer = { data: {} } as SearchResponse;
  const signals: (AbortSignal | undefined)[] = [];
  const search = async (scenario: unknown, init?: { signal?: AbortSignal }) => (calls.push(scenario), signals.push(init?.signal), answer);
  return { calls, signals, api: { search }, answer };
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

  it("on: hands the abort signal to the API, so a newer search can cancel it", async () => {
    const { signals, api } = fakeApi();
    const controller = new AbortController();
    await runSearch(api, defaultScenario(), true, controller.signal);
    expect(signals).toEqual([controller.signal]);
  });
});
