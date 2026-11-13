import "./globals.css";

import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import { bodyFont, titleFont } from "./fonts";

export const metadata: Metadata = {
  title: { default: "Vida Fácil · Encuentra tu sitio en Madrid", template: "%s · Vida Fácil" },
  description:
    "Qué zonas de la Comunidad de Madrid encajan con tu hogar y qué le falta a cada barrio, con datos abiertos.",
  applicationName: "Vida Fácil",
};

export const viewport: Viewport = { themeColor: "#f6f5fc" };

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="es" className={`${titleFont.variable} ${bodyFont.variable}`}>
      <body>{children}</body>
    </html>
  );
}
