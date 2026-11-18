// Captures and checks of «Suelo público para vivienda» (D-246) on the zone screen: the line and its
// folded list of parcels in «Vivienda nueva y lo que viene», against the API's own rows; nothing in a
// zone without parcels; texts of 16 px or more, targets of 44 px or more, and axe, at 1440 and 390 px.
//   node capture-portal-suelo.mjs <repoRoot> <webBase> <apiBase> <outDir>
import { writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";

const [repo, base, api, out] = process.argv.slice(2);
const require = createRequire(join(repo, "package.json"));
const { chromium } = require("playwright");
const AXE = require.resolve("axe-core/axe.min.js");

const WAIT = 30_000;
const FEATURE = "suelo_publico_vivienda_m2";
const PROFILES = {
  1440: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
};
const ZONES = [
  { shot: "01-majadahonda", level: "municipio", code: "28080", name: "Majadahonda" },
  { shot: "02-vicalvaro", level: "distrito", code: "2807919", name: "Vicálvaro" },
  { shot: "03-puente-de-vallecas-sin-parcelas", level: "distrito", code: "2807913", name: "Puente de Vallecas" },
];
const report = { web: base, api, checks: [] };
const check = (w, zone, name, ok, detail = "") => report.checks.push({ width: w, zone, name, ok: Boolean(ok), detail: String(detail).slice(0, 300) });
const es = (n) => Math.round(n).toLocaleString("es-ES").replace(/(\d)\s(\d)/g, "$1.$2");

async function apiRow(level, code) {
  const body = await (await fetch(`${api}/api/v1/features/${FEATURE}/values?level=${level}`)).json();
  return body.data.values.find((r) => r.territory_code === code);
}

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    const r = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } });
    return r.violations.map((v) => `${v.id} (${v.nodes.length})`);
  });
}

/** Texts under 16 px and targets (links, buttons, summaries) under 44 px inside `root`, rendered only. */
async function sizes(root) {
  return root.evaluate((el) => {
    const small = [];
    const tiny = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let n = walker.nextNode(); n; n = walker.nextNode()) {
      const parent = n.parentElement;
      if (!n.textContent.trim() || !parent || !parent.checkVisibility() || parent.closest(".visually-hidden")) continue;
      const px = parseFloat(getComputedStyle(parent).fontSize);
      if (px < 16) small.push(`${n.textContent.trim().slice(0, 40)} ${px}px`);
    }
    for (const t of el.querySelectorAll("a[href], button, summary")) {
      const r = t.getBoundingClientRect();
      if (t.checkVisibility() && (r.height < 44 || r.width < 44)) tiny.push(`${t.textContent.trim().slice(0, 30)} ${Math.round(r.width)}x${Math.round(r.height)}`);
    }
    return { small, tiny };
  });
}

/** The card at 1440 px; on a phone, what the sheet shows once `el` is scrolled to its top. */
async function shoot(page, el, w, path) {
  await el.evaluate((node) => node.scrollIntoView({ block: "start" }));
  await page.waitForTimeout(500);
  if (w < 760) await page.screenshot({ path });
  else await el.screenshot({ path });
}

