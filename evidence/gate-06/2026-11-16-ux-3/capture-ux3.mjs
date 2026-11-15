// Captures and checks of what the PR changes (UX mobile 3): the household's words in «Casi valen», the
// near miss's card and «¿Queréis ver más zonas?», and the barrio panel (with and without outline).
//   node capture-ux3.mjs <repoRoot> <base> <outDir>
import { createRequire } from "node:module";
import { join } from "node:path";

const [repo, base, out] = process.argv.slice(2);
const require = createRequire(join(repo, "package.json"));
const { chromium } = require("playwright");
const AXE = require.resolve("axe-core/axe.min.js");

const WAIT = 30_000;
const PROFILES = {
  390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  1440: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
};
const isSearch = (r) => r.url().endsWith("/api/v1/search") && r.request().method() === "POST";
const report = { base, checks: [] };
const check = (w, name, ok, detail = "") => report.checks.push({ width: w, name, ok: Boolean(ok), detail: String(detail).slice(0, 300) });

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    const r = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } });
    return r.violations.map((v) => `${v.id} (${v.nodes.length})`);
  });
}

/** Texts under 16 px and buttons under 44 px inside the elements matched by `selector` (rendered only). */
async function sizes(page, selector) {
  return page.evaluate((sel) => {
    const small = [];
    const tiny = [];
    for (const root of document.querySelectorAll(sel)) {
      const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      for (let n = walker.nextNode(); n; n = walker.nextNode()) {
        const el = n.parentElement;
        if (!n.textContent.trim() || !el || !el.checkVisibility() || el.closest(".visually-hidden")) continue;
        const px = parseFloat(getComputedStyle(el).fontSize);
        if (px < 16) small.push(`${n.textContent.trim().slice(0, 40)} ${px}px`);
      }
      for (const b of root.querySelectorAll("button")) {
        const r = b.getBoundingClientRect();
        if (b.checkVisibility() && (r.height < 44 || r.width < 44)) tiny.push(`${b.textContent.trim().slice(0, 30)} ${r.width}x${r.height}`);
      }
    }
    return { small, tiny };
  }, selector);
}

async function into(page, locator) {
  await locator.evaluate((el) => el.scrollIntoView({ block: "start" }));
  await page.waitForTimeout(600);
}

