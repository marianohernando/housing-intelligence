// Gate evidence for the web (LINEAS.md): every route at desktop (1440 px) and mobile (390 px),
// the desktop shot next to its reference mockup, and a non-zero exit on any browser error.
//
//   npm run -w apps/web capture -- --route inicio=/@mockup_1_mapa.png --route que-falta=/que-falta
//
// Options: --base (default http://localhost:3011), --out (default evidence/map-004/<today>),
// --prefix for file names, --wait extra ms after load (map animations).
// MOCKUP_DIR points to the folder with the mockups; they are read, never copied into the repo.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { parseArgs } from "node:util";

import { chromium } from "playwright";

const VIEWPORTS = [
  { id: "desktop", viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 },
  { id: "mobile", viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
];

const today = new Date().toLocaleDateString("sv-SE");
const { values } = parseArgs({
  options: {
    base: { type: "string", default: "http://localhost:3011" },
    out: { type: "string", default: join("..", "..", "evidence", "map-004", today) },
    prefix: { type: "string", default: "" },
    route: { type: "string", multiple: true, default: ["inicio=/"] },
    wait: { type: "string", default: "0" },
  },
});

/** "name=/path@mockup.png" -> { name, path, mockup } */
function parseRoute(spec) {
  const [name, rest] = spec.split(/=(.*)/s);
  const [path, mockup] = (rest ?? "").split("@");
  if (!name || !path?.startsWith("/")) throw new Error(`Bad --route ${spec}; expected name=/path[@mockup.png]`);
  return { name, path, mockup: mockup || null };
}

function dataUrl(file) {
  return `data:image/png;base64,${readFileSync(file).toString("base64")}`;
}

async function sideBySide(browser, shotFile, mockupFile, outFile) {
  const page = await browser.newPage({ viewport: { width: 2960, height: 1000 } });
  await page.setContent(`<!doctype html><html><body style="margin:0;padding:24px;background:#e9e8f2;font:600 22px system-ui;color:#141b3d">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start">
      <figure style="margin:0"><figcaption style="margin-bottom:10px">Vida Fácil (captura, 1440 px)</figcaption><img src="${dataUrl(shotFile)}" style="width:100%;display:block"></figure>
      <figure style="margin:0"><figcaption style="margin-bottom:10px">Mockup de referencia</figcaption><img src="${dataUrl(mockupFile)}" style="width:100%;display:block"></figure>
    </div></body></html>`);
  await page.screenshot({ path: outFile, fullPage: true, type: "jpeg", quality: 82 });
  await page.close();
}

async function capture(browser, route, profile, outDir) {
  const { id, ...contextOptions } = profile;
  const context = await browser.newContext({ ...contextOptions, locale: "es-ES" });
  const page = await context.newPage();
  const problems = [];
  const warnings = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") problems.push(`console: ${msg.text()}`);
    if (msg.type() === "warning") warnings.push(msg.text());
  });
  page.on("pageerror", (err) => problems.push(`pageerror: ${err.message}`));
  page.on("requestfailed", (req) => {
    const reason = req.failure()?.errorText ?? "";
    // MapLibre cancels tile requests it no longer needs while the camera moves: not a failure.
    if (reason === "net::ERR_ABORTED") return;
    problems.push(`requestfailed: ${req.url()} ${reason}`);
  });
  page.on("response", (res) => {
    if (res.status() >= 400) problems.push(`http ${res.status()}: ${res.url()}`);
  });
  await page.goto(new URL(route.path, values.base).toString(), { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(Number(values.wait));
  // How far the page scrolls past the viewport: 0 means everything fits on one screen.
  const overflowPx = await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight);
  const file = join(outDir, `${values.prefix}${route.name}_${id}.png`);
  await page.screenshot({ path: file });
  await context.close();
  return { route: route.path, viewport: id, file, overflow_px: overflowPx, problems, warnings };
}

const outDir = resolve(values.out);
mkdirSync(outDir, { recursive: true });
const routes = values.route.map(parseRoute);
const browser = await chromium.launch();
const shots = [];
try {
  for (const route of routes) {
    for (const profile of VIEWPORTS) {
      const shot = await capture(browser, route, profile, outDir);
      shots.push(shot);
      if (profile.id === "desktop" && route.mockup && process.env.MOCKUP_DIR) {
        shot.comparison = join(outDir, `${values.prefix}${route.name}_desktop_vs_mockup.jpg`);
        await sideBySide(browser, shot.file, join(process.env.MOCKUP_DIR, route.mockup), shot.comparison);
      }
    }
  }
} finally {
  await browser.close();
}

const relative = (file) => file?.replace(`${outDir}/`, "");
const report = {
  base: values.base,
  generated_at: new Date().toISOString(),
  shots: shots.map((s) => ({ ...s, file: relative(s.file), comparison: relative(s.comparison) })),
};
writeFileSync(join(outDir, `${values.prefix}capture.json`), `${JSON.stringify(report, null, 2)}\n`);
const failed = shots.filter((s) => s.problems.length > 0);
for (const shot of shots) {
  console.log(`${shot.problems.length ? "FAIL" : "ok  "} ${shot.viewport.padEnd(7)} ${shot.route} -> ${relative(shot.file)}`);
  for (const problem of shot.problems) console.log(`       ${problem}`);
}
if (failed.length > 0) process.exit(1);
