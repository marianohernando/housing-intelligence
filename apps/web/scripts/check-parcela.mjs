// «Busca tu parcela» (D-250): the UX rules of D-244 and D-245 on its screens, at 360, 390 and
// 1440 px: every text under 16 px and every touch target under 44 px, horizontal overflow and axe
// (WCAG 2.2 AA) on the search (with the address box answering), the sheet of each of the four
// demo parcels with its calculator, and the print view. Only the demo parcels: run it against an
// API started with PARCEL_UPSTREAMS=false, which never calls the Catastro, the Ayuntamiento or
// CartoCiudad. With --shots, the screenshots of the evidence and the sheet saved as PDF.
//
//   node apps/web/scripts/check-parcela.mjs --base http://localhost:3096 --out DIR [--shots]
//
// Exit 1 if axe finds a violation, any text or target is under its floor or the page overflows.
import { mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join, resolve } from "node:path";
import { parseArgs } from "node:util";

import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const AXE = require.resolve("axe-core/axe.min.js");

const { values: opts } = parseArgs({
  options: {
    base: { type: "string", default: "http://localhost:3096" },
    out: { type: "string", default: "." },
    shots: { type: "boolean", default: false },
  },
});
const BASE = opts.base.replace(/\/$/, "");
const OUT = resolve(opts.out);
mkdirSync(OUT, { recursive: true });
const WAIT = 45_000;
// The four demo parcels (apps/web/src/lib/parcels.ts, DEMO_PARCELS) and what each must show
const DEMOS = [
  { rc: "2122202VK4722A", name: "mendez-alvaro", mark: "Dato" },
  { rc: "3959601VK4735H", name: "almeria", mark: "Dato" },
  { rc: "0390314VK4709A", name: "luis-misson", mark: "Sin dato" },
  { rc: "9943003VK3794D", name: "mayor", mark: "Supuesto" },
];
const PROFILES = {
  360: { viewport: { width: 360, height: 780 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  1440: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
};

/** In the page: as check-inversores.mjs, inside [data-investors] (the footer has its own check). */
function measureInPage({ minText, minTarget }) {
  const roots = [...document.querySelectorAll("[data-investors]")];
  const hidden = (el) => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.display === "none" || s.visibility === "hidden" || Number(s.opacity) === 0) return true;
      if (s.clipPath === "inset(50%)" || n.classList.contains("visually-hidden")) return true;
      if (n.parentElement?.tagName === "DETAILS" && !n.parentElement.open && n.tagName !== "SUMMARY") return true;
    }
    return el.getClientRects().length === 0;
  };
  const texts = [];
  const targets = [];
  const seen = new Set();
  for (const root of roots) {
    for (const el of root.querySelectorAll("*")) {
      if (el.closest("svg") || el.closest(".maplibregl-map")) continue;
      const own = [...el.childNodes].filter((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim()).map((n) => n.textContent.trim()).join(" ");
      if (!own || hidden(el)) continue;
      const size = parseFloat(getComputedStyle(el).fontSize);
      if (size < minText - 0.01) texts.push({ px: size, tag: el.tagName.toLowerCase(), text: own.slice(0, 70) });
    }
    for (let el of root.querySelectorAll("a[href], button, select, input:not([type=hidden]), textarea, summary, [role=button]")) {
      if (el.closest(".maplibregl-map")) continue;
      if (el.matches("input[type=checkbox], input[type=radio]") && el.closest("label")) el = el.closest("label");
      if (seen.has(el)) continue;
      seen.add(el);
      if (hidden(el) && !el.matches("input[type=radio], input[type=checkbox]")) continue;
      if (el.getClientRects().length === 0) continue;
      const r = el.getBoundingClientRect();
      if (r.height >= minTarget - 0.5 && r.width >= minTarget - 0.5) continue;
      targets.push({ w: Math.round(r.width), h: Math.round(r.height), tag: el.tagName.toLowerCase(), name: (el.textContent ?? "").trim().slice(0, 60) });
    }
  }
  const overflow = document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;
  return { texts, targets, overflow };
}

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    const result = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } });
    return result.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help, target: v.nodes[0]?.target }));
  });
}

