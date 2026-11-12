// End-to-end checks of the public demo along the journeys of the pitch script (pitch/guion.md):
//   J1 home → «Ver un ejemplo» → 1st zone → «¿Y si cambias algo?» (apply and undo)
//   J2 «Qué falta» → «Madrid (toda la ciudad)»
//   J3 map by row («¿Qué quieres ver?»)
//   J4 the list of zones
// Every figure on screen is compared with the API response the page itself received: no fixed
// numbers, so the checks survive a data sync. Browser console errors and horizontal overflow fail.
//
//   node infra/deploy/e2e/e2e_prod.mjs [--base URL] [--browsers chromium,webkit,firefox]
//        [--devices desktop-1440,desktop-1920,mobile-390,projector-125] [--out DIR] [--shots]
//        [--block-external]   (the offline package: every request off localhost fails, as without network)
//   make e2e-prod                       (Chromium at 1440 px and 390 px, no screenshots)
// Needs the repo's Playwright (npm ci) and its browsers (npx playwright install chromium ...).
// Exit 0 only if every check of every combination passes.
import { mkdirSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { parseArgs } from "node:util";

import { chromium, firefox, webkit } from "playwright";

const BROWSERS = { chromium, webkit, firefox };
// The projector: 1280×720 at 125 % zoom is a 1024×576 CSS viewport with 1.25 device pixels per px.
const DEVICES = {
  "desktop-1440": { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  "desktop-1920": { viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 },
  "mobile-390": { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  "projector-125": { viewport: { width: 1024, height: 576 }, deviceScaleFactor: 1.25 },
};
const WAIT = 30_000; // a cold container plus the first search of an instance take a few seconds

const { values: opts } = parseArgs({
  options: {
    base: { type: "string", default: process.env.E2E_BASE_URL ?? "https://vidafacil-madrid.vercel.app" },
    browsers: { type: "string", default: "chromium" },
    devices: { type: "string", default: "desktop-1440,mobile-390" },
    out: { type: "string", default: join(tmpdir(), "vida-facil-e2e") },
    shots: { type: "boolean", default: false },
    "block-external": { type: "boolean", default: false },
  },
});
const BASE = opts.base.replace(/\/$/, "");

const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const squash = (s) => s.replace(/\s+/g, " ").trim();
const zonesText = (n) => (n === 1 ? "1 zona" : `${n} zonas`);
const passingText = (n, changed = false) => {
  const start = changed ? "Con este cambio" : "Con tu búsqueda tal cual";
  return n === 0 ? `${start} no sale ninguna zona.` : n === 1 ? `${start} sale 1 zona.` : `${start} salen ${n} zonas.`;
};
const isSearch = (r) => r.url().endsWith("/api/v1/search") && r.request().method() === "POST";

/** One run: a browser and a device, the four journeys, every check with its detail. */
class Run {
  constructor(browserName, device) {
    Object.assign(this, { browserName, device, checks: [], shots: [], consoleErrors: [], blocked: new Set() });
  }
  check(journey, name, ok, detail = "") {
    this.checks.push({ journey, name, ok: Boolean(ok), detail: String(detail) });
  }
  skip(journey, name, reason) {
    this.checks.push({ journey, name, ok: true, skipped: true, detail: reason });
  }
  async shot(page, step) {
    if (!opts.shots) return;
    await page.waitForTimeout(1500); // headless WebKit and Firefox paint the WebGL map later than Chromium
    const file = `${this.browserName}-${this.device}-${step}.jpg`;
    await page.screenshot({ path: join(opts.out, file), type: "jpeg", quality: 70 });
    this.shots.push(file);
  }
  async overflow(page, journey) {
    const px = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    this.check(journey, "no horizontal overflow", px <= 0, `${px} px`);
  }
}

async function journeySearch(run, page) {
  const J = "J1 search";
  const searches = [];
  page.on("request", (r) => r.url().endsWith("/api/v1/search") && searches.push(r.postDataJSON()));
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  const [first] = await Promise.all([
    page.waitForResponse(isSearch, { timeout: WAIT }),
    page.getByRole("button", { name: /Ver un ejemplo/ }).click(),
  ]);
  const result = (await first.json()).data;
  const rc = result.reality_check;
  run.check(J, "POST /search 200", first.status() === 200, first.status());
  const summary = page.getByText(passingText(rc.zones_passing)).first();
  await summary.waitFor({ timeout: WAIT });
  run.check(J, "summary = API zones_passing", true, passingText(rc.zones_passing));
  const total = await page.getByText(`De ${result.all_zones.length} zonas de la Comunidad de Madrid.`).count();
  run.check(J, "«De N zonas» = API all_zones", total > 0, result.all_zones.length);
  await checkFitLegend(run, page, rc);
  await run.shot(page, "j1-results");
  await checkFirstZone(run, page, result.results[0]);
  await checkRealityCheck(run, page, rc);
  run.check(J, "every /search sends max_minutes: null", searches.length > 0 &&
    searches.every((s) => (s?.anchors ?? []).every((a) => a.max_minutes === null)), `${searches.length} requests`);
  await run.overflow(page, J);
}

/** Legend counts against the API; narrow layouts hide the counts on purpose (Legend.module.css). */
async function checkLegendCounts(run, journey, page, expected) {
  const legend = squash(await page.locator("section[aria-label='Leyenda del mapa']").first().innerText());
  if (!/\d+ zonas?\b/.test(legend)) return run.skip(journey, "legend counts = API", "counts hidden at this width");
  for (const [label, n] of expected) {
    const ok = new RegExp(`${escapeRe(label)}\\s*${escapeRe(zonesText(n))}`).test(legend);
    run.check(journey, `legend «${label}» = ${zonesText(n)}`, ok, ok ? "" : legend.slice(0, 200));
  }
}

function checkFitLegend(run, page, rc) {
  const failing = rc.zones_evaluated - rc.zones_passing - rc.zones_unknown;
  return checkLegendCounts(run, "J1 search", page,
    [["Cumple todo", rc.zones_passing], ["No cumple todo", failing], ["Sin datos", rc.zones_unknown]]);
}

async function checkFirstZone(run, page, top) {
  const J = "J1 search";
  const name = top.zone.name;
  await page.getByRole("button", { name: new RegExp(`^1 ${escapeRe(name)}\\b`) }).first().click();
  const card = page.locator("aside").filter({ hasText: "Lo que tienes aquí" }).first();
  await card.waitFor({ timeout: WAIT });
  const text = squash(await card.innerText());
  run.check(J, "card name = API 1st zone", text.includes(name), name);
  run.check(J, "card % = API match_pct", new RegExp(`${top.match_pct}\\s*%`).test(text), `${top.match_pct} %`);
  const facts = card.getByRole("region", { name: "Lo que tienes aquí" }).locator("li");
  const shown = await facts.count();
  const missing = top.facts.filter((f) => !text.includes(squash(f.text)));
  run.check(J, "card facts = API facts", shown === top.facts.length && missing.length === 0,
    `${shown} on screen, ${top.facts.length} in the API${missing.length ? `; missing: ${missing[0].text}` : ""}`);
  await run.shot(page, "j1-card");
  await page.getByRole("button", { name: "Cerrar" }).first().click();
}

async function checkRealityCheck(run, page, rc) {
  const J = "J1 search";
  const region = page.getByRole("region", { name: "¿Y si cambias algo?", exact: true });
  const option = rc.relaxations.find((r) => r.added_zones > 0);
  if (!option) return run.check(J, "«¿Y si cambias algo?» has an option that adds zones", false, "none in the API");
  const text = squash(await region.innerText());
  run.check(J, "1st option = API relaxation", text.includes(option.label) &&
    text.includes(`saldrían ${zonesText(option.zones_if_relaxed)}`), `${option.label}: ${option.zones_if_relaxed}`);
  const [applied] = await Promise.all([
    page.waitForResponse(isSearch, { timeout: WAIT }),
    region.getByRole("button", { name: new RegExp(`^${escapeRe(option.label)}`) }).first().click(),
  ]);
  const after = (await applied.json()).data.reality_check.zones_passing;
  run.check(J, "applied: API zones = the option's zones_if_relaxed", after === option.zones_if_relaxed, after);
  await page.getByText(passingText(after, true)).first().waitFor({ timeout: WAIT });
  run.check(J, "applied: summary on screen", true, passingText(after, true));
  await run.shot(page, "j1-applied");
  const [undone] = await Promise.all([
    page.waitForResponse(isSearch, { timeout: WAIT }),
    page.getByRole("button", { name: "Volver a mi búsqueda" }).first().click(),
  ]);
  const back = (await undone.json()).data.reality_check.zones_passing;
  await page.getByText(passingText(back)).first().waitFor({ timeout: WAIT });
  run.check(J, "undone: back to the original zones", back === rc.zones_passing, back);
}

async function journeyMadrid(run, page) {
  const J = "J2 Qué falta Madrid";
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  await page.getByRole("link", { name: "Qué falta", exact: true }).first().click();
  const [gaps] = await Promise.all([
    page.waitForResponse((r) => /\/api\/v1\/gaps\/municipio\/28079$/.test(r.url()), { timeout: WAIT }),
    page.getByRole("link", { name: "Madrid (toda la ciudad)" }).first().click(),
  ]);
  const api = (await gaps.json()).data;
  const list = page.locator('ul[class*="rows"]').first();
  await list.waitFor({ timeout: WAIT });
  const items = list.locator(":scope > li");
  run.check(J, "rows on screen = API rows", (await items.count()) === api.rows.length, api.rows.length);
  // The web orders rows by status (FALTA first), so each API row is found by its label.
  for (const row of api.rows) {
    const item = items.filter({ has: page.getByRole("heading", { name: row.label, exact: true }) }).first();
    const found = (await item.count()) > 0;
    const text = found ? squash(await item.innerText()) : "";
    const status = row.status === "SIN_DATOS" ? "SIN DATOS" : row.status;
    const small = text.includes("Zona pequeña para comparar");
    run.check(J, `«${row.label}» ${status}${row.reliable === false ? " · zona pequeña" : ""}`,
      found && text.includes(status) && small === (row.reliable === false), found ? text.slice(0, 120) : "row not on screen");
  }
  await run.shot(page, "j2-madrid");
  await run.overflow(page, J);
}

/** The map's categories from the two /gaps responses of a row (Madrid counts as its districts). */
function expectedRowCounts(responses) {
  const counts = { FALTA: 0, JUSTO: 0, CUBIERTO: 0, "Zona pequeña para comparar": 0, "SIN DATOS": 0 };
  for (const data of responses) {
    for (const z of data.zones) {
      if (data.level === "municipio" && z.code === "28079") continue;
      counts[z.reliable === false ? "Zona pequeña para comparar" : z.status === "SIN_DATOS" ? "SIN DATOS" : z.status] += 1;
    }
  }
  return counts;
}

async function journeyRowMap(run, page, rows) {
  const J = "J3 map by row";
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  const picker = page.getByLabel("¿Qué quieres ver?").first();
  const values = (await picker.locator("option").evaluateAll((os) => os.map((o) => o.value))).filter(Boolean);
  run.check(J, "selector lists the gap rows", values.length > 0, values.join(", "));
  for (const row of values.slice(0, rows)) {
    const wanted = (level) => (r) => r.url().includes("/api/v1/gaps?") && r.url().includes(`level=${level}`) && r.url().includes(`row=${row}`);
    const [d, m] = await Promise.all([page.waitForResponse(wanted("distrito"), { timeout: WAIT }),
      page.waitForResponse(wanted("municipio"), { timeout: WAIT }), picker.selectOption(row)]);
    const district = (await d.json()).data;
    const expected = expectedRowCounts([district, (await m.json()).data]);
    const legend = page.locator("section[aria-label='Leyenda del mapa']").first();
    await legend.getByText(district.indicator_label).first().waitFor({ timeout: WAIT });
    await page.waitForTimeout(300); // the counts follow the caption in the same render
    run.check(J, `«${row}» legend caption = API indicator`, true, district.indicator_label);
    await checkLegendCounts(run, J, page, Object.entries(expected));
    if (row === values[0]) await run.shot(page, "j3-row-map");
  }
  await run.overflow(page, J);
}

async function journeyZoneList(run, page) {
  const J = "J4 zone list";
  const responses = []; // the page asks for districts and municipios separately
  page.on("response", (r) => r.url().includes("/api/v1/geo/admin-units") && r.ok() && responses.push(r.json()));
  await page.goto(`${BASE}/zonas`, { waitUntil: "networkidle" });
  const zones = new Map();
  for (const body of await Promise.all(responses)) for (const f of body.data.features) zones.set(f.properties.admin_unit_id, f.properties);
  // A municipio split into districts (Madrid) is listed as its districts plus «<name> (toda la ciudad)».
  const districts = [...zones.values()].filter((z) => z.level === "distrito");
  const split = [...zones.values()].filter((z) => z.level === "municipio" && districts.some((d) => d.code.startsWith(z.code)));
  const expected = { distrito: districts.length, municipio: [...zones.values()].filter((z) => z.level === "municipio").length - split.length };
  for (const [title, level] of [["Distritos de Madrid", "distrito"], ["Municipios", "municipio"]]) {
    const section = page.locator("section").filter({ has: page.getByRole("heading", { name: new RegExp(`^${title}`) }) }).first();
    const heading = squash(await section.getByRole("heading").first().innerText());
    const links = await section.getByRole("link").count();
    const shown = Number(heading.match(/\((\d+)\)/)?.[1]);
    run.check(J, `«${title}» = API ${level}s`, shown === expected[level] && links === shown,
      `${shown} in the title, ${links} links, ${expected[level]} in the API${level === "municipio" ? ` (${split.length} split into districts)` : ""}`);
  }
  for (const city of split) {
    const link = await page.getByRole("link", { name: `${city.name} (toda la ciudad)` }).count();
    run.check(J, `«${city.name} (toda la ciudad)» listed`, link > 0, city.code);
  }
  await run.shot(page, "j4-zone-list");
  await run.overflow(page, J);
}

async function runCombination(browserName, device) {
  const run = new Run(browserName, device);
  const options = { ...DEVICES[device], locale: "es-ES" };
  if (browserName === "firefox") delete options.isMobile; // Firefox has no mobile emulation in Playwright
  const browser = await BROWSERS[browserName].launch();
  const started = Date.now();
  try {
    for (const [name, journey] of [["J1 search", journeySearch], ["J2 Qué falta Madrid", journeyMadrid],
      ["J3 map by row", (r, p) => journeyRowMap(r, p, opts.shots ? 1 : 99)], ["J4 zone list", journeyZoneList]]) {
      const context = await browser.newContext(options);
      if (opts["block-external"]) {
        await context.route("**/*", (route) => {
          const { hostname } = new URL(route.request().url());
          if (["localhost", "127.0.0.1"].includes(hostname) || route.request().url().startsWith("data:")) return route.continue();
          run.blocked.add(hostname);
          return route.abort("internetdisconnected");
        });
      }
      const page = await context.newPage();
      page.on("console", (m) => m.type() === "error" && run.consoleErrors.push(`${name}: ${m.text()}`));
      page.on("pageerror", (e) => run.consoleErrors.push(`${name}: ${e.message}`));
      try {
        await journey(run, page);
      } catch (e) {
        run.check(name, "journey completed", false, squash(e.message).slice(0, 300));
        await run.shot(page, `${name.split(" ")[0].toLowerCase()}-error`).catch(() => {});
      }
      await context.close();
    }
  } finally {
    await browser.close();
  }
  run.check("all", "no browser console errors", run.consoleErrors.length === 0, run.consoleErrors.slice(0, 3).join(" | "));
  run.seconds = Math.round((Date.now() - started) / 1000);
  run.blocked = [...run.blocked];
  return run;
}

mkdirSync(opts.out, { recursive: true });
const runs = [];
for (const browserName of opts.browsers.split(",")) {
  for (const device of opts.devices.split(",")) {
    const run = await runCombination(browserName, device);
    const failed = run.checks.filter((c) => !c.ok);
    console.log(`${failed.length ? "FAIL" : "ok  "} ${browserName.padEnd(8)} ${device.padEnd(13)} ${run.checks.length - failed.length}/${run.checks.length} checks · ${run.seconds} s`);
    for (const c of failed) console.log(`       ${c.journey} · ${c.name}: ${c.detail}`);
    runs.push(run);
  }
}
const report = { base: BASE, checked_at: new Date().toISOString(), runs };
writeFileSync(join(opts.out, "e2e-report.json"), `${JSON.stringify(report, null, 1)}\n`);
console.log(`report: ${join(opts.out, "e2e-report.json")}`);
process.exit(runs.some((r) => r.checks.some((c) => !c.ok)) ? 1 : 0);
