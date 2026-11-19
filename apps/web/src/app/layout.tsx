import "./globals.css";

import { Analytics } from "@vercel/analytics/next";
import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import { bodyFont, titleFont } from "./fonts";

/**
 * Vercel Web Analytics: cookieless, aggregated page views (no personal data, no consent banner).
 * Only on the production deployment on Vercel. The offline demo package and local builds have no
 * /_vercel/insights endpoint, so loading the script there would only add console errors.
 */
const ANALYTICS_ON = process.env.NEXT_PUBLIC_VERCEL_ENV === "production";

const TITLE = "Vida Fácil · Encuentra tu sitio en Madrid";
const DESCRIPTION =
  "En qué zonas de la Comunidad de Madrid puedes vivir con tu presupuesto y con lo que necesitas cerca, y qué le falta a cada una, con datos abiertos.";

export const metadata: Metadata = {
  metadataBase: new URL("https://vidafacil-madrid.vercel.app"),
  title: { default: TITLE, template: "%s · Vida Fácil" },
  description: DESCRIPTION,
  applicationName: "Vida Fácil",
  openGraph: { siteName: "Vida Fácil", locale: "es_ES", type: "website", title: TITLE, description: DESCRIPTION },
  twitter: { card: "summary_large_image" },
};

export const viewport: Viewport = { themeColor: "#f6f5fc" };

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="es" className={`${titleFont.variable} ${bodyFont.variable}`}>
      <body>
        {children}
        {ANALYTICS_ON && <Analytics />}
      </body>
    </html>
  );
}
