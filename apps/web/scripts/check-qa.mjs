// Quality check of the web for the test phase (FASE_PRUEBAS, line B), against the real API, with
// axe WCAG 2.2 AA and the browser console, at 1440 and 390 px:
//
//   node scripts/check-qa.mjs fixes [outDir]    # phase 1: PENDIENTES fixes (texts, search, R-06)
//   node scripts/check-qa.mjs t3 [outDir]       # phase 2: every facility of a zone (T3)
//   node scripts/check-qa.mjs proyector [outDir] # phase 3: no overlaps from 1024×576 to 1440×900
//   node scripts/check-qa.mjs offline [outDir]   # phase 5: street tiles blocked (offline package)
//   node scripts/check-qa.mjs tiles-local [outDir] # phase 5: web built with NEXT_PUBLIC_MAP_TILES_URL=http://localhost:3999/madrid.json
//   node scripts/check-qa.mjs gap03 [outDir]     # phase 6: gap-0.3 (D-217): neighbours, 2SFCA copy and the hospital
//   node scripts/check-qa.mjs hosp [outDir]      # HOSP-001 (D-218): hospital names, beds, management and source
//   node scripts/check-qa.mjs gaps-colgado [outDir] # /gaps that hangs: the zone and its map still load
//   node scripts/check-qa.mjs licencias [outDir] # footer and map cite the Ministry of Health and CartoCiudad
//   node scripts/check-qa.mjs textos [outDir]    # line D's copy after gap-0.3 and D-218 (method page, «Qué falta», centres)
//   node scripts/check-qa.mjs capturas-deck [outDir] # captures C3 and C4 of line D's deck, after gap-0.3
//   node scripts/check-qa.mjs revision [outDir]  # review of PR #16: beds without /datasets and new-tab links
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
  await page.getByText(/^Con tu búsqueda tal cual (sale|salen|no sale)/).first().waitFor({ timeout: 20000 });
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

const API = "http://localhost:8011";
const ZONE = { path: "/zona/distrito/2807905", id: "ES.28.DIS.2807905", name: "Chamartín" };
const box = (locator) => locator.evaluate((el) => {
  const r = el.getBoundingClientRect();
  return { top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left), right: Math.round(r.right) };
});

/**
 * How many places the API has in the zone for a type (the panel must show the same): those of its
 * subcategories that its row of «Qué falta» counts (gap_rows, places-1). Asked from Node, not the page.
 */
async function apiCount(category, subcategories, row = null) {
  const q = new URLSearchParams({ category, admin_unit_id: ZONE.id });
  for (const s of subcategories) q.append("subcategory", s);
  const r = await fetch(`${API}/api/v1/places?${q}`);
  if (!r.ok) return `HTTP ${r.status}`;
  const { data } = await r.json();
  return data.features.filter((f) => !row || f.properties.gap_rows.includes(row)).length;
}

/** Phase 2 (T3): «Todos los centros» of a zone, its clustered layer, counts and accessible list. */
async function facilities(browser) {
  const d = (report.escritorio = {});
  const { ctx, page, errors } = await open(browser, DESKTOP, ZONE.path);
  const panel = page.getByRole("region", { name: "Todos los centros", exact: true });
  await panel.getByRole("button", { name: /^Colegios/ }).waitFor({ timeout: 20000 });
  await page.waitForTimeout(7000); // the camera lands and the layer shows
  d.botones = (await panel.getByRole("group", { name: "Ver en el mapa" }).getByRole("button").allInnerTexts()).map(flat);
  d.pulsado = flat(await panel.locator("button[aria-pressed='true']").innerText());
  d.frase = flat(await panel.locator("[aria-live='polite']").innerText());
  d.api_colegios = await apiCount("education", [
    "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA", "COLEGIO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA", "COLEGIO DE EDUCACIÓN PRIMARIA",
    "CENTRO PRIVADO DE EDUCACIÓN INFANTIL Y PRIMARIA", "CENTRO PRIVADO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA",
    "CENTRO PRIVADO DE EDUCACIÓN PRIMARIA", "CENTRO PRIVADO DE EDUCACIÓN PRIMARIA Y SECUNDARIA",
  ], "colegio");
  d.api_hospitales = await apiCount("health", ["Hospital general", "Hospital especializado", "Hospital de media y larga estancia", "Hospital de salud mental y tratamiento de toxicomanías"]);
  d.api_farmacias = await apiCount("pharmacy", ["Farmacia"], "farmacia");
  d.api_mayores = await apiCount("social", ["CENTROS DE DÍA: OTROS", "HOGARES Y CLUBES"], "mayores");
  d.mapa_aria = await page.locator("[role='region'][aria-label^='Mapa']").first().getAttribute("aria-label");
  await page.screenshot({ path: `${out}/t3_zona_colegios_desktop.png` });

  // The list, as the way without the map
  await panel.getByText(/^Ver la lista/).click();
  const list = panel.getByRole("list", { name: /colegios con primaria/ });
  d.lista = { elementos: await list.locator("li").count(), primeros: (await list.locator("li").allInnerTexts()).slice(0, 5).map(flat) };
  await panel.screenshot({ path: `${out}/t3_lista_colegios_desktop.png` });
  d.axe_lista = await axe(page);

  // Keyboard: another type with Tab and Enter, then none
  const hospitals = panel.getByRole("button", { name: /^Hospitales/ });
  await hospitals.focus();
  await page.keyboard.press("Enter");
  await page.waitForTimeout(1500);
  d.hospitales = {
    pulsado: await hospitals.getAttribute("aria-pressed"),
    frase: flat(await panel.locator("[aria-live='polite']").innerText()),
    mapa_aria: await page.locator("[role='region'][aria-label^='Mapa']").first().getAttribute("aria-label"),
  };
  await page.screenshot({ path: `${out}/t3_zona_hospitales_desktop.png` });
  await page.keyboard.press("Enter");
  d.ninguno = flat(await panel.locator("[aria-live='polite']").innerText());

  // Nothing hidden under the fixed barrios bar once scrolled to the end
  await panel.getByRole("button", { name: /^Colegios/ }).click();
  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  await page.waitForTimeout(400);
  const bar = await box(page.getByRole("region", { name: "Ir a un barrio" }));
  const search = await box(page.getByRole("heading", { name: "Tu búsqueda" }).locator("xpath=ancestor::*[contains(@class,'glass')][1]"));
  d.solape_busqueda_barra = { busqueda: search, barra: bar, libre: search.bottom <= bar.top };
  d.axe = await axe(page);
  d.overflow_px = await overflow(page);
  d.consola = errors;
  await ctx.close();

  // «Qué falta» of the zone: the source links name the dataset first (WCAG 2.5.3)
  const q = await open(browser, DESKTOP, "/que-falta?zona=distrito/2807905");
  await q.page.getByText(/De dónde sale/).first().waitFor({ timeout: 20000 });
  report.que_falta = { axe: await axe(q.page), consola: q.errors };
  await q.ctx.close();

  // ---------- Mobile ----------
  const m = (report.movil = {});
  const mob = await open(browser, MOBILE, ZONE.path);
  const mpanel = mob.page.getByRole("region", { name: "Todos los centros", exact: true });
  await mpanel.getByRole("button", { name: /^Colegios/ }).waitFor({ timeout: 20000 });
  await mob.page.waitForTimeout(7000);
  await mob.page.screenshot({ path: `${out}/t3_zona_colegios_mobile.png` });
  await mob.page.getByRole("button", { name: /Desliza hacia arriba/ }).tap();
  await mob.page.waitForTimeout(600);
  await mpanel.scrollIntoViewIfNeeded();
  await mpanel.getByRole("button", { name: /^Centros de salud/ }).tap();
  await mob.page.waitForTimeout(500);
  m.frase = flat(await mpanel.locator("[aria-live='polite']").innerText());
  await mpanel.screenshot({ path: `${out}/t3_panel_mobile.png` });
  m.axe = await axe(mob.page);
  m.overflow_px = await overflow(mob.page);
  m.consola = mob.errors;
  await mob.ctx.close();
}

