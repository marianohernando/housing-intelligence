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
//   node scripts/check-qa.mjs licencias [outDir] # footer and map show every attribution_text of /datasets
//   node scripts/check-qa.mjs atribucion [outDir] # map attribution folded behind its (i) on every screen, never the LCP
//   node scripts/check-qa.mjs iconos [outDir]    # favicon, icon and apple-touch-icon linked and served, no 404
//   node scripts/check-qa.mjs escaleras [outDir] # «Sin escaleras» opt-in, and the API's accessibility fact in the card
//   node scripts/check-qa.mjs parques [outDir]   # «Parques» in «Todos los centros» and green on the map (DATA-018)
//   node scripts/check-qa.mjs seguridad [outDir] # how the neighbours rate their barrio's safety, only in Madrid's districts (D-226)
//   node scripts/check-qa.mjs verdes [outDir]    # «Zonas verdes» (fit-0.3), the same checks; neither leaves a «Muy pronto» line
//   node scripts/check-qa.mjs textos [outDir]    # line D's copy after gap-0.3 and D-218 (method page, «Qué falta», centres)
//   node scripts/check-qa.mjs capturas-deck [outDir] # captures C1–C4 of line D's deck (gap-0.3, fit-0.2)
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

const FUENCARRAL = { path: "/zona/distrito/2807908", id: "ES.28.DIS.2807908", name: "Fuencarral-El Pardo" };
const HOSPITALS = ["Hospital general", "Hospital especializado", "Hospital de media y larga estancia", "Hospital de salud mental y tratamiento de toxicomanías"];
const NO_NAME_NOTICE = "Algunos centros salen sin nombre porque no hemos podido comprobarlo en las fuentes oficiales.";

/**
 * Hospitals of Fuencarral-El Pardo without a proper name in the API, on every page of /places: an
 * empty name, or only the type, «Hospital general (Madrid)» (lib/map/places.ts).
 */
async function unnamedHospitals() {
  const features = [];
  for (let page = 1, pages = 1; page <= pages; page++) {
    const q = new URLSearchParams({ category: "health", admin_unit_id: FUENCARRAL.id, page: String(page) });
    for (const s of HOSPITALS) q.append("subcategory", s);
    const response = await fetch(`${API}/api/v1/places?${q}`);
    if (!response.ok) throw new Error(`GET /places ${response.status}`);
    const { data } = await response.json();
    features.push(...data.features);
    pages = data.pages;
  }
  return features.filter(({ properties: { name, subcategory } }) => !name?.trim() || name.startsWith(`${subcategory} (`)).length;
}

