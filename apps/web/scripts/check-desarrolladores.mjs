// «Para desarrolladores» (D-249): the UX rules of D-244 and D-245 on /desarrolladores at 360, 390
// and 1440 px: every text under 16 px (the page and its footer) and every touch target under 44 px
// (the page and the footer's own links, /inversores and /desarrolladores; the footer's citations
// of each licence are shared by every page and counted apart, as check-inversores.mjs leaves the
// footer to check-ux-mobile.mjs), horizontal overflow (the code wraps inside its own box, never
// the page) and axe (WCAG 2.2 AA), before and after copying an example. With --shots, the
// screenshots of the evidence.
//
//   node apps/web/scripts/check-desarrolladores.mjs --base http://localhost:3095 --out DIR [--shots]
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
    base: { type: "string", default: "http://localhost:3095" },
    out: { type: "string", default: "." },
    shots: { type: "boolean", default: false },
  },
});
const BASE = opts.base.replace(/\/$/, "");
const OUT = resolve(opts.out);
mkdirSync(OUT, { recursive: true });
const WAIT = 30_000;
const PHONE = { deviceScaleFactor: 2, isMobile: true, hasTouch: true };
const PROFILES = {
  360: { viewport: { width: 360, height: 780 }, ...PHONE },
  390: { viewport: { width: 390, height: 844 }, ...PHONE },
  1440: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
};

/** In the page: texts under 16 px and targets under 44 px in <main> (the page and its footer). */
function measureInPage({ minText, minTarget }) {
  const root = document.querySelector("main") ?? document.body;
  const hidden = (el) => {
    for (let n = el; n && n !== document.body; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (s.display === "none" || s.visibility === "hidden" || Number(s.opacity) === 0) return true;
      if (s.clipPath === "inset(50%)" || n.classList.contains("visually-hidden")) return true;
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
  for (const el of root.querySelectorAll("a[href], button, select, input:not([type=hidden]), textarea, summary, [role=button]")) {
    if (hidden(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.height >= minTarget - 0.5 && r.width >= minTarget - 0.5) continue;
    const parent = el.parentElement;
    const inline = getComputedStyle(el).display.startsWith("inline") && parent && (parent.textContent ?? "").trim().length > (el.textContent ?? "").trim().length + 3;
    targets.push({ w: Math.round(r.width), h: Math.round(r.height), tag: el.tagName.toLowerCase(), name: (el.textContent ?? "").trim().slice(0, 60), inline: Boolean(inline), ours: Boolean(el.closest("[data-developers]") || el.matches('footer a[href^="/"]')) });
  }
  const overflow = document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;
  const wider = [...root.querySelectorAll("pre, code, a")].filter((el) => el.getBoundingClientRect().right > document.documentElement.clientWidth + 1).map((el) => el.textContent.slice(0, 50));
  return { texts, targets, overflow, wider };
}

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    const result = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } });
    return result.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length, help: v.help, target: v.nodes[0]?.target }));
  });
}

async function check(page, name, report) {
  const measured = await page.evaluate(measureInPage, { minText: 16, minTarget: 44 });
  const violations = await axe(page);
  const ours = measured.targets.filter((t) => t.ours);
  report.push({ name, texts: measured.texts.length, targets: ours.length, footerCitations: measured.targets.length - ours.length, overflow: measured.overflow, axe: violations.length, details: { ...measured, violations } });
}

const section = (page, id) => page.locator(`section:has(> h2#${id})`);

async function run() {
  const browser = await chromium.launch();
  const report = [];
  const errors = [];
  for (const [width, profile] of Object.entries(PROFILES)) {
    const ctx = await browser.newContext({ ...profile, locale: "es-ES" });
    await ctx.grantPermissions(["clipboard-read", "clipboard-write"], { origin: BASE });
    const page = await ctx.newPage();
    page.on("console", (m) => m.type() === "error" && errors.push(`${width}: ${m.text()}`));
    page.on("pageerror", (e) => errors.push(`${width}: ${e.message}`));

    await page.goto(`${BASE}/desarrolladores`);
    await page.getByRole("heading", { level: 1, name: "API y MCP para desarrolladores" }).waitFor({ timeout: WAIT });
    await page.locator("footer").getByText(/^Datos: \d+ conjuntos/).waitFor({ timeout: WAIT });
    await check(page, `${width}-desarrolladores`, report);
    if (opts.shots) {
      await page.screenshot({ path: join(OUT, `${width}-desarrolladores.png`), fullPage: width === "1440" });
      await section(page, "funciona-hoy").locator("article").first().screenshot({ path: join(OUT, `${width}-ejemplo-search.png`) });
      await section(page, "mcp").screenshot({ path: join(OUT, `${width}-mcp.png`) });
      await section(page, "planteado").screenshot({ path: join(OUT, `${width}-planteado.png`) });
    }

    // Copy an example: the button says it, and the text in the clipboard is the command
    const example = section(page, "funciona-hoy").locator("figure").first();
    await example.getByRole("button", { name: /^Copiar/ }).click();
    await example.getByRole("status").getByText("Copiado").waitFor({ timeout: WAIT });
    const copied = await page.evaluate(() => navigator.clipboard.readText());
    const shown = await example.locator("pre").innerText();
    if (copied.trim() !== shown.trim()) errors.push(`${width}: the clipboard is not the example shown`);
    await check(page, `${width}-copiado`, report);
    if (opts.shots && width === "390") await example.screenshot({ path: join(OUT, "390-copiado.png") });
    await ctx.close();
  }
  await browser.close();
  writeFileSync(join(OUT, "check-desarrolladores.json"), JSON.stringify({ base: "local", report, consoleErrors: errors }, null, 2));
  for (const r of report) console.log(`${r.name}: textos <16px ${r.texts} · objetivos <44px ${r.targets} (+${r.footerCitations} citas del pie, compartidas) · desborde ${r.overflow} · axe ${r.axe}`);
  if (errors.length) console.log("errores:", errors);
  const failed = report.some((r) => r.texts || r.targets || r.axe || r.overflow) || errors.length > 0;
  process.exit(failed ? 1 : 0);
}

run().catch((exc) => {
  console.error(exc);
  process.exit(2);
});
