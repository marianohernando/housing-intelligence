# Gate 03 — FAIL

- Fecha: 2026-10-22
- Commit: `d2dabef0e48ede91181493909750034ea1d53cca` (claude/sprint-p1-cm-data)
- Generado: 2026-10-22T10:06:35.488533+00:00 por `scripts/evidence.py`

- Alcance: Metrics / Feature Store — started: 12 municipal features (target 75–125 for Sprint P1).

| Check | Criterio | Resultado |
|---|---|---|
| dictionary | Feature Dictionary entries valid; no protected characteristics; methods implemented | PASS |
| methods | deterministic methods, null propagation, monotonicity (property tests) | PASS |
| invariants | computed values satisfy the invariants declared in each dictionary entry | PASS |
| coverage | 12 features x 179 municipios, null contract and lineage in the dev DB | PASS |
| ci | CI green for HEAD | FAIL |

Cada fila tiene su salida completa en `<check>.txt`. Entorno en `environment.json`.
