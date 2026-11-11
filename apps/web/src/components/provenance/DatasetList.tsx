"use client";

import { ExternalLink } from "lucide-react";

import Button from "@/components/ui/Button";
import { errorMessage } from "@/lib/errors";
import { datasetLines, sortDatasets } from "@/lib/provenance";

import styles from "./DatasetList.module.css";
import { useDatasets } from "./useDatasets";

// Copy from pitch/textos_web.md (fuente.*, error.reintentar). The loading line is provisional (pending line D).
const TEXT = {
  loading: "Cargando la lista de datos…",
  retry: "Reintentar",
  open: "Abrir en el portal",
};

/** Every dataset behind Vida Fácil (GET /api/v1/datasets): who publishes it, version, licence and link. */
export default function DatasetList() {
  const { loading, data, error, retry } = useDatasets();

  if (loading) return <p role="status">{TEXT.loading}</p>;
  if (error || !data) {
    return (
      <div role="alert" className={styles.error}>
        <p>{error ? errorMessage(error) : TEXT.loading}</p>
        <Button variant="secondary" onClick={retry}>
          {TEXT.retry}
        </Button>
      </div>
    );
  }
  return (
    <ul className={styles.list}>
      {sortDatasets(data.datasets).map((ref) => {
        const lines = datasetLines(ref);
        return (
          <li key={ref.dataset_id} className={styles.item}>
            <p className={styles.title}>{lines.title}</p>
            {lines.portal && <p className={styles.portal}>{lines.portal}</p>}
            {[lines.version, lines.license].filter(Boolean).map((line) => (
              <p key={line} className={styles.meta}>
                {line}
              </p>
            ))}
            {lines.url && (
              <a href={lines.url} target="_blank" rel="noopener noreferrer" aria-label={lines.openLabel} className={styles.link}>
                {TEXT.open}
                <ExternalLink size={16} aria-hidden="true" />
              </a>
            )}
          </li>
        );
      })}
    </ul>
  );
}