/** HOSP-001 (D-218): hospitals with their name, beds and who runs them, and the source of the beds. */
async function hospitals(browser) {
  const failures = [];
  // The notice shows when some hospital has no name, as the API says: since D-221 all may have one
  report.hospitales_sin_nombre_api = await unnamedHospitals();
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
    // centros.camas, with the link on the catalogue once /datasets is in
    await panel.getByText(/^Camas instaladas a 31 de diciembre de 2024, según el /).getByRole("link").waitFor({ timeout: 20000 });
    await panel.getByText(/^Ver la lista/).click();
    const list = panel.getByRole("list", { name: /hospital/ });
    const items = (await list.locator("li").allInnerTexts()).map(flat);
    const source = panel.getByText(/^Camas instaladas /);
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
    if (entry.frase.includes(NO_NAME_NOTICE) !== report.hospitales_sin_nombre_api > 0) failures.push(`${id}: aviso de nombres distinto de la API`);
    if (!entry.fuente.startsWith("Camas instaladas a 31 de diciembre de 2024, según el Catálogo Nacional de Hospitales 2025")) failures.push(`${id}: frase de las camas`);
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

/**
 * Every citation in a list of lines: each dataset's attribution_text (from the source catalogue,
 * via /datasets) must be made of lines shown, in order. Lines the API does not give are left out.
 */
function citedAll(lines, datasets) {
  const missing = [];
  for (const ref of datasets) {
    let rest = (ref.attribution_text ?? "").trim();
    while (rest) {
      const line = lines.find((l) => rest.startsWith(l));
      if (!line) {
        missing.push(`${ref.dataset_id}: «${rest}»`);
        break;
      }
      rest = rest.slice(line.length).trim();
    }
  }
  return missing;
}

/** Licences: the footer and the map show every citation the API gives (attribution_text), as the catalogue writes it. */
async function licences(browser) {
  const failures = [];
  const { datasets } = (await (await fetch(`${API}/api/v1/datasets`)).json()).data;
  report.citas_api = [...new Set(datasets.map((d) => d.attribution_text))];
  for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
    for (const [name, path] of [["que_falta", "/que-falta?zona=distrito/2807913"], ["como_lo_calculamos", "/como-lo-calculamos"]]) {
      const p = await open(browser, profile, path);
      const footer = p.page.locator("footer").last();
      await footer.getByText(/^Datos: \d+ conjuntos/).waitFor({ timeout: 20000 });
      await footer.scrollIntoViewIfNeeded();
      const lines = (await footer.locator("li").evaluateAll((items) =>
        items.map((li) => {
          const visible = li.cloneNode(true);
          visible.querySelectorAll(".visually-hidden").forEach((h) => h.remove());
          return visible.textContent?.replace(/\s+/g, " ").trim() ?? "";
        }),
      ));
      const entry = (report[`pie_${name}_${id}`] = {
        citas: lines,
        resto: (await footer.locator(":scope > p, :scope > a").allInnerTexts()).map(flat),
        axe: await axe(p.page),
        overflow_px: await overflow(p.page),
        consola: p.errors,
      });
      await footer.screenshot({ path: `${out}/licencias_pie_${name}_${id}.png` });
      for (const m of citedAll(lines, datasets)) failures.push(`${name} ${id}: falta ${m}`);
      const rest = entry.resto.join(" | ");
      for (const must of ["del CRTM ni del Ministerio de Sanidad.", "(con los del CRTM) + Ayuntamiento de Madrid + Ministerio de Sanidad"]) {
        if (!rest.includes(must)) failures.push(`${name} ${id}: falta «${must}»`);
      }
      if (entry.axe.length) failures.push(`${name} ${id}: axe ${entry.axe.map((a) => a.id).join(", ")}`);
      if (entry.consola.length) failures.push(`${name} ${id}: consola`);
      if (entry.overflow_px > 0) failures.push(`${name} ${id}: desborde`);
      await p.ctx.close();
    }
  }
  // The zone screen has no footer: the map's attribution carries the same citations, behind its (i)
  const z = await open(browser, DESKTOP, "/zona/distrito/2807908");
  await z.page.locator(".maplibregl-ctrl-attrib").first().waitFor({ timeout: 20000 });
  await z.page.locator(".maplibregl-ctrl-attrib-button").first().click();
  await z.page.locator(".maplibregl-ctrl-attrib.maplibregl-compact-show .maplibregl-ctrl-attrib-inner").first().waitFor({ timeout: 10000 });
  report.mapa_atribucion = flat(await z.page.locator(".maplibregl-ctrl-attrib-inner").first().innerText());
  const mapLines = report.mapa_atribucion.split(/ · | \| /);
  for (const m of citedAll(mapLines, datasets)) failures.push(`mapa: falta ${m}`);
  await z.page.locator(".maplibregl-ctrl-attrib").first().screenshot({ path: `${out}/licencias_mapa_desktop.png` });
  await z.ctx.close();
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/** Candidates for the largest paint on a phone over slow 4G (the profile of infra/deploy/e2e/perf_prod.mjs). */
async function lcpOnSlow4g(browser, path) {
  const ctx = await browser.newContext({ ...MOBILE, locale: "es-ES" });
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  await cdp.send("Network.enable");
  await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
  await cdp.send("Network.emulateNetworkConditions", { offline: false, latency: 150, downloadThroughput: (1.6 * 1024 * 1024) / 8, uploadThroughput: (750 * 1024) / 8 });
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
  await page.addInitScript(() => {
    window.__lcp = [];
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) {
        window.__lcp.push({ ms: Math.round(e.startTime), en_atribucion: Boolean(e.element?.closest(".maplibregl-ctrl-attrib")), texto: (e.element?.textContent ?? "").trim().slice(0, 50) });
      }
    }).observe({ type: "largest-contentful-paint", buffered: true });
  });
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle", timeout: 180_000 });
  const entries = await page.evaluate(() => window.__lcp);
  await ctx.close();
  return entries;
}

/** What the map's attribution must stay clear of: the header, the sheet and every card, button or link outside the map. */
function aroundAttribution(page) {
  return page.evaluate(() => {
    const rect = (el) => { const r = el.getBoundingClientRect(); return { top: Math.round(r.top), bottom: Math.round(r.bottom), left: Math.round(r.left), right: Math.round(r.right) }; };
    const sheet = document.querySelector("[data-sheet='folded']");
    const sheetTop = sheet && getComputedStyle(sheet).position === "fixed" ? sheet.getBoundingClientRect().top : innerHeight;
    const controls = [...document.querySelectorAll("a, button, select, .glass")]
      .filter((el) => !el.closest(".maplibregl-map") && el.getClientRects().length > 0)
      .map((el) => ({ el: `${el.tagName.toLowerCase()} «${(el.getAttribute("aria-label") ?? el.textContent ?? "").trim().replace(/\s+/g, " ").slice(0, 40)}»`, ...rect(el) }))
      .filter((r) => r.top < sheetTop && r.bottom > 0 && r.right > 0 && r.left < innerWidth);
    return { cabecera: rect(document.querySelector("header")), hoja_arriba: Math.round(sheetTop), controles: controls };
  });
}

