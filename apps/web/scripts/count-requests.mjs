// Requests to the API of one visit to a zone screen (incident EMAXCONNSESSION, 12 nov): each API
// request can hold a database connection, and the pooler admits 15 clients. Counts, per step, the
// requests the page sends, the same URL asked twice, and the most in flight at once: until the
// answer starts (what the API holds) and until its body has arrived.
//
//   node scripts/count-requests.mjs [outDir]
//
// Steps, in one tab: open the zone (Chamartín, then Fuencarral-El Pardo) with an empty cache and
// wait for the camera to land; press every type of «Todos los centros»; go to the tab «Qué falta»
// and back with the browser; hide and show the page as when switching browser tabs. Web on 3011
// (next build + start) and API on 8011, as in LINEAS.md. Writes requests.json to outDir.
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { chromium } from "playwright";

const today = new Date().toLocaleDateString("sv-SE");
const [out = join("..", "..", "evidence", "map-004", today, "perf")] = process.argv.slice(2);
const BASE = "http://localhost:3011";
const API_HOST = "localhost:8011";
const ZONES = [
  ["Chamartín", "/zona/distrito/2807905"],
  ["Fuencarral-El Pardo", "/zona/distrito/2807908"],
];
const PROFILES = {
  desktop: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  mobile: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
};
const LANDING_MS = 9000; // the camera flies to the zone; key points are asked once it lands

/** «/api/v1/places?category=health» -> «places health»: the endpoint and what tells two apart. */
function label(url) {
  const u = new URL(url);
  const path = u.pathname.replace(/^\/api\/v1\//, "");
  if (path === "places") return `places ${u.searchParams.getAll("category").join("+")}`;
  if (path.startsWith("geo/admin-units")) return `admin-units ${u.searchParams.get("level")}`;
  return path.split("/").slice(0, 1).join("/");
}

/** Most intervals [start, end) open at the same time. */
function most(requests, end) {
  const events = requests.flatMap((r) => [[r.start, 1], [r[end] ?? Infinity, -1]]).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  let open = 0;
  let peak = 0;
  for (const [, delta] of events) {
    open += delta;
    peak = Math.max(peak, open);
  }
  return peak;
}

function summary(requests) {
  const byUrl = new Map();
  for (const r of requests) byUrl.set(r.url, (byUrl.get(r.url) ?? 0) + 1);
  const byEndpoint = {};
  for (const r of requests) byEndpoint[label(r.url)] = (byEndpoint[label(r.url)] ?? 0) + 1;
  return {
    peticiones: requests.length,
    // Sent and not yet answered (the API holds a database connection until it answers)
    max_en_paralelo: most(requests, "answered"),
    // The same, until the body has arrived
    max_descargando: most(requests, "end"),
    cronologia_ms: requests.map((r) => [label(r.url), r.start, r.answered, r.end]),
    repetidas: [...byUrl].filter(([, n]) => n > 1).map(([url, n]) => `${n}× ${label(url)}`),
    por_endpoint: byEndpoint,
    fallidas: requests.filter((r) => r.failed).map((r) => `${label(r.url)}: ${r.failed}`),
  };
}

async function visit(browser, profileName, [zoneName, path]) {
  const ctx = await browser.newContext({ ...PROFILES[profileName], locale: "es-ES" });
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send("Network.enable");
  await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
  const errors = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  page.on("pageerror", (e) => errors.push(e.message));
  let step = [];
  const t0 = Date.now();
  const inFlight = new Map();
  page.on("request", (req) => {
    if (new URL(req.url()).host !== API_HOST || req.method() === "OPTIONS") return;
    const entry = { url: req.url(), start: Date.now() - t0, answered: null, end: null, failed: null };
    inFlight.set(req, entry);
    step.push(entry);
  });
  page.on("response", (res) => {
    const entry = inFlight.get(res.request());
    if (entry) entry.answered = Date.now() - t0;
  });
  page.on("requestfinished", (req) => {
    const entry = inFlight.get(req);
    if (entry) entry.end = Date.now() - t0;
  });
  page.on("requestfailed", (req) => {
    const entry = inFlight.get(req);
    if (entry) Object.assign(entry, { answered: entry.answered ?? Date.now() - t0, end: Date.now() - t0, failed: req.failure()?.errorText ?? "failed" });
  });
  const take = () => {
    const done = summary(step);
    step = [];
    return done;
  };

  const result = { zona: zoneName, perfil: profileName };
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(LANDING_MS);
  await page.waitForLoadState("networkidle");
  result.carga = take();

  // Every type of «Todos los centros», as a person comparing them
  const panel = page.getByRole("region", { name: "Todos los centros", exact: true });
  if (profileName === "mobile") {
    await page.getByRole("button", { name: /Desliza hacia arriba/ }).tap();
    await page.waitForTimeout(600);
  }
  for (const name of ["Escuelas infantiles", "Centros de salud", "Hospitales", "Farmacias", "Mayores", "Colegios"]) {
    const chip = panel.getByRole("button", { name: new RegExp(`^${name}`) });
    await chip.scrollIntoViewIfNeeded();
    await (profileName === "mobile" ? chip.tap() : chip.click());
    await page.waitForTimeout(400);
  }
  await page.waitForLoadState("networkidle");
  result.tipos_de_centro = take();

  // Tab «Qué falta» of the zone and back to the zone with the browser
  await page.getByRole("navigation", { name: "Secciones" }).getByRole("link", { name: "Qué falta" }).click();
  await page.getByText(/De dónde sale/).first().waitFor({ timeout: 20000 });
  await page.waitForLoadState("networkidle");
  result.pestana_que_falta = take();
  await page.goBack();
  await panel.getByRole("button", { name: /^Colegios/ }).waitFor({ timeout: 20000 });
  await page.waitForTimeout(LANDING_MS);
  await page.waitForLoadState("networkidle");
  result.vuelta_a_la_zona = take();

  // Another browser tab in front, then this one again
  const other = await ctx.newPage();
  await other.bringToFront();
  await other.waitForTimeout(1500);
  await page.bringToFront();
  await page.waitForTimeout(1500);
  await page.waitForLoadState("networkidle");
  result.cambio_de_pestana_del_navegador = take();
  await other.close();

  result.total = ["carga", "tipos_de_centro", "pestana_que_falta", "vuelta_a_la_zona", "cambio_de_pestana_del_navegador"].reduce(
    (n, key) => n + result[key].peticiones,
    0,
  );
  result.consola = errors;
  await ctx.close();
  return result;
}

mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const report = { como: "Playwright contra web 3011 (next build + start) y API 8011, caché vacía", visitas: [] };
for (const profile of Object.keys(PROFILES)) {
  for (const zone of ZONES) report.visitas.push(await visit(browser, profile, zone));
}
await browser.close();
const name = process.env.REQUESTS_NAME ?? "requests";
writeFileSync(join(out, `${name}.json`), `${JSON.stringify(report, null, 1)}\n`);
for (const v of report.visitas) {
  console.log(
    `${v.perfil.padEnd(8)} ${v.zona.padEnd(20)} carga ${v.carga.peticiones} (máx. ${v.carga.max_en_paralelo} en paralelo, ${v.carga.max_descargando} descargando, ${v.carga.repetidas.length} repetidas) · tipos ${v.tipos_de_centro.peticiones} · «Qué falta» ${v.pestana_que_falta.peticiones} · vuelta ${v.vuelta_a_la_zona.peticiones} · pestaña ${v.cambio_de_pestana_del_navegador.peticiones} · total ${v.total} · consola ${v.consola.length}`,
  );
}
