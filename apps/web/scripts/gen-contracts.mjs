// Generates the TypeScript types of the PUBLIC API contracts from the JSON Schemas that line A
// exports with `make schemas` (data/schemas/api/*.schema.json). The types are never written
// by hand: run `npm run -w apps/web contracts` after A changes a contract.
//
//   node scripts/gen-contracts.mjs          write src/contracts/<name>.ts
//   node scripts/gen-contracts.mjs --check  exit 1 if any generated file is stale or missing
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { compile } from "json-schema-to-typescript";

const APP = join(dirname(fileURLToPath(import.meta.url)), "..");
const SCHEMAS = join(APP, "..", "..", "data", "schemas", "api");
const OUT = join(APP, "src", "contracts");

const BANNER = (source) =>
  [
    "/**",
    ` * Generated from data/schemas/api/${source} by scripts/gen-contracts.mjs. Do not edit:`,
    " * change the Pydantic contract in packages/contracts, run `make schemas`, then",
    " * `npm run -w apps/web contracts`.",
    " */",
  ].join("\n");

const OPTIONS = {
  additionalProperties: false,
  maxItems: -1, // max_length in Pydantic is validation, not a tuple
  strictIndexSignatures: true,
  unknownAny: true,
  unreachableDefinitions: false,
  style: { printWidth: 100, singleQuote: false, trailingComma: "all" },
};

async function generate() {
  const files = readdirSync(SCHEMAS).filter((f) => f.endsWith(".schema.json")).sort();
  const outputs = new Map();
  for (const file of files) {
    const schema = JSON.parse(readFileSync(join(SCHEMAS, file), "utf8"));
    const code = await compile(schema, schema.title, { ...OPTIONS, bannerComment: BANNER(file), cwd: SCHEMAS });
    outputs.set(`${basename(file, ".schema.json")}.ts`, code);
  }
  return outputs;
}

const outputs = await generate();
if (process.argv.includes("--check")) {
  const stale = [...outputs].filter(([name, code]) => {
    const path = join(OUT, name);
    return !existsSync(path) || readFileSync(path, "utf8") !== code;
  });
  for (const [name] of stale) console.error(`stale: src/contracts/${name}`);
  if (stale.length > 0) {
    console.error("Run `npm run -w apps/web contracts` to regenerate the contract types.");
    process.exit(1);
  }
  console.log(`contracts up to date (${outputs.size} files)`);
} else {
  mkdirSync(OUT, { recursive: true });
  for (const [name, code] of outputs) writeFileSync(join(OUT, name), code);
  console.log(`wrote ${outputs.size} files to src/contracts/`);
}
