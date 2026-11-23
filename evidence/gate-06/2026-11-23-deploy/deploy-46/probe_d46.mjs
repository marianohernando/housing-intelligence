// probe_d46.mjs BASE OUT: deploy-46's web checks (#123 remote MCP, #124 DCAT/SDM files, #126 texts) against production, at 1440 and 390 px.
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { chromium } from "playwright";

const [, , BASE = "https://vidafacil-madrid.vercel.app", OUT = "."] = process.argv;
mkdirSync(OUT, { recursive: true });
const TAG = "vida-facil-smoke/d46-probe";
const PROFILES = {
  1440: { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  390: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
};
const MCP_URL = `${BASE}/api/v1/mcp`;
const squash = (s) => s.replace(/\s+/g, " ").trim();
const results = [];
const check = (width, page, name, ok, detail = "") => results.push({ width, page, name, ok: Boolean(ok), detail: String(detail).slice(0, 300) });
const section = (page, id) => page.locator(`section[aria-labelledby="${id}"]`).first();

const browser = await chromium.launch();
for (const [width, profile] of Object.entries(PROFILES)) {
  const probe = await browser.newContext(profile);
  const ua = await (await probe.newPage()).evaluate(() => navigator.userAgent);
  await probe.close();
  const ctx = await browser.newContext({ ...profile, locale: "es-ES", userAgent: `${ua} ${TAG}` });
  const p = await ctx.newPage();
  const errors = [];
  p.on("console", (m) => { if (m.type() === "error") errors.push(`${p.url()} ${m.text()}`); });
  const overflow = async () => p.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);

  // /desarrolladores: the remote MCP «Funciona hoy», its URL and clients; 3 planned; the open data files
  await p.goto(`${BASE}/desarrolladores`, { waitUntil: "networkidle" });
  const mcp = squash(await section(p, "mcp").innerText());
  check(width, "/desarrolladores", "MCP section marked «Funciona hoy»", mcp.includes("Funciona hoy"), mcp.slice(0, 80));
  check(width, "/desarrolladores", "remote URL shown", mcp.includes(MCP_URL), MCP_URL);
  check(width, "/desarrolladores", "Claude Code command", mcp.includes(`claude mcp add --transport http vida-facil ${MCP_URL}`));
  check(width, "/desarrolladores", "mcp-remote bridge", mcp.includes(`npx -y mcp-remote ${MCP_URL}`));
  check(width, "/desarrolladores", "«Sus 7 herramientas»", mcp.includes("Sus 7 herramientas"));
  const planned = squash(await section(p, "planteado").innerText());
  const plannedItems = await section(p, "planteado").locator("li").count();
  check(width, "/desarrolladores", "3 planned items, none is the remote MCP", plannedItems === 3 && !/MCP en remoto/i.test(planned), `${plannedItems} items`);
  const links = await p.locator('a[href^="/datos/"]').evaluateAll((as) => as.map((a) => a.getAttribute("href")));
  check(width, "/desarrolladores", "3 links to /datos/", links.length === 3, links.join(", "));
  for (const href of links) {
    const r = await p.request.get(`${BASE}${href}`, { headers: { "user-agent": `${ua} ${TAG}` } });
    const body = await r.body();
    let parsed = false;
    try { JSON.parse(body.toString("utf8")); parsed = true; } catch {}
    check(width, "/desarrolladores", `link ${href} reaches the file`, r.status() === 200 && parsed, `${r.status()} ${r.headers()["content-type"]} ${body.length} B`);
  }
  check(width, "/desarrolladores", "no horizontal overflow", (await overflow()) <= 0, await overflow());
  if (width === "1440") await section(p, "mcp").screenshot({ path: join(OUT, "1440-desarrolladores-mcp.jpg"), type: "jpeg", quality: 80 });

  // /inversores: the paid plan's new words
  await p.goto(`${BASE}/inversores`, { waitUntil: "networkidle" });
  const inv = squash(await p.locator("main").innerText());
  check(width, "/inversores", "«plan empresarial e informes personalizados»", inv.includes("Para inversores y promotores habrá un plan empresarial e informes personalizados"));
  check(width, "/inversores", "no «plan de pago»", !inv.includes("plan de pago"));

  // /como-lo-calculamos and the home: no «no es casualidad»
  await p.goto(`${BASE}/como-lo-calculamos`, { waitUntil: "networkidle" });
  const method = squash(await p.locator("main").innerText());
  check(width, "/como-lo-calculamos", "no «no es casualidad»", !method.includes("no es casualidad"));
  const n = method.split("demasiado grande para explicarla por el tamaño de la zona").length - 1;
  check(width, "/como-lo-calculamos", "«demasiado grande para explicarla por el tamaño de la zona»", n >= 1, `${n} times`);
  await p.goto(`${BASE}/`, { waitUntil: "networkidle" });
  const home = squash(await p.locator("body").innerText());
  check(width, "/", "no «no es casualidad» on the home either", !home.includes("no es casualidad"));

  check(width, "all", "0 console errors", errors.length === 0, errors.join(" | "));
  await ctx.close();
}
await browser.close();
writeFileSync(join(OUT, "probe-d46.json"), JSON.stringify({ base: BASE, checked_at: new Date().toISOString(), results }, null, 2));
const failed = results.filter((r) => !r.ok);
for (const r of results) console.log(`${r.ok ? "ok  " : "FAIL"} ${r.width} ${r.page} · ${r.name} · ${r.detail}`);
console.log(`${results.length - failed.length}/${results.length}`);
process.exit(failed.length ? 1 : 0);
