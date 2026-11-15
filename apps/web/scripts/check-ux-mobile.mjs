// Mobile clarity check (UX mobile audit, prompts/UX_AUDITORIA_MOVIL.md §3 C1 and M1): on the four
// screens of the journey (portada, formulario, lista, tarjeta) it lists every text under 16 px and
// every touch target under 44 px at a phone width, runs axe (WCAG 2.2 AA) on each state and, with
// --shots, takes the screenshots of the evidence at 390, 360 and 1440 px.
//
//   node apps/web/scripts/check-ux-mobile.mjs --base http://localhost:3061 --out DIR --label despues [--shots]
//
// The names of the screens are matched by the texts before and after the first delivery of the
// audit, so the same script measures both. Exit 1 if axe finds any violation.
import { mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join, resolve } from "node:path";
import { parseArgs } from "node:util";

import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const AXE = require.resolve("axe-core/axe.min.js");

const { values: opts } = parseArgs({
  options: {
    base: { type: "string", default: "http://localhost:3061" },
    out: { type: "string", default: "." },
    label: { type: "string", default: "medida" },
    shots: { type: "boolean", default: false },
    widths: { type: "string", default: "390" },
    profiles: { type: "string", default: "390,360,1440" },
  },
});
const BASE = opts.base.replace(/\/$/, "");
const OUT = resolve(opts.out);
mkdirSync(OUT, { recursive: true });

const WAIT = 30_000;
const MIN_TEXT_PX = 16;
const MIN_TARGET_PX = 44;
// Before and after the first delivery (textos_web.md)
const NAMES = {
  search: /^Tu búsqueda$/,
  results: /^(Zonas que encajan|Zonas que te convienen)$/,
  changes: /^(¿Y si cambias algo\?|¿Quieres ver más zonas\?)$/,
  family: /pareja con 2 hijos/,
  seniorsExample: /pareja jubilada/i,
  seniors: /^Somos mayores/,
  sheetOpen: /^(Desliza hacia arriba para ver más|Toca aquí para ver más)$/,
};

const phone = (width) => ({ viewport: { width, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
const DESKTOP = { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 };

/**
 * In the page: texts under 16 px and targets under 44 px inside `scope` (a CSS selector resolved
 * by `pick`), skipping what is not rendered or only for screen readers.
 */
function measureInPage({ pick, minText, minTarget }) {
  const roots = {
    search: () => [...document.querySelectorAll("section")].find((s) => /^Tu búsqueda$/.test(s.querySelector("h2")?.textContent?.trim() ?? "")),
    results: () => document.querySelector("h2[tabindex='-1']")?.closest("section")?.parentElement ?? null,
    card: () => [...document.querySelectorAll("aside")].find((a) => a.querySelector("h2") && a.textContent.includes("Lo que tienes aquí")) ?? null,
    method: () => document.querySelector("main") ?? document.body,
  };
  const search = roots.search();
  const root = pick === "portada" ? document.body : roots[pick]();
  if (!root) return { error: `no ${pick} on screen` };
  const inScope = (el) => (pick === "portada" ? !(search && search.contains(el)) : true);
  const hiddenForSight = (el) => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.display === "none" || s.visibility === "hidden" || Number(s.opacity) === 0) return true;
      if (s.clipPath === "inset(50%)" || n.classList.contains("visually-hidden")) return true;
    }
    return el.getClientRects().length === 0;
  };
  const label = (el) => (el.getAttribute("aria-label") ?? el.textContent ?? el.value ?? "").replace(/\s+/g, " ").trim().slice(0, 70);
  const where = (el) => (el.closest(".maplibregl-map") ? "mapa" : "página");

  const texts = [];
  for (const el of root.querySelectorAll("*")) {
    if (!inScope(el) || el.closest("svg")) continue;
    const own = [...el.childNodes].filter((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim()).map((n) => n.textContent.trim()).join(" ");
    if (!own || hiddenForSight(el)) continue;
    const size = parseFloat(getComputedStyle(el).fontSize);
    if (size < minText - 0.01) texts.push({ px: Math.round(size * 10) / 10, tag: el.tagName.toLowerCase(), text: own.slice(0, 70), where: where(el) });
  }

  const targets = [];
  const seen = new Set();
  for (let el of root.querySelectorAll("a[href], button, select, input:not([type=hidden]), textarea, summary, [role=button]")) {
    // A box or radio inside its label: the label is what the finger touches
    if (el.matches("input[type=checkbox], input[type=radio]") && el.closest("label")) el = el.closest("label");
    if (seen.has(el) || !inScope(el)) continue;
    seen.add(el);
    if (el.closest(".skip-link") || el.classList.contains("skip-link")) continue;
    if (hiddenForSight(el) && !el.matches("input[type=radio], input[type=checkbox]")) continue;
    if (el.getClientRects().length === 0) continue;
    const r = el.getBoundingClientRect();
    if (r.height >= minTarget - 0.5 && r.width >= minTarget - 0.5) continue;
    const parent = el.parentElement;
    const inline = getComputedStyle(el).display.startsWith("inline") && parent && (parent.textContent ?? "").trim().length > (el.textContent ?? "").trim().length + 3;
    targets.push({ w: Math.round(r.width), h: Math.round(r.height), tag: el.tagName.toLowerCase(), name: label(el), where: where(el), inline: Boolean(inline) });
  }
  return { texts, targets };
}

async function measure(page, pick) {
  return page.evaluate(measureInPage, { pick, minText: MIN_TEXT_PX, minTarget: MIN_TARGET_PX });
}

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    const r = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } });
    return r.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, ejemplo: v.nodes[0]?.target }));
  });
}

