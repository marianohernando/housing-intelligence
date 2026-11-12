// Search check for the web (PUB-001 F4, F9): the demo case, «¿Y si cambias algo?», «Trabajo en»,
// buying and the flag, against the real API, with axe WCAG 2.2 AA and the browser console. Every
// figure is compared with the POST /search answer the page received (summary, first zone and its
// card, the first option of «¿Y si cambias algo?»): it fails if the screen and the API disagree.
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

const WAIT = 30_000;
const squash = (text) => text.replace(/\s+/g, " ").trim();
const escapeRe = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
const zonesText = (n) => (n === 1 ? "1 zona" : `${n} zonas`);
/** resultados.resumen and rc.cambio, as the web writes them (lib/fit.ts). */
const passingText = (n, changed = false) => {
  const start = changed ? "Con este cambio" : "Con tu búsqueda tal cual";
  return n === 0 ? `${start} no sale ninguna zona.` : n === 1 ? `${start} sale 1 zona.` : `${start} salen ${n} zonas.`;
};
const isSearch = (r) => r.url().endsWith("/api/v1/search") && r.request().method() === "POST";

/** The `data` of the POST /search the page sends when `act` runs: what the screen must show. */
async function searchAnswer(page, act) {
  const [response] = await Promise.all([page.waitForResponse(isSearch, { timeout: WAIT }), act()]);
  if (response.status() !== 200) throw new Error(`POST /search ${response.status()}`);
  return (await response.json()).data;
}

