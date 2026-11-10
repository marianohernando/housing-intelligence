# Gate 01 — PASS

- Fecha: 2026-10-22
- Commit: `59db1615a6588db73d6c76d400ce1f3a2c814753` (claude/sprint-p1-cm-data)
- Generado: 2026-10-22T10:16:36.380525+00:00 por `scripts/evidence.py`

- Alcance: Source / Bronze ingestion — 10 datasets (geography, 6 statistical tables, 3 facility registers).

| Check | Criterio | Resultado |
|---|---|---|
| registry | Source/dataset/metric/pipeline registry valid | PASS |
| pipeline-unit | parsers deterministic, QA, null semantics, privacy filters (fixtures) | PASS |
| pipeline-integration | Bronze->Silver->PostGIS, skip on same checksum, last-valid survives broken ingestion | PASS |
| real-run-quality | latest full-region QA report PASS for 10 datasets | PASS |
| last-valid-versions | every dataset has a last-valid version with QA PASSED | PASS |
| idempotent-rerun | re-fetch every source: unchanged -> SKIPPED, changed -> new version, none FAILED | PASS |
| ci | CI green for HEAD | PASS |

Cada fila tiene su salida completa en `<check>.txt`. Entorno en `environment.json`.