const SIZES = [[1024, 768], [1024, 576], [1280, 720], [1366, 768], [1440, 900]];

/**
 * Overlaps of the fixed elements (map legend, barrios bar) with any card, link or button of the
 * page, by their bounding boxes in the viewport; and cards that cover each other.
 */
async function overlaps(page) {
  return page.evaluate(() => {
    // The part of an element on screen: clipped by the viewport and by its scrolling ancestors (the
    // mobile sheet) up to the first fixed one, since overflow does not clip what is fixed above it
    const clip = (el) => {
      let r = el.getBoundingClientRect();
      let box = { left: r.left, top: r.top, right: r.right, bottom: r.bottom };
      for (let a = el; a; a = a.parentElement) {
        const style = getComputedStyle(a);
        if (a !== el && (style.overflowX !== "visible" || style.overflowY !== "visible")) {
          r = a.getBoundingClientRect();
          box = { left: Math.max(box.left, r.left), top: Math.max(box.top, r.top), right: Math.min(box.right, r.right), bottom: Math.min(box.bottom, r.bottom) };
        }
        if (style.position === "fixed") break;
      }
      box = { left: Math.max(box.left, 0), top: Math.max(box.top, 0), right: Math.min(box.right, innerWidth), bottom: Math.min(box.bottom, innerHeight) };
      return { ...box, width: box.right - box.left, height: box.bottom - box.top };
    };
    const visible = (r) => r.width > 0 && r.height > 0;
    const name = (el) => (el.getAttribute("aria-label") ?? el.querySelector("h1, h2")?.textContent ?? el.textContent ?? "").trim().replace(/\s+/g, " ").slice(0, 40);
    const hit = (a, b) => a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1;
    const isFixed = (el) => getComputedStyle(el).position === "fixed";
    const skip = (el) => el.closest(".maplibregl-map, header");
    const fixed = [...document.querySelectorAll(".glass")].filter((el) => isFixed(el) && visible(clip(el)));
    const others = [...document.querySelectorAll(".glass, a, button, select, h1")].filter(
      (el) => !skip(el) && !fixed.some((f) => f.contains(el) || el.contains(f)) && visible(clip(el)),
    );
    const found = [];
    for (const f of fixed) {
      const fr = clip(f);
      for (const el of others) if (hit(fr, clip(el))) found.push(`${name(f)} ⟂ ${el.tagName.toLowerCase()} «${name(el)}»`);
    }
    return { fijos: fixed.map((f) => { const r = f.getBoundingClientRect(); return [name(f), Math.round(r.left), Math.round(r.top), Math.round(r.right), Math.round(r.bottom)]; }), solapes: found };
  });
}