/**
 * One screen of the attribution: folded at load behind its (i), one tap or click opens every
 * citation the API gives and another folds it, clear of the header, the sheet, the cards and the
 * buttons, with axe and the console clean. `label` names the captures; failures go to `failures`.
 */
async function attributionScreen(p, label, datasets, failures, touch) {
  const control = p.page.locator(".maplibregl-ctrl-attrib").first();
  const button = p.page.locator(".maplibregl-ctrl-attrib-button").first();
  await control.waitFor({ timeout: 20000 });
  const state = () => control.evaluate((el) => el.classList.contains("maplibregl-compact-show") && el.hasAttribute("open"));
  const press = () => (touch ? button.tap() : button.click());
  const hits = (b, ctx) => ctx.controles.filter((r) => b.left < r.right - 1 && r.left < b.right - 1 && b.top < r.bottom - 1 && r.top < b.bottom - 1).map((r) => r.el);
  const ctx = await aroundAttribution(p.page);
  const entry = { abierta_al_cargar: await state(), boton: { nombre: await button.getAttribute("aria-label"), caja: await box(button) } };
  entry.boton_pisa = hits(entry.boton.caja, ctx);
  // mapa.atribucion.movil: OSM and the CRTM always in view beside the (i), each with its link
  const credits = control.locator("xpath=following-sibling::p[1]");
  const visibleCredits = async () => (await credits.count()) > 0 && credits.isVisible();
  entry.creditos = {
    texto: (await credits.count()) ? flat(await credits.evaluate((el) => { const c = el.cloneNode(true); c.querySelectorAll(".visually-hidden").forEach((h) => h.remove()); return c.textContent ?? ""; })) : null,
    enlaces: await credits.locator("a").evaluateAll((links) => links.map((a) => a.getAttribute("href"))),
    visible_plegada: await visibleCredits(),
    caja: (await credits.count()) ? await box(credits) : null,
  };
  entry.creditos.pisa = entry.creditos.caja ? hits(entry.creditos.caja, ctx) : [];
  await p.page.screenshot({ path: `${out}/atribucion_${label}_plegada.png` });
  await press();
  await p.page.waitForTimeout(300);
  entry.abierta_tras_un_toque = await state();
  entry.abierta = { caja: await box(control), texto: flat(await p.page.locator(".maplibregl-ctrl-attrib-inner").first().innerText()) };
  entry.abierta_pisa = hits(entry.abierta.caja, ctx);
  entry.creditos.visible_abierta = await visibleCredits();
  await p.page.screenshot({ path: `${out}/atribucion_${label}_abierta.png` });
  entry.axe_abierta = await axe(p.page);
  await press();
  await p.page.waitForTimeout(300);
  entry.abierta_tras_otro_toque = await state();
  entry.axe = await axe(p.page);
  entry.overflow_px = await overflow(p.page);
  entry.consola = p.errors;
  if (entry.abierta_al_cargar) failures.push(`${label}: abierta al cargar`);
  if (!entry.abierta_tras_un_toque || entry.abierta_tras_otro_toque) failures.push(`${label}: el (i) no abre y cierra`);
  if (entry.boton.nombre !== "Fuentes y licencias de los datos") failures.push(`${label}: nombre del (i) «${entry.boton.nombre}»`);
  const c = entry.creditos;
  if (c.texto !== "© OpenStreetMap · Powered by CRTM" || c.enlaces.join(" ") !== "https://www.openstreetmap.org/copyright https://www.crtm.es") failures.push(`${label}: créditos «${c.texto}» ${c.enlaces}`);
  if (!c.visible_plegada || c.visible_abierta) failures.push(`${label}: créditos no visibles con el (i) plegado, o repetidos con la lista abierta`);
  const lowest = Math.max(entry.abierta.caja.bottom, c.caja?.bottom ?? 0);
  if (entry.boton.caja.top < ctx.cabecera.bottom || lowest > ctx.hoja_arriba) failures.push(`${label}: pisa la cabecera o la hoja`);
  const overlapping = [...entry.boton_pisa, ...c.pisa, ...entry.abierta_pisa];
  if (overlapping.length) failures.push(`${label}: pisa ${overlapping.join(", ")}`);
  for (const m of citedAll(entry.abierta.texto.split(/ · | \| /), datasets)) failures.push(`${label}: falta ${m}`);
  if (entry.axe.length || entry.axe_abierta.length) failures.push(`${label}: axe ${[...entry.axe, ...entry.axe_abierta].map((a) => a.id).join(", ")}`);
  if (entry.consola.length) failures.push(`${label}: consola`);
  if (entry.overflow_px > 0) failures.push(`${label}: desborde`);
  return entry;
}

/**
 * Attribution of the map (LCP of C on slow 4G, cards over it on desktop): on every screen folded
 * behind its (i) in the map's free area with OSM and the CRTM in view beside it (line D, review of
 * PR #22), opened with one tap or click, clear of the cards, the legend, the sheet and the buttons,
 * also after turning the phone; never the largest paint.
 */