async function zoneScreen(browser, w, zone) {
  const ctx = await browser.newContext({ ...PROFILES[w], locale: "es-ES" });
  const page = await ctx.newPage();
  const label = zone.name;
  await page.goto(`${base}/zona/${zone.level}/${zone.code}`, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  // On a phone the zone screen is a sheet over the map: open it, as a person does
  const sheet = page.getByRole("button", { name: /^(Desliza hacia arriba para ver más|Toca aquí para ver más)$/ });
  if (w < 760 && (await sheet.count())) await sheet.first().click();
  const fold = page.locator("summary").filter({ hasText: "Más datos de la zona" }).first();
  await fold.click();
  const card = page.locator("section[aria-label='Vivienda nueva y lo que viene']").first();
  await card.waitFor({ timeout: WAIT });
  await page.waitForTimeout(2500);
  const row = await apiRow(zone.level, zone.code);
  const items = row?.detail?.items ?? [];
  const text = (await card.innerText()).replace(/\s+/g, " ");
  check(w, label, "never «0 parcelas»", !/\b0 parcelas/.test(text), "");
  if (items.length === 0) {
    check(w, label, "a zone without parcels shows no line", !text.includes("Suelo público para vivienda"), text.slice(0, 200));
    await shoot(page, card, w, join(out, `${zone.shot}-${w}.png`));
  } else {
    const line = `Suelo público para vivienda: ${items.length} parcelas, ${es(row.value)} m² edificables.`;
    check(w, label, `the line says the API's parcels and m² («${line}»)`, text.includes(line), text.slice(0, 300));
    check(w, label, "with its source and date", /Portal del Suelo 4\.0 de la Comunidad de Madrid, en su portal de datos abiertos, a \d+ de [a-z]+ de 2026\./.test(text), "");
    const toggle = card.locator("summary").filter({ hasText: `Ver las ${items.length} parcelas` });
    check(w, label, "the list is folded", (await toggle.count()) === 1 && !(await toggle.evaluate((s) => s.parentElement.open)), "");
    const land = card.locator("li").filter({ hasText: "Suelo público para vivienda" }).first();
    await shoot(page, w < 760 ? land : card, w, join(out, `${zone.shot}-${w}.png`));
    await toggle.click();
    await page.waitForTimeout(500);
    const links = card.locator("a[href^='https://idem.comunidad.madrid/visor/']");
    check(w, label, "one «Ver en el visor de la Comunidad» link per parcel, in a new tab", (await links.count()) === items.length && (await links.first().getAttribute("target")) === "_blank", `${await links.count()} of ${items.length}`);
    const heights = await links.evaluateAll((all) => all.map((l) => l.getBoundingClientRect().height));
    check(w, label, "«Ver en el visor de la Comunidad» in one line of 44 px at least, its icon after the text", heights.every((h) => h >= 43.5 && h < 60), heights.slice(0, 3).map(Math.round).join(", "));
    const regimes = await card.locator("li li").allInnerTexts();
    check(w, label, "a regime only when the Comunidad explains its code", items.every((item, i) => (item.regime ? /En venta|En concesión/.test(regimes[i]) : !/En venta|En concesión/.test(regimes[i]))), "");
    await land.evaluate((el) => el.scrollIntoView({ block: "start" }));
    await page.waitForTimeout(500);
    await page.screenshot({ path: join(out, `${zone.shot}-lista-${w}.png`) });
  }
  const s = await sizes(card);
  check(w, label, "card: no text < 16 px, no target < 44 px", s.small.length === 0 && s.tiny.length === 0, [...s.small, ...s.tiny].join(" | "));
  const colours = await card.evaluate((el) => [...el.querySelectorAll("*")].map((n) => getComputedStyle(n).color).filter((c) => /rgb\((2[0-4]\d|25[0-5]), (\d|[1-9]\d), (\d|[1-9]\d)\)/.test(c)));
  check(w, label, "no alarm (red) colour", colours.length === 0, colours.slice(0, 3).join(" "));
  const violations = await axe(page);
  check(w, label, "axe, zone screen with the context and the list open", violations.length === 0, violations.join(", "));
  // The essential card never says it
  const essential = await page.locator("aside").first().innerText().catch(() => "");
  check(w, label, "not in the essential card", !/Suelo público/.test(essential.split("Más datos de la zona")[0] ?? ""), "");
  await ctx.close();
}

const browser = await chromium.launch();
for (const w of [1440, 390]) for (const zone of ZONES) await zoneScreen(browser, Number(w), zone);
await browser.close();
const failed = report.checks.filter((c) => !c.ok);
report.summary = `${report.checks.length - failed.length}/${report.checks.length}`;
writeFileSync(join(out, "capturas-portal-suelo.json"), `${JSON.stringify(report, null, 2)}\n`);
console.log(report.summary);
for (const c of failed) console.log(`FAIL ${c.width} ${c.zone} · ${c.name}: ${c.detail}`);
process.exit(failed.length ? 1 : 0);
