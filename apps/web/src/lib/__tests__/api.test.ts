import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import type { ScenarioState } from "../../contracts/scenario_state";
import { ApiError, createApi, type FetchLike, fetchThrough } from "../api";
import { createLimiter } from "../limit";

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

  it("asks for one gap row for every zone of a level (the map)", async () => {
    const calls: Call[] = [];
    const api = createApi(BASE, fakeFetch(200, envelope(fixture("gap_row_map.centro_salud_distrito.fixture.json")), calls));
    const body = await api.gapRowMap("distrito", "centro_salud");
    expect(calls[0]?.url).toBe(`${BASE}/api/v1/gaps?level=distrito&row=centro_salud`);
    expect(body.data.row).toBe("centro_salud");
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

  it("passes the abort signal of a search to fetch, and tells an aborted search apart", async () => {
    const calls: Call[] = [];
    const controller = new AbortController();
    await createApi(BASE, fakeFetch(200, envelope({}), calls)).search({}, { signal: controller.signal });
    expect(calls[0]?.init?.signal).toBe(controller.signal);
    controller.abort();
    const aborting: FetchLike = async () => {
      throw new DOMException("The operation was aborted.", "AbortError");
    };
    const error = await createApi(BASE, aborting).search({}, { signal: controller.signal }).catch((e: unknown) => e);
    expect(error).toMatchObject({ status: 0, code: "ABORTED" });
  });

  it("tells a request that took too long apart from one the caller cancelled (TIMEOUT)", async () => {
    const calls: Call[] = [];
    const timingOut: FetchLike = async (url, init) => {
      calls.push({ url: String(url), init });
      throw new DOMException("The operation timed out.", "TimeoutError");
    };
    const error = await createApi(BASE, timingOut).zoneGaps("distrito", "2807905", { timeoutMs: 10 }).catch((e: unknown) => e);
    expect(calls[0]?.init).toMatchObject({ timeoutMs: 10 });
    expect(error).toMatchObject({ status: 0, code: "TIMEOUT" });
  });

  it("never waits forever for its turn behind requests that hang: the wait has the same limit (TIMEOUT)", async () => {
    const run = createLimiter(1);
    const hanging = (() => new Promise<Response>(() => undefined)) as unknown as typeof fetch;
    const inTurn = fetchThrough(run, hanging);
    void inTurn("hangs");
    const error = await createApi(BASE, inTurn).zoneGaps("distrito", "2807905", { timeoutMs: 20 }).catch((e: unknown) => e);
    expect(error).toMatchObject({ status: 0, code: "TIMEOUT" });
  });

  it("starts a request's timeout when it leaves the queue, not while it waits its turn", async () => {
    const run = createLimiter(1);
    const signals: (AbortSignal | null | undefined)[] = [];
    // Each request takes 40 ms; the second waits for the first, so 60 ms counted from the call would expire
    const slow = (async (_url: string, init?: RequestInit) => {
      signals.push(init?.signal);
      await new Promise((resolve) => setTimeout(resolve, 40));
      if (init?.signal?.aborted) throw init.signal.reason;
      return new Response("{}");
    }) as typeof fetch;
    const inTurn = fetchThrough(run, slow);
    const answers = await Promise.all([inTurn("a", { timeoutMs: 60 }), inTurn("b", { timeoutMs: 60 })]);
    expect(answers.map((r) => r.status)).toEqual([200, 200]);
    expect(signals.every((s) => s instanceof AbortSignal)).toBe(true);
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

describe("api client, routes used by the map", () => {
  it("asks for simplified zone outlines by level", async () => {
    const calls: Call[] = [];
    await createApi(BASE, fakeFetch(200, envelope({ type: "FeatureCollection", features: [] }), calls)).adminUnits("distrito", 25);
    expect(calls[0]?.url).toBe(`${BASE}/api/v1/geo/admin-units?level=distrito&simplify_m=25`);
  });

  it("asks only for the districts of one municipio", async () => {
    const calls: Call[] = [];
    const api = createApi(BASE, fakeFetch(200, envelope({ type: "FeatureCollection", features: [] }), calls));
    await api.adminUnits("distrito", 25, "ES.28.MUN.28079");
    expect(calls[0]?.url).toBe(`${BASE}/api/v1/geo/admin-units?level=distrito&simplify_m=25&parent=ES.28.MUN.28079`);
  });

  it("asks for a zone's places of one category, repeating subcategory", async () => {
    const calls: Call[] = [];
    const page = envelope({ type: "FeatureCollection", features: [], total: 0, page: 1, pages: 1 });
    await createApi(BASE, fakeFetch(200, page, calls)).places({
      category: "transport",
      adminUnitId: "ES.28.DIS.2807905",
      subcategories: ["metro", "cercanias"],
    });
    expect(calls.map((c) => c.url)).toEqual([
      `${BASE}/api/v1/places?category=transport&admin_unit_id=ES.28.DIS.2807905&subcategory=metro&subcategory=cercanias`,
    ]);
  });

  it("asks for several categories of a zone in one request, comma-separated (since 12 nov)", async () => {
    const calls: Call[] = [];
    const page = envelope({ type: "FeatureCollection", features: [], total: 0, page: 1, pages: 1 });
    await createApi(BASE, fakeFetch(200, page, calls)).places({
      category: ["education", "health", "pharmacy"],
      adminUnitId: "ES.28.DIS.2807905",
      subcategories: ["Farmacia"],
    });
    expect(calls.map((c) => c.url)).toEqual([
      `${BASE}/api/v1/places?category=education%2Chealth%2Cpharmacy&admin_unit_id=ES.28.DIS.2807905&subcategory=Farmacia`,
    ]);
  });

  it("follows every page of places instead of cutting at the first", async () => {
    const calls: Call[] = [];
    const point = (id: string) => ({ type: "Feature", id, geometry: { type: "Point", coordinates: [0, 0] }, properties: {} });
    const pages: FetchLike = async (url) => {
      calls.push({ url: String(url) });
      const n = Number(new URL(String(url)).searchParams.get("page") ?? "1");
      const body = envelope({ type: "FeatureCollection", features: [point(`p${n}`)], total: 3, page: n, pages: 3 });
      return new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });
    };
    const places = await createApi(BASE, pages).places({ category: "education", adminUnitId: "ES.28.MUN.28092" });
    expect(places.map((p) => p.id)).toEqual(["p1", "p2", "p3"]);
    expect(calls.map((c) => new URL(c.url).searchParams.get("page"))).toEqual([null, "2", "3"]);
  });
});
