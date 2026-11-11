# Board — Sprint 1 comprimido (10–18 nov 2026) · Demo para el formulario

Listas según `docs/11_engineering/24_trello_board_blueprint.md`. Una card pasa a DONE solo con gate + evidence.
Plan y criterios del jurado: `docs/09_datamad/25_plan_competicion.md`. Decisiones D-191 a D-195. Rama de trabajo: `claude/sprint-1-public` (solo la escribe la sesión de desarrollo).
Última actualización: 2026-11-10 (noche, cierre de DATA-007 y DATA-016).

## Calendario hasta la entrega
| Fechas | Bloque | Salida |
|---|---|---|
| 10 nov | Arranque | Tag `pre-datamad`, merge de P0/P1/POIs, licencia, plan y board |
| 11–16 nov | Demo core | Buscador para personas + lista de lo que falta por zona, con datos CM reales |
| 16 nov (noche) | Cut review 1 | Mariano prueba la demo 20 min; lo que no esté en verde se recorta |
| 17 nov | Demo pública | OPS-001: Supabase + despliegue; enlace estable con caso precargado |
| 18 nov | **Formulario** | Repo público (antes si hay algo enseñable) · Mariano envía el formulario (límite real 19 nov) |
| 19–22 nov | Mejoras | Tiempo a polos de empleo, MCP 3–5 tools, más datasets, accesibilidad · 22: cut review 2 |
| 23 nov | Freeze | Solo fixes, manifest final de fuentes, README |
| 24–25 nov | Pitch | 4 slides (§8), guion, vídeo de respaldo, banco de preguntas, 5 ensayos |
| 26 nov | Final | Slides antes de las 14:00 · presentaciones de 17:00 a 19:00 en URJC Vicálvaro |

## 03 — CLAUDE CODE (en curso)
_(vacío: la siguiente card es CORE-005)_

### Estado de la sesión del 10 nov (noche)
- **Done:** DATA-007 (transporte CRTM nivel A, D-196) y DATA-016 (5 datasets CM nuevos). En total hay 21 datasets del portal CM con Quality Gate.
- **Blocked:** OPS-001, porque falta la contraseña de Supabase en `.env` (antes del 17 nov). DATAMAD-PUBLIC-01, porque falta decidir qué hacer con el historial de fixtures con datos de contacto (el OK al email y a `docs/` llegó el 11 nov).
- **Next:** CORE-005, indicadores por sección y H3 (distancia a pie a escuela infantil, colegio, salud, farmacia, mayores y transporte). Hay que empezar proponiendo su plan de fases.
- **Gate status:** G1 PASS con 21 datasets (`evidence/gate-01/2026-11-10`). G2 PASS para transporte (`evidence/gate-02/2026-11-10`). Las features se recalcularon tras la re-ejecución, con 8 fuentes que publicaron datos nuevos (12×179, contrato de nulos íntegro). CI en verde.
- **Notas para las siguientes cards:**
  - `colegios_publicos_por_1000_menores` cuenta también escuelas infantiles e institutos públicos (corregir en GAP-001).
  - Las farmacias salen en la capa «health» del mapa: separarlas en MAP-004.
  - Unidades escolares: elegir el nivel de enseñanza, nunca sumar miembros.