async function check(page, name, report, { shot = false, full = false } = {}) {
  const measured = await page.evaluate(measureInPage, { minText: 16, minTarget: 44 });
  const violations = await axe(page);
  report.push({ name, texts: measured.texts.length, targets: measured.targets.length, overflow: measured.overflow, axe: violations.length, details: { ...measured, violations } });
  if (shot && opts.shots) {
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: join(OUT, `${name}.png`), fullPage: full });
  }
}

const section = (page, id) => page.locator(`section:has(> #${id})`);

async function run() {
  const browser = await chromium.launch();
  const report = [];
  const errors = [];
  for (const [width, profile] of Object.entries(PROFILES)) {
    const ctx = await browser.newContext({ ...profile, locale: "es-ES" });
    const page = await ctx.newPage();
    // The basemap's tiles are not the page's: a tile that fails offline is not a page error
    page.on("console", (m) => m.type() === "error" && !/tiles\.openfreemap|Failed to load resource/.test(m.text()) && errors.push(`${width}: ${m.text()}`));
    page.on("pageerror", (e) => errors.push(`${width}: ${e.message}`));

    // The search: its first screen, then the address box (offline it says the box does not answer)
    await page.goto(`${BASE}/inversores`);
    await page.getByRole("heading", { level: 1, name: "Busca tu parcela" }).waitFor({ timeout: WAIT });
    await page.getByRole("heading", { name: "Explorar barrios" }).waitFor({ timeout: WAIT });
    await check(page, `${width}-buscar`, report, { shot: true });
    await page.getByRole("searchbox", { name: "Calle y número" }).fill("calle de prueba 1");
    await page.getByText(/no responde ahora|portales? coincide|No encontramos/).first().waitFor({ timeout: WAIT });
    await page.getByRole("textbox", { name: "Referencia catastral" }).fill("12345");
    await page.getByRole("button", { name: "Buscar la parcela" }).click();
    await page.getByText("Una referencia catastral tiene 14, 18 o 20 letras y números.").waitFor({ timeout: WAIT });
    await check(page, `${width}-buscar-estados`, report, { shot: width !== "1440" });
    if (opts.shots && width === "1440") {
      await page.locator("section").filter({ has: page.getByRole("heading", { name: "En el mapa" }) }).first().screenshot({ path: join(OUT, "1440-buscar-mapa.png") });
    }

    for (const demo of DEMOS) {
      await page.goto(`${BASE}/inversores/parcela/${demo.rc}`);
      await page.getByRole("heading", { level: 1 }).waitFor({ timeout: WAIT });
      await page.getByRole("heading", { name: "Resultado: tres escenarios" }).waitFor({ timeout: WAIT });
      await page.getByText(/^Lo máximo que se puede pagar por el suelo:|^Ni con el suelo gratis|^Pon la superficie edificable/).first().waitFor({ timeout: WAIT });
      const mark = await section(page, "edificabilidad").getByText(demo.mark, { exact: true }).count();
      if (mark === 0) throw new Error(`${demo.rc}: the buildability is not marked «${demo.mark}»`);
      await check(page, `${width}-ficha-${demo.name}`, report, { shot: width !== "360", full: width === "1440" });
    }

    // The print view of the last sheet (Mayor 61): sources, notices and every breakdown open
    await page.emulateMedia({ media: "print" });
    await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
    await check(page, `${width}-impresion`, report);
    if (opts.shots && width === "1440") {
      await page.pdf({ path: join(OUT, "ficha-parcela-mayor.pdf"), format: "A4", printBackground: true, margin: { top: "12mm", bottom: "12mm", left: "10mm", right: "10mm" } });
    }
    await ctx.close();
  }
  await browser.close();
  writeFileSync(join(OUT, "check-parcela.json"), JSON.stringify({ base: "local", parcels: DEMOS.map((d) => d.rc), report, consoleErrors: errors }, null, 2));
  for (const r of report) console.log(`${r.name}: textos <16px ${r.texts} · objetivos <44px ${r.targets} · desborde ${r.overflow} · axe ${r.axe}`);
  if (errors.length) console.log("errores de consola:", errors);
  const failed = report.some((r) => r.texts || r.targets || r.axe || r.overflow) || errors.length > 0;
  process.exit(failed ? 1 : 0);
}

run().catch((exc) => {
  console.error(exc);
  process.exit(2);
});
