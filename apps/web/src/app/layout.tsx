import "./globals.css";

import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import { bodyFont, titleFont } from "./fonts";

const TITLE = "Vida Fácil · Encuentra tu sitio en Madrid";
const DESCRIPTION =
  "Qué zonas de la Comunidad de Madrid encajan con tu hogar y qué le falta a cada barrio, con datos abiertos.";

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
      <body>{children}</body>
    </html>
  );
}
