// «Para inversores» (D-248): the UX rules of D-244 and D-245 on its pages, at 390 and 1440 px:
// every text under 16 px and every touch target under 44 px, and axe (WCAG 2.2 AA) on the list, a
// barrio's sheet with its calculator (without and with a land price) and the print view. With
// --shots, the screenshots of the evidence (and the sheet saved as PDF, as «Guardar como PDF»).
//
//   node apps/web/scripts/check-inversores.mjs --base http://localhost:3094 --barrio 28079164 --out DIR [--shots]
//
// Exit 1 if axe finds a violation or any text or target is under its floor.
import { mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join, resolve } from "node:path";
import { parseArgs } from "node:util";

import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const AXE = require.resolve("axe-core/axe.min.js");

const { values: opts } = parseArgs({
  options: {
    base: { type: "string", default: "http://localhost:3094" },
    barrio: { type: "string", default: "28079164" },
    land: { type: "string", default: "2200" },
    out: { type: "string", default: "." },
    shots: { type: "boolean", default: false },
  },
});
const BASE = opts.base.replace(/\/$/, "");
const OUT = resolve(opts.out);
mkdirSync(OUT, { recursive: true });
const WAIT = 30_000;
const PROFILES = {
  390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  1440: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
};

/**
 * In the page: texts under 16 px and targets under 44 px in the investor content ([data-investors]),
 * as check-ux-mobile.mjs counts them; the shared footer (SiteFooter) is measured by that script.
 */
function measureInPage({ minText, minTarget }) {
  const root = document.querySelector("[data-investors]") ?? document.querySelector("main") ?? document.body;
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
  for (const el of root.querySelectorAll("*")) {
    if (el.closest("svg")) continue;
    const own = [...el.childNodes].filter((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim()).map((n) => n.textContent.trim()).join(" ");
    if (!own || hidden(el)) continue;
    const size = parseFloat(getComputedStyle(el).fontSize);
    if (size < minText - 0.01) texts.push({ px: size, tag: el.tagName.toLowerCase(), text: own.slice(0, 70) });
  }
  const targets = [];
  const seen = new Set();
  for (let el of root.querySelectorAll("a[href], button, select, input:not([type=hidden]), textarea, summary, [role=button]")) {
    if (el.matches("input[type=checkbox], input[type=radio]") && el.closest("label")) el = el.closest("label");
    if (seen.has(el)) continue;
    seen.add(el);
    if (hidden(el) && !el.matches("input[type=radio], input[type=checkbox]")) continue;
    if (el.getClientRects().length === 0) continue;
    const r = el.getBoundingClientRect();
    if (r.height >= minTarget - 0.5 && r.width >= minTarget - 0.5) continue;
    targets.push({ w: Math.round(r.width), h: Math.round(r.height), tag: el.tagName.toLowerCase(), name: (el.textContent ?? "").trim().slice(0, 60) });
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

/** The whole page on the desktop; on a phone, what the first screen shows (a whole page is metres long). */
async function check(page, name, report, shot) {
  const measured = await page.evaluate(measureInPage, { minText: 16, minTarget: 44 });
  const violations = await axe(page);
  report.push({ name, texts: measured.texts.length, targets: measured.targets.length, overflow: measured.overflow, axe: violations.length, details: { ...measured, violations } });
  if (shot && opts.shots) {
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: join(OUT, `${name}.png`), fullPage: name.startsWith("1440") });
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
    page.on("console", (m) => m.type() === "error" && errors.push(`${width}: ${m.text()}`));

    await page.goto(`${BASE}/inversores`);
    await page.getByRole("heading", { name: "Explorar barrios" }).waitFor({ timeout: WAIT });
    await page.getByRole("link").filter({ hasText: /Pinar del Rey/ }).first().waitFor({ timeout: WAIT });
    await check(page, `${width}-lista`, report, true);

    await page.goto(`${BASE}/inversores/${opts.barrio}`);
    await page.getByRole("heading", { level: 1 }).waitFor({ timeout: WAIT });
    await page.getByRole("heading", { name: "Resultado: tres escenarios" }).waitFor({ timeout: WAIT });
    // Without a land price there is no verdict: the residual land value of each scenario
    await page.getByText(/^Lo máximo que se puede pagar por el suelo, antes de/).first().waitFor({ timeout: WAIT });
    if ((await page.getByText(/^(Sale|Ajustar|No sale)$/).count()) > 0) throw new Error("a verdict without a land price");
    await check(page, `${width}-ficha`, report, true);
    if (opts.shots) {
      await section(page, "suelo").screenshot({ path: join(OUT, `${width}-ficha-suelo.png`) });
      await section(page, "resultado").screenshot({ path: join(OUT, `${width}-escenarios-sin-suelo.png`) });
      if (width === "1440") await section(page, "viabilidad").screenshot({ path: join(OUT, "1440-calculadora.png") });
    }

    // A land price: the margin and its verdict
    await page.getByLabel("Precio del suelo (opcional)").fill("");
    await page.getByLabel("El precio del suelo es").selectOption("m2");
    await page.getByLabel("Precio del suelo (opcional)").fill(opts.land);
    await page.getByText(/^Margen sobre ventas$/).first().waitFor({ timeout: WAIT });
    await page.getByText(/^(Sale|Ajustar|No sale)$/).first().waitFor({ timeout: WAIT });
    await page.waitForTimeout(300);
    await check(page, `${width}-calculadora-con-suelo`, report, false);
    if (opts.shots) await section(page, "resultado").screenshot({ path: join(OUT, `${width}-escenarios-con-suelo.png`) });

    await page.emulateMedia({ media: "print" });
    await page.evaluate(() => window.dispatchEvent(new Event("beforeprint")));
    await check(page, `${width}-impresion`, report, true);
    if (opts.shots && width === "1440") {
      await page.pdf({ path: join(OUT, "ficha-inversores.pdf"), format: "A4", printBackground: true, margin: { top: "12mm", bottom: "12mm", left: "10mm", right: "10mm" } });
    }
    await ctx.close();
  }
  await browser.close();
  writeFileSync(join(OUT, "check-inversores.json"), JSON.stringify({ base: "local", barrio: opts.barrio, report, consoleErrors: errors }, null, 2));
  for (const r of report) console.log(`${r.name}: textos <16px ${r.texts} · objetivos <44px ${r.targets} · desborde ${r.overflow} · axe ${r.axe}`);
  if (errors.length) console.log("errores de consola:", errors);
  const failed = report.some((r) => r.texts || r.targets || r.axe || r.overflow) || errors.length > 0;
  process.exit(failed ? 1 : 0);
}

run().catch((exc) => {
  console.error(exc);
  process.exit(2);
});
