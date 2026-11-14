import { BedDouble } from "lucide-react";

import DependencyPill from "@/components/zone/DependencyPill";
import { FACILITY_ICON, facilityLine } from "@/components/zone/FacilitiesPanel";
import { type Facility, hospitalLine } from "@/lib/map/facilities";

import styles from "./VidaMap.module.css";

/** A hospital's label: the pill and its type (what a phone shows), then its name and beds, as in its list (centros.hospital.fila). */
function HospitalText({ facility }: { facility: Facility }) {
  const { dependency, name, notes, beds } = hospitalLine(facility);
  const kind = [facility.label, ...notes.filter((n) => n !== facility.label)].join(" · ");
  return (
    <span className={styles.labelText}>
      <span className={styles.labelKind}>
        {dependency && <DependencyPill dependency={dependency} />} {kind}
      </span>
      {facility.name && (
        <span className={styles.labelName}>
          {name}
          {beds && (
            <span className={styles.labelBeds}>
              {" · "}
              <BedDouble size={14} aria-hidden="true" />
              <span aria-hidden="true">{beds.short}</span>
              <span className="visually-hidden">{beds.full}</span>
            </span>
          )}
        </span>
      )}
    </span>
  );
}

/** Glass label of the facility tapped on the map, like a key point: its type, name and, when known, capacity. Parks in green. */
export default function FacilityLabel({ facility }: { facility: Facility }) {
  const Icon = FACILITY_ICON[facility.type];
  const { label, rest } = facilityLine(facility);
  return (
    <div className={facility.type === "parque" ? `${styles.label} ${styles.park}` : styles.label} role="status">
      <span className={styles.labelIcon} aria-hidden="true">
        <Icon size={22} strokeWidth={2} />
      </span>
      {facility.type === "hospital" ? (
        <HospitalText facility={facility} />
      ) : (
        <span className={styles.labelText}>
          <span className={rest ? styles.labelKind : styles.labelName}>{label}</span>
          {rest && <span className={styles.labelName}>{rest}</span>}
        </span>
      )}
      <span className={styles.labelPin} aria-hidden="true" />
    </div>
  );
}
