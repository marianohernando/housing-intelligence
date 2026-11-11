# Gate 01 — PASS

- Fecha: 2026-11-10
- Commit: `f59676bc18be54f9bdcdf7361f71b0f6c1b47827` (claude/sprint-1-public)
- Generado: 2026-11-10T19:39:05.556097+00:00 por `scripts/evidence.py`

- Alcance: Source / Bronze ingestion — 21 datasets of the Comunidad de Madrid open data portal (geography, 10 statistical tables, 4 facility registers, 6 CRTM GTFS feeds).

| Check | Criterio | Resultado |
|---|---|---|
| registry | Source/dataset/metric/pipeline registry valid | PASS |
| pipeline-unit | parsers deterministic, QA, null semantics, privacy filters (fixtures) | PASS |
| pipeline-integration | Bronze->Silver->PostGIS, skip on same checksum, last-valid survives broken ingestion | PASS |
| real-run-quality | latest full-region QA report PASS for 21 datasets | PASS |
| last-valid-versions | every dataset has a last-valid version with QA PASSED | PASS |
| idempotent-rerun | re-fetch every source: unchanged -> SKIPPED, changed -> new version, none FAILED | PASS |
| ci | CI green for HEAD | PASS |

Cada fila tiene su salida completa en `<check>.txt`. Entorno en `environment.json`.
