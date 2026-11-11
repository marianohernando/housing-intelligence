import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

import { compositeOver, contrastRatio } from "../color";

const CSS = readFileSync(new URL("../../styles/tokens.css", import.meta.url), "utf8");
const DECLARATION = /--([a-z0-9-]+)\s*:\s*([^;]+);/g;
const RAW = new Map([...CSS.matchAll(DECLARATION)].map(([, name, value]) => [name as string, (value as string).trim()]));

function token(name: string): string {
  const value = RAW.get(name);
  if (value === undefined) throw new Error(`Missing token --${name}`);
  const reference = /^var\(--([a-z0-9-]+)\)$/.exec(value)?.[1];
  return reference ? token(reference) : value;
}

/** Glass cards over the page background and over the darkest colour the map can show. */
const BACKDROPS = {
  "bg": () => token("bg"),
  "glass/bg": () => compositeOver(token("glass-bg"), token("bg")),
  "glass/map": () => compositeOver(token("glass-bg"), token("map-darkest")),
};

const TEXT = 4.5; // WCAG 1.4.3, normal text
const UI = 3; // WCAG 1.4.11, icons, borders and focus

const STATUSES = ["falta", "justo", "cubierto", "sin-datos"] as const;

const PAIRS: [fg: string, bg: string, min: number][] = [
  ["ink", "bg", TEXT],
  ["ink", "glass/map", TEXT],
  ["ink-soft", "bg", TEXT],
  ["ink-soft", "glass/bg", TEXT],
  ["ink-soft", "glass/map", TEXT],
  ["violet-strong", "bg", TEXT],
  ["violet-strong", "violet-soft", TEXT],
  ["violet-strong", "glass/map", TEXT],
  ["on-violet", "violet", TEXT],
  ["violet", "glass/map", UI],
  ["focus", "bg", UI],
  ["focus", "glass/map", UI],
  ["control-border", "surface", UI],
  ...STATUSES.flatMap((s): [string, string, number][] => [
    [`${s}-ink`, `${s}-bg`, TEXT],
    [`${s}-ink`, "surface", TEXT],
    [`${s}-ink`, "glass/map", TEXT],
    [s, "surface", UI],
    [s, "glass/map", UI],
  ]),
];

function resolve(name: string): string {
  const backdrop = BACKDROPS[name as keyof typeof BACKDROPS];
  return backdrop ? backdrop() : token(name);
}

describe("design tokens (src/styles/tokens.css)", () => {
  it.each(PAIRS)("--%s on %s reaches %s:1", (fg, bg, min) => {
    expect(contrastRatio(resolve(fg), resolve(bg))).toBeGreaterThanOrEqual(min);
  });

  it("keeps the base text size at 17 px or more", () => {
    expect(CSS).toMatch(/font-size:\s*106\.25%/);
  });

  it("keeps touch targets at 44 px or more", () => {
    expect(token("target")).toMatch(/^max\(44px,/);
  });
});
