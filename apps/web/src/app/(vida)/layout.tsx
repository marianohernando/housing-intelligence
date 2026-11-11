import type { ReactNode } from "react";

import SiteHeader from "@/components/shell/SiteHeader";

import styles from "./layout.module.css";

/** Shell shared by the Vida Fácil pages: skip link, brand and tabs. */
export default function VidaLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <div className={styles.shell}>
      <a className="skip-link" href="#contenido">
        Saltar al contenido
      </a>
      <SiteHeader />
      <main id="contenido" tabIndex={-1} className={styles.main}>
        {children}
      </main>
    </div>
  );
}
