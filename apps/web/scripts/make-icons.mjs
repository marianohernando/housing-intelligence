// Raster icons of the web from src/app/icon.svg (the header's mark, Logo.tsx), for the browsers
// and phones that do not take the SVG: src/app/favicon.ico (16, 32 and 48 px, PNG inside) and
// src/app/apple-icon.png (180 px, a full square: iOS rounds the corners itself). Next serves them
// and writes their <link> tags (file conventions favicon, icon and apple-icon). Run it again when
// the mark changes:
//
//   node scripts/make-icons.mjs
import { readFileSync, writeFileSync } from "node:fs";

import { chromium } from "playwright";

const APP = new URL("../src/app/", import.meta.url);
const svg = readFileSync(new URL("icon.svg", APP), "utf8");
const square = svg.replace(' rx="10"', "");
if (square === svg) throw new Error("icon.svg: no rounded tile to square for iOS");

async function png(page, source, size) {
  await page.setViewportSize({ width: size, height: size });
  const sized = source.replace("<svg ", `<svg width="${size}" height="${size}" `);
  await page.setContent(`<!doctype html><body style="margin:0">${sized}</body>`);
  return page.screenshot({ omitBackground: true });
}

/** An .ico with PNG images inside (read by every current browser): header, directory, images. */
function ico(images) {
  const header = Buffer.alloc(6);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(images.length, 4);
  let offset = header.length + 16 * images.length;
  const entries = images.map(({ size, data }) => {
    const entry = Buffer.alloc(16);
    entry.writeUInt8(size, 0);
    entry.writeUInt8(size, 1);
    entry.writeUInt16LE(1, 4);
    entry.writeUInt16LE(32, 6);
    entry.writeUInt32LE(data.length, 8);
    entry.writeUInt32LE(offset, 12);
    offset += data.length;
    return entry;
  });
  return Buffer.concat([header, ...entries, ...images.map(({ data }) => data)]);
}

const browser = await chromium.launch();
try {
  const page = await browser.newPage();
  const favicon = [];
  for (const size of [16, 32, 48]) favicon.push({ size, data: await png(page, svg, size) });
  writeFileSync(new URL("favicon.ico", APP), ico(favicon));
  writeFileSync(new URL("apple-icon.png", APP), await png(page, square, 180));
} finally {
  await browser.close();
}
console.log("favicon.ico and apple-icon.png written to src/app");
