import type { ReactNode } from "react";

import ScenarioProvider from "@/components/search/ScenarioProvider";
import SiteHeader from "@/components/shell/SiteHeader";

import styles from "./layout.module.css";

/**
 * Shell shared by the Vida Fácil pages: skip link, brand and tabs. The search lives here, so it
 * survives going between the map, a zone and the list of zones.
 */
export default function VidaLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <ScenarioProvider>
      <div className={styles.shell}>
        <a className="skip-link" href="#contenido">
          Saltar al contenido
        </a>
        <SiteHeader />
        <main id="contenido" tabIndex={-1} className={styles.main}>
          {children}
        </main>
      </div>
    </ScenarioProvider>
  );
}
