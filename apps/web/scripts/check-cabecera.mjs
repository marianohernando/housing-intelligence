// The header with its four tabs (D-251): on the map (the home page, no footer) and on pages with a
// footer, at 360, 390 and 1440 px. For each page: the tabs in one row inside the screen, no text
// under 16 px and no target under 44 px in the header, no horizontal overflow, the active tab
// marked with aria-current, a tint and a ring (not colour alone), axe (WCAG 2.2 AA) on the header,
// and the contrast of every tab's words over what is really behind them: the page is captured with
// and without the words, the pixels the letters cover are those that change, and each one's
// background (from the capture without words) is compared with the words' colour; the worst one
// counts. So map labels showing through a translucent header are caught, and a pill's own ring
// beside the letters is not. With --shots, the screenshots of the evidence. Only a demo parcel:
// run the API with PARCEL_UPSTREAMS=false.
//
//   node apps/web/scripts/check-cabecera.mjs --base http://localhost:3096 --out DIR [--shots]
//
// Exit 1 if any check fails.
import { mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join, resolve } from "node:path";
import { parseArgs } from "node:util";

import { chromium } from "playwright";

const require = createRequire(import.meta.url);
const AXE = require.resolve("axe-core/axe.min.js");
// sharp comes with Next (image optimisation): it decodes the screenshot to read its pixels
const sharp = require("sharp");

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
const MIN_CONTRAST = 4.5;
const PAGES = [
  ["mapa", "/"],
  ["que-falta", "/que-falta"],
  ["como", "/como-lo-calculamos"],
  ["inversores", "/inversores"],
  ["parcela", "/inversores/parcela/2122202VK4722A"], // a demo parcel (D-250)
];
const PROFILES = {
  360: { viewport: { width: 360, height: 780 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  1440: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
};
// A pixel the letters cover changes by more than this (0-255, any channel) when they are hidden
const GLYPH_DELTA = 24;

const channel = (c) => {
  const v = c / 255;
  return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
};
const luminance = ([r, g, b]) => 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
const contrast = (a, b) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};
const rgb = (css) => css.match(/\d+(\.\d+)?/g).slice(0, 3).map(Number);

/** In the page: the header's tabs, their words' boxes and colours, and the size rules. */
function measure() {
  const header = document.querySelector("[data-site-header]");
  const links = [...header.querySelectorAll("nav a")];
  const smallText = [...header.querySelectorAll("*")]
    .filter((el) => [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()))
    .filter((el) => parseFloat(getComputedStyle(el).fontSize) < 15.99)
    .map((el) => el.textContent.trim());
  const smallTargets = [...header.querySelectorAll("a")]
    .filter((a) => {
      const r = a.getBoundingClientRect();
      return r.width < 43.5 || r.height < 43.5;
    })
    .map((a) => a.textContent.trim());
  const active = links.find((a) => a.getAttribute("aria-current") === "page");
  const style = active ? getComputedStyle(active) : null;
  return {
    labels: links.map((a) => a.textContent.trim()),
    words: links.map((a) => {
      const range = document.createRange();
      range.selectNodeContents(a);
      const r = range.getBoundingClientRect();
      return { label: a.textContent.trim(), color: getComputedStyle(a).color, x: r.left, y: r.top, w: r.width, h: r.height };
    }),
    active: active?.textContent.trim() ?? null,
    activeRing: style ? style.boxShadow !== "none" : false,
    activeTint: style ? style.backgroundColor !== "rgba(0, 0, 0, 0)" : false,
    oneRow: new Set(links.map((a) => Math.round(a.getBoundingClientRect().top))).size === 1,
    inside: Math.max(...links.map((a) => a.getBoundingClientRect().right)) <= document.documentElement.clientWidth,
    overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
    smallText,
    smallTargets,
  };
}

const pixels = async (shot) => sharp(shot).raw().toBuffer({ resolveWithObject: true });

/** The worst contrast of each tab's letters over the pixels behind them. */
async function wordsContrast(page, words, width) {
  const withWords = await pixels(await page.screenshot());
  await page.addStyleTag({ content: "[data-site-header] nav a { color: transparent !important; }" });
  await page.waitForTimeout(100);
  const behind = await pixels(await page.screenshot());
  await page.evaluate(() => document.querySelectorAll("style").forEach((s) => s.textContent.includes("color: transparent !important") && s.remove()));
  await page.waitForTimeout(100);
  const { info } = behind;
  const dpr = info.width / width;
  return words.map((w) => {
    const text = rgb(w.color);
    let worst = Infinity;
    let letters = 0;
    for (let y = Math.floor(w.y * dpr); y < Math.ceil((w.y + w.h) * dpr); y++) {
      for (let x = Math.floor(w.x * dpr); x < Math.ceil((w.x + w.w) * dpr); x++) {
        const i = (y * info.width + x) * info.channels;
        const covered = [0, 1, 2].some((c) => Math.abs(withWords.data[i + c] - behind.data[i + c]) > GLYPH_DELTA);
        if (!covered) continue;
        letters += 1;
        worst = Math.min(worst, contrast(text, [behind.data[i], behind.data[i + 1], behind.data[i + 2]]));
      }
    }
    return { label: w.label, worst: letters ? Math.round(worst * 100) / 100 : null, letters };
  });
}

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    const result = await window.axe.run(document.querySelector("[data-site-header]"), {
      runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] },
    });
    return result.violations.map((v) => v.id);
  });
}

