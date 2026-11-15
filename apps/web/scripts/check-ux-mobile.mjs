// Mobile clarity check (UX mobile audit, prompts/UX_AUDITORIA_MOVIL.md §3 C1, C2 and M1): on the
// screens of the journey (portada, formulario, lista, tarjeta, distrito) it lists every text under
// 16 px and every touch target under 44 px at a phone width and runs axe (WCAG 2.2 AA) on each state;
// it counts the things a person sees per row of the list and in the zone card (second delivery,
// --counts) and, with --shots, takes the screenshots of the evidence at 390, 360 and 1440 px.
//
//   node apps/web/scripts/check-ux-mobile.mjs --base http://localhost:3061 --out DIR --label despues [--shots]
//
// The names of the screens are matched by the texts before and after each delivery of the audit, so
// the same script measures both. Exit 1 if axe finds any violation.
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
    // Things per row and in the zone card (second delivery), at these profiles; empty: none
    counts: { type: "string", default: "390,360,1440" },
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
    card: () => [...document.querySelectorAll("aside")].find((a) => a.querySelector("h2") && /Lo que tienes aquí|Ver más sobre/.test(a.textContent)) ?? null,
    // The zone screen (second delivery): its intro, the card, the barrios and «Más datos de la zona»
    zone: () => document.querySelector("main") ?? document.body,
    method: () => document.querySelector("main") ?? document.body,
    // The rows of «Qué falta» (No comparable): what the person reads there, without the shared footer
    gaps: () => document.querySelector("ul[class*='rows']") ?? null,
    // A district's screen after a search: «Los barrios que más te convienen» (review R-04 of PR #79)
    district: () => [...document.querySelectorAll("section")].find((s) => /^Los barrios que (más te convienen|mejor encajan)$/.test(s.querySelector("h2")?.textContent?.trim() ?? "")) ?? null,
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
      // Folded in a closed <details> (its summary shows): Chrome keeps a box for it, nobody sees it
      if (n.parentElement?.tagName === "DETAILS" && !n.parentElement.open && n.tagName !== "SUMMARY") return true;
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

/**
 * In the page: how many things a person sees (second delivery, «muchos datos juntos»). A thing is
 * a visible element with its own text (a name, a band, a figure, a label) or a control without
 * text of its own (an icon button); what is only for screen readers, folded or off the area does
 * not count. `rows`: each of the first rows of the list. `card`: the zone card, in its first
 * screen (what is in view once the card is brought up, inside the bottom sheet on a phone) and whole.
 */
function countInPage({ rows: rowCount }) {
  const hidden = (el) => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.display === "none" || s.visibility === "hidden" || Number(s.opacity) === 0) return true;
      if (s.clipPath === "inset(50%)" || n.classList.contains("visually-hidden")) return true;
      if (n.parentElement?.tagName === "DETAILS" && !n.parentElement.open && n.tagName !== "SUMMARY") return true;
    }
    return el.getClientRects().length === 0;
  };
  const ownText = (el) => [...el.childNodes].some((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim());
  const things = (root, inArea = () => true) => {
    const texts = [...root.querySelectorAll("*")].filter((el) => !el.closest("svg") && ownText(el) && !hidden(el) && inArea(el));
    const controls = [...root.querySelectorAll("a[href], button, summary, select, input")].filter(
      (c) => !hidden(c) && inArea(c) && !texts.some((t) => c === t || c.contains(t)),
    );
    return { n: texts.length + controls.length, items: [...texts.map((t) => t.textContent.replace(/\s+/g, " ").trim().slice(0, 50)), ...controls.map((c) => `[${c.tagName.toLowerCase()}]`)] };
  };
  const list = document.querySelector("h2[tabindex='-1']")?.closest("section")?.querySelector("ol");
  const rows = list ? [...list.querySelectorAll(":scope > li")].slice(0, rowCount).map((li) => things(li)) : [];
  const card = [...document.querySelectorAll("aside")].find((a) => a.querySelector("h2") && /Lo que tienes aquí|Ver más sobre/.test(a.textContent)) ?? null;
  if (!card) return { rows, card: null };
  // The area in view: the screen, and on a phone the scrolling content of the bottom sheet
  let clip = { top: 0, bottom: window.innerHeight };
  for (let n = card.parentElement; n; n = n.parentElement) {
    const s = getComputedStyle(n);
    if (/(auto|scroll)/.test(s.overflowY) && n.scrollHeight > n.clientHeight) {
      const r = n.getBoundingClientRect();
      clip = { top: Math.max(clip.top, r.top), bottom: Math.min(clip.bottom, r.bottom) };
      break;
    }
  }
  const inView = (el) => {
    const r = el.getBoundingClientRect();
    return r.bottom > clip.top + 1 && r.top < clip.bottom - 1;
  };
  return { rows, card: { firstScreen: things(card, inView), whole: things(card) } };
}

/** The zone card of the overview, before and after the second delivery («Ver más sobre…»). */
const zoneCard = (page) => page.locator("aside").filter({ has: page.getByRole("heading", { level: 2 }) }).filter({ hasText: /Lo que tienes aquí|Ver más sobre/ }).first();