/** Opens the card of the API's first zone from the ranking; its name and % must be the API's. */
async function firstZone(page, zone, where, tap = false) {
  const button = page.getByRole("button", { name: new RegExp(`^1 ${escapeRe(zone.zone.name)}\\b`) }).first();
  await (tap ? button.tap() : button.click());
  const card = page.locator("aside").filter({ hasText: "Lo que tienes aquí" }).first();
  await card.waitFor({ timeout: WAIT });
  await page.waitForTimeout(1500);
  const text = squash(await card.innerText());
  const missing = zone.facts.filter((f) => !text.includes(squash(f.text)));
  if (!text.includes(zone.zone.name) || !new RegExp(`(?<!\\d)${zone.match_pct}\\s*%`).test(text) || missing.length) {
    report.fallos.push(`${where}: tarjeta de ${zone.zone.name} distinta de la API${missing.length ? ` (falta «${missing[0].text}»)` : ""}`);
  }
}

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
  // Every figure on screen is checked against the /search answer the page itself received
  // (fit-0.2 and later), as infra/deploy/e2e/e2e_prod.mjs does: nothing fixed here, nothing relaxed.
  const failures = (report.fallos = []);
  const check = (name, ok, detail = "") => {
    if (!ok) failures.push(`${name}${detail ? `: ${detail}` : ""}`);
  };

  // ---------- Desktop ----------
  const { ctx, page, errors, searches } = await open(browser, DESKTOP);
  const d = (report.escritorio = {});
  d.axe_antes = await axe(page);
  // The demo case from the portada, with the keyboard
  await page.getByRole("button", { name: /Ver un ejemplo/ }).focus();
  const api = await searchAnswer(page, () => page.keyboard.press("Enter"));
  const rc = api.reality_check;
  const top = api.results[0];
  const option = rc.relaxations.find((r) => r.added_zones > 0);
  d.api = {
    methodology_version: api.methodology_version,
    zones_evaluated: rc.zones_evaluated,
    zones_passing: rc.zones_passing,
    zones_unknown: rc.zones_unknown,
    primera: [top.zone.name, top.match_pct],
    primera_relajacion: option ? [option.label, option.added_zones, option.zones_if_relaxed] : null,
  };
  await page.getByText(passingText(rc.zones_passing)).first().waitFor({ timeout: WAIT });
  await page.waitForTimeout(2500);
  d.peticion = searches[0];
  d.max_minutes_enviados = searches.flatMap((s) => (s?.anchors ?? []).map((a) => a.max_minutes));
  d.resumen = squash(await page.getByRole("region", { name: "Zonas que encajan", exact: true }).locator("p strong").first().innerText());
  check("resumen = zones_passing de la API", d.resumen === passingText(rc.zones_passing), `${d.resumen} / ${rc.zones_passing}`);
  await page.getByRole("button", { name: /Ver las 10 primeras/ }).click();
  d.ranking = (await page.locator("ol li button").allInnerTexts()).map(squash);
  check("1.ª del ranking = 1.ª de la API", d.ranking[0]?.startsWith(`1 ${top.zone.name}`) && d.ranking[0].includes(`${top.match_pct} %`), d.ranking[0]);
  d.y_si_cambias_plegado = squash(await page.getByRole("region", { name: "¿Y si cambias algo?", exact: true }).innerText());
  const legend = page.locator("section[aria-label='Leyenda del mapa']");
  d.leyenda = squash(await legend.innerText());
  const legendCount = Number((await legend.locator("li").first().innerText()).match(/(\d+) zonas?/)?.[1]);
  check("leyenda «Cumple todo» = zones_passing", legendCount === rc.zones_passing, `${legendCount} / ${rc.zones_passing}`);
  d.axe_resultados = await axe(page);
  await page.getByRole("button", { name: /Ver menos/ }).first().click();

  // C1: the search filled with the demo case, the fit choropleth and the first zone's card open
  await firstZone(page, top, "escritorio");
  const card = page.locator("aside").filter({ hasText: "Lo que tienes aquí" });
  d.tarjeta = squash(await card.innerText());
  await page.screenshot({ path: `${out}/c1_busqueda_desktop.png` });
  await card.screenshot({ path: `${out}/c2_tarjeta_zona_desktop.png` });
  d.axe_tarjeta = await axe(page);
  await page.getByRole("button", { name: "Cerrar" }).click();

  // C3: «¿Y si cambias algo?» unfolded, with the API's first option that adds zones
  const rcRegion = page.getByRole("region", { name: "¿Y si cambias algo?", exact: true });
  await rcRegion.getByRole("button", { name: /Ver todas las opciones/ }).click();
  await page.waitForTimeout(300);
  await rcRegion.screenshot({ path: `${out}/c3_y_si_cambias_desktop.png` });
  d.y_si_cambias_desplegado = squash(await rcRegion.innerText());
  check("«¿Y si cambias algo?» tiene una opción que suma zonas", Boolean(option), "ninguna en la API");
  if (option) {
    const would = `${option.zones_if_relaxed === 1 ? "saldría" : "saldrían"} ${zonesText(option.zones_if_relaxed)}, ${option.added_zones} más`;
    check("1.ª opción = 1.ª relajación de la API", d.y_si_cambias_desplegado.includes(`${option.label} ${would}`), `${option.label} ${would}`);

    // Apply it with the keyboard, then undo
    await rcRegion.getByRole("button", { name: new RegExp(`^${escapeRe(option.label)}`) }).focus();
    const applied = await searchAnswer(page, () => page.keyboard.press("Enter"));
    check("aplicada: la API da las zonas de la opción", applied.reality_check.zones_passing === option.zones_if_relaxed, applied.reality_check.zones_passing);
    await page.getByText(passingText(applied.reality_check.zones_passing, true)).first().waitFor({ timeout: WAIT });
    await page.waitForTimeout(800);
    d.aplicada = {
      zonas_api: applied.reality_check.zones_passing,
      aviso: squash(await page.getByText(/Ahora ves las zonas con/).innerText()),
      minutos_en_tu_busqueda: await page.getByLabel("Minutos andando hasta colegio").inputValue(),
      foco: await focused(page),
      relaxed_enviado: searches.at(-1)?.nearby,
    };
    await page.screenshot({ path: `${out}/f9_aplicada_desktop.png` });
    await page.getByRole("button", { name: "Volver a mi búsqueda" }).focus();
    const undone = await searchAnswer(page, () => page.keyboard.press("Enter"));
    check("deshecha: la API vuelve a las zonas de la búsqueda", undone.reality_check.zones_passing === rc.zones_passing, undone.reality_check.zones_passing);
    await page.getByText(passingText(undone.reality_check.zones_passing)).first().waitFor({ timeout: WAIT });
    await page.waitForTimeout(500);
    d.deshecha = { minutos: await page.getByLabel("Minutos andando hasta colegio").inputValue(), foco: await focused(page) };
  }

  // «Trabajo en» with the keyboard: remove, type, arrows, Enter
  await page.getByRole("button", { name: /Quitar este lugar/ }).focus();
  await page.keyboard.press("Enter");
  const combo = page.getByRole("combobox", { name: /Trabajo en/ });
  d.trabajo = { foco_tras_quitar: await focused(page) };
  await combo.pressSequentially("nuevos min", { delay: 30 });
  await page.getByRole("listbox", { name: "Trabajo en" }).getByRole("option").first().waitFor({ timeout: 10000 });
  d.trabajo.opciones = (await page.getByRole("listbox", { name: "Trabajo en" }).getByRole("option").allInnerTexts()).map(squash);
  await page.keyboard.press("ArrowDown");
  d.trabajo.activa = await combo.getAttribute("aria-activedescendant");
  await page.screenshot({ path: `${out}/f9_trabajo_desktop.png` });
  await page.keyboard.press("Enter");
  d.trabajo.elegido = await page.getByRole("button", { name: /Quitar este lugar/ }).getAttribute("aria-label");
  d.trabajo.foco_tras_elegir = await focused(page);
  const work = await searchAnswer(page, () => page.getByRole("button", { name: "Ver zonas que encajan" }).click());
  await page.getByText(passingText(work.reality_check.zones_passing)).first().waitFor({ timeout: WAIT });
  d.trabajo.ancla_enviada = searches.at(-1)?.anchors;
  d.trabajo.api = { zones_passing: work.reality_check.zones_passing, primera: [work.results[0]?.zone.name, work.results[0]?.match_pct] };
  if (work.results[0]) {
    await firstZone(page, work.results[0], "trabajo");
    d.trabajo.tarjeta = squash(await page.locator("aside").filter({ hasText: "Lo que tienes aquí" }).innerText());
    await page.getByRole("button", { name: "Cerrar" }).click();
  }

  // Buying: «Sin datos» with its explanation; what the API answers is what shows
  await page.getByRole("radio", { name: "Comprar" }).check();
  d.compra = { nota: squash(await page.getByText(/Aún no tenemos precios oficiales de compra/).first().innerText()) };
  const buy = await searchAnswer(page, () => page.getByRole("button", { name: "Ver zonas que encajan" }).click());
  await page.getByText(passingText(buy.reality_check.zones_passing)).first().waitFor({ timeout: WAIT });
  await page.waitForTimeout(1500);
  d.compra.api = { zones_passing: buy.reality_check.zones_passing, zones_unknown: buy.reality_check.zones_unknown };
  d.compra.resultados = squash(await page.getByRole("region", { name: "Zonas que encajan", exact: true }).innerText());
  d.compra.y_si_cambias = squash(await page.getByRole("region", { name: "¿Y si cambias algo?", exact: true }).innerText());
  d.compra.axe = await axe(page);
  await page.screenshot({ path: `${out}/f9_compra_desktop.png` });
  d.peticiones_search = searches.length;
  d.todas_sin_max_minutes = searches.every((s) => (s?.anchors ?? []).every((a) => a.max_minutes === null));
  check("todas las búsquedas sin max_minutes", d.todas_sin_max_minutes);
  d.overflow_px = await overflow(page);
  d.consola = errors;
  for (const key of ["axe_antes", "axe_resultados", "axe_tarjeta"]) check(`escritorio ${key}`, d[key].length === 0, d[key].map((a) => a.id).join(", "));
  check("escritorio compra axe", d.compra.axe.length === 0, d.compra.axe.map((a) => a.id).join(", "));
  check("escritorio consola", errors.length === 0, errors[0]);
  check("escritorio desborde", d.overflow_px <= 0, d.overflow_px);
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
  const mApi = await searchAnswer(mob.page, () => mob.page.getByRole("button", { name: /Ver un ejemplo/ }).tap());
  await mob.page.getByText(passingText(mApi.reality_check.zones_passing)).first().waitFor({ timeout: WAIT });
  await mob.page.waitForTimeout(2500);
  m.api = { zones_passing: mApi.reality_check.zones_passing, primera: [mApi.results[0].zone.name, mApi.results[0].match_pct] };
  m.resultados_a_la_vista = await mob.page.getByRole("heading", { name: "Zonas que encajan" }).isVisible();
  await mob.page.screenshot({ path: `${out}/c1_busqueda_mobile.png` });
  m.axe_resultados = await axe(mob.page);
  const mrc = mob.page.getByRole("region", { name: "¿Y si cambias algo?", exact: true });
  await mrc.getByRole("button", { name: /Ver todas las opciones/ }).tap();
  await mob.page.waitForTimeout(400);
  await mrc.screenshot({ path: `${out}/c3_y_si_cambias_mobile.png` });
  await firstZone(mob.page, mApi.results[0], "móvil", true);
  await mob.page.locator("aside").filter({ hasText: "Lo que tienes aquí" }).screenshot({ path: `${out}/c2_tarjeta_zona_mobile.png` });
  m.axe_tarjeta = await axe(mob.page);
  m.overflow_px = await overflow(mob.page);
  m.consola = mob.errors;
  for (const key of ["axe_resultados", "axe_tarjeta"]) check(`móvil ${key}`, m[key].length === 0, m[key].map((a) => a.id).join(", "));
  check("móvil consola", mob.errors.length === 0, mob.errors[0]);
  check("móvil desborde", m.overflow_px <= 0, m.overflow_px);
  await mob.ctx.close();
  if (failures.length) process.exitCode = 1;
}

writeFileSync(`${out}/f9_${mode === "off" ? "bandera_off" : "buscador"}.json`, JSON.stringify(report, null, 1));
console.log(JSON.stringify(report, null, 1).slice(0, 6000));
await browser.close();
