# Gate 01 — PASS

- Fecha: 2026-10-20
- Commit: `6e635030a49de5324446e31364ba489711d63501` (claude/sprint-p0)
- Generado: 2026-10-20T11:37:32.135032+00:00 por `scripts/evidence.py`

- Alcance: Source / Bronze ingestion — scope: cm_secciones_censales (1 of 17 P0 datasets). Remaining P0 datasets are registered and licensed but not yet ingested.

| Check | Criterio | Resultado |
|---|---|---|
| registry | Source/dataset registry valid | PASS |
| pipeline-unit | parser deterministic + QA + H3 invariants (fixture) | PASS |
| pipeline-integration | Bronze->Silver->PostGIS, skip on same checksum, last-valid survives broken ingestion | PASS |
| real-run-quality | cm_secciones_censales full-region QA report PASS | PASS |
| last-valid-version | dataset_version marked last valid with QA PASSED | PASS |
| idempotent-rerun | re-fetch + rerun with same content is SKIPPED | PASS |
| ci | CI green for HEAD | PASS |

Cada fila tiene su salida completa en `<check>.txt`. Entorno en `environment.json`.
