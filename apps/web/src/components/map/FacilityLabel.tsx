import { FACILITY_ICON, facilityLine } from "@/components/zone/FacilitiesPanel";
import type { Facility } from "@/lib/map/facilities";

import styles from "./VidaMap.module.css";

/** Glass label of the facility tapped on the map, like a key point: its type, name and, when known, capacity. Parks in green. */
export default function FacilityLabel({ facility }: { facility: Facility }) {
  const Icon = FACILITY_ICON[facility.type];
  const { label, rest } = facilityLine(facility);
  return (
    <div className={facility.type === "parque" ? `${styles.label} ${styles.park}` : styles.label} role="status">
      <span className={styles.labelIcon} aria-hidden="true">
        <Icon size={22} strokeWidth={2} />
      </span>
      <span className={styles.labelText}>
        <span className={rest ? styles.labelKind : styles.labelName}>{label}</span>
        {rest && <span className={styles.labelName}>{rest}</span>}
      </span>
      <span className={styles.labelPin} aria-hidden="true" />
    </div>
  );
}
