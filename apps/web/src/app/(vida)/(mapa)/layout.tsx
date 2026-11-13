import type { ReactNode } from "react";

import FacilityLayerProvider from "@/components/map/FacilityLayerProvider";
import GapLayerProvider from "@/components/map/GapLayerProvider";
import MapProvider from "@/components/map/MapProvider";
import VidaMap from "@/components/map/VidaMap";
import ScenarioProvider from "@/components/search/ScenarioProvider";
import MapSheet from "@/components/shell/MapSheet";

import styles from "./layout.module.css";

/**
 * Pages over the map (Mapa and Zona). The map stays mounted between them, so the camera can
 * fly from the 2D overview to a zone in 3D. On mobile the content goes in a bottom sheet.
 */
export default function MapaLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <ScenarioProvider>
      <MapProvider>
        <GapLayerProvider>
          <FacilityLayerProvider>
            <VidaMap />
            <div className={styles.overlay}>
              <MapSheet>{children}</MapSheet>
            </div>
          </FacilityLayerProvider>
        </GapLayerProvider>
      </MapProvider>
    </ScenarioProvider>
  );
}
