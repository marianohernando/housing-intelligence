// Search check for the web (PUB-001 F4, F9): the demo case, «¿Y si cambias algo?», «Trabajo en»,
// buying and the flag, against the real API, with axe WCAG 2.2 AA and the browser console.
//
//   node scripts/check-search.mjs on  [outDir]   # web built with NEXT_PUBLIC_FEATURE_SEARCH=true
//   node scripts/check-search.mjs off [outDir]   # web built without the flag
//
// Web on 3011 (next build + start) and API on 8011, as in LINEAS.md. Writes f9_*.json and the
// C1–C3 captures of pitch/slides.md to outDir (default evidence/map-004/<today>). MOCKUP_DIR
// points to the folder with the mockups, for the side-by-side of C1; they are never copied.
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";

import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const AXE = require.resolve("axe-core/axe.min.js");
const MOCKUP = process.env.MOCKUP_DIR ? join(process.env.MOCKUP_DIR, "mockup_1_mapa.png") : null;
const today = new Date().toLocaleDateString("sv-SE");
const [mode = "on", out = join("..", "..", "evidence", "map-004", today)] = process.argv.slice(2);
const BASE = "http://localhost:3011";
const report = { fase: "PUB-001 F4 (F9): buscador y «¿Y si cambias algo?» contra POST /api/v1/search", bandera: mode, como: "Playwright contra web 3011 (next build + start) y API 8011 (rama claude/sprint-1-public, datos reales)" };

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    const r = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } });
    return r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, ejemplo: v.nodes[0]?.target }));
  });
}

async function open(browser, profile) {
  const ctx = await browser.newContext({ ...profile, locale: "es-ES" });
  const page = await ctx.newPage();
  const errors = [];
  const searches = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("request", (r) => { if (r.url().includes("/api/v1/search")) searches.push(JSON.parse(r.postData() ?? "null")); });
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1500);
  return { ctx, page, errors, searches };
}

const DESKTOP = { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 };
const MOBILE = { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true };
const overflow = (page) => page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
const focused = (page) => page.evaluate(() => { const el = document.activeElement; return el ? `${el.tagName.toLowerCase()}: ${(el.getAttribute("aria-label") ?? el.textContent ?? "").trim().slice(0, 80)}` : null; });

const browser = await chromium.launch();

