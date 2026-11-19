import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import CodeBlock from "@/components/developers/CodeBlock";

describe("CodeBlock (D-249, review R-03 of #97)", () => {
  it("the focusable box that scrolls is a region named after its example", () => {
    const html = renderToStaticMarkup(
      createElement(CodeBlock, { code: 'curl -s "https://example"', caption: "curl", label: "GET /api/v1/gaps/impact" }),
    );
    const pre = /<pre\b[^>]*>/.exec(html)?.[0] ?? "";
    expect(pre).toContain('tabindex="0"');
    expect(pre).toContain('role="region"');
    expect(pre).toContain('aria-label="GET /api/v1/gaps/impact"');
  });
});
