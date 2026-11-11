// Quality check of the web for the test phase (FASE_PRUEBAS, line B), against the real API, with
// axe WCAG 2.2 AA and the browser console, at 1440 and 390 px:
//
//   node scripts/check-qa.mjs fixes [outDir]    # phase 1: PENDIENTES fixes (texts, search, R-06)
//
// Web on 3011 (next build + start, NEXT_PUBLIC_FEATURE_SEARCH=true) and API on 8011, as in
// LINEAS.md. Writes qa_<mode>.json and the captures to outDir (default evidence/map-004/<today>).
import { mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";

import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const AXE = require.resolve("axe-core/axe.min.js");
const today = new Date().toLocaleDateString("sv-SE");
const [mode = "fixes", out = join("..", "..", "evidence", "map-004", today)] = process.argv.slice(2);
const BASE = "http://localhost:3011";
const DESKTOP = { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 };
const MOBILE = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true };
const PASSING = "Con tu búsqueda tal cual salen 32 zonas.";

mkdirSync(out, { recursive: true });
const report = { modo: mode, como: "Playwright contra web 3011 (next build + start) y API 8011 (datos reales)" };
const flat = (text) => text.replace(/\s+/g, " ").trim();

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    const r = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } });
    return r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, ejemplo: v.nodes[0]?.target }));
  });
}

async function open(browser, profile, path = "/") {
  const ctx = await browser.newContext({ ...profile, locale: "es-ES" });
  const page = await ctx.newPage();
  const errors = [];
  const aborted = [];
  page.on("console", (m) => {
    if (m.type() === "error") errors.push(m.text());
  });
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("requestfailed", (r) => {
    if (r.url().includes("/api/v1/search")) aborted.push(r.failure()?.errorText ?? "failed");
  });
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1200);
  return { ctx, page, errors, aborted };
}

const overflow = (page) => page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);

async function loadExample(page, tap = false) {
  const button = page.getByRole("button", { name: /Ver un ejemplo/ });
  await (tap ? button.tap() : button.click());
  await page.getByText(PASSING).first().waitFor({ timeout: 20000 });
  await page.waitForTimeout(2500);
}

/** Phase 1: texts of D, the method of D-213, the search requests (abort, edits kept) and R-06. */
async function fixes(browser) {
  // ---------- Desktop ----------
  const { ctx, page, errors, aborted } = await open(browser, DESKTOP);
  const d = (report.escritorio = {});
  await loadExample(page);
  d.cerca_item = flat(await page.locator("li").filter({ has: page.getByLabel("Minutos andando hasta colegio") }).first().innerText());
  d.servicios_a_un_paseo = (await page.getByLabel("Añadir un servicio a un paseo").locator("option").allInnerTexts()).map(flat);
  d.casi_encajan = flat(await page.getByText("Cumplen todo menos una cosa.").first().innerText());
  const legend = page.locator("section[aria-label='Leyenda del mapa']");
  d.leyenda = flat(await legend.innerText());
  d.leyenda_parches = await legend.locator("li span[aria-hidden='true']").evaluateAll((spans) =>
    spans.map((s) => getComputedStyle(s).backgroundImage.split("gradient(").length - 1),
  );
  await legend.screenshot({ path: `${out}/qa1_leyenda_cumple_no_cumple_desktop.png` });
  await page.screenshot({ path: `${out}/qa1_mapa_encaje_desktop.png` });
  const rc = page.getByRole("region", { name: "¿Y si cambias algo?", exact: true });
  await rc.getByRole("button", { name: /Ver todas las opciones/ }).click();
  d.y_si_cambias = flat(await rc.innerText());
  d.axe_resultados = await axe(page);

  // A search that fails while the person edits: the edit is kept
  const search = page.getByRole("button", { name: "Ver zonas que encajan" });
  await page.route("**/api/v1/search", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    await route.abort("failed");
  });
  const before = errors.length;
  await search.click();
  await page.getByRole("radio", { name: "Comprar" }).check();
  await page.getByRole("alert").filter({ hasText: /No hemos podido conectar/ }).first().waitFor({ timeout: 10000 });
  d.fallo_simulado = {
    aviso: flat(await page.getByRole("alert").filter({ hasText: /No hemos podido conectar/ }).first().innerText()),
    comprar_sigue_marcado: await page.getByRole("radio", { name: "Comprar" }).isChecked(),
    consola_esperada: errors.splice(before),
  };
  await page.unroute("**/api/v1/search");

  // A row of «Qué falta» on the map: the label of the map (D-213)
  await page.getByLabel("¿Qué quieres ver?").selectOption("centro_salud");
  await page.getByText(/frente a los municipios de su tipo/).first().waitFor({ timeout: 20000 });
  d.mapa_aria_fila = await page.locator("[role='region'][aria-label^='Mapa']").first().getAttribute("aria-label");
  d.overflow_px = await overflow(page);

  // Leaving the map while a search is in flight cancels it (the answer would go nowhere)
  await page.getByLabel("¿Qué quieres ver?").selectOption("");
  await page.route("**/api/v1/search", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1500));
    await route.continue().catch(() => undefined);
  });
  await page.getByRole("radio", { name: "Alquilar" }).check();
  const abortedBefore = aborted.length;
  await search.click();
  await page.getByRole("link", { name: "Cómo lo calculamos" }).first().click();
  await page.getByRole("heading", { level: 1, name: "Cómo lo calculamos" }).waitFor({ timeout: 10000 });
  await page.waitForTimeout(2500);
  d.busqueda_cancelada_al_salir = aborted.slice(abortedBefore);
  d.consola = errors;
  await ctx.close();

  // ---------- Other pages ----------
  const pages = (report.paginas = {});
  for (const [name, path] of [["como_lo_calculamos", "/como-lo-calculamos"], ["zonas_fila", "/zonas?fila=centro_salud"]]) {
    for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
      const p = await open(browser, profile, path);
      const entry = (pages[`${name}_${id}`] = {});
      if (name === "como_lo_calculamos") {
        entry.primera_regla = flat(await p.page.locator("#principios").locator("..").locator("li").first().innerText());
        entry.ejemplo_hecho = flat(await p.page.getByText(/van entre 3 y 5 hechos/).innerText());
        await p.page.locator("#principios").locator("..").screenshot({ path: `${out}/qa1_${name}_${id}.png` });
      } else {
        entry.intro = flat(await p.page.getByText(/^Con su estado en/).innerText());
        await p.page.getByText(/Cargando el estado de cada zona/).waitFor({ state: "detached", timeout: 20000 }).catch(() => undefined);
        await p.page.screenshot({ path: `${out}/qa1_${name}_${id}.png` });
      }
      entry.axe = await axe(p.page);
      entry.overflow_px = await overflow(p.page);
      entry.consola = p.errors;
      await p.ctx.close();
    }
  }

  // ---------- Mobile ----------
  const m = (report.movil = {});
  const mob = await open(browser, MOBILE);
  await loadExample(mob.page, true);
  m.axe_resultados = await axe(mob.page);
  // The folded sheet leaves the map in view, crossed-out zones included, above the results
  await mob.page.screenshot({ path: `${out}/qa1_mapa_encaje_mobile.png` });
  m.overflow_px = await overflow(mob.page);
  m.consola = mob.errors;
  await mob.ctx.close();
}

const browser = await chromium.launch();
if (mode === "fixes") await fixes(browser);
else throw new Error(`Unknown mode ${mode}`);
await browser.close();

writeFileSync(`${out}/qa_${mode}.json`, `${JSON.stringify(report, null, 1)}\n`);
console.log(JSON.stringify(report, null, 1));