/** The «Ver más sobre…» of the card, when it has one (second delivery), opened. */
async function openMore(page) {
  const more = page.locator("aside summary").filter({ hasText: /^Ver más sobre/ }).first();
  if ((await more.count()) === 0) return false;
  await more.click();
  await page.waitForTimeout(400);
  return true;
}

/** Things per row of the list and in the zone card of each example, at one profile. */
async function counts(browser, id, profile) {
  const out = { profile: id };
  for (const [example, name] of [
    ["familia", NAMES.family],
    ["pareja_jubilada", NAMES.seniorsExample],
  ]) {
    const { ctx, page } = await openPage(browser, profile);
    if ((await page.getByRole("button", { name }).count()) === 0) {
      await ctx.close();
      continue;
    }
    await runExample(page, name);
    const heading = page.getByRole("heading", { name: NAMES.results }).first();
    await bringIntoView(heading);
    const listed = await page.evaluate(countInPage, { rows: 5 });
    const results = page.locator("section").filter({ has: heading }).first();
    await results.locator("ol li button").first().click();
    const card = zoneCard(page);
    await card.waitFor({ timeout: WAIT });
    await page.waitForTimeout(2500);
    if (profile.isMobile) await bringIntoView(card);
    await page.waitForTimeout(500);
    const closed = await page.evaluate(countInPage, { rows: 0 });
    const opened = (await openMore(page)) ? (await page.evaluate(countInPage, { rows: 0 })).card.whole : null;
    out[example] = {
      rows: listed.rows.map((r) => r.n),
      row_items: listed.rows[0]?.items ?? [],
      card_first_screen: closed.card?.firstScreen.n ?? null,
      card_first_screen_items: closed.card?.firstScreen.items ?? [],
      card_whole: closed.card?.whole.n ?? null,
      card_whole_with_more: opened?.n ?? null,
    };
    await ctx.close();
  }
  return out;
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
  await zoneCard(page).waitFor({ timeout: WAIT });
  await page.waitForTimeout(1500);
  report.screens.tarjeta = await measure(page, "card");
  report.axe.tarjeta = await axe(page);
  // Everything behind «Ver más sobre…» (second delivery), measured and checked too
  if (await openMore(page)) {
    report.screens.tarjeta_ver_mas = await measure(page, "card");
    report.axe.tarjeta_ver_mas = await axe(page);
  }
  // «Ver la zona» of that card: a district of Madrid, with its barrios for the same search
  await openDistrict(page);
  report.screens.distrito = await measure(page, "district");
  report.screens.pantalla_zona = await measure(page, "zone");
  report.axe.distrito = await axe(page);
  // «No comparable» in «Qué falta» (Barajas, its health centre: debt of the first delivery)
  await page.goto(`${BASE}${NOT_COMPARABLE_PATH}`, { waitUntil: "networkidle" });
  await page.getByText(/^Para la gente que vive aquí/).first().waitFor({ timeout: WAIT });
  report.screens.no_comparable = await measure(page, "gaps");
  report.axe.no_comparable = await axe(page);
  report.console_errors = errors;
  await ctx.close();
  if ((await sizesOlder(browser, width, report)) === false) report.screens.formulario_mayores = { error: "no «Somos mayores»" };
  return report;
}

/**
 * «Somos mayores» with a place picked (review H6 of PR #79): «En pareja», «Somos mayores» and the
 * Ciudad Lineal metro station in «¿Dónde vivís ahora?», so the minutes selector and «Quitar» show.
 */
async function olderWithPlace(page) {
  await page.getByRole("button", { name: /^En pareja/ }).click();
  await page.getByRole("button", { name: NAMES.seniors }).click();
  const field = page.getByRole("combobox", { name: /^¿Dónde vivís ahora\?/ });
  await field.click();
  await field.fill("Ciudad Lineal");
  await page.getByRole("option", { name: /^Ciudad Lineal \(metro\)/ }).first().click({ timeout: WAIT });
  await page.getByRole("button", { name: /^Quitar este lugar/ }).first().waitFor({ timeout: WAIT });
}

/** «Qué falta» of Barajas, whose health centre is «No comparable» (D-230), for its new words. */
const NOT_COMPARABLE_PATH = "/que-falta?zona=distrito/2807921";

/** From the zone card to the district's screen (behind «Ver más» since the second delivery), once its barrios for the search are on it. */
async function openDistrict(page) {
  const card = zoneCard(page);
  const more = card.locator("summary").filter({ hasText: /^Ver más sobre/ }).first();
  if ((await more.count()) > 0 && !(await more.evaluate((s) => s.parentElement.open))) await more.click();
  await card.getByRole("link", { name: /^Ver (la zona|el distrito)/ }).click();
  await page.getByRole("heading", { name: /^Los barrios que (más te convienen|mejor encajan)$/ }).first().waitFor({ timeout: WAIT });
  await page.waitForTimeout(1500);
}