async function run() {
  const browser = await chromium.launch();
  const report = [];
  for (const [width, profile] of Object.entries(PROFILES)) {
    const page = await (await browser.newContext({ ...profile, locale: "es-ES" })).newPage();
    for (const [name, path] of PAGES) {
      await page.goto(`${BASE}${path}`, { waitUntil: "load" });
      await page.locator("[data-site-header] nav a").first().waitFor({ timeout: 30_000 });
      await page.waitForTimeout(name === "mapa" ? 3500 : 1200); // the map's tiles and their labels
      // The tabs animate their colour: no transition while measuring, or a mid-fade colour is read
      await page.addStyleTag({ content: "[data-site-header] nav a { transition: none !important; }" });
      const { words, ...measured } = await page.evaluate(measure);
      const tabsContrast = await wordsContrast(page, words, profile.viewport.width);
      const violations = await axe(page);
      const read = tabsContrast.filter((c) => c.worst !== null);
      const minContrast = read.length === tabsContrast.length ? Math.min(...read.map((c) => c.worst)) : 0;
      const ok =
        measured.oneRow && measured.inside && !measured.overflow && measured.active && measured.activeRing && measured.activeTint &&
        measured.smallText.length === 0 && measured.smallTargets.length === 0 && violations.length === 0 && minContrast >= MIN_CONTRAST;
      report.push({ width: Number(width), page: name, ok, ...measured, contrast: tabsContrast, minContrast, axe: violations });
      if (opts.shots && (width !== "390" || name === "mapa")) {
        await page.locator("[data-site-header]").screenshot({ path: join(OUT, `${width}-cabecera-${name}.png`) });
        if (name === "mapa" || name === "inversores") await page.screenshot({ path: join(OUT, `${width}-${name}-primera-pantalla.png`) });
      }
    }
  }
  await browser.close();
  writeFileSync(join(OUT, "check-cabecera.json"), `${JSON.stringify({ base: "local", minContrast: MIN_CONTRAST, report }, null, 2)}\n`);
  for (const r of report) {
    console.log(
      `${r.width} ${r.page.padEnd(10)} ${r.ok ? "ok  " : "FAIL"} activa=${r.active} una fila=${r.oneRow} dentro=${r.inside} textos<16=${r.smallText.length} objetivos<44=${r.smallTargets.length} desborde=${r.overflow} axe=${r.axe.length} contraste mín=${r.minContrast}`,
    );
  }
  process.exit(report.every((r) => r.ok) ? 0 : 1);
}

run().catch((exc) => {
  console.error(exc);
  process.exit(2);
});
