import { Inter, Plus_Jakarta_Sans } from "next/font/google";

/** Titles: Plus Jakarta Sans 600/700. Exposed as --font-jakarta (see --font-title in tokens.css). */
export const titleFont = Plus_Jakarta_Sans({
  subsets: ["latin"],
  weight: ["600", "700"],
  variable: "--font-jakarta",
  display: "swap",
});

/** Body text: Inter 400/500. Exposed as --font-inter (see --font-body in tokens.css). */
export const bodyFont = Inter({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-inter",
  display: "swap",
});
