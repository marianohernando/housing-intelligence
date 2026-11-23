// probe_d45.mjs BASE OUT: deploy-45's specific web checks (#120/#121) against production, at 1440 and 390 px.
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { chromium } from "playwright";

const [, , BASE = "https://vidafacil-madrid.vercel.app", OUT = "."] = process.argv;
mkdirSync(OUT, { recursive: true });
const UA_TAG = "vida-facil-smoke/d45-probe";
const PROFILES = {
  1440: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
};
const squash = (s) => s.replace(/\s+/g, " ").trim();
const results = [];
const check = (width, page, name, ok, detail = "") => { results.push({ width, page, name, ok: Boolean(ok), detail: String(detail).slice(0, 300) }); };
const section = (page, id) => page.locator(`section[aria-labelledby="${id}"]`).first();
const TXT = {
  h1: "La zona que te conviene, y lo que le falta",
  title: "Vida Fácil · La zona que te conviene, y lo que le falta",
  catalogued: "Edificio catalogado: una cuenta de obra nueva no sirve; hace falta un estudio de rehabilitación.",
  calcCatalogued: "Ponla tú si quieres: en un edificio catalogado no partimos de ninguna cifra",
  planningFirst: "Antes de pedir licencia, el ámbito necesita su planeamiento y su gestión.",
  worksPending: "La ley permite pedir licencia con la urbanización a la vez",
  takeIt: "Llévate esta ficha",
  leavesOut: "La cuenta no incluye sótanos, urbanización, financiación ni IVA.",
};
const SHEETS = { mendez: "2122202VK4722A", almeria: "3959601VK4735H", misson: "0390314VK4709A", mayor: "9943003VK3794D" };

