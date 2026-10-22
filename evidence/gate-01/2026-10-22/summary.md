# Gate 01 — FAIL

- Fecha: 2026-10-22
- Commit: `d2dabef0e48ede91181493909750034ea1d53cca` (claude/sprint-p1-cm-data)
- Generado: 2026-10-22T10:06:17.990855+00:00 por `scripts/evidence.py`

- Alcance: Source / Bronze ingestion — 10 datasets (geography, 6 statistical tables, 3 facility registers).

| Check | Criterio | Resultado |
|---|---|---|
| registry | Source/dataset/metric/pipeline registry valid | PASS |
| pipeline-unit | parsers deterministic, QA, null semantics, privacy filters (fixtures) | PASS |
| pipeline-integration | Bronze->Silver->PostGIS, skip on same checksum, last-valid survives broken ingestion | PASS |
| real-run-quality | latest full-region QA report PASS for 10 datasets | PASS |
| last-valid-versions | every dataset has a last-valid version with QA PASSED | PASS |
| idempotent-rerun | re-fetch + rerun of every pipeline with same content is SKIPPED | FAIL |
| ci | CI green for HEAD | FAIL |

Cada fila tiene su salida completa en `<check>.txt`. Entorno en `environment.json`.
