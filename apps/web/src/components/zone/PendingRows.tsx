import { Clock } from "lucide-react";

import { pendingRows, ROW_NAME } from "@/lib/gaps";

// Copy from pitch/textos_web.md (falta.filas_pendientes). «Próximamente» is the label datamad-10 asked for.
const TEXT = {
  soon: "Próximamente",
  pending: "Estamos calculando el resto de servicios para esta zona.",
};

/**
 * Rows the API has not computed at this level yet (one INSUFFICIENT_DATA warning each). A row we
 * do not compute yet is not a missing value, so it is never painted as SIN DATOS.
 */
export default function PendingRows({ warnings, className }: { warnings: readonly string[] | undefined; className?: string }) {
  const rows = pendingRows(warnings);
  if (rows.length === 0) return null;
  const names = new Intl.ListFormat("es", { type: "conjunction" }).format(rows.map((key) => ROW_NAME[key].toLowerCase()));
  return (
    <p className={className}>
      <Clock size={16} aria-hidden="true" /> <strong>{TEXT.soon}:</strong> {names}. {TEXT.pending}
    </p>
  );
}
