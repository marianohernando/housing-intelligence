# Board — Sprint 1 comprimido (10–16 nov 2026) · PUBLIC core

Listas según `docs/11_engineering/24_trello_board_blueprint.md`. Una card pasa a DONE solo con gate + evidence.
Calendario vigente: D-192 (`docs/00_index/01_decisions_log.md`). Rama de trabajo: `claude/sprint-1-public`.
Última actualización: 2026-11-10.

## Calendario hasta la entrega
| Fechas | Bloque | Salida |
|---|---|---|
| 10–11 nov | Arranque | Tag `pre-datamad`, merge de P0/P1/POIs, licencia, board |
| 11–16 nov | PUBLIC core | Demo de principio a fin sin mocks críticos (G4/G5/G6 mínimo) |
| 16 nov (noche) | Cut review 1 | Si el PUBLIC core no está en verde, Housing Gap pasa a YELLOW |
| 17–20 nov | Diferenciador | Housing Gap municipal + API/MCP con 3–5 tools + demo desplegada |
| 21–22 nov | Cut review 2 | Clasificación GREEN/YELLOW/RED, pulido y snapshot offline |
| 23 nov | Freeze | Solo fixes, manifest final de fuentes, README |
| 24–25 nov | Pitch | 4 slides (§8 de las bases), ensayos de 5 min y 10 demos seguidas |
| 26 nov | Entrega | Antes de las 14:00 · presentaciones de 17:00 a 19:00 en URJC Vicálvaro |

## 03 — CLAUDE CODE (en curso)
_(vacío: la siguiente card es DATA-007)_

## 02 — READY THIS SPRINT (en orden)
1. DATA-007 CRTM GTFS (metro, EMT, cercanías, interurbanos, metro ligero) → paradas y frecuencias · G1/G2 · 11–12 nov
2. CORE-005 Features por sección censal y H3: accesibilidad a pie a colegios, salud, mayores y transporte · G3 · 12–13 nov
3. CORE-001 Contrato ScenarioState mínimo (perfil, presupuesto, anchors, prioridades) · G4 · 13 nov
4. CORE-006 Affordability baseline: alquiler €/m² CM frente a presupuesto, con confidence · G4 · 13–14 nov
5. CORE-003 Residential Fit baseline: constraints PASS/FAIL/UNKNOWN → scoring → golden profiles · G4 · 14–15 nov
6. MAP-004 PUBLIC map-first: chips y filtros sobre ScenarioState y ranking de zonas en el mapa · G6 · 15–16 nov
7. PUB-001 Explicación en lenguaje cotidiano y panel de procedencia (datasets CM usados) · G5/G7 · 16 nov

## 01 — BACKLOG (17–20 nov si el cut review 1 está en verde)
- CORE-008 Housing Gap municipal: qué vivienda necesita el territorio (hogares, tamaño, renta, oferta)
- API-001 / MCP-001 API versionada + 3–5 tools MCP sobre servicios de dominio (nunca SQL)
- OPS-001 Supabase remoto + despliegue de la demo (bloqueado por la contraseña)
- DATA-012 Panel de indicadores de distritos y barrios (Ayuntamiento)
- MAP-002 Resaltar selección, navegación por teclado y lista accesible (WCAG, Gate 6)
- MAP-003 Vector tiles para secciones censales (payload)
- DATA-013 Códigos postales (geometría) para cruzar alquiler por CP
- DATA-015 Zonas estadísticas de la Comunidad (sin geometría publicada; observaciones ya guardadas)
- DATA-008 Seccionado INE 2025 como actualización declarada de la geografía

## 06 — BLOCKED (decisión de Mariano)
- OPS-001 Supabase: todo preparado y simulado (`make supabase-migrate`, `make supabase-sync`). Falta `SUPABASE_DATABASE_URL` con la contraseña en `.env` (ver `.env.example`).

## 07 — DONE (con evidencia)
- DATAMAD-TAG-01 Tag `pre-datamad` en `08cc526` (22 oct) y merge de PR #2 y #3 en `main` · 2026-11-10
- LEGAL-001 Licencia: Apache-2.0 (código) + CC BY 4.0 (docs y catálogo) · D-191
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
- DATA-009 Equipamientos CM → place_master: 3.851 centros educativos, 1.543 de atención primaria y hospitales, 1.001 servicios para mayores · G1/G2 · `evidence/gate-01/2026-10-22`
- DATA-010 Alquiler €/m² por municipio y por código postal → metric_observation · G1
- DATA-011 Población (189.090 obs), hogares, viviendas por superficie y renta (3 métricas) · G1
- CORE-004 Feature Store: 12 features municipales con lineage, confidence y nulos explícitos · G3 (inicio) · `evidence/gate-03`
- MAP-002 Coropletas por municipio y capas de equipamientos · G6 (parcial) · `evidence/map-002/2026-10-22`

## 08 — CUT / LATER (D-192)
- PRO workspace, parcel analysis y Product Recommender
- ML, Place Model y embeddings
- Timeline histórico, scenario engine ampliado y 3D polish
- HomeFit por URL o dirección
- Chat con LLM (la demo usa chips y filtros sobre ScenarioState)
- DATA-014 POIs abiertos (Overture Places + FSQ OS Places) con Entity Resolution
- Catastro (INSPIRE) y geocoding de direcciones
- Google Maps vía Gosom — REJECTED, confirmado por Mariano (D-185)
