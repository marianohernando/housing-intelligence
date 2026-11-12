// Load performance of the public demo: LCP, FCP, load and bytes transferred, with an empty cache,
// on a phone over slow 4G (the Lighthouse mobile profile: 150 ms RTT, 1.6 Mbps down, 750 kbps up,
// CPU 4× slower) and on an unthrottled desktop for reference. Chromium only (CDP throttling).
// CDP throttles the page's own requests, not those of the map's Web Worker (the basemap tiles):
// bytes are counted for every request (Playwright sizes, workers included), and the tiles' time on
// slow 4G is estimated from their bytes.
//
//   node infra/deploy/e2e/perf_prod.mjs [--base URL] [--runs 3] [--out DIR]
// Prints a table and writes perf-report.json. Medians over the runs; every run is in the report.
import { mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { parseArgs } from "node:util";

import { chromium } from "playwright";

const { values: opts } = parseArgs({
  options: {
    base: { type: "string", default: process.env.E2E_BASE_URL ?? "https://vidafacil-madrid.vercel.app" },
    runs: { type: "string", default: "3" },
    out: { type: "string", default: join(tmpdir(), "vida-facil-perf") },
  },
});
const BASE = opts.base.replace(/\/$/, "");
const HOST = new URL(BASE).host;

const PROFILES = {
  "mobile-slow4g": {
    context: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
    network: { latency: 150, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8 },
    cpu: 4,
  },
  desktop: { context: { viewport: { width: 1440, height: 900 } }, network: null, cpu: 1 },
};
const PAGES = [
  ["portada", "/"],
  ["zona Chamartín", "/zona/distrito/2807905"],
  ["qué falta Madrid", "/que-falta?zona=municipio/28079"],
];

const median = (xs) => [...xs].sort((a, b) => a - b)[Math.floor(xs.length / 2)];
const kb = (n) => Math.round(n / 1024);

function bucket(url) {
  const u = new URL(url);
  if (u.host === HOST) return u.pathname.startsWith("/api/") ? "api" : "web";
  return /openfreemap|tiles|maptiler|openmaptiles/.test(u.host) ? "map tiles" : "other";
}

/** A fresh context (empty cache) with throttling, LCP observer and per-request byte counts. */
async function open(browser, profile) {
  const context = await browser.newContext({ ...profile.context, locale: "es-ES" });
  const page = await context.newPage();
  const cdp = await context.newCDPSession(page);
  await cdp.send("Network.enable");
  await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
  if (profile.network) await cdp.send("Network.emulateNetworkConditions", { offline: false, ...profile.network });
  if (profile.cpu > 1) await cdp.send("Emulation.setCPUThrottlingRate", { rate: profile.cpu });
  const bytes = { web: 0, api: 0, "map tiles": 0, other: 0 };
  let count = 0;
  const pending = [];
  context.on("requestfinished", (r) => {
    if (r.url().startsWith("data:")) return;
    count += 1;
    pending.push(r.sizes().then((s) => { bytes[bucket(r.url())] += s.responseBodySize + s.responseHeadersSize; }).catch(() => {}));
  });
  await page.addInitScript(() => {
    window.__lcp = 0;
    new PerformanceObserver((list) => { for (const e of list.getEntries()) window.__lcp = e.startTime; })
      .observe({ type: "largest-contentful-paint", buffered: true });
  });
  return { context, page, bytes, requests: () => count, settled: () => Promise.all(pending) };
}

async function measurePage(browser, profile, path) {
  const { context, page, bytes, requests, settled } = await open(browser, profile);
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle", timeout: 180_000 });
  const timing = await page.evaluate(() => {
    const nav = performance.getEntriesByType("navigation")[0];
    return {
      lcp_ms: Math.round(window.__lcp),
      fcp_ms: Math.round(performance.getEntriesByName("first-contentful-paint")[0]?.startTime ?? 0),
      load_ms: Math.round(nav.loadEventEnd),
    };
  });
  await page.waitForTimeout(2000); // late tiles of the map's worker
  await settled();
  await context.close();
  const tilesSlow4g = profile.network ? Math.round((bytes["map tiles"] / profile.network.downloadThroughput) * 10) / 10 : null;
  return { ...timing, requests: requests(), map_tiles_slow4g_estimate_s: tilesSlow4g, kb: Object.fromEntries(Object.entries(bytes).map(([k, v]) => [k, kb(v)])),
    total_kb: kb(Object.values(bytes).reduce((a, b) => a + b, 0)) };
}

/** From the click on «Ver un ejemplo» to the results on screen, and the /search response. */
async function measureSearch(browser, profile) {
  const { context, page } = await open(browser, profile);
  await page.goto(`${BASE}/`, { waitUntil: "networkidle", timeout: 180_000 });
  const started = Date.now();
  const [response] = await Promise.all([
    page.waitForResponse((r) => r.url().endsWith("/api/v1/search"), { timeout: 120_000 }),
    page.getByRole("button", { name: /Ver un ejemplo/ }).click(),
  ]);
  const body = await response.body();
  const apiMs = Date.now() - started;
  await page.getByText(/Con tu búsqueda tal cual (salen|sale|no sale)/).first().waitFor({ timeout: 120_000 });
  const screenMs = Date.now() - started;
  await context.close();
  return { click_to_response_ms: apiMs, click_to_results_ms: screenMs, search_body_kb: kb(body.length) };
}

mkdirSync(opts.out, { recursive: true });
const browser = await chromium.launch();
const report = { base: BASE, measured_at: new Date().toISOString(), runs: Number(opts.runs), profiles: {} };
try {
  for (const [name, profile] of Object.entries(PROFILES)) {
    const result = (report.profiles[name] = { pages: {}, search: [] });
    for (const [label, path] of PAGES) {
      const runs = [];
      for (let i = 0; i < Number(opts.runs); i++) runs.push(await measurePage(browser, profile, path));
      result.pages[label] = { path, runs, median: Object.fromEntries(["lcp_ms", "fcp_ms", "load_ms", "total_kb"].map((k) => [k, median(runs.map((r) => r[k]))])) };
      const m = result.pages[label].median;
      const tiles = runs[0].map_tiles_slow4g_estimate_s;
      console.log(`${name.padEnd(14)} ${label.padEnd(17)} LCP ${m.lcp_ms} ms · FCP ${m.fcp_ms} ms · load ${m.load_ms} ms · ${m.total_kb} KB (${JSON.stringify(runs[0].kb)})${tiles ? ` · tiles ≈ ${tiles} s` : ""}`);
    }
    for (let i = 0; i < Number(opts.runs); i++) result.search.push(await measureSearch(browser, profile));
    const s = result.search;
    console.log(`${name.padEnd(14)} ejemplo → resultados: ${median(s.map((r) => r.click_to_results_ms))} ms (respuesta ${median(s.map((r) => r.click_to_response_ms))} ms, ${s[0].search_body_kb} KB)`);
  }
} finally {
  await browser.close();
}
writeFileSync(join(opts.out, "perf-report.json"), `${JSON.stringify(report, null, 1)}\n`);
console.log(`report: ${join(opts.out, "perf-report.json")}`);