if (mode === "off") {
  const { ctx, page, errors, searches } = await open(browser, DESKTOP);
  report.escritorio = {
    boton_ejemplo: await page.getByRole("button", { name: /Ver un ejemplo/ }).count(),
    muy_pronto: await page.getByText(/Muy pronto podrás ver qué zonas encajan contigo/).count(),
    trabajo_muy_pronto: await page.getByText("Trabajo en").count(),
    lo_quiero_a_un_paseo: await page.getByText("Lo quiero a un paseo").count(),
    peticiones_search: searches.length,
    axe: await axe(page),
    consola: errors,
  };
  await page.screenshot({ path: `${out}/f9_bandera_off_inicio_desktop.png` });
  await ctx.close();
} else {
  // ---------- Desktop ----------
  const { ctx, page, errors, searches } = await open(browser, DESKTOP);
  const d = (report.escritorio = {});
  d.axe_antes = await axe(page);
  // The demo case from the portada, with the keyboard
  await page.getByRole("button", { name: /Ver un ejemplo/ }).focus();
  await page.keyboard.press("Enter");
  await page.getByText("Con tu búsqueda tal cual salen 32 zonas.").first().waitFor({ timeout: 20000 });
  await page.waitForTimeout(2500);
  d.peticion = searches[0];
  d.max_minutes_enviados = searches.flatMap((s) => (s?.anchors ?? []).map((a) => a.max_minutes));
  const api = await page.evaluate(async (body) => (await (await fetch("http://localhost:8011/api/v1/search", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })).json()).data, searches[0]);
  d.api = {
    zones_evaluated: api.reality_check.zones_evaluated,
    zones_passing: api.reality_check.zones_passing,
    zones_unknown: api.reality_check.zones_unknown,
    primera: [api.results[0].zone.name, api.results[0].match_pct],
    chamartin: api.results.filter((z) => z.zone.name === "Chamartín").map((z) => [z.rank, z.match_pct])[0],
    primera_relajacion: api.reality_check.relaxations.map((r) => [r.label, r.added_zones, r.zones_if_relaxed])[0],
  };
  d.resumen = await page.getByRole("region", { name: "Zonas que encajan", exact: true }).locator("p strong").first().innerText();
  await page.getByRole("button", { name: /Ver las 10 primeras/ }).click();
  d.ranking = (await page.locator("ol li button").allInnerTexts()).map((t) => t.replace(/\s+/g, " ").trim());
  d.y_si_cambias_plegado = (await page.getByRole("region", { name: "¿Y si cambias algo?", exact: true }).innerText()).replace(/\s+/g, " ");
  const legend = page.locator("section[aria-label='Leyenda del mapa']");
  d.leyenda = (await legend.innerText()).replace(/\s+/g, " ");
  const legendCount = Number((await legend.locator("li").first().innerText()).match(/(\d+) zonas?/)?.[1]);
  d.leyenda_coincide_con_api = legendCount === api.reality_check.zones_passing;
  d.axe_resultados = await axe(page);
  await page.getByRole("button", { name: /Ver menos/ }).first().click();

  // C1: the search filled with the demo case, the fit choropleth and the zone card open
  await page.getByRole("button", { name: /^1 Ciudad Lineal/ }).click();
  await page.waitForTimeout(2000);
  const card = page.locator("aside").filter({ hasText: "Lo que tienes aquí" });
  d.tarjeta = (await card.innerText()).replace(/\s+/g, " ");
  await page.screenshot({ path: `${out}/c1_busqueda_desktop.png` });
  await card.screenshot({ path: `${out}/c2_tarjeta_zona_desktop.png` });
  d.axe_tarjeta = await axe(page);
  await page.getByRole("button", { name: "Cerrar" }).click();

  // C3: «¿Y si cambias algo?» unfolded
  const rc = page.getByRole("region", { name: "¿Y si cambias algo?", exact: true });
  await rc.getByRole("button", { name: /Ver todas las opciones/ }).click();
  await page.waitForTimeout(300);
  await rc.screenshot({ path: `${out}/c3_y_si_cambias_desktop.png` });
  d.y_si_cambias_desplegado = (await rc.innerText()).replace(/\s+/g, " ");

  // Apply the first option with the keyboard, then undo
  await rc.getByRole("button", { name: /^\+5 min a pie/ }).focus();
  await page.keyboard.press("Enter");
  await page.getByText(/Con este cambio salen 49 zonas/).first().waitFor({ timeout: 20000 });
  await page.waitForTimeout(800);
  d.aplicada = {
    aviso: (await page.getByText(/Ahora ves las zonas con/).innerText()).replace(/\s+/g, " "),
    minutos_en_tu_busqueda: await page.getByLabel("Minutos andando hasta colegio").inputValue(),
    foco: await focused(page),
    relaxed_enviado: searches.at(-1)?.nearby,
  };
  await page.screenshot({ path: `${out}/f9_aplicada_desktop.png` });
  await page.getByRole("button", { name: "Volver a mi búsqueda" }).focus();
  await page.keyboard.press("Enter");
  await page.getByText("Con tu búsqueda tal cual salen 32 zonas.").first().waitFor({ timeout: 20000 });
  await page.waitForTimeout(500);
  d.deshecha = { minutos: await page.getByLabel("Minutos andando hasta colegio").inputValue(), foco: await focused(page) };

  // «Trabajo en» with the keyboard: remove, type, arrows, Enter
  await page.getByRole("button", { name: /Quitar este lugar/ }).focus();
  await page.keyboard.press("Enter");
  const combo = page.getByRole("combobox", { name: /Trabajo en/ });
  d.trabajo = { foco_tras_quitar: await focused(page) };
  await combo.pressSequentially("nuevos min", { delay: 30 });
  await page.getByRole("listbox", { name: "Trabajo en" }).getByRole("option").first().waitFor({ timeout: 10000 });
  d.trabajo.opciones = (await page.getByRole("listbox", { name: "Trabajo en" }).getByRole("option").allInnerTexts()).map((t) => t.replace(/\s+/g, " "));
  await page.keyboard.press("ArrowDown");
  d.trabajo.activa = await combo.getAttribute("aria-activedescendant");
  await page.screenshot({ path: `${out}/f9_trabajo_desktop.png` });
  await page.keyboard.press("Enter");
  d.trabajo.elegido = (await page.getByRole("button", { name: /Quitar este lugar/ }).getAttribute("aria-label"));
  d.trabajo.foco_tras_elegir = await focused(page);
  await page.getByRole("button", { name: "Ver zonas que encajan" }).click();
  await page.getByText("Con tu búsqueda tal cual salen 32 zonas.").first().waitFor({ timeout: 20000 });
  d.trabajo.ancla_enviada = searches.at(-1)?.anchors;
  await page.getByRole("button", { name: /^1 Ciudad Lineal/ }).click();
  await page.waitForTimeout(800);
  d.trabajo.hecho_trayecto = (await page.locator("aside li").filter({ hasText: "línea recta" }).innerText()).replace(/\s+/g, " ");
  await page.getByRole("button", { name: "Cerrar" }).click();

  // Buying: «Sin datos» with its explanation; the API answers UNKNOWN everywhere
  await page.getByRole("radio", { name: "Comprar" }).check();
  d.compra = { nota: (await page.getByText(/Aún no tenemos precios oficiales de compra/).first().innerText()).replace(/\s+/g, " ") };
  await page.getByRole("button", { name: "Ver zonas que encajan" }).click();
  await page.getByText("Con tu búsqueda tal cual no sale ninguna zona.").first().waitFor({ timeout: 20000 });
  await page.waitForTimeout(1500);
  d.compra.resultados = (await page.getByRole("region", { name: "Zonas que encajan", exact: true }).innerText()).replace(/\s+/g, " ");
  d.compra.y_si_cambias = (await page.getByRole("region", { name: "¿Y si cambias algo?", exact: true }).innerText()).replace(/\s+/g, " ");
  d.compra.axe = await axe(page);
  await page.screenshot({ path: `${out}/f9_compra_desktop.png` });
  d.peticiones_search = searches.length;
  d.todas_sin_max_minutes = searches.every((s) => (s?.anchors ?? []).every((a) => a.max_minutes === null));
  d.overflow_px = await overflow(page);
  d.consola = errors;
  await ctx.close();

  // C1 next to mockup 1
  try {
    if (!MOCKUP) throw new Error("MOCKUP_DIR not set");
    const shot = readFileSync(`${out}/c1_busqueda_desktop.png`).toString("base64");
    const mock = readFileSync(MOCKUP).toString("base64");
    const p = await browser.newPage({ viewport: { width: 2960, height: 1000 } });
    await p.setContent(`<!doctype html><html><body style="margin:0;padding:24px;background:#e9e8f2;font:600 22px system-ui;color:#141b3d"><div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start"><figure style="margin:0"><figcaption style="margin-bottom:10px">Vida Fácil (captura, 1440 px)</figcaption><img src="data:image/png;base64,${shot}" style="width:100%;display:block"></figure><figure style="margin:0"><figcaption style="margin-bottom:10px">Mockup de referencia</figcaption><img src="data:image/png;base64,${mock}" style="width:100%;display:block"></figure></div></body></html>`);
    await p.screenshot({ path: `${out}/c1_busqueda_desktop_vs_mockup.jpg`, fullPage: true, type: "jpeg", quality: 82 });
    await p.close();
  } catch (e) { report.mockup = `sin comparación: ${e.message}`; }

  // ---------- Mobile ----------
  const m = (report.movil = {});
  const mob = await open(browser, MOBILE);
  await mob.page.getByRole("button", { name: /Ver un ejemplo/ }).tap();
  await mob.page.getByText("Con tu búsqueda tal cual salen 32 zonas.").first().waitFor({ timeout: 20000 });
  await mob.page.waitForTimeout(2500);
  m.resultados_a_la_vista = await mob.page.getByRole("heading", { name: "Zonas que encajan" }).isVisible();
  await mob.page.screenshot({ path: `${out}/c1_busqueda_mobile.png` });
  m.axe_resultados = await axe(mob.page);
  const mrc = mob.page.getByRole("region", { name: "¿Y si cambias algo?", exact: true });
  await mrc.getByRole("button", { name: /Ver todas las opciones/ }).tap();
  await mob.page.waitForTimeout(400);
  await mrc.screenshot({ path: `${out}/c3_y_si_cambias_mobile.png` });
  await mob.page.getByRole("button", { name: /^1 Ciudad Lineal/ }).tap();
  await mob.page.waitForTimeout(2000);
  await mob.page.locator("aside").filter({ hasText: "Lo que tienes aquí" }).screenshot({ path: `${out}/c2_tarjeta_zona_mobile.png` });
  m.axe_tarjeta = await axe(mob.page);
  m.overflow_px = await overflow(mob.page);
  m.consola = mob.errors;
  await mob.ctx.close();
}

writeFileSync(`${out}/f9_${mode === "off" ? "bandera_off" : "buscador"}.json`, JSON.stringify(report, null, 1));
console.log(JSON.stringify(report, null, 1).slice(0, 6000));
await browser.close();
