// Captures of what F7 changes on screen, at 390 and 1440 px, against the built web and its API:
//   1. «Somos mayores» with «Solo/a»: «¿Cerca de dónde quieres vivir?», «Donde vivo ahora» with a
//      place picked, then «En pareja» («queréis», «Donde vivimos ahora»), and the search: the place
//      reaches the API as «donde vivo ahora» and the card's trip says the same words;
//   2. «Cómo lo calculamos»: the paragraph «A igual %» (no «Empatan al 94 %»).
// The barrio panels (one at a time, outlines late) are captured by `check-qa.mjs barrios` (qa/).
//
//   node evidence/gate-06/2026-11-18-f7-web/capture-f7.mjs --base http://localhost:3091 --out DIR
// Run from apps/web (its Playwright and axe-core). Exit 1 if a check fails.
import { mkdirSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join, resolve } from "node:path";
import { parseArgs } from "node:util";

const require = createRequire(join(process.cwd(), "package.json"));
const { chromium } = require("playwright");
const AXE = require.resolve("axe-core/axe.min.js");

const { values: opts } = parseArgs({ options: { base: { type: "string", default: "http://localhost:3091" }, out: { type: "string", default: "." } } });
const BASE = opts.base.replace(/\/$/, "");
const OUT = resolve(opts.out);
mkdirSync(OUT, { recursive: true });

const PROFILES = {
  390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  1440: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
};
const WAIT = 30_000;
const flat = (text) => text.replace(/\s+/g, " ").trim();
const isSearch = (r) => r.url().endsWith("/api/v1/search") && r.request().method() === "POST";
const report = { base: BASE, checks: [] };
const check = (name, ok, detail = "") => report.checks.push({ name, ok: Boolean(ok), detail: String(detail).slice(0, 300) });

async function axe(page) {
  await page.addScriptTag({ path: AXE });
  return page.evaluate(async () => {
    const r = await window.axe.run(document, { runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"] } });
    return r.violations.map((v) => ({ id: v.id, nodes: v.nodes.length }));
  });
}

async function older(browser, width) {
  const ctx = await browser.newContext({ ...PROFILES[width], locale: "es-ES" });
  const page = await ctx.newPage();
  const errors = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  await page.goto(`${BASE}/`, { waitUntil: "networkidle" });
  await page.getByRole("button", { name: /^Somos mayores/ }).click();
  const field = page.getByRole("group", { name: /^¿Cerca de dónde (quieres|queréis) vivir\?/ }).first();
  await field.waitFor({ timeout: WAIT });
  const blank = flat(await field.innerText());
  check(`${width}: alone, «¿Cerca de dónde quieres vivir?», «Donde vivo ahora», «Cerca de mi familia»`,
    blank.startsWith("¿Cerca de dónde quieres vivir?") && blank.includes("Donde vivo ahora") && blank.includes("Cerca de mi familia") && blank.includes("¿Dónde vives ahora?") &&
      !/queréis|vivimos|nuestra|vivís|vuestra/.test(blank), blank);
  const combo = page.getByRole("combobox", { name: /^¿Dónde vives ahora\?/ });
  await combo.click();
  await combo.fill("Ciudad Lineal");
  await page.getByRole("option", { name: /^Ciudad Lineal \(metro\)/ }).first().click({ timeout: WAIT });
  await page.getByRole("button", { name: /^Quitar este lugar/ }).first().waitFor({ timeout: WAIT });
  const picked = flat(await field.innerText());
  check(`${width}: the place picked reads «Donde vivo ahora: Ciudad Lineal (metro)»`, picked.includes("Donde vivo ahora: Ciudad Lineal (metro)"), picked);
  const limit = await page.getByRole("combobox", { name: "Tardar como mucho hasta donde vivo ahora, en transporte público" }).count();
  check(`${width}: its limit is called «… hasta donde vivo ahora…»`, limit === 1, limit);
  report[`axe_solo_${width}`] = await axe(page);
  check(`${width}: axe 0 with «Solo/a» and the place`, report[`axe_solo_${width}`].length === 0, JSON.stringify(report[`axe_solo_${width}`]));
  await field.evaluate((el) => el.scrollIntoView({ block: "center" }));
  await field.screenshot({ path: join(OUT, `01-mayor-solo-${width}.png`) });

  // The search: the place's label goes to the API as the household says it, and its trip comes back in the same words
  const [response] = await Promise.all([page.waitForResponse(isSearch, { timeout: WAIT }), page.getByRole("button", { name: "Buscar zonas para mí" }).click()]);
  const sent = response.request().postDataJSON();
  const data = (await response.json()).data;
  check(`${width}: /search gets the place as «donde vivo ahora»`, sent?.anchors?.some((a) => a.kind === "other" && a.label === "donde vivo ahora"), JSON.stringify(sent?.anchors));
  const trips = data.results.flatMap((z) => z.facts.map((f) => f.text)).filter((t) => t.includes("donde viv"));
  check(`${width}: the API's trips say «hasta donde vivo ahora»`, trips.length > 0 && trips.every((t) => t.includes("hasta donde vivo ahora")), trips[0] ?? "no trips");

  // «En pareja»: the same field speaks to both, and the place follows («Donde vivimos ahora»)
  await page.getByRole("button", { name: "En pareja", exact: true }).click();
  const couple = flat(await page.getByRole("group", { name: /^¿Cerca de dónde queréis vivir\?/ }).first().innerText());
  check(`${width}: a couple reads «queréis» and «Donde vivimos ahora: Ciudad Lineal (metro)»`,
    couple.startsWith("¿Cerca de dónde queréis vivir?") && couple.includes("Donde vivimos ahora: Ciudad Lineal (metro)"), couple);
  await page.getByRole("group", { name: /^¿Cerca de dónde queréis vivir\?/ }).first().screenshot({ path: join(OUT, `02-mayores-pareja-${width}.png`) });
  report[`consola_${width}`] = errors;
  check(`${width}: no console errors`, errors.length === 0, errors[0] ?? "");
  await ctx.close();
}

async function method(browser, width) {
  const ctx = await browser.newContext({ ...PROFILES[width], locale: "es-ES" });
  const page = await ctx.newPage();
  await page.goto(`${BASE}/como-lo-calculamos`, { waitUntil: "networkidle" });
  const para = page.locator("p").filter({ hasText: /^A igual %/ }).first();
  const text = flat(await para.innerText());
  check(`${width}: «Cómo lo calculamos» says where the tie is, without «Empatan al»`,
    !/Empatan al/.test(text) && text.includes("Ver más sobre…") && text.includes("Igual de buena que Latina (94 %)"), text);
  await para.evaluate((el) => el.scrollIntoView({ block: "center" }));
  await para.screenshot({ path: join(OUT, `03-como-lo-calculamos-empate-${width}.png`) });
  await ctx.close();
}

const browser = await chromium.launch();
for (const width of [390, 1440]) {
  await older(browser, width);
  await method(browser, width);
}
await browser.close();
const failed = report.checks.filter((c) => !c.ok);
report.summary = `${report.checks.length - failed.length}/${report.checks.length}`;
writeFileSync(join(OUT, "capturas-f7.json"), `${JSON.stringify(report, null, 1)}\n`);
console.log(report.summary, failed.map((c) => `${c.name}: ${c.detail}`).join("\n"));
if (failed.length) process.exitCode = 1;