async function openPage(browser, profile) {
  const ctx = await browser.newContext({ ...profile, locale: "es-ES" });
  const page = await ctx.newPage();
  const errors = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  return { ctx, page, errors };
}

const isSearch = (r) => r.url().endsWith("/api/v1/search") && r.request().method() === "POST";

/** Opens every closed fold of the search card (help, «Más opciones», m²), to measure what hides behind them. */
async function openFolds(page) {
  await page.evaluate(() => {
    const card = [...document.querySelectorAll("section")].find((s) => /^Tu búsqueda$/.test(s.querySelector("h2")?.textContent?.trim() ?? ""));
    card?.querySelectorAll("details:not([open])").forEach((d) => d.setAttribute("open", ""));
  });
  const closed = page.locator("section").filter({ has: page.getByRole("heading", { name: NAMES.search }) }).locator("button[aria-expanded='false']");
  for (let i = await closed.count(); i > 0; i -= 1) await closed.first().click();
}

async function runExample(page, name) {
  const [response] = await Promise.all([page.waitForResponse(isSearch, { timeout: WAIT }), page.getByRole("button", { name }).first().click()]);
  await page.getByRole("heading", { name: NAMES.results }).first().waitFor({ timeout: WAIT });
  await page.waitForTimeout(600);
  return (await response.json()).data;
}

async function shot(page, file) {
  await page.waitForTimeout(700);
  await page.screenshot({ path: join(OUT, file) });
}

/** The sizes of the four screens at one phone width, with axe on each state. */
async function sizes(browser, width) {
  const { ctx, page, errors } = await openPage(browser, phone(width));
  const report = { width, screens: {}, axe: {} };
  report.screens.portada = await measure(page, "portada");
  report.axe.portada = await axe(page);
  report.screens.formulario = await measure(page, "search");
  await openFolds(page);
  report.screens.formulario_abierto = await measure(page, "search");
  report.axe.formulario_abierto = await axe(page);
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  await runExample(page, NAMES.family);
  report.screens.formulario_ejemplo = await measure(page, "search");
  report.screens.lista = await measure(page, "results");
  report.axe.lista = await axe(page);
  const results = page.locator("section").filter({ has: page.getByRole("heading", { name: NAMES.results }) }).first();
  await results.locator("ol li button").first().click();
  await page.locator("aside").filter({ hasText: "Lo que tienes aquí" }).first().waitFor({ timeout: WAIT });
  await page.waitForTimeout(1500);
  report.screens.tarjeta = await measure(page, "card");
  report.axe.tarjeta = await axe(page);
  report.console_errors = errors;
  await ctx.close();
  return report;
}

/** Scrolls an element into view, also inside the bottom sheet's own scroll. */
async function bringIntoView(locator) {
  await locator.evaluate((el) => el.scrollIntoView({ block: "start" }));
}

