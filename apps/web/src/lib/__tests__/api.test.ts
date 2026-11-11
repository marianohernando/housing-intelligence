import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { ScenarioState } from "../../contracts/scenario_state";
import { ApiError, createApi, type FetchLike } from "../api";

const BASE = "http://api.test";
const FIXTURES = new URL("../../../../../data/fixtures/contracts/", import.meta.url);

function fixture(name: string): unknown {
  return JSON.parse(readFileSync(new URL(name, FIXTURES), "utf8"));
}

interface Call {
  url: string;
  init?: RequestInit;
}

function fakeFetch(status: number, body: unknown, calls: Call[] = []): FetchLike {
  return async (url, init) => {
    calls.push({ url: String(url), init });
    return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
  };
}

const envelope = (data: unknown) => ({
  data,
  meta: { request_id: "r", generated_at: "2026-11-11T00:00:00Z", api_version: "v1" },
  warnings: [],
});

describe("api client", () => {
  it("asks for a zone's gap list by level and code under /api/v1", async () => {
    const calls: Call[] = [];
    const api = createApi(BASE, fakeFetch(200, envelope(fixture("zone_gap_list.madrid.fixture.json")), calls));
    const body = await api.zoneGaps("distrito", "2807905");
    expect(calls[0]?.url).toBe(`${BASE}/api/v1/gaps/distrito/2807905`);
    expect(body.data.zone.code).toBe("28079");
  });

  it("asks only for CM datasets when told so (footer counter)", async () => {
    const calls: Call[] = [];
    const api = createApi(BASE, fakeFetch(200, envelope(fixture("dataset_list.all.fixture.json")), calls));
    const body = await api.datasets({ cmOnly: true });
    expect(calls[0]?.url).toBe(`${BASE}/api/v1/datasets?cm_only=true`);
    expect(body.data.cm_open_data_count).toBeGreaterThan(0);
  });

  it("posts the scenario as JSON to /search", async () => {
    const calls: Call[] = [];
    const scenario = fixture("scenario_state.familia_castellana.fixture.json") as ScenarioState;
    const api = createApi(BASE, fakeFetch(200, envelope({}), calls));
    await api.search(scenario);
    expect(calls[0]?.url).toBe(`${BASE}/api/v1/search`);
    expect(calls[0]?.init?.method).toBe("POST");
    expect(new Headers(calls[0]?.init?.headers).get("Content-Type")).toBe("application/json");
    expect(JSON.parse(String(calls[0]?.init?.body))).toEqual(scenario);
  });

  it("escapes path segments", async () => {
    const calls: Call[] = [];
    await createApi(BASE, fakeFetch(200, envelope({}), calls)).zoneGaps("municipio", "28/079");
    expect(calls[0]?.url).toBe(`${BASE}/api/v1/gaps/municipio/28%2F079`);
  });

  it("turns the API error body {detail: {code, message}} into an ApiError", async () => {
    const api = createApi(BASE, fakeFetch(404, { detail: { code: "NOT_FOUND", message: "No zone 99999" } }));
    const error = await api.zoneGaps("municipio", "99999").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 404, code: "NOT_FOUND", message: "No zone 99999" });
  });

  it("reads FastAPI validation errors (detail is a list)", async () => {
    const api = createApi(BASE, fakeFetch(422, { detail: [{ loc: ["path", "level"], msg: "Input should be…" }] }));
    await expect(api.zoneGaps("municipio", "x")).rejects.toMatchObject({ status: 422, code: "VALIDATION" });
  });

  it("keeps the HTTP status when the error body is not JSON", async () => {
    const api = createApi(BASE, async () => new Response("Bad gateway", { status: 502 }));
    await expect(api.datasets()).rejects.toMatchObject({ status: 502, code: "HTTP_502" });
  });

  it("reports an unreachable API as NETWORK, not as missing data", async () => {
    const api = createApi(BASE, async () => {
      throw new TypeError("fetch failed");
    });
    await expect(api.datasets()).rejects.toMatchObject({ status: 0, code: "NETWORK" });
  });
});
