import localFont from "next/font/local";

/*
 * Served from the repo (src/fonts, latin subset of the variable fonts, SIL Open Font License 1.1
 * next to each file): the build and the demo never depend on Google Fonts being reachable.
 */

/** Titles: Plus Jakarta Sans 600/700. Exposed as --font-jakarta (see --font-title in tokens.css). */
export const titleFont = localFont({
  src: "../fonts/plus-jakarta-sans/PlusJakartaSansVariable-latin.woff2",
  weight: "600 700",
  variable: "--font-jakarta",
  display: "swap",
});

/** Body text: Inter 400/500. Exposed as --font-inter (see --font-body in tokens.css). */
export const bodyFont = localFont({
  src: "../fonts/inter/InterVariable-latin.woff2",
  weight: "400 500",
  variable: "--font-inter",
  display: "swap",
});
