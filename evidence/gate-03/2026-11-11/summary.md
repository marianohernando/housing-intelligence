# Gate 03 — PASS

- Fecha: 2026-11-11
- Commit: `ec126b077cf782bcc365ae54840b9a11d1303e60` (claude/sprint-1-public)
- Generado: 2026-11-11T16:15:06.357822+00:00 por `scripts/evidence.py`

- Alcance: Metrics / Feature Store — 12 municipal features (7 also by district of Madrid) and 12 walking-access features by census section, municipio and district (CORE-005).

| Check | Criterio | Resultado |
|---|---|---|
| dictionary | Feature Dictionary entries valid; no protected characteristics; methods implemented | PASS |
| methods | deterministic methods, null propagation, monotonicity (property tests) | PASS |
| invariants | computed values satisfy the invariants declared in each dictionary entry | PASS |
| coverage | 24 features with at least the 179 municipios, null contract and lineage in the dev DB | PASS |
| walk-coverage | 12 walking features x 4843 zones (4,417 sections, 179 municipios, 246 districts and the region), never 0 for a zone without streets (CORE-005) | PASS |
| walk-golden | golden zones within known bounds; median within the window <=> half the street or more | PASS |
| district-coverage | 7 features with the 21 districts of Madrid (D-200, D-209) | PASS |
| ci | CI green for HEAD | PASS |

Cada fila tiene su salida completa en `<check>.txt`. Entorno en `environment.json`.