const browser = await chromium.launch();
for (const [width, profile] of Object.entries(PROFILES)) {
  const ctx = await browser.newContext({ ...profile, locale: "es-ES", userAgent: undefined });
  const page = await ctx.newPage();
  const ua = await page.evaluate(() => navigator.userAgent);
  await ctx.setExtraHTTPHeaders({});
  await page.close();
  const ctx2 = await browser.newContext({ ...profile, locale: "es-ES", userAgent: `${ua} ${UA_TAG}` });
  const errors = [];
  const cache = [];
  const p = await ctx2.newPage();
  p.on("console", (m) => { if (m.type() === "error") errors.push(`${p.url()} ${m.text()}`); });
  p.on("response", (r) => { if (r.url().includes("/api/v1/investors/parcels?rc=")) cache.push(`${r.url().split("rc=")[1]} ${r.status()} ${r.headers()["x-vercel-cache"] ?? "-"} ${r.headers()["cache-control"] ?? "-"}`); });

  // 1. Home: the H1 and the <title>
  await p.goto(`${BASE}/`, { waitUntil: "networkidle" });
  const h1 = squash(await p.getByRole("heading", { level: 1 }).first().innerText());
  check(width, "/", "H1 = new tagline", h1 === TXT.h1, h1);
  const title = await p.title();
  check(width, "/", "<title> = new tagline", title === TXT.title, title);
  if (width === "1440") await p.locator("section[aria-labelledby=titulo]").first().screenshot({ path: join(OUT, "1440-portada-h1.jpg"), type: "jpeg", quality: 80 });

  // 2. Mayor 61: calculator at «Sin dato», with the catalogued notice
  await p.goto(`${BASE}/inversores/parcela/${SHEETS.mayor}`, { waitUntil: "networkidle" });
  await p.getByLabel("Superficie edificable residencial").waitFor({ timeout: 45_000 });
  const field = await p.getByLabel("Superficie edificable residencial").inputValue();
  check(width, "Mayor 61", "calculator m² empty", field === "", field);
  const calc = squash(await section(p, "viabilidad").innerText());
  check(width, "Mayor 61", "calculator marked «Sin dato»", calc.includes("Sin dato"), calc.slice(0, 200));
  check(width, "Mayor 61", "calculator help for a catalogued building", calc.includes(TXT.calcCatalogued));
  check(width, "Mayor 61", "rehabilitation notice", calc.includes(TXT.catalogued));
  const built = squash(await section(p, "edificabilidad").innerText());
  check(width, "Mayor 61", "buildability still «Supuesto» 224 m² in its section", built.includes("Supuesto") && built.includes("224 m²"), built.slice(0, 160));
  const mayorAll = squash(await p.locator("main").innerText());
  check(width, "Mayor 61", "«Llévate esta ficha» once", mayorAll.split(TXT.takeIt).length - 1 === 1, mayorAll.split(TXT.takeIt).length - 1);
  if (width === "1440") await section(p, "viabilidad").screenshot({ path: join(OUT, "1440-mayor-calculadora.jpg"), type: "jpeg", quality: 80 });

  // 3. Almería 1: planning and management first
  await p.goto(`${BASE}/inversores/parcela/${SHEETS.almeria}`, { waitUntil: "networkidle" });
  await section(p, "servicios").waitFor({ timeout: 45_000 });
  const services = squash(await section(p, "servicios").innerText());
  check(width, "Almería 1", "«Antes de pedir licencia…»", services.includes(TXT.planningFirst), services.slice(0, 200));
  check(width, "Almería 1", "no licence-with-urbanization sentence", !services.includes(TXT.worksPending));
  const almAll = squash(await p.locator("main").innerText());
  check(width, "Almería 1", "«Llévate esta ficha» once", almAll.split(TXT.takeIt).length - 1 === 1, almAll.split(TXT.takeIt).length - 1);
  if (width === "1440") await section(p, "servicios").screenshot({ path: join(OUT, "1440-almeria-servicios.jpg"), type: "jpeg", quality: 80 });

  // 4. Méndez Álvaro: the residual per m² buildable and as a share of the sales
  await p.goto(`${BASE}/inversores/parcela/${SHEETS.mendez}`, { waitUntil: "networkidle" });
  await p.getByRole("heading", { name: "Resultado: tres escenarios" }).waitFor({ timeout: 45_000 });
  const via = squash(await section(p, "viabilidad").innerText());
  // The scenario cards' row (residualText, #120); the API's verdict sentence before them («…, antes de financiación…: unos …») is not that row
  const residual = (via.match(/Lo máximo que se puede pagar por el suelo unos [^)]*\)/g) ?? []);
  const verdict = via.match(/Lo máximo que se puede pagar por el suelo, antes de[^)]*\)/)?.[0] ?? "";
  check(width, "Méndez Álvaro", "residual row «€ por m² edificable» and «% de los ingresos por ventas» (3 scenarios)",
    residual.length === 3 && residual.every((r) => /€ por m² edificable; el \d+ % de los ingresos por ventas/.test(r)), residual.join(" | "));
  check(width, "Méndez Álvaro", "(info) the API's verdict sentence, unchanged by #120", true, verdict);
  check(width, "Méndez Álvaro", "what the account leaves out", via.includes(TXT.leavesOut));
  const method = via.match(/Método de la cuenta: [^.]+\./)?.[0] ?? "";
  check(width, "Méndez Álvaro", "the method's real version", /Método de la cuenta: viability-\d/.test(method), method);
  const menAll = squash(await p.locator("main").innerText());
  check(width, "Méndez Álvaro", "«Llévate esta ficha» once", menAll.split(TXT.takeIt).length - 1 === 1, menAll.split(TXT.takeIt).length - 1);
  if (width === "1440") await section(p, "viabilidad").screenshot({ path: join(OUT, "1440-mendez-alvaro-residual.jpg"), type: "jpeg", quality: 80 });

  // 5. Luis Misson: «Llévate esta ficha» once
  await p.goto(`${BASE}/inversores/parcela/${SHEETS.misson}`, { waitUntil: "networkidle" });
  await section(p, "viabilidad").waitFor({ timeout: 45_000 });
  const misAll = squash(await p.locator("main").innerText());
  check(width, "Luis Misson", "«Llévate esta ficha» once", misAll.split(TXT.takeIt).length - 1 === 1, misAll.split(TXT.takeIt).length - 1);

  // 6. Pinar del Rey's barrio sheet: «Estimación» on the sale price, vacant land «de toda la ciudad», the method
  await p.goto(`${BASE}/inversores/28079164`, { waitUntil: "networkidle" });
  await section(p, "precios").waitFor({ timeout: 45_000 });
  const prices = squash(await section(p, "precios").innerText());
  check(width, "Pinar del Rey", "sale price marked «Estimación»", prices.includes("Estimación"), prices.slice(0, 200));
  const land = squash(await section(p, "suelo").innerText());
  check(width, "Pinar del Rey", "«Suelo vacante de toda la ciudad (Catastro)»", land.includes("Suelo vacante de toda la ciudad (Catastro)"), land.slice(-160));
  const src = squash(await section(p, "fuentes").innerText());
  const m = src.match(/Método: [^.]+\./)?.[0] ?? "";
  check(width, "Pinar del Rey", "the method as the API serves it (not «viabilidad v0 (D-248)»)", /Método: viability-\d/.test(m) && !src.includes("viabilidad v0"), m);

  // 7. /como-lo-calculamos#inversores: the ICIO without «vigente en 2025»
  await p.goto(`${BASE}/como-lo-calculamos#inversores`, { waitUntil: "networkidle" });
  const methodPage = squash(await p.locator("main").innerText());
  check(width, "/como-lo-calculamos", "ICIO cited without «vigente en 2025»", methodPage.includes("Libro de Ordenanzas Fiscales 2024, p. 154") && !methodPage.includes("vigente en 2025"));
  check(width, "/como-lo-calculamos", "housing «(solo contexto)»", methodPage.includes("Vivienda (solo contexto)"));

  check(width, "all", "0 console errors", errors.length === 0, errors.join(" | "));
  check(width, "all", "every parcel sheet request from the CDN (HIT)", cache.length > 0 && cache.every((c) => c.includes(" 200 HIT ")), cache.join(" | "));
  await ctx2.close();
  await ctx.close();
}
await browser.close();
writeFileSync(join(OUT, "probe-d45.json"), JSON.stringify({ base: BASE, checked_at: new Date().toISOString(), results }, null, 2));
const failed = results.filter((r) => !r.ok);
for (const r of results) console.log(`${r.ok ? "ok  " : "FAIL"} ${r.width} ${r.page} · ${r.name}${r.ok ? "" : ` · ${r.detail}`}`);
console.log(`${results.length - failed.length}/${results.length}`);
process.exit(failed.length ? 1 : 0);
