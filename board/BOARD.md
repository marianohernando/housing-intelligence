# Board — Sprint P0 (20–25 oct 2026) · Control Tower + Data Recon

Listas según `docs/11_engineering/24_trello_board_blueprint.md`. Una card pasa a DONE solo con gate + evidence.
Última actualización: 2026-10-20 (sesión autónoma, rama `claude/sprint-p0`).

## 07 — DONE (con evidencia)
- ENG-001 Bootstrap monorepo · G0 · `evidence/gate-00/2026-10-20`
- ENG-002 Docker services (Postgres 17 + PostGIS 3.6 + pgvector 0.8, Redis) · G0
- ENG-003 CI + static checks (5 jobs en GitHub Actions) · G0
- ENG-004 DB migrations (Alembic 0001, up/down + drift) · G0
- QA-001 Gate 0 test harness (`scripts/evidence.py`) · G0
- DATA-001 Source Registry (8 fuentes, licencias revisadas) · G1
- DATA-002 Dataset Scorecard: 6.736 candidatos, 28 curados (17 P0, 10 P1), 120 borradores · G1
- DATA-003 Geografía canónica: 179 municipios, 246 distritos, 131 barrios, 4.417 secciones · G2 · `evidence/gate-01/2026-10-20`
- DATA-004 H3 r8/r9 (86.361 celdas, solape + centroide) · G2
- DATA-005 Primer dataset CM de Bronze a Silver con tests · G1
- DATA-006 QA geoespacial (CRS, validez 25830/4326, bounds, contención, golden points) · G2
- CORE-002 Golden user profiles (9) y golden Madrid zones (5) · G4
- DATAMAD-PREWORK-01 Resuelto por §6 de las bases (D-174)
- MAP-001 Map shell: API GeoJSON + MapLibre, zona seleccionable con procedencia · G6 (parcial) · `evidence/map-001/2026-10-20`

## 02 — READY THIS SPRINT (siguientes)
- DATA-007 CRTM GTFS (metro, EMT, cercanías, interurbanos, metro ligero) · G1/G2 · P0
- DATA-009 Centros educativos, sanitarios y de atención social (puntos) → PostGIS + H3 · G1/G2 · P0
- DATA-010 Alquiler €/m² por código postal y municipio → features de affordability · G1/G3 · P0
- DATA-011 Población, hogares, viviendas por superficie y renta municipal · G1/G3 · P0
- DATA-012 Panel de indicadores de distritos y barrios (Ayuntamiento) · G1 · P0

## 01 — BACKLOG
- DATA-014 POIs abiertos: Overture Places + FSQ OS Places para Madrid (bbox), Entity Resolution con censo de locales y OSM
- MAP-002 Resaltar selección, navegación por teclado y lista accesible (WCAG, Gate 6)
- MAP-003 Vector tiles para secciones censales (payload)
- DATA-008 Seccionado INE 2025 como actualización declarada de la geografía
- DATA-013 Códigos postales (geometría) para cruzar alquiler por CP
- CORE-001 ScenarioState contracts · G4
- CORE-003 Residential Fit baseline test harness · G4
- OPS-001 Supabase remoto: connection string + `alembic upgrade head` + carga de geografía
- LEGAL-001 Licencia open source del repo (propuesta Apache-2.0 código + CC BY 4.0 docs)

## 06 — BLOCKED (decisión de Mariano)
- OPS-001 necesita la connection string de Supabase (Session pooler) y aprobar el MCP `supabase-datamad`.
- LEGAL-001 necesita decisión de licencia.

## 08 — CUT / LATER
- Google Maps vía Gosom — REJECTED, confirmado por Mariano (D-185).