## 02 — READY THIS SPRINT (en orden)
1. CORE-005 Indicadores por sección censal y H3: distancia a pie a escuela infantil, colegio, salud, farmacia, mayores y transporte · G3 · 12–13 nov
2. GAP-001 Lista de lo que falta por zona: FALTA / JUSTO / CUBIERTO frente a la referencia regional, con confidence. Filas: escuela infantil, colegio, centro de salud, mayores, farmacia, vivienda (tamaño de hogares frente a superficie de viviendas) · G3/G4 · 13–14 nov · D-194
3. CORE-001 Contrato ScenarioState mínimo (presupuesto, tamaño del hogar, lugar de trabajo, prioridades) · G4 · 15 nov
4. CORE-006 Affordability baseline: alquiler €/m² CM frente a presupuesto, con confidence · G4 · 15 nov
5. CORE-003 Residential Fit baseline + Reality Check: constraints PASS/FAIL/UNKNOWN → scoring → cuántas zonas aparecen al relajar cada condición · golden profiles · G4 · 15–16 nov
6. MAP-004 Demo map-first: chips sobre ScenarioState, ranking de zonas y vista de zona con su lista de lo que falta · G6 · 16 nov
7. PUB-001 Explicación en lenguaje cotidiano y panel de procedencia (datasets CM con enlace) · G5/G7 · 16 nov
8. OPS-001 Supabase remoto + despliegue de la demo con caso precargado · G6 · 17 nov
9. DATAMAD-PUBLIC-01 Repo público (checklist en §7 del plan) · como tarde 18 nov · D-195
10. DATAMAD-FORM-01 Formulario (https://forms.gle/NyatKHN95aPxvQro8) · lo envía Mariano · 18 nov (límite real 19) · D-193

## 01 — BACKLOG (19–22 nov, si el cut review 1 está en verde)
- CORE-009 Tiempo en transporte público a 5 polos de empleo (nivel B de transporte)
- DATA-017 Transacciones inmobiliarias (libre/protegida y nueva/usada) por municipio: trimestrales y solo con nombre de municipio → tipo de pipeline nuevo (periodo trimestral + resolución de nombre a código INE). Recortado de DATA-016: el objetivo de datasets CM ya se superó (21)
- MCP-001 / API-001 API versionada + 3–5 tools MCP sobre servicios de dominio (nunca SQL)
- MAP-002 Resaltar selección, navegación por teclado y lista accesible (WCAG, Gate 6)
- DATA-012 Panel de indicadores de distritos y barrios (Ayuntamiento)
- MAP-003 Vector tiles para secciones censales (payload)
- DATA-013 Códigos postales (geometría) para cruzar alquiler por CP
- DATA-015 Zonas estadísticas de la Comunidad (sin geometría publicada; observaciones ya guardadas)
- DATA-008 Seccionado INE 2025 como actualización declarada de la geografía

## 01b — PITCH (23–25 nov)
- PITCH-001 4 slides de §8 con el estilo del PDF del 31 oct
- PITCH-002 Guion de 5 min y banco de preguntas (§8 del plan)
- PITCH-003 Vídeo de respaldo de 2 min y snapshot offline de la demo
- PITCH-004 5 ensayos cronometrados (Mariano)

## 06 — BLOCKED (decisión de Mariano)
- OPS-001 Supabase: todo preparado y simulado (`make supabase-migrate`, `make supabase-sync`). Falta `SUPABASE_DATABASE_URL` con la contraseña en `.env` (ver `.env.example`). **Necesaria antes del 17 nov.**
- DATAMAD-PUBLIC-01 Mariano aceptó el 11 nov que el email de autor y `docs/` sean visibles. Los fixtures de HEAD ya no tienen datos de contacto, pero el historial del 20–22 oct sí (datos abiertos CM). Falta decidir si se publica con ese historial o se reescribe (§7 del plan).

## 07 — DONE (con evidencia)
- DATA-016 Datasets CM nuevos: oficinas de farmacia (2.953 puntos, sin nombres de titulares), farmacias por municipio, unidades escolares (desde 2015), nacidos vivos y viviendas por régimen de tenencia. `cm_stat_table` gana `period_min` y `points_csv` gana `subcategory_value`/`name_template`. Total: 21 datasets del portal CM · G1 PASS `evidence/gate-01/2026-11-10` · 2026-11-10
- DATA-007 Transporte CRTM nivel A: 6 GTFS (también en el portal CM) → 14.982 paradas y estaciones con salidas/día, salidas en punta, headway, primer/último servicio y líneas · G1 `evidence/gate-01/2026-11-10/crtm_gtfs_*` · G2 PASS `evidence/gate-02/2026-11-10` (10/10 golden) · D-196 · 2026-11-10
- DATAMAD-PLAN-01 Plan de competición y criterios del jurado (`docs/09_datamad/25_plan_competicion.md`) · D-194/D-195 · 2026-11-10
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

## 08 — CUT / LATER (D-192, D-194)
- Housing Gap como recomendador de producto residencial (la vivienda entra como fila de GAP-001)
- Empresas «qué abrir» calculado (solo slides + API/MCP)
- Zonas verdes (solo hay datos de Madrid capital)
- Necesidad declarada por usuarios agregada por zona (siguiente paso; nunca se simula)
- PRO workspace, parcel analysis, ML, embeddings, timeline, 3D polish, HomeFit, chat con LLM
- DATA-014 POIs abiertos (Overture + FSQ) con Entity Resolution
- Catastro (INSPIRE) y geocoding de direcciones
- Google Maps vía Gosom — REJECTED, confirmado por Mariano (D-185)
