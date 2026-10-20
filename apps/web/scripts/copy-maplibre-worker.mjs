// Copies the MapLibre v6 worker (and the shared module it imports) into public/ so the
// browser can load it from a stable URL. Runs before dev/build; output is gitignored.
import { copyFileSync, mkdirSync } from "node:fs";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const dist = dirname(require.resolve("maplibre-gl/dist/maplibre-gl.mjs"));
const target = join(dirname(fileURLToPath(import.meta.url)), "..", "public", "maplibre");
mkdirSync(target, { recursive: true });
for (const file of ["maplibre-gl-worker.mjs", "maplibre-gl-shared.mjs"]) {
  copyFileSync(join(dist, file), join(target, file));
}
console.log(`maplibre worker copied to ${target}`);
