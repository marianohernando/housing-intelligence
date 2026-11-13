import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

import { describe, expect, it } from "vitest";

const APP = fileURLToPath(new URL("../../../", import.meta.url));

describe("generated contract types (src/contracts)", () => {
  it("match data/schemas/api: regenerate with `npm run -w apps/web contracts`", () => {
    expect(() =>
      execFileSync(process.execPath, ["scripts/gen-contracts.mjs", "--check"], { cwd: APP, stdio: "pipe" }),
    ).not.toThrow();
  }, 30_000);
});
