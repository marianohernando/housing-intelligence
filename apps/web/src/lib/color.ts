/** WCAG 2.2 contrast helpers (pure, unit tested). Used to keep the design tokens AA. */

export interface Rgba {
  r: number;
  g: number;
  b: number;
  a: number;
}

const HEX = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i;
const RGBA = /^rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*(?:,\s*(\d*\.?\d+)\s*)?\)$/i;

export function parseColor(color: string): Rgba {
  const value = color.trim();
  const hex = HEX.exec(value)?.[1];
  if (hex) {
    const full = hex.length === 3 ? [...hex].map((c) => c + c).join("") : hex;
    const [r, g, b] = [0, 2, 4].map((i) => Number.parseInt(full.slice(i, i + 2), 16)) as [number, number, number];
    return { r, g, b, a: 1 };
  }
  const rgba = RGBA.exec(value);
  if (rgba) {
    const [, r, g, b, a] = rgba;
    return { r: Number(r), g: Number(g), b: Number(b), a: a === undefined ? 1 : Number(a) };
  }
  throw new Error(`Unsupported colour: ${color}`);
}

function toHex({ r, g, b }: Rgba): string {
  return `#${[r, g, b].map((c) => Math.round(c).toString(16).padStart(2, "0")).join("")}`;
}

function channel(value: number): number {
  const srgb = value / 255;
  return srgb <= 0.04045 ? srgb / 12.92 : ((srgb + 0.055) / 1.055) ** 2.4;
}

export function relativeLuminance(color: string): number {
  const { r, g, b, a } = parseColor(color);
  if (a < 1) throw new Error(`Composite ${color} over its backdrop before measuring it`);
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

export function contrastRatio(foreground: string, background: string): number {
  const [light, dark] = [relativeLuminance(foreground), relativeLuminance(background)].sort((x, y) => y - x) as [
    number,
    number,
  ];
  return (light + 0.05) / (dark + 0.05);
}

/** The opaque colour seen when `color` (possibly translucent) lies over an opaque `backdrop`. */
export function compositeOver(color: string, backdrop: string): string {
  const top = parseColor(color);
  const bottom = parseColor(backdrop);
  if (bottom.a < 1) throw new Error(`Backdrop must be opaque: ${backdrop}`);
  const mix = (front: number, back: number) => front * top.a + back * (1 - top.a);
  return toHex({ r: mix(top.r, bottom.r), g: mix(top.g, bottom.g), b: mix(top.b, bottom.b), a: 1 });
}
