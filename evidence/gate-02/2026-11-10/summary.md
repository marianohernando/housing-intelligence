# Gate 02 — PASS

- Fecha: 2026-11-10
- Commit: `f5589b7f8979e32792b32f69125a3c0bade439a7` (claude/sprint-1-public)
- Generado: 2026-11-10T18:47:12.334710+00:00 por `scripts/evidence.py`

- Alcance: Geospatial QA — transport stops and stations from the CRTM GTFS feeds (the 2026-10-20 geography QA lives in gate-01/2026-10-20).

| Check | Criterio | Resultado |
|---|---|---|
| geo-unit | CRS, bounds, H3, coordinate parsing and GTFS stop/station rules (unit + fixtures) | PASS |
| geo-integration | places and stops assigned to the section that contains them; no invalid geometry | PASS |
| transport-golden | golden stations: near the public landmark, right municipio and section, plausible service | PASS |
| transport-geometry | transport stops: 0 invalid, 0 outside region bounds, 0 CRS mismatch >1 m, 0 missed sections | PASS |
| section-assignment | at least 95% of transport stops inside a census section (the rest lie outside the region) | PASS |
| colocated-stops | duplicate control: official ids unique by constraint; co-located stops per feed reported | PASS |
| manual-sample | 20 stops sampled deterministically (md5 of id) for manual review | PASS |
| ci | CI green for HEAD | PASS |

Cada fila tiene su salida completa en `<check>.txt`. Entorno en `environment.json`.
