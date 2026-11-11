import type { ReactNode } from "react";

import MapProvider from "@/components/map/MapProvider";
import VidaMap from "@/components/map/VidaMap";
import ScenarioProvider from "@/components/search/ScenarioProvider";

import styles from "./layout.module.css";

/**
 * Pages over the map (Mapa and Zona). The map stays mounted between them, so the camera can
 * fly from the 2D overview to a zone in 3D.
 */
export default function MapaLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <ScenarioProvider>
      <MapProvider>
        <VidaMap />
        <div className={styles.overlay}>{children}</div>
      </MapProvider>
    </ScenarioProvider>
  );
}