async function open(browser, w, block = false) {
  const ctx = await browser.newContext({ ...PROFILES[w], locale: "es-ES" });
  const page = await ctx.newPage();
  if (block) await page.route(/level=barrio/, (route) => route.abort());
  await page.goto(`${base}/`, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  return { ctx, page };
}

async function family(page) {
  const [response] = await Promise.all([page.waitForResponse(isSearch, { timeout: WAIT }), page.getByRole("button", { name: /pareja con 2 hijos/ }).first().click()]);
  await page.getByRole("heading", { name: "Zonas que os convienen" }).first().waitFor({ timeout: WAIT });
  await page.waitForTimeout(1500);
  return (await response.json()).data;
}

const results = (page) => page.getByRole("region", { name: "Zonas que os convienen" });

async function listAndCard(browser, w) {
  const { ctx, page } = await open(browser, w);
  const data = await family(page);
  // «Casi valen» unfolded: what each lacks, in the couple's words
  const toggle = results(page).getByRole("button", { name: /^Casi valen/ });
  await toggle.click();
  await into(page, toggle);
  const near = results(page).locator("ul > li > button");
  const lines = [];
  for (let i = 0; i < (await near.count()); i += 1) lines.push((await near.nth(i).locator("span[aria-hidden='true']").first().innerText()).trim());
  check(w, "«Casi valen» says «vuestro presupuesto» or «pedís»", lines.length > 0 && lines.every((l) => /vuestro presupuesto|pedís|^No cumple: /.test(l)), lines.join(" | "));
  await page.screenshot({ path: join(out, `01-casi-valen-${w}.png`) });
  if (w === 1440) {
    const legend = (await page.locator("section[aria-label='Leyenda del mapa']").first().innerText()).replace(/\s+/g, " ");
    check(w, "legend: «Zonas que os convienen», «Os conviene menos», «Os conviene más»", ["Zonas que os convienen", "Os conviene menos", "Os conviene más"].every((t) => legend.includes(t)), legend.slice(0, 120));
  }
  // «¿Queréis ver más zonas?»
  const changes = page.getByRole("region", { name: "¿Queréis ver más zonas?", exact: true });
  await changes.getByRole("button", { name: /^Ver todas las opciones/ }).click().catch(() => {});
  await into(page, changes);
  const rcText = (await changes.innerText()).replace(/\s+/g, " ");
  check(w, "«¿Queréis ver más zonas?» with «Mirad… cambiáis», «vuestra búsqueda» and «No os decimos que gastéis…»",
    /Mirad cuántas salen si cambiáis una sola cosa/.test(rcText) && /No os decimos que gastéis más: os enseñamos/.test(rcText), rcText.slice(0, 300));
  await page.screenshot({ path: join(out, `02-quereis-ver-mas-zonas-${w}.png`) });
  // The card of the first near miss: what it fails, in their words
  await into(page, toggle);
  await near.first().click();
  const card = page.locator("aside").filter({ has: page.getByRole("button", { name: "Volver a la lista" }) }).first();
  await card.getByRole("heading", { name: data.near_misses[0].zone.name, exact: true }).waitFor({ timeout: WAIT });
  await page.waitForTimeout(2500);
  const cardText = (await card.innerText()).replace(/\s+/g, " ");
  check(w, "card of a near miss: «… de vuestro presupuesto» / «pedís»", /vuestro presupuesto|pedís/.test(cardText) && !/tu presupuesto|lo que pides/.test(cardText), cardText.slice(0, 200));
  await into(page, card);
  await page.screenshot({ path: join(out, `03-tarjeta-casi-valen-${w}.png`) });
  const more = card.locator("summary").filter({ hasText: /^Ver más sobre/ }).first();
  await more.click();
  await page.waitForTimeout(600);
  const opened = (await card.innerText()).replace(/\s+/g, " ");
  check(w, "card «Ver más»: no «tú» about the search", !/tu presupuesto|lo que pides|Lo que tienes aquí|Fuera de tu búsqueda/.test(opened), opened.slice(0, 200));
  const violations = await axe(page);
  check(w, "axe, card of a near miss with «Ver más»", violations.length === 0, violations.join(", "));
  const s = await sizes(page, "aside");
  check(w, "card: no text < 16 px, no button < 44 px", s.small.length === 0 && s.tiny.length === 0, [...s.small, ...s.tiny].join(" | "));
  await ctx.close();
}

/** The district of the family's first zone, with its barrios; `block`: the barrios' outlines fail. */
async function district(browser, w, block) {
  const { ctx, page } = await open(browser, w, block);
  const data = await family(page);
  await results(page).locator("ol > li > button").first().click();
  const card = page.locator("aside").filter({ has: page.getByRole("button", { name: "Volver a la lista" }) }).first();
  await card.getByRole("heading", { name: data.results[0].zone.name, exact: true }).waitFor({ timeout: WAIT });
  await card.locator("summary").filter({ hasText: /^Ver más sobre/ }).first().click();
  await card.getByRole("link", { name: /^Ver (la zona|el distrito)/ }).click();
  const title = page.getByRole("heading", { name: "Los barrios que más os convienen" }).first();
  await title.waitFor({ timeout: WAIT });
  await page.waitForTimeout(2500);
  const section = page.locator("section").filter({ has: title }).first();
  const rows = section.locator("ol > li button");
  const first = rows.first();
  const name = block ? "sin contorno" : "con contorno";
  if (block) {
    const expanded = await rows.evaluateAll((bs) => bs.map((b) => b.getAttribute("aria-expanded")));
    check(w, "barrios without outline: rows are buttons, all folded (aria-expanded=false)", expanded.length > 0 && expanded.every((e) => e === "false"), expanded.join(","));
    const panels = await section.locator("ol [id] span").count();
    check(w, "barrios without outline: no panel open at first", panels === 0, `${panels}`);
    await into(page, title);
    await page.screenshot({ path: join(out, `05-barrios-sin-contorno-plegados-${w}.png`) });
  }
  const rowLines = (await first.innerText()).split("\n").map((l) => l.replace(/\s+/g, " ").trim()).filter(Boolean);
  const rowText = rowLines.join(" / ");
  const rowBand = rowLines.find((l) => /opción|Poco recomendable/.test(l))?.replace(/ · \d+ %$/, "") ?? null;
  const rowPrice = rowLines.find((l) => l.startsWith("Unos ")) ?? null;
  await first.click();
  await page.waitForTimeout(1200);
  const panel = section.locator("ol > li").first().locator(":scope > div > span[id]");
  await panel.waitFor({ timeout: WAIT });
  const panelText = (await panel.innerText()).replace(/\s+/g, " ").trim();
  check(w, `barrio panel (${name}): no band or price of the row again`, rowBand !== null && rowPrice !== null && !panelText.includes(rowBand) && !panelText.includes(rowPrice), `fila: ${rowText} || panel: ${panelText}`);
  check(w, `barrio panel (${name}): the % only on the phone`, w === 390 ? /\d+\s*%/.test(panelText) : !/^\d+\s*%/.test(panelText), panelText.slice(0, 120));
  check(w, `barrio panel (${name}): what the price is for`, /Para un piso de unos \d+\s*m²/.test(panelText), panelText.slice(0, 160));
  if (block) {
    const state = await first.getAttribute("aria-expanded");
    check(w, "barrio without outline: opens with aria-expanded=true", state === "true", state);
  }
  await into(page, title);
  await page.screenshot({ path: join(out, `${block ? "05b-barrio-sin-contorno-abierto" : "04-barrio-panel"}-${w}.png`) });
  const violations = await axe(page);
  check(w, `axe, district with a barrio panel open (${name})`, violations.length === 0, violations.join(", "));
  const s = await sizes(page, "section");
  check(w, `barrios (${name}): no text < 16 px, no button < 44 px`, s.small.length === 0 && s.tiny.length === 0, [...s.small, ...s.tiny].join(" | "));
  await ctx.close();
}

const browser = await chromium.launch();
try {
  for (const w of [390, 1440]) {
    await listAndCard(browser, w);
    await district(browser, w, false);
    await district(browser, w, true);
  }
} finally {
  await browser.close();
}
const failed = report.checks.filter((c) => !c.ok);
for (const c of report.checks) console.log(`${c.ok ? "ok  " : "FAIL"} ${c.width} ${c.name}${c.ok ? "" : ` :: ${c.detail}`}`);
const { writeFileSync } = await import("node:fs");
writeFileSync(join(out, "capturas-ux3.json"), `${JSON.stringify(report, null, 1)}\n`);
process.exit(failed.length ? 1 : 0);