async function attribution(browser) {
  const failures = [];
  const { datasets } = (await (await fetch(`${API}/api/v1/datasets`)).json()).data;
  const screens = [
    ["mobile", MOBILE, true, [["portada", "/"], ["zona", ZONE.path]]],
    ["desktop", DESKTOP, false, [["portada", "/"], ["zona", ZONE.path]]],
    ["1280x720", { viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 }, false, [["zona", ZONE.path]]],
    ["1024x768", { viewport: { width: 1024, height: 768 }, deviceScaleFactor: 1 }, false, [["portada", "/"]]],
  ];
  for (const [id, profile, touch, pages] of screens) {
    for (const [name, path] of pages) {
      const p = await open(browser, profile, path);
      const entry = (report[`${name}_${id}`] = await attributionScreen(p, `${name}_${id}`, datasets, failures, touch));
      // Turned to landscape (wider than the mobile layout) and back: still folded, in its place. On
      // the zone screen: at 390 px of height the overview's legend covers almost all the map (before
      // this change too, over the attribution spelled out at the bottom right)
      if (id === "mobile" && name === "zona") {
        await p.page.setViewportSize({ width: 844, height: 390 });
        await p.page.waitForTimeout(1200);
        entry.girado = await attributionScreen(p, `${name}_mobile_girado`, datasets, failures, true);
        await p.page.setViewportSize({ width: 390, height: 844 });
        await p.page.waitForTimeout(1200);
        entry.vuelta = await attributionScreen(p, `${name}_mobile_vuelta`, datasets, failures, true);
      }
      if (id === "mobile") {
        entry.lcp_slow4g = await lcpOnSlow4g(browser, path);
        const last = entry.lcp_slow4g.at(-1);
        if (!last || last.en_atribucion) failures.push(`${name} mobile: la atribución es el LCP`);
      }
      await p.ctx.close();
    }
  }
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/** The two chips that left «Muy pronto»: what each one says, sends and finds in the card. */
const PRIORITY_CHIPS = {
  // fit-0.4, DATA-019, D-223: opt-in, its icon is the station it measures (D-204, PR #26 of D)
  escaleras: {
    label: "Sin escaleras",
    key: "sin_escaleras",
    topic: "accesibilidad",
    icon: "lucide-train-front",
    help: "Estación de metro o tren accesible (sin escaleras) según el CRTM, cerca de casa.",
  },
  // fit-0.3, D-222: importa.zonas_verdes of line D
  verdes: {
    label: "Zonas verdes",
    key: "zonas_verdes",
    topic: "zonas_verdes",
    icon: "lucide-trees",
    help: "Parques de una hectárea o más, cerca de casa.",
  },
};

/**
 * A «Me importa» chip with data (PRIORITY_CHIPS): optional and not marked for the person (D-204),
 * with its icon and help, no «Muy pronto» line left under the chips, no wheelchair anywhere, and
 * after a search with it the first zone's card shows the API's facts of its topic as they come.
 */
async function priorityChip(browser, spec) {
  const failures = [];
  const isSearch = (r) => r.url().endsWith("/api/v1/search") && r.request().method() === "POST";
  const escapeRe = (text) => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  for (const [id, profile, touch] of [["desktop", DESKTOP, false], ["mobile", MOBILE, true]]) {
    const p = await open(browser, profile, "/");
    const press = (locator) => (touch ? locator.tap() : locator.click());
    const entry = (report[id] = {});
    // The demo case (which does not mark it), then the chip and the search
    const [base] = await Promise.all([p.page.waitForResponse(isSearch, { timeout: 30000 }), press(p.page.getByRole("button", { name: /Ver un ejemplo/ }))]);
    const baseFacts = (await base.json()).data.results.flatMap((r) => r.facts).filter((f) => f.topic === spec.topic);
    entry.hechos_sin_chip = baseFacts.length;
    await p.page.waitForTimeout(1500);
    const chip = p.page.getByRole("button", { name: new RegExp(`^${spec.label}`) });
    entry.chip = {
      pulsado_antes: await chip.getAttribute("aria-pressed"),
      ayuda: await chip.getAttribute("title"),
      icono: await chip.locator("svg").first().getAttribute("class"),
    };
    await press(chip);
    entry.chip.pulsado_despues = await chip.getAttribute("aria-pressed");
    entry.muy_pronto_lineas = await p.page.getByText(/^Muy pronto:/).count();
    entry.sillas_de_ruedas = await p.page.locator("svg.lucide-accessibility").count();
    await p.page.locator("fieldset").filter({ hasText: "Me importa" }).first().screenshot({ path: `${out}/${mode}_chips_${id}.png` });
    const [response] = await Promise.all([p.page.waitForResponse(isSearch, { timeout: 30000 }), press(p.page.getByRole("button", { name: "Ver zonas que encajan" }))]);
    entry.prioridades_enviadas = JSON.parse(response.request().postData() ?? "{}").priorities;
    const { data } = await response.json();
    await p.page.waitForTimeout(2000);
    const top = data.results[0];
    const facts = top.facts.filter((f) => f.topic === spec.topic).map((f) => f.text);
    entry.api = { metodo: data.methodology_version, primera: top.zone.name, hechos: facts };
    await press(p.page.getByRole("button", { name: new RegExp(`^1 ${escapeRe(top.zone.name)}\\b`) }).first());
    const card = p.page.locator("aside").filter({ hasText: "Lo que tienes aquí" }).first();
    await card.waitFor({ timeout: 20000 });
    await p.page.waitForTimeout(1200);
    const text = flat(await card.innerText());
    entry.tarjeta_muestra = facts.map((f) => text.includes(flat(f)));
    entry.tarjeta_sillas_de_ruedas = await card.locator("svg.lucide-accessibility").count();
    await card.screenshot({ path: `${out}/${mode}_tarjeta_${id}.png` });
    entry.axe = await axe(p.page);
    entry.overflow_px = await overflow(p.page);
    entry.consola = p.errors;
    if (entry.chip.pulsado_antes !== "false" || entry.chip.pulsado_despues !== "true") failures.push(`${id}: el chip no es opcional (${entry.chip.pulsado_antes} → ${entry.chip.pulsado_despues})`);
    if (entry.chip.ayuda !== spec.help) failures.push(`${id}: ayuda del chip «${entry.chip.ayuda}»`);
    if (!entry.chip.icono?.split(" ").includes(spec.icon)) failures.push(`${id}: icono del chip «${entry.chip.icono}»`);
    // The fact comes with the chip: the demo case, without it, has none
    if (entry.hechos_sin_chip > 0) failures.push(`${id}: hay hechos de ${spec.topic} sin marcar el chip`);
    if (entry.muy_pronto_lineas > 0) failures.push(`${id}: sigue la línea «Muy pronto:» bajo los chips`);
    if (entry.sillas_de_ruedas + entry.tarjeta_sillas_de_ruedas > 0) failures.push(`${id}: queda una silla de ruedas`);
    if (!entry.prioridades_enviadas?.includes(spec.key)) failures.push(`${id}: la búsqueda no lleva ${spec.key}`);
    if (!facts.length) failures.push(`${id}: la API no da hecho de ${spec.topic} en ${top.zone.name}`);
    if (entry.tarjeta_muestra.includes(false)) failures.push(`${id}: la tarjeta no muestra tal cual el hecho de la API`);
    if (entry.axe.length) failures.push(`${id}: axe ${entry.axe.map((a) => a.id).join(", ")}`);
    if (entry.consola.length) failures.push(`${id}: consola`);
    if (entry.overflow_px > 0) failures.push(`${id}: desborde`);
    await p.ctx.close();
  }
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/** Zones of the parks check (DATA-018): the Retiro, the Casa de Campo, and a town with no park of 1 ha. */
const PARK_ZONES = [
  { id: "retiro", path: "/zona/distrito/2807903", unit: "ES.28.DIS.2807903", must: ["Parque del Retiro"] },
  { id: "moncloa", path: "/zona/distrito/2807909", unit: "ES.28.DIS.2807909", must: ["Casa de Campo", "Parque sin nombre"] },
  { id: "perales", path: "/zona/municipio/28110", unit: "ES.28.MUN.28110", must: [] },
];

/**
 * «Parques» in «Todos los centros» (DATA-018, D-222, petición de Mariano): as many as /places gives
 * for the zone, named as it names them, green on the map with the base map's parks lit up, the
 * same single request to /places for the zone, and the zone's LCP on slow 4G.
 */
async function parks(browser) {
  const failures = [];
  for (const zone of PARK_ZONES) {
    const r = await fetch(`${API}/api/v1/places?${new URLSearchParams({ category: "green", admin_unit_id: zone.unit })}`);
    const api = (await r.json()).data.total;
    for (const [id, profile, touch] of [["desktop", DESKTOP, false], ["mobile", MOBILE, true]]) {
      const key = `${zone.id}_${id}`;
      const p = await open(browser, profile, zone.path);
      const press = (locator) => (touch ? locator.tap() : locator.click());
      const panel = p.page.getByRole("region", { name: "Todos los centros", exact: true });
      const chip = panel.getByRole("button", { name: /^Parques/ });
      await chip.waitFor({ timeout: 20000 });
      await p.page.waitForTimeout(6000); // the camera lands
      const entry = (report[key] = { api_total: api });
      if (touch) {
        await press(p.page.getByRole("button", { name: /Desliza hacia arriba/ }));
        await p.page.waitForTimeout(600);
        await chip.scrollIntoViewIfNeeded();
      }
      entry.chip = flat(await chip.innerText());
      await press(chip);
      await p.page.waitForTimeout(1500);
      entry.pulsado = await chip.getAttribute("aria-pressed");
      entry.frase = flat(await panel.locator("[aria-live='polite']").innerText());
      entry.icono = await chip.locator("svg").first().getAttribute("class");
      const summary = panel.getByText(/^Ver la lista/);
      if (await summary.count()) {
        await press(summary);
        const items = await panel.getByRole("list", { name: /parques? de 1 ha/ }).locator("li").allInnerTexts();
        entry.lista = { elementos: items.length, primeras: items.slice(0, 6).map(flat), sin_nombre: items.filter((t) => /^Parque sin nombre$/.test(flat(t))).length };
        entry.lista_tiene = Object.fromEntries(zone.must.map((name) => [name, items.some((t) => flat(t) === name)]));
        await panel.screenshot({ path: `${out}/parques_${key}_lista.png` });
      }
      entry.axe = await axe(p.page);
      if (touch) {
        await press(p.page.getByRole("button", { name: "Ver el mapa" }));
        await p.page.waitForTimeout(1500);
      }
      entry.mapa_aria = await p.page.locator("[role='region'][aria-label^='Mapa']").first().getAttribute("aria-label");
      await p.page.screenshot({ path: `${out}/parques_${key}_mapa.png` });
      // Every /places request of the visit (resource timing, from the start), by its categories
      entry.peticiones_places = await p.page.evaluate(() =>
        performance.getEntriesByType("resource").flatMap((e) => (e.name.includes("/api/v1/places") ? [new URL(e.name).searchParams.get("category")] : [])),
      );
      entry.overflow_px = await overflow(p.page);
      entry.consola = p.errors;
      const count = Number((entry.chip.match(/\d[\d.]*/)?.[0] ?? "-1").replace(/\./g, ""));
      if (count !== api) failures.push(`${key}: el chip dice ${count} y /places ${api}`);
      if (entry.pulsado !== "true") failures.push(`${key}: el chip no queda pulsado`);
      if (!entry.icono?.split(" ").includes("lucide-trees")) failures.push(`${key}: icono «${entry.icono}»`);
      if (api === 0 && !/^Ningún parque de 1 ha o más en /.test(entry.frase)) failures.push(`${key}: frase «${entry.frase}»`);
      if (api > 0 && entry.lista?.elementos !== api) failures.push(`${key}: la lista tiene ${entry.lista?.elementos} y /places ${api}`);
      for (const [name, found] of Object.entries(entry.lista_tiene ?? {})) if (!found) failures.push(`${key}: falta «${name}» en la lista`);
      if (api > 0 && !entry.mapa_aria?.includes("parques de 1 ha o más")) failures.push(`${key}: el mapa no dice que salen los parques`);
      if (entry.peticiones_places.length !== 1 || !entry.peticiones_places[0]?.split(",").includes("green")) failures.push(`${key}: /places ${JSON.stringify(entry.peticiones_places)}`);
      if (entry.axe.length) failures.push(`${key}: axe ${entry.axe.map((v) => v.id).join(", ")}`);
      if (entry.consola.length) failures.push(`${key}: consola`);
      if (entry.overflow_px > 0) failures.push(`${key}: desborde`);
      await p.ctx.close();
    }
  }
  // The zone's LCP on slow 4G, mobile (it was about 2 s before the parks)
  report.lcp_retiro_slow4g = await lcpOnSlow4g(browser, PARK_ZONES[0].path);
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/**
 * zona.seguridad_vecinos (DATA-020, D-226 §1): in a Madrid district, its neighbours' rating of the
 * safety of their barrio with the city's, as /features gives them; nothing outside Madrid, and no
 * request to /features there. Neutral colours, no alarm words.
 */
async function perceivedSafety(browser) {
  const failures = [];
  const latest = async (id, level, code) => {
    const r = await fetch(`${API}/api/v1/features/${id}/values?level=${level}`);
    const rows = (await r.json()).data.values.filter((v) => v.territory_code === code && v.value !== null);
    return rows.sort((a, b) => b.period_start.localeCompare(a.period_start))[0]?.value ?? null;
  };
  const score = (v) => v.toLocaleString("es-ES", { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const city = [await latest("seguridad_percibida_noche", "municipio", "28079"), await latest("seguridad_percibida_dia", "municipio", "28079")];
  for (const zone of [
    { id: "retiro", path: "/zona/distrito/2807903", code: "2807903" },
    { id: "centro", path: "/zona/distrito/2807901", code: "2807901" },
    { id: "perales", path: "/zona/municipio/28110", code: null },
  ]) {
    const expected = zone.code
      ? `Así valoran sus vecinos la seguridad de su barrio: ${score(await latest("seguridad_percibida_noche", "distrito", zone.code))} de noche y ${score(await latest("seguridad_percibida_dia", "distrito", zone.code))} de día, de 0 a 10 (en todo Madrid, ${score(city[0])} y ${score(city[1])}).`
      : null;
    for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
      const key = `${zone.id}_${id}`;
      const p = await open(browser, profile, zone.path);
      await p.page.getByRole("region", { name: "Todos los centros", exact: true }).waitFor({ timeout: 20000 });
      await p.page.waitForTimeout(2500);
      const block = p.page.getByText(/^Así valoran sus vecinos/).locator("xpath=..");
      const entry = (report[key] = { esperado: expected });
      entry.bloques = await block.count();
      if (entry.bloques) {
        entry.texto = flat(await block.first().innerText());
        entry.colores = await block.first().evaluate((el) => [...el.querySelectorAll("p")].map((q) => getComputedStyle(q).color));
        await block.first().screenshot({ path: `${out}/seguridad_${key}.png` });
      }
      entry.peticiones_features = await p.page.evaluate(() =>
        performance.getEntriesByType("resource").flatMap((e) => (e.name.includes("/api/v1/features/") ? [new URL(e.name).pathname.split("/")[4] + "?" + new URL(e.name).search.slice(1)] : [])),
      );
      entry.axe = await axe(p.page);
      entry.overflow_px = await overflow(p.page);
      entry.consola = p.errors;
      if (expected && !entry.texto?.startsWith(expected)) failures.push(`${key}: «${entry.texto}»`);
      if (expected && !entry.texto?.includes("Encuesta de calidad de vida del Ayuntamiento de Madrid, 2025, unas 400 personas por distrito.")) failures.push(`${key}: sin la fuente`);
      if (expected && entry.peticiones_features.length !== 4) failures.push(`${key}: ${entry.peticiones_features.length} peticiones a /features`);
      if (!expected && (entry.bloques > 0 || entry.peticiones_features.length > 0)) failures.push(`${key}: sale fuera de Madrid`);
      if (/peligros|insegur/i.test(entry.texto ?? "")) failures.push(`${key}: palabra de alarma`);
      if (entry.axe.length) failures.push(`${key}: axe ${entry.axe.map((v) => v.id).join(", ")}`);
      if (entry.consola.length) failures.push(`${key}: consola`);
      if (entry.overflow_px > 0) failures.push(`${key}: desborde`);
      await p.ctx.close();
    }
  }
  report.lcp_retiro_slow4g = await lcpOnSlow4g(browser, "/zona/distrito/2807903");
  report.fallos = failures;
  if (failures.length) process.exitCode = 1;
}

/**
 * Icons (favicon.ico and apple-touch-icon gave 404 in the deploy logs): every page links them, they
 * load, the old fixed paths phones ask for answer too, and no request of the page fails.
 */
async function icons(browser) {
  const failures = [];
  for (const [id, profile] of [["desktop", DESKTOP], ["mobile", MOBILE]]) {
    for (const [name, path] of [["portada", "/"], ["zona", ZONE.path], ["que_falta", "/que-falta?zona=distrito/2807905"]]) {
      const ctx = await browser.newContext({ ...profile, locale: "es-ES" });
      const page = await ctx.newPage();
      const errors = [];
      const notFound = [];
      page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
      page.on("response", (r) => { if (r.status() >= 400) notFound.push(`${r.status()} ${new URL(r.url()).pathname}`); });
      await page.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
      await page.waitForTimeout(1200);
      const links = await page.locator("link[rel='icon'], link[rel='apple-touch-icon']").evaluateAll((els) =>
        els.map((el) => ({ rel: el.getAttribute("rel"), href: el.getAttribute("href"), sizes: el.getAttribute("sizes"), type: el.getAttribute("type") })),
      );
      const entry = (report[`${name}_${id}`] = { links, errores_http: notFound, axe: await axe(page), consola: errors });
      const rels = links.map((l) => `${l.rel} ${l.type}`);
      for (const must of ["icon image/x-icon", "icon image/svg+xml", "apple-touch-icon image/png"]) {
        if (!rels.includes(must)) failures.push(`${name} ${id}: falta <link> ${must}`);
      }
      if (notFound.length) failures.push(`${name} ${id}: ${notFound.join(", ")}`);
      if (entry.axe.length || errors.length) failures.push(`${name} ${id}: axe o consola`);
      await ctx.close();
    }
  }
  report.rutas = {};
  for (const path of ["/favicon.ico", "/icon.svg", "/apple-icon.png", "/apple-touch-icon.png", "/apple-touch-icon-precomposed.png"]) {
    const r = await fetch(`${BASE}${path}`);
    const body = Buffer.from(await r.arrayBuffer());
    report.rutas[path] = { status: r.status, tipo: r.headers.get("content-type"), bytes: body.length };
    if (r.status !== 200) failures.push(`${path}: ${r.status}`);
  }
  // A sheet with the icons at the sizes a browser and a phone use, from the routes themselves
  const page = await browser.newPage({ viewport: { width: 520, height: 230 }, deviceScaleFactor: 2 });
  await page.setContent(`<body style="margin:0;padding:24px;display:flex;gap:28px;align-items:end;font:14px sans-serif;color:#141b3d;background:#f6f5fc">
    ${[16, 32, 48].map((s) => `<figure style="margin:0;text-align:center"><img src="${BASE}/favicon.ico" width="${s}" height="${s}" alt=""><figcaption>${s} px (.ico)</figcaption></figure>`).join("")}
    <figure style="margin:0;text-align:center"><img src="${BASE}/icon.svg" width="64" height="64" alt=""><figcaption>SVG</figcaption></figure>
    <figure style="margin:0;text-align:center"><img src="${BASE}/apple-icon.png" width="120" height="120" style="border-radius:27px" alt=""><figcaption>iPhone (180 px)</figcaption></figure>
  </body>`);
  await page.waitForLoadState("networkidle");
  await page.screenshot({ path: `${out}/iconos.png` });
  await page.close();
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
    entry.que_cuenta = flat(await section("que-falta").locator("ul").first().innerText());
    entry.tablas = await section("que-falta").locator("table").count();
    expect(`como ${id} qué cuenta`, entry.que_cuenta, ["Escuelas infantiles, para niños de 0 a 4 años: cada escuela", "Vivienda, para hogares de 4 o más personas: no va a pie."]);
    if (entry.tablas !== 1) failures.push(`como ${id}: ${entry.tablas} tablas (solo la de estados)`);
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

/** Captures C1–C4 of line D's deck (pitch/slides.md, «Recaptura tras gap-0.3» and fit-0.2), at 1440 px. */
async function deckCaptures(browser) {
  const failures = [];
  // C1 and C2 (fit-0.2): the demo search, the map and the first zone's card, checked against the
  // /search answer the page receives (first zone and its facts, the commute in transit minutes)
  const s = await open(browser, DESKTOP);
  const [answer] = await Promise.all([
    s.page.waitForResponse((r) => r.url().endsWith("/api/v1/search") && r.request().method() === "POST", { timeout: 30000 }),
    loadExample(s.page),
  ]);
  const api = (await answer.json()).data;
  const top = api.results[0];
  const commute = top.facts.find((f) => /min en transporte público/.test(f.text));
  report.c1_c2 = { metodo: api.methodology_version, primera: [top.zone.name, top.match_pct], trabajo: commute?.text ?? null };
  if (!commute) failures.push("C2: la 1.ª zona no trae el trabajo en minutos de transporte público");
  await s.page.getByRole("button", { name: new RegExp(`^1 ${top.zone.name}\\b`) }).first().click();
  const card = s.page.locator("aside").filter({ hasText: "Lo que tienes aquí" }).first();
  await card.waitFor({ timeout: 20000 });
  await s.page.waitForTimeout(2500);
  const cardText = flat(await card.innerText());
  report.c1_c2.tarjeta = cardText;
  for (const fact of top.facts) if (!cardText.includes(flat(fact.text))) failures.push(`C2: falta «${fact.text}»`);
  if (!cardText.includes(`${top.match_pct} %`)) failures.push("C2: % de encaje distinto de la API");
  await s.page.screenshot({ path: `${out}/deck_c1_busqueda_1440.png` });
  await card.screenshot({ path: `${out}/deck_c2_tarjeta_zona_1440.png` });
  // trabajo.ayuda of fit-0.2, and no «Tiempo en transporte: muy pronto» any more (D, 0186ae9)
  report.c1_c2.trabajo_ayuda = await s.page.getByText("Miramos cuánto tardarías en transporte público para llegar a las 9:00.").count();
  report.c1_c2.muy_pronto = await s.page.getByText("Tiempo en transporte: muy pronto").count();
  if (!report.c1_c2.trabajo_ayuda || report.c1_c2.muy_pronto) failures.push("C1: textos de «Trabajo en»");
  report.c1_c2.consola = s.errors;
  if (s.errors.length) failures.push("C1: consola");
  await s.ctx.close();

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
    const source = panel.getByText(/^Camas instaladas /);
    await source.waitFor({ timeout: 20000 });
    const entry = (report[`camas_sin_datasets_${id}`] = {
      fuente: flat(await source.innerText()),
      enlaces: await source.getByRole("link").count(),
      consola_otros: errors.filter((e) => !/datasets|ERR_FAILED|Failed to load resource/.test(e)),
    });
    await panel.screenshot({ path: `${out}/revision_camas_sin_datasets_${id}.png` });
    // Line D's fixed text, without the link that /datasets gives
    if (entry.fuente !== "Camas instaladas a 31 de diciembre de 2024, según el Catálogo Nacional de Hospitales 2025 del Ministerio de Sanidad.") failures.push(`${id}: fuente sin /datasets «${entry.fuente}»`);
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
else if (mode === "atribucion") await attribution(browser);
else if (mode === "iconos") await icons(browser);
else if (mode === "parques") await parks(browser);
else if (mode === "seguridad") await perceivedSafety(browser);
else if (Object.hasOwn(PRIORITY_CHIPS, mode)) await priorityChip(browser, PRIORITY_CHIPS[mode]);
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