/** The screenshots of the evidence at one profile (390, 360 or 1440). */
async function screenshots(browser, id, profile) {
  const mobile = profile.isMobile === true;
  const files = [];
  const take = async (page, name) => {
    const file = `${name}-${id}.png`;
    await shot(page, file);
    files.push(file);
  };
  let { ctx, page } = await openPage(browser, profile);
  await take(page, "01-portada");
  const card = page.locator("section").filter({ has: page.getByRole("heading", { name: NAMES.search }) }).first();
  await bringIntoView(card);
  await take(page, "02-formulario");
  const seniors = page.getByRole("button", { name: NAMES.seniors });
  if ((await seniors.count()) > 0) {
    await page.getByRole("button", { name: /^En pareja/ }).click();
    await seniors.click();
    await bringIntoView(page.locator("fieldset").filter({ has: seniors }).first());
    await take(page, "03-somos-mayores");
  }
  await ctx.close();
  ({ ctx, page } = await openPage(browser, profile));
  if ((await page.getByRole("button", { name: NAMES.seniorsExample }).count()) > 0) {
    await runExample(page, NAMES.seniorsExample);
    await bringIntoView(page.getByRole("heading", { name: NAMES.results }).first());
    await take(page, "04-ejemplo-pareja-jubilada");
  }
  await ctx.close();
  ({ ctx, page } = await openPage(browser, profile));
  await runExample(page, NAMES.family);
  await bringIntoView(page.getByRole("heading", { name: NAMES.results }).first());
  await take(page, "05-lista");
  const results = page.locator("section").filter({ has: page.getByRole("heading", { name: NAMES.results }) }).first();
  await results.locator("ol li button").first().click();
  const zone = page.locator("aside").filter({ hasText: "Lo que tienes aquí" }).first();
  await zone.waitFor({ timeout: WAIT });
  await page.waitForTimeout(2500);
  if (mobile) await bringIntoView(zone);
  await take(page, "06-tarjeta");
  await ctx.close();
  ({ ctx, page } = await openPage(browser, profile));
  await page.goto(`${BASE}/como-lo-calculamos`, { waitUntil: "networkidle" });
  // The tie-break and the real example: every «94 %» has a no-break space before its «%»
  await page.getByText(/^A igual %\./).first().evaluate((el) => el.closest("p").scrollIntoView({ block: "start" }));
  await take(page, "07-como-lo-calculamos");
  await ctx.close();
  return files;
}

const browser = await chromium.launch();
const report = { base: BASE, label: opts.label, checked_at: new Date().toISOString(), sizes: [], shots: [] };
try {
  for (const width of opts.widths.split(",").map(Number)) report.sizes.push(await sizes(browser, width));
  if (opts.shots) {
    for (const id of opts.profiles.split(",")) report.shots.push(...(await screenshots(browser, id, id === "1440" ? DESKTOP : phone(Number(id)))));
  }
} finally {
  await browser.close();
}

writeFileSync(join(OUT, `tamanos-${opts.label}.json`), `${JSON.stringify(report, null, 1)}\n`);
const violations = report.sizes.flatMap((s) => Object.entries(s.axe).flatMap(([state, list]) => list.map((v) => `${s.width} px ${state}: ${v.id} (${v.nodes})`)));
for (const s of report.sizes) {
  console.log(`${opts.label} · ${s.width} px`);
  for (const [screen, m] of Object.entries(s.screens)) {
    if (m.error) {
      console.log(`  ${screen.padEnd(19)} ${m.error}`);
      continue;
    }
    const page = (list) => list.filter((x) => x.where === "página");
    const blocks = page(m.targets).filter((t) => !t.inline).length;
    console.log(`  ${screen.padEnd(19)} texto < 16 px: ${page(m.texts).length} · objetivos < 44 px: ${blocks} (+${page(m.targets).filter((t) => t.inline).length} dentro de una frase, +${m.targets.length - page(m.targets).length} del mapa)`);
  }
}
console.log(violations.length ? `axe: ${violations.join(" | ")}` : "axe: 0 incidencias");
console.log(`informe: ${join(OUT, `tamanos-${opts.label}.json`)}`);
process.exit(violations.length ? 1 : 0);
