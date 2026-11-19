import { describe, expect, it } from "vitest";

import { API_BASE, API_GROUPS, curlOf, MCP_CLAUDE_CODE, MCP_CLAUDE_DESKTOP, MCP_SETUP, SITE_URL } from "@/lib/developers";

const EXAMPLES = API_GROUPS.flatMap((group) => group.examples);

/** The body a POST example sends, read back from its command as a shell would pass it. */
function sentBody(command: string): unknown {
  const quoted = /-d '([\s\S]*)'$/.exec(command)?.[1];
  if (quoted === undefined) throw new Error(`no body in ${command}`);
  return JSON.parse(quoted);
}

describe("«Para desarrolladores» (D-249)", () => {
  it("documents every public data route, once", () => {
    const routes = EXAMPLES.map((e) => `${e.method} ${e.path.split("?")[0]}`);
    expect(new Set(routes).size).toBe(routes.length);
    expect(routes.sort()).toEqual(
      [
        "GET /api/v1/datasets",
        "GET /api/v1/features",
        "GET /api/v1/features/{feature_id}/values",
        "GET /api/v1/gaps",
        "GET /api/v1/gaps/impact",
        "GET /api/v1/gaps/{level}/{code}",
        "GET /api/v1/geo/admin-units",
        "GET /api/v1/investors/zones",
        "GET /api/v1/investors/zones/{admin_unit_id}",
        "GET /api/v1/places",
        "POST /api/v1/investors/viability",
        "POST /api/v1/search",
        "POST /api/v1/search/barrios",
      ].sort(),
    );
  });

  it("every example asks production for its own route", () => {
    expect(API_BASE).toBe("https://vidafacil-madrid.vercel.app/api/v1");
    for (const example of EXAMPLES) {
      const command = curlOf(example);
      expect(command.startsWith(`curl -s ${example.method === "GET" ? '"' : "-X POST "}${API_BASE}/`)).toBe(true);
      const asked = example.request.split("?")[0] ?? "";
      const route = example.path.replace("/api/v1", "").split("?")[0] ?? "";
      const documented = new RegExp(`^${route.replace(/\{\w+\}/g, "[^/]+")}$`);
      expect(asked).toMatch(documented);
    }
  });

  it("POST examples send their body as JSON the shell passes unchanged", () => {
    for (const example of EXAMPLES.filter((e) => e.method === "POST")) {
      expect(JSON.stringify(example.body)).not.toContain("'");
      expect(sentBody(curlOf(example))).toEqual(example.body);
    }
  });

  it("the MCP setup runs hi-mcp from a clone, against a database with the data", () => {
    const desktop = JSON.parse(MCP_CLAUDE_DESKTOP).mcpServers["vida-facil"];
    expect(desktop.command).toBe("uv");
    expect(desktop.args.at(-1)).toBe("hi-mcp");
    expect(desktop.env.DATABASE_URL).toMatch(/^postgresql\+psycopg:\/\//);
    expect(MCP_CLAUDE_CODE).toContain("hi-mcp");
    expect(MCP_SETUP).toContain("make ingest-all");
  });

  it("names only the public address of the site", () => {
    const everything = JSON.stringify({ API_GROUPS, MCP_CLAUDE_CODE, MCP_CLAUDE_DESKTOP, MCP_SETUP });
    for (const host of everything.match(/[\w.-]+\.vercel\.app/g) ?? []) expect(`https://${host}`).toBe(SITE_URL);
    expect(everything).not.toMatch(/\/Users\/|\/private\/|~\/Desktop/);
  });
});