/** The search card of «Somos mayores» with a place picked, measured and checked with axe. */
async function sizesOlder(browser, width, report) {
  const { ctx, page, errors } = await openPage(browser, phone(width));
  if ((await page.getByRole("button", { name: NAMES.seniors }).count()) === 0) {
    await ctx.close();
    return false;
  }
  await olderWithPlace(page);
  report.screens.formulario_mayores = await measure(page, "search");
  report.axe.formulario_mayores = await axe(page);
  report.console_errors.push(...errors);
  await ctx.close();
  return true;
}

/** Scrolls an element into view, also inside the bottom sheet's own scroll. */
async function bringIntoView(locator) {
  await locator.evaluate((el) => el.scrollIntoView({ block: "start" }));
}

/** The card of the first row of the list, once its «Qué falta» is in. */
async function openFirstCard(page) {
  const list = page.locator("section").filter({ has: page.getByRole("heading", { name: NAMES.results }) }).first();
  await list.locator("ol li button").first().click();
  const card = zoneCard(page);
  await card.waitFor({ timeout: WAIT });
  await page.waitForTimeout(2500);
  return card;
}

/**
 * The screenshots of the evidence at one profile (390, 360 or 1440), second delivery: the lists of
 * both examples, the card closed and with «Ver más» open, the zone screen folded, the district's
 * barrios and «No comparable».
 */
async function screenshots(browser, id, profile) {
  const mobile = profile.isMobile === true;
  const files = [];
  const take = async (page, name) => {
    const file = `${name}-${id}.png`;
    await shot(page, file);
    files.push(file);
  };
  let { ctx, page } = await openPage(browser, profile);
  if ((await page.getByRole("button", { name: NAMES.seniorsExample }).count()) > 0) {
    await runExample(page, NAMES.seniorsExample);
    await bringIntoView(page.getByRole("heading", { name: NAMES.results }).first());
    await take(page, "01-lista-pareja-jubilada");
    const card = await openFirstCard(page);
    if (mobile) await bringIntoView(card);
    await take(page, "02-tarjeta-pareja-jubilada");
  }
  await ctx.close();
  ({ ctx, page } = await openPage(browser, profile));
  await runExample(page, NAMES.family);
  await bringIntoView(page.getByRole("heading", { name: NAMES.results }).first());
  await take(page, "03-lista-familia");
  const card = await openFirstCard(page);
  if (mobile) await bringIntoView(card);
  await take(page, "04-tarjeta-familia");
  if (await openMore(page)) {
    await bringIntoView(card.locator("summary").filter({ hasText: /^Ver más sobre/ }).first());
    await take(page, "05-tarjeta-ver-mas");
  }
  await openDistrict(page);
  await page.evaluate(() => window.scrollTo(0, 0));
  await bringIntoView(page.getByRole("navigation", { name: "Estás en" }).first());
  await take(page, "06-pantalla-zona");
  const fold = page.locator("summary").filter({ hasText: "Más datos de la zona" }).first();
  if ((await fold.count()) > 0) {
    await fold.evaluate((el) => el.scrollIntoView({ block: "center" }));
    await take(page, "06b-pantalla-zona-plegada");
  }
  await bringIntoView(page.getByRole("heading", { name: /^Los barrios que (más te convienen|mejor encajan)$/ }).first());
  await take(page, "07-distrito-barrios");
  await ctx.close();
  ({ ctx, page } = await openPage(browser, profile));
  await page.goto(`${BASE}${NOT_COMPARABLE_PATH}`, { waitUntil: "networkidle" });
  const reason = page.locator("li").filter({ has: page.getByRole("heading", { name: "Centros de salud", exact: true }) }).first();
  await reason.waitFor({ timeout: WAIT });
  await bringIntoView(reason);
  await take(page, "08-no-comparable");
  await ctx.close();
  return files;
}

const browser = await chromium.launch();
const report = { base: BASE, label: opts.label, checked_at: new Date().toISOString(), sizes: [], counts: [], shots: [] };
const profileOf = (id) => (id === "1440" ? DESKTOP : phone(Number(id)));
try {
  for (const width of opts.widths.split(",").filter(Boolean).map(Number)) report.sizes.push(await sizes(browser, width));
  for (const id of opts.counts.split(",").filter(Boolean)) report.counts.push(await counts(browser, id, profileOf(id)));
  if (opts.shots) {
    for (const id of opts.profiles.split(",")) report.shots.push(...(await screenshots(browser, id, profileOf(id))));
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
for (const c of report.counts) {
  for (const [example, n] of Object.entries(c)) {
    if (example === "profile") continue;
    console.log(`${opts.label} · ${c.profile} · ${example}: filas ${n.rows.join(", ")} · tarjeta, primera pantalla ${n.card_first_screen} · entera ${n.card_whole}${n.card_whole_with_more === null ? "" : ` · con «Ver más» ${n.card_whole_with_more}`}`);
  }
}
console.log(violations.length ? `axe: ${violations.join(" | ")}` : "axe: 0 incidencias");
console.log(`informe: ${join(OUT, `tamanos-${opts.label}.json`)}`);
process.exit(violations.length ? 1 : 0);