/** Phase 3: the projector at 125 % (1024 px) and short screens, overview and zone. */
async function projector(browser) {
  const result = (report.tamanos = {});
  for (const [width, height] of SIZES) {
    const id = `${width}x${height}`;
    const entry = (result[id] = {});
    const profile = { viewport: { width, height }, deviceScaleFactor: 1 };
    const home = await open(browser, profile);
    await home.page.waitForTimeout(1500);
    entry.portada = await overlaps(home.page);
    await home.page.screenshot({ path: `${out}/p3_portada_${id}.png` });
    await loadExample(home.page);
    entry.resultados = await overlaps(home.page);
    await home.page.screenshot({ path: `${out}/p3_resultados_${id}.png` });
    await home.page.getByRole("button", { name: /^1 Ciudad Lineal/ }).click();
    await home.page.waitForTimeout(1500);
    entry.tarjeta = await overlaps(home.page);
    entry.axe = await axe(home.page);
    entry.overflow_px = await overflow(home.page);
    // The map by a row of «Qué falta»: the longest legend (2SFCA label and the neighbours, gap-0.3)
    await home.page.getByRole("button", { name: "Cerrar" }).first().click().catch(() => undefined);
    await home.page.getByLabel("¿Qué quieres ver?").selectOption("colegio");
    await home.page.getByText(/frente a los municipios de su tipo/).first().waitFor({ timeout: 20000 });
    await home.page.waitForTimeout(1500);
    entry.mapa_fila = await overlaps(home.page);
    entry.mapa_fila_axe = await axe(home.page);
    await home.page.screenshot({ path: `${out}/p3_mapa_fila_${id}.png` });
    entry.consola = home.errors;
    await home.ctx.close();

    // «Qué falta» of a small municipio compared with its neighbours (gap-0.3)
    const gaps = await open(browser, profile, "/que-falta?zona=municipio/28004");
    await gaps.page.getByText(/De dónde sale/).first().waitFor({ timeout: 20000 });
    entry.que_falta = await overlaps(gaps.page);
    entry.que_falta_axe = await axe(gaps.page);
    entry.que_falta_overflow_px = await overflow(gaps.page);
    entry.que_falta_consola = gaps.errors;
    await gaps.page.screenshot({ path: `${out}/p3_que_falta_${id}.png` });
    await gaps.ctx.close();

    const zone = await open(browser, profile, ZONE.path);
    await zone.page.getByRole("region", { name: "Todos los centros", exact: true }).waitFor({ timeout: 20000 });
    await zone.page.waitForTimeout(7000);
    entry.zona = await overlaps(zone.page);
    entry.zona_axe = await axe(zone.page);
    entry.zona_consola = zone.errors;
    await zone.page.screenshot({ path: `${out}/p3_zona_${id}.png` });
    await zone.ctx.close();
  }
  const mob = await open(browser, MOBILE);
  report.movil = { portada: await overlaps(mob.page), consola: mob.errors };
  await mob.page.screenshot({ path: `${out}/p3_portada_390x844.png` });
  await mob.ctx.close();
  report.sin_solapes = Object.values(result).every((e) => ["portada", "resultados", "tarjeta", "mapa_fila", "zona", "que_falta"].every((k) => e[k].solapes.length === 0));
}

const TILES = "https://tiles.openfreemap.org/**";
const isTileFailure = (text) => /ERR_FAILED|ERR_BLOCKED|openfreemap/.test(text);

/** Phase 5: without the street tiles the zones still work with a quiet note; without zones too, the alert. */
async function offline(browser) {
  for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
    const ctx = await browser.newContext({ ...profile, locale: "es-ES" });
    await ctx.route(TILES, (route) => route.abort("failed"));
    const page = await ctx.newPage();
    const errors = [];
    page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
    await page.getByText("Mapa sin fondo de calles.").waitFor({ timeout: 20000 });
    const entry = (report[`sin_calles_${id}`] = {});
    entry.nota = await page.getByRole("status").filter({ hasText: "Mapa sin fondo de calles." }).count();
    entry.aviso_fuerte = await page.getByRole("alert").filter({ hasText: /No se ha podido cargar el mapa/ }).count();
    await loadExample(page, id === "mobile");
    entry.resultados = flat(await page.getByText(/^Con tu búsqueda tal cual/).first().innerText());
    entry.solapes = (await overlaps(page)).solapes;
    entry.axe = await axe(page);
    entry.consola_esperada = errors.filter(isTileFailure).length;
    entry.consola_otros = errors.filter((e) => !isTileFailure(e));
    await page.screenshot({ path: `${out}/p5_sin_calles_${id}.png` });
    await ctx.close();
  }
  // Neither the street tiles nor the zones: the strong alert with the list of zones
  const ctx = await browser.newContext({ ...DESKTOP, locale: "es-ES" });
  await ctx.route(TILES, (route) => route.abort("failed"));
  await ctx.route("**/api/v1/geo/**", (route) => route.abort("failed"));
  const page = await ctx.newPage();
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  await page.getByRole("alert").filter({ hasText: /No se ha podido cargar el mapa/ }).waitFor({ timeout: 20000 });
  report.sin_calles_ni_zonas = {
    aviso_fuerte: flat(await page.getByRole("alert").filter({ hasText: /No se ha podido cargar el mapa/ }).innerText()),
    nota: await page.getByText("Mapa sin fondo de calles.").count(),
  };
  await page.screenshot({ path: `${out}/p5_sin_calles_ni_zonas_desktop.png` });
  await ctx.close();
}

/** Phase 5: the base map from a local TileJSON (NEXT_PUBLIC_MAP_TILES_URL), served here by Playwright. */
async function tilesLocal(browser) {
  const tilejson = await (await fetch("https://tiles.openfreemap.org/planet")).json();
  const ctx = await browser.newContext({ ...DESKTOP, locale: "es-ES" });
  const asked = [];
  await ctx.route("http://localhost:3999/madrid.json", (route) => {
    asked.push(route.request().url());
    return route.fulfill({ json: tilejson, headers: { "Access-Control-Allow-Origin": "*" } });
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  await page.goto(`${BASE}${ZONE.path}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(7000);
  report.tilejson_local = {
    pedido: asked.length > 0,
    nota: await page.getByText("Mapa sin fondo de calles.").count(),
    aviso_fuerte: await page.getByRole("alert").filter({ hasText: /No se ha podido cargar el mapa/ }).count(),
    consola: errors,
  };
  await page.screenshot({ path: `${out}/p5_tilejson_local_zona_desktop.png` });
  await ctx.close();
}

const SMALL = { level: "municipio", code: "28004", name: "El Álamo" };

/** Rows of «Qué falta» as the page shows them: label, badges, the group sentence and the walking minutes. */
async function gapRows(page) {
  return page.locator("main li.glass").evaluateAll((items) =>
    items.map((li) => ({
      fila: li.querySelector("h2")?.textContent?.trim(),
      etiquetas: [...(li.querySelector("h2")?.nextElementSibling?.children ?? [])].map((b) => {
        const visible = b.cloneNode(true);
        visible.querySelectorAll(".visually-hidden").forEach((h) => h.remove());
        return visible.textContent?.trim();
      }),
      mide: li.querySelector("h2")?.parentElement?.nextElementSibling?.textContent?.trim(),
      a_pie: [...li.querySelectorAll("dl > div")].filter((d) => d.querySelector("svg")).map((d) => d.textContent?.replace(/\s+/g, " ").trim()),
      grupo: [...li.querySelectorAll("p")].map((p) => p.textContent?.trim() ?? "").find((t) => t.startsWith("Comparado con")) ?? null,
      hospital: [...li.querySelectorAll("p")].map((p) => p.textContent?.trim() ?? "").find((t) => t.startsWith("El hospital:")) ?? null,
    })),
  );
}

/** Phase 6: gap-0.3 (D-217) in the web, against the real API. */
async function gap03(browser) {
  const api = async (path) => {
    const r = await fetch(`${API}${path}`);
    if (!r.ok) throw new Error(`API ${path}: HTTP ${r.status}`);
    return (await r.json()).data;
  };
  for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
    // A small municipio compared with its neighbours, and a district with the hospital minutes
    for (const [name, zone] of [["el_alamo", SMALL], ["chamartin", { level: "distrito", code: "2807905" }]]) {
      const p = await open(browser, profile, `/que-falta?zona=${zone.level}/${zone.code}`);
      await p.page.getByText(/De dónde sale/).first().waitFor({ timeout: 20000 });
      const fromApi = await api(`/api/v1/gaps/${zone.level}/${zone.code}`);
      const entry = (report[`que_falta_${name}_${id}`] = {});
      entry.metodo_api = fromApi.method.version;
      entry.grupos_api = fromApi.rows.filter((r) => r.comparison_group).map((r) => [r.row, r.comparison_group.names.length - 1]);
      entry.filas = await gapRows(p.page);
      entry.axe = await axe(p.page);
      entry.overflow_px = await overflow(p.page);
      entry.consola = p.errors;
      const health = p.page.locator("main li.glass").filter({ has: p.page.getByRole("heading", { name: "Centros de salud" }) });
      await health.scrollIntoViewIfNeeded();
      await health.screenshot({ path: `${out}/g3_fila_salud_${name}_${id}.png` });
      await p.ctx.close();
    }
    // The zone card on the zone screen: the group under the row name
    const z = await open(browser, profile, `/zona/${SMALL.level}/${SMALL.code}`);
    await z.page.getByRole("heading", { name: "Qué falta aquí" }).first().waitFor({ timeout: 20000 });
    const card = z.page.locator("aside").filter({ has: z.page.getByRole("heading", { name: "Qué falta aquí" }) }).first();
    await card.locator("ul li").first().waitFor({ timeout: 20000 });
    await z.page.waitForTimeout(6000); // the camera lands, for the capture
    report[`zona_el_alamo_${id}`] = {
      filas: (await card.locator("ul li").allInnerTexts()).map(flat),
      axe: await axe(z.page),
      overflow_px: await overflow(z.page),
      consola: z.errors,
    };
    await z.page.screenshot({ path: `${out}/g3_zona_el_alamo_${id}.png` });
    await z.ctx.close();

    // «Cómo lo calculamos»: 2SFCA in plain words, the old «Contamos centros» gone
    const m = await open(browser, profile, "/como-lo-calculamos");
    const method = m.page.locator("#que-falta").locator("..");
    report[`como_lo_calculamos_${id}`] = {
      a_pie: flat(await method.locator("p").first().innerText()),
      vecinos: flat(await method.getByText(/^Los pueblos pequeños, junto con sus vecinos/).locator("..").innerText()),
      hospital: flat(await method.getByText(/^El hospital\./).locator("..").innerText()),
      contamos_centros: await m.page.getByText("Contamos centros, no plazas").count(),
      limites: (await m.page.locator("#limites").locator("..").locator("li strong").allInnerTexts()).map(flat),
      axe: await axe(m.page),
      overflow_px: await overflow(m.page),
      consola: m.errors,
    };
    await method.screenshot({ path: `${out}/g3_como_lo_calculamos_${id}.png` });
    await m.ctx.close();

    // The list of zones for one row: one «Junto con sus vecinos» per zone the API compares with its group
    const l = await open(browser, profile, "/zonas?fila=colegio");
    await l.page.getByText(/Cargando el estado de cada zona/).waitFor({ state: "detached", timeout: 20000 }).catch(() => undefined);
    const grouped = l.page.locator("li:has(> a)").filter({ hasText: "Junto con sus vecinos" });
    await grouped.first().waitFor({ timeout: 20000 });
    const rowMap = await api("/api/v1/gaps?level=municipio&row=colegio");
    report[`zonas_colegio_${id}`] = {
      intro: flat(await l.page.getByText(/^Con su estado en/).innerText()),
      con_vecinos_web: await grouped.count(),
      con_vecinos_api: rowMap.zones.filter((zone) => zone.comparison_group).length,
      axe: await axe(l.page),
      overflow_px: await overflow(l.page),
      consola: l.errors,
    };
    await l.page.screenshot({ path: `${out}/g3_zonas_colegio_${id}.png` });
    await l.ctx.close();
  }

  // The map coloured by a row: the legend says the small towns go with their neighbours
  const h = await open(browser, DESKTOP);
  await h.page.getByLabel("¿Qué quieres ver?").selectOption("colegio");
  await h.page.getByText(/frente a los municipios de su tipo/).first().waitFor({ timeout: 20000 });
  await h.page.waitForTimeout(2500);
  const legend = h.page.locator("section[aria-label='Leyenda del mapa']");
  report.mapa_colegio = {
    leyenda: flat(await legend.innerText()),
    aria: await h.page.locator("[role='region'][aria-label^='Mapa']").first().getAttribute("aria-label"),
    solapes: (await overlaps(h.page)).solapes,
    axe: await axe(h.page),
    consola: h.errors,
  };
  await h.page.screenshot({ path: `${out}/g3_mapa_colegio_desktop.png` });
  await h.ctx.close();

  // What must hold, so the run fails instead of only dumping JSON
  const entries = Object.entries(report).filter(([, v]) => typeof v === "object");
  const failures = [];
  for (const [key, v] of entries) {
    if (v.axe?.length) failures.push(`${key}: axe ${v.axe.map((a) => a.id).join(", ")}`);
    if (v.consola?.length) failures.push(`${key}: consola`);
    if (v.overflow_px > 0) failures.push(`${key}: desborde ${v.overflow_px}px`);
    if (v.solapes?.length) failures.push(`${key}: solapes`);
    if (v.metodo_api && v.metodo_api !== "gap-0.3") failures.push(`${key}: método ${v.metodo_api}`);
    if (v.filas?.[0]?.fila !== undefined) {
      const shown = v.filas.filter((f) => f.etiquetas.includes("Junto con sus vecinos") && f.grupo).length;
      if (shown !== v.grupos_api.length) failures.push(`${key}: ${shown} filas con vecinos, la API ${v.grupos_api.length}`);
      const health = v.filas.find((f) => f.fila === "Centros de salud");
      if (!health?.a_pie.some((t) => t.includes("hospital general")) || !health.hospital) failures.push(`${key}: sin el hospital`);
    }
    if ("con_vecinos_api" in v && v.con_vecinos_web !== v.con_vecinos_api) failures.push(`${key}: ${v.con_vecinos_web} con vecinos, la API ${v.con_vecinos_api}`);
    if (v.contamos_centros) failures.push(`${key}: sigue «Contamos centros»`);
  }
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

const FUENCARRAL = { path: "/zona/distrito/2807908", name: "Fuencarral-El Pardo" };

/** HOSP-001 (D-218): hospitals with their name, beds and who runs them, and the source of the beds. */
async function hospitals(browser) {
  const failures = [];
  for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
    const { ctx, page, errors } = await open(browser, profile, FUENCARRAL.path);
    const panel = page.getByRole("region", { name: "Todos los centros", exact: true });
    const chip = panel.getByRole("button", { name: /^Hospitales/ });
    await chip.waitFor({ timeout: 20000 });
    await page.waitForTimeout(6000); // the camera lands, for the capture
    if (id === "mobile") {
      await page.getByRole("button", { name: /Desliza hacia arriba/ }).tap();
      await page.waitForTimeout(600);
    }
    await panel.scrollIntoViewIfNeeded();
    await (id === "mobile" ? chip.tap() : chip.click());
    await panel.getByText(/^Camas: /).waitFor({ timeout: 20000 });
    await panel.getByText(/^Ver la lista/).click();
    const list = panel.getByRole("list", { name: /hospital/ });
    const items = (await list.locator("li").allInnerTexts()).map(flat);
    const source = panel.getByText(/^Camas: /);
    const entry = (report[`hospitales_${id}`] = {
      frase: flat(await panel.locator("[aria-live='polite']").innerText()),
      lista: items,
      fuente: flat(await source.innerText()),
      fuente_enlace: await source.getByRole("link").getAttribute("href"),
      axe: await axe(page),
      overflow_px: await overflow(page),
      consola: errors,
    });
    await panel.screenshot({ path: `${out}/hosp_hospitales_fuencarral_${id}.png` });
    if (!items.some((t) => t.includes("Hospital Universitario La Paz · 966 camas instaladas · gestión pública"))) failures.push(`${id}: sin La Paz`);
    if (items.some((t) => /privado|(^|· )privada/.test(t))) failures.push(`${id}: «privado» a secas`);
    if (!entry.frase.includes("el nombre de algunos")) failures.push(`${id}: aviso de nombres`);
    if (entry.axe.length) failures.push(`${id}: axe ${entry.axe.map((a) => a.id).join(", ")}`);
    if (entry.consola.length) failures.push(`${id}: consola`);
    if (entry.overflow_px > 0) failures.push(`${id}: desborde ${entry.overflow_px}px`);
    await ctx.close();
  }
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/**
 * Incident EMAXCONNSESSION (review of PR #16): if /gaps of the zone hangs, the request gives up
 * after 10 s; the map and the zone still load from the outlines and the card offers «Reintentar».
 */
async function hungGaps(browser) {
  const failures = [];
  for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
    const ctx = await browser.newContext({ ...profile, locale: "es-ES" });
    // Never answered (the preload of the HTML and the page's request), as an API that hangs; once
    // the card shows the failure, «Reintentar» goes through
    let hang = true;
    await ctx.route("**/api/v1/gaps/distrito/2807905", (route) => (hang ? undefined : route.continue()));
    const page = await ctx.newPage();
    const errors = [];
    page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
    page.on("pageerror", (e) => errors.push(e.message));
    const started = Date.now();
    await page.goto(`${BASE}${ZONE.path}`, { waitUntil: "domcontentloaded" });
    await page.getByRole("heading", { level: 1, name: /Chamartín/ }).waitFor({ timeout: 30000 });
    const zoneAfter = Date.now() - started;
    const alert = page.getByRole("alert").filter({ has: page.getByRole("button", { name: "Reintentar" }) }).first();
    await alert.waitFor({ timeout: 20000 });
    const entry = (report[`gaps_colgado_${id}`] = { zona_a_los_ms: zoneAfter, aviso: flat(await alert.innerText()) });
    await page.screenshot({ path: `${out}/peticiones_gaps_colgado_${id}.png` });
    hang = false;
    await alert.getByRole("button", { name: "Reintentar" }).click();
    await page.getByRole("heading", { name: "Qué falta aquí" }).first().locator("xpath=..").getByRole("list").first().waitFor({ timeout: 20000 });
    entry.tras_reintentar = await page.getByRole("alert").filter({ has: page.getByRole("button", { name: "Reintentar" }) }).count();
    // The aborted request is the only expected console line, if any
    entry.consola = errors.filter((e) => !/gaps\/distrito\/2807905|ERR_ABORTED|TimeoutError|signal timed out/.test(e));
    if (zoneAfter > 15000) failures.push(`${id}: la zona tardó ${zoneAfter} ms`);
    if (entry.tras_reintentar) failures.push(`${id}: Reintentar no recupera la tarjeta`);
    if (entry.consola.length) failures.push(`${id}: consola`);
    await ctx.close();
  }
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/** Licences (D, 12 nov): the footer and the map cite the Ministry of Health with its update dates, and CartoCiudad. */
async function licences(browser) {
  const failures = [];
  for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
    for (const [name, path] of [["que_falta", "/que-falta?zona=distrito/2807913"], ["como_lo_calculamos", "/como-lo-calculamos"]]) {
      const p = await open(browser, profile, path);
      const footer = p.page.locator("footer").last();
      await footer.getByText(/^Datos: \d+ conjuntos/).waitFor({ timeout: 20000 });
      await footer.scrollIntoViewIfNeeded();
      const entry = (report[`pie_${name}_${id}`] = {
        pie: (await footer.locator("li, p, a").allInnerTexts()).map(flat).filter(Boolean),
        axe: await axe(p.page),
        overflow_px: await overflow(p.page),
        consola: p.errors,
      });
      await footer.screenshot({ path: `${out}/licencias_pie_${name}_${id}.png` });
      const text = entry.pie.join(" | ");
      for (const must of [
        "Fuente: Ministerio de Sanidad — Catálogo Nacional de Hospitales 2025 (actualizado a 31/12/2024) y Catálogo de Centros de Atención Primaria del SNS 2026 (actualizado a 31/12/2025).",
        "Geocodificación: CartoCiudad (IGN), CC BY 4.0 scne.es.",
        "del CRTM ni del Ministerio de Sanidad.",
        "(con los del CRTM) + Ayuntamiento de Madrid + Ministerio de Sanidad",
      ]) {
        if (!text.includes(must)) failures.push(`${name} ${id}: falta «${must}»`);
      }
      if (entry.axe.length) failures.push(`${name} ${id}: axe ${entry.axe.map((a) => a.id).join(", ")}`);
      if (entry.consola.length) failures.push(`${name} ${id}: consola`);
      if (entry.overflow_px > 0) failures.push(`${name} ${id}: desborde`);
      await p.ctx.close();
    }
  }
  // The zone screen has no footer: the map's attribution cites them
  const z = await open(browser, DESKTOP, "/zona/distrito/2807908");
  await z.page.locator(".maplibregl-ctrl-attrib").first().waitFor({ timeout: 20000 });
  report.mapa_atribucion = flat(await z.page.locator(".maplibregl-ctrl-attrib-inner").first().innerText());
  if (!/Ministerio de Sanidad/.test(report.mapa_atribucion) || !/CartoCiudad/.test(report.mapa_atribucion)) failures.push("mapa: atribución");
  await z.page.locator(".maplibregl-ctrl-attrib").first().screenshot({ path: `${out}/licencias_mapa_desktop.png` });
  await z.ctx.close();
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/** Copy of line D after gap-0.3 and D-218 (pitch/textos_web.md, «Novedades del 12 nov»; metodologia §1.4–1.8). */
async function texts(browser) {
  const failures = [];
  const expect = (key, text, must, mustNot = []) => {
    for (const m of must) if (!text.includes(m)) failures.push(`${key}: falta «${m}»`);
    for (const m of mustNot) if (text.includes(m)) failures.push(`${key}: sigue «${m}»`);
  };
  const clean = (key, entry) => {
    if (entry.axe.length) failures.push(`${key}: axe ${entry.axe.map((a) => a.id).join(", ")}`);
    if (entry.consola.length) failures.push(`${key}: consola`);
    if (entry.overflow_px > 0) failures.push(`${key}: desborde ${entry.overflow_px}px`);
  };
  for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
    // «Cómo lo calculamos»
    const m = await open(browser, profile, "/como-lo-calculamos");
    const section = (sid) => m.page.locator(`#${sid}`).locator("..");
    const entry = (report[`como_lo_calculamos_${id}`] = {
      hospital: flat(await section("que-falta").getByText(/^El hospital\./).locator("..").innerText()),
      limites: (await section("limites").locator("li strong").allInnerTexts()).map(flat),
      fiabilidad: flat(await section("fiabilidad").innerText()),
      datos: flat(await section("datos").locator("ul").first().innerText()),
      a_pie: flat(await section("a-pie").innerText()),
      axe: await axe(m.page),
      overflow_px: await overflow(m.page),
      consola: m.errors,
    });
    expect(`como ${id} hospital`, entry.hospital, ["No cuenta para el estado de la fila", "camas instaladas", "Catálogo Nacional de Hospitales"], ["tampoco las tenemos"]);
    expect(`como ${id} límites`, entry.limites.join(" | "), ["Colocamos a la gente por calles.", "Las camas de hospital no cuentan en la lista."]);
    expect(`como ${id} fiabilidad`, entry.fiabilidad, ["300 niños de 5 a 14 años", "Aulas repartidas."], ["500 menores de 15 años"]);
    expect(`como ${id} datos`, entry.datos, ["Ministerio de Sanidad", "CartoCiudad del IGN"]);
    clean(`como ${id}`, entry);
    await section("que-falta").screenshot({ path: `${out}/textos_como_lo_calculamos_metodo_${id}.png` });
    await m.ctx.close();

    // «Qué falta» of a small municipio with its neighbours (group sentence) and the hospital note
    const q = await open(browser, profile, "/que-falta?zona=municipio/28004");
    await q.page.getByText(/De dónde sale/).first().waitFor({ timeout: 20000 });
    const rows = await gapRows(q.page);
    const qEntry = (report[`que_falta_el_alamo_${id}`] = {
      intro: flat(await q.page.getByText(/^Miramos lo que tiene la gente/).first().innerText()),
      grupos: rows.map((r) => r.grupo).filter(Boolean),
      hospital: rows.find((r) => r.hospital)?.hospital ?? null,
      axe: await axe(q.page),
      overflow_px: await overflow(q.page),
      consola: q.errors,
    });
    expect(`qué falta ${id} intro`, qEntry.intro, ["a 15 minutos andando, repartido entre todos los que lo comparten"]);
    expect(`qué falta ${id} grupo`, qEntry.grupos.join(" | "), ["de lo que tienen de media los municipios de su tipo"], ["tendrían"]);
    expect(`qué falta ${id} hospital`, qEntry.hospital ?? "", ["y no cuenta para el estado de la fila."]);
    clean(`qué falta ${id}`, qEntry);
    await q.page.screenshot({ path: `${out}/textos_que_falta_el_alamo_${id}.png` });
    await q.ctx.close();
  }
  // «Todos los centros»: centros de salud y consultorios
  const z = await open(browser, DESKTOP, ZONE.path);
  const panel = z.page.getByRole("region", { name: "Todos los centros", exact: true });
  await panel.getByRole("button", { name: /^Centros de salud/ }).click();
  report.centros_salud = flat(await panel.locator("[aria-live='polite']").innerText());
  expect("centros de salud", report.centros_salud, ["centros de salud y consultorios en Chamartín"]);
  await z.ctx.close();
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/** Captures C3 and C4 of line D's deck (pitch/slides.md, «Recaptura tras gap-0.3»), at 1440 px. */
async function deckCaptures(browser) {
  const failures = [];
  // C4: «Qué falta» of Puente de Vallecas, escuelas infantiles in FALTA
  const q = await open(browser, DESKTOP, "/que-falta?zona=distrito/2807913");
  await q.page.getByText(/De dónde sale/).first().waitFor({ timeout: 20000 });
  const rows = await gapRows(q.page);
  const nursery = rows.find((r) => r.fila === "Escuelas infantiles");
  report.c4 = { filas: rows.map((r) => [r.fila, r.etiquetas.join(" "), r.mide]), escuelas_infantiles: nursery ?? null, consola: q.errors };
  if (!nursery?.etiquetas.some((t) => /FALTA/.test(t ?? ""))) failures.push("C4: escuelas infantiles no sale FALTA");
  await q.page.screenshot({ path: `${out}/deck_c4_puente_de_vallecas_que_falta_1440.png` });
  await q.page.screenshot({ path: `${out}/deck_c4_puente_de_vallecas_que_falta_1440_completa.png`, fullPage: true });
  const row = q.page.locator("main li.glass").filter({ has: q.page.getByRole("heading", { name: "Escuelas infantiles" }) });
  await row.screenshot({ path: `${out}/deck_c4_puente_de_vallecas_escuelas_infantiles_1440.png` });
  await q.ctx.close();

  // C3: Portada → «Ver un ejemplo…» → «Ver todas las opciones»; then the view with the +5 min change
  const h = await open(browser, DESKTOP);
  await loadExample(h.page);
  const rc = h.page.getByRole("region", { name: "¿Y si cambias algo?", exact: true });
  await rc.getByRole("button", { name: /Ver todas las opciones/ }).click();
  await h.page.waitForTimeout(800);
  report.c3 = { y_si_cambias: flat(await rc.innerText()) };
  if (!/50 zonas, 17 más/.test(report.c3.y_si_cambias)) failures.push("C3: no dice «50 zonas, 17 más»");
  await rc.screenshot({ path: `${out}/deck_c3_y_si_cambias_1440.png` });
  await h.page.screenshot({ path: `${out}/deck_c3_resultados_con_opciones_1440.png` });
  const option = rc.getByRole("button", { name: /colegio con primaria/i }).first();
  if (await option.count()) {
    await option.click();
    await h.page.getByText(/^Con este cambio salen? \d+ zonas?/).first().waitFor({ timeout: 20000 }).catch(() => undefined);
    await h.page.waitForTimeout(2500);
    report.c3.con_el_cambio = flat(await h.page.getByText(/^Con (este cambio|tu búsqueda)/).first().innerText());
    await h.page.evaluate(() => window.scrollTo(0, 0));
    await h.page.waitForTimeout(400);
    await h.page.screenshot({ path: `${out}/deck_c3_vista_50_zonas_1440.png` });
  } else {
    failures.push("C3: sin botón para aplicar el cambio de +5 min");
  }
  report.c3.consola = h.errors;
  await h.ctx.close();
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/** Review of PR #16: beds keep their source without /datasets, and links say they open a new tab. */
async function review(browser) {
  const failures = [];
  for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
    // /datasets down: the beds still cite their source
    const ctx = await browser.newContext({ ...profile, locale: "es-ES" });
    await ctx.route("**/api/v1/datasets*", (route) => route.abort("failed"));
    const page = await ctx.newPage();
    const errors = [];
    page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(`${BASE}${FUENCARRAL.path}`, { waitUntil: "networkidle" });
    const panel = page.getByRole("region", { name: "Todos los centros", exact: true });
    const chip = panel.getByRole("button", { name: /^Hospitales/ });
    await chip.waitFor({ timeout: 20000 });
    if (id === "mobile") {
      await page.getByRole("button", { name: /Desliza hacia arriba/ }).tap();
      await page.waitForTimeout(600);
    }
    await chip.scrollIntoViewIfNeeded();
    await (id === "mobile" ? chip.tap() : chip.click());
    const source = panel.getByText(/^Camas: /);
    await source.waitFor({ timeout: 20000 });
    const entry = (report[`camas_sin_datasets_${id}`] = {
      fuente: flat(await source.innerText()),
      enlaces: await source.getByRole("link").count(),
      consola_otros: errors.filter((e) => !/datasets|ERR_FAILED|Failed to load resource/.test(e)),
    });
    await panel.screenshot({ path: `${out}/revision_camas_sin_datasets_${id}.png` });
    if (entry.fuente !== "Camas: Ministerio de Sanidad, Catálogo Nacional de Hospitales") failures.push(`${id}: fuente fija «${entry.fuente}»`);
    if (entry.consola_otros.length) failures.push(`${id}: consola`);
    await ctx.close();
  }
  // Every link of the footer and the beds' source says it opens in a new tab, for screen readers only
  const f = await open(browser, DESKTOP, "/que-falta?zona=distrito/2807913");
  const footer = f.page.locator("footer").last();
  await footer.getByText(/^Datos: \d+ conjuntos/).waitFor({ timeout: 20000 });
  const names = await footer.getByRole("link").evaluateAll((links) =>
    links.filter((a) => a.target === "_blank").map((a) => a.textContent?.replace(/\s+/g, " ").trim()),
  );
  report.pie_enlaces = names;
  if (!names.length || names.some((n) => !n?.endsWith("(se abre en una pestaña nueva)"))) failures.push("pie: enlaces sin aviso de pestaña nueva");
  report.pie_axe = await axe(f.page);
  if (report.pie_axe.length) failures.push(`pie: axe ${report.pie_axe.map((a) => a.id).join(", ")}`);
  await f.ctx.close();
  // A malformed zone code: Next answers it before the page (it cannot decode the path), so the
  // page's own guard (MapProvider) only covers client navigation. Recorded, not a failure.
  report.zona_mal_formada_http = (await fetch(`${BASE}/zona/distrito/%E0%A4%A`)).status;
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

const browser = await chromium.launch();
if (mode === "fixes") await fixes(browser);
else if (mode === "revision") await review(browser);
else if (mode === "capturas-deck") await deckCaptures(browser);
else if (mode === "textos") await texts(browser);
else if (mode === "licencias") await licences(browser);
else if (mode === "gaps-colgado") await hungGaps(browser);
else if (mode === "hosp") await hospitals(browser);
else if (mode === "offline") await offline(browser);
else if (mode === "tiles-local") await tilesLocal(browser);
else if (mode === "t3") await facilities(browser);
else if (mode === "proyector") await projector(browser);
else if (mode === "gap03") await gap03(browser);
else throw new Error(`Unknown mode ${mode}`);
await browser.close();

writeFileSync(`${out}/qa_${mode}.json`, `${JSON.stringify(report, null, 1)}\n`);
console.log(JSON.stringify(report, null, 1));
