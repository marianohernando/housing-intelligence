# Board — Sprint 1 comprimido (10–18 nov 2026) · Demo para el formulario

Listas según `docs/11_engineering/24_trello_board_blueprint.md`. Una card pasa a DONE solo con gate + evidence.
Plan y criterios del jurado: `docs/09_datamad/25_plan_competicion.md`. Decisiones desde D-191. Protocolo de trabajo: `~/Desktop/DATAMAD/prompts/LINEAS.md` (4 líneas paralelas desde el 11 nov; este board lo escribe solo la línea A).
Última actualización: 2026-11-11 (tarde: contratos publicados y lista con datos reales por la API).

## Líneas paralelas (LINEAS.md)
| Línea | Rama | Alcance | Estado |
|---|---|---|---|
| **A** · datos, motor y API · integradora | `claude/sprint-1-public` | Contratos, CORE-005, GAP-001, CORE-006, CORE-003, rutas de la API, Supabase | **Contratos publicados: `7541527`** · lista de lo que falta por la API con datos reales (`2da5d4d`) · siguiente: CORE-005 Fase 3 |
| **B** · web de la demo | `claude/s1-web` | MAP-004 y PUB-001 (parte web) | Sin PR todavía |
| **C** · despliegue | `claude/s1-deploy` | OPS-001 (alojamiento de la API y la web) | Sin PR todavía |
| **D** · formulario y pitch | `claude/coord` | DATAMAD-FORM-01, PITCH-00x | Sin PR todavía |

Checkpoints: **13 nov** la lista de lo que falta sale por la API con datos reales · **15 nov** el buscador funciona con un perfil dorado · **16 nov (noche)** todo integrado con la web de B.

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

## 03 — CLAUDE CODE (en curso, línea A)
- **CONTRACTS** Contratos PUBLIC: `ScenarioState`, `SearchResult` (ranking, motivos y Reality Check) y `ZoneGapList` (FALTA / JUSTO / CUBIERTO / SIN DATOS). JSON Schema en `data/schemas/api/`, rutas en `docs/04_technical_architecture/31_public_api_routes.md` y fixtures reales en `data/fixtures/contracts/`. **Contratos publicados: `7541527`** · `evidence/gate-04/2026-11-11/phase-contracts-f1.txt`
- **CORE-005** Distancia a pie por sección censal y H3:
  - Fase 1 `4cdee28`: red peatonal OSM como dataset `osm_red_peatonal` (solo Silver; 2,38 M nodos y 57.659 km; componente principal del 98,25 %). Evidencia en `evidence/gate-01/2026-11-11`.
  - Fase 2 `e31770b`: dominio puro de accesibilidad con tests de propiedades (`evidence/gate-03/2026-11-11`).
  - Faltan la Fase 3 (método de features y 12 features en 3 niveles) y la Fase 4 (ejecución real y Gate 3).

- **GAP-001** Fase 0 `2da5d4d`, esqueleto andante. `GET /api/v1/gaps/{level}/{code}` responde con datos reales: filas de colegio y centro de salud por municipio, frente a la referencia regional (fila `ccaa` del Feature Store: total de la región / población). Las filas se declaran en el Feature Dictionary (`gap_row`). La migración 0004 guarda el enlace al portal CM e `is_cm_open_data`. Evidencia: `evidence/gate-04/2026-11-11/phase-gap001-f0.txt`. **Checkpoint del 13 nov adelantado para 2 filas: B ya puede integrar contra la API real.**

### Estado de la sesión del 11 nov (cierre)
- **Done:**
  - README con el tag `cf39459` y PR #1 a `main` (abierto; lo fusiona Mariano).
  - CORE-005 Fases 1 y 2.
  - Contratos publicados (`7541527`).
  - GAP-001 Fase 0 (`2da5d4d`).
  - La base local está en la migración 0004, con el catálogo sincronizado y las features recalculadas (incluidas las 3 filas regionales).
- **Blocked:** nada. Seguridad pendiente de Mariano: rotar el token `sbp_…` del MCP que se pegó en el chat.
- **Next (línea A), en orden:**
  1. CORE-005 Fase 3: método `network_walk_time` sobre `hi_domain.access`; 12 features (6 servicios × mediana de minutos y % de calle a ≤ N min) en sección, municipio y H3 r9; fixture OSM recortado; persist multinivel ya preparado.
  2. CORE-005 Fase 4: ejecución real, golden checks, Gate 3 y ADR D-199 (4,5 km/h; ventanas: transporte 5 min, salud 15 min y el resto 10 min).
  3. GAP-001 completo: filas de escuela infantil, mayores, farmacia y vivienda. Corregir el filtro de colegios (hoy incluye escuelas infantiles e IES). Añadir la distancia a pie como `extra_indicators`, la lista por sección y `GET /api/v1/gaps?level=&row=`. ADR de los cortes.
  4. CORE-006.
  5. CORE-003 con Reality Check.
  6. `POST /api/v1/search` (CORS con `POST`).
- **Para Supabase (17 nov):** `make supabase-migrate` (ya hay migración 0004) y después `make supabase-sync PROFILE=demo`.
- **Gate status:**
  - G1 PASS (21 datasets CM); la red OSM pasa su calidad.
  - G2 PASS.
  - G3: fases de CORE-005 en verde; el Gate 3 completo llega con la Fase 4.
  - G4: contratos y esqueleto de la lista en verde.
  - G6: Supabase en la migración 0003. Le falta la 0004 (se aplica el 17 nov o antes, si C despliega).
- **Notas para las siguientes cards:**
  - `colegios_publicos_por_1000_menores` cuenta también escuelas infantiles e institutos públicos (corregir en GAP-001; el `proxy_note` ya lo avisa).
  - Las farmacias salen en la capa «health» del mapa: separarlas en MAP-004 (línea B).
  - Unidades escolares: elegir el nivel de enseñanza, nunca sumar miembros.
  - La API devuelve los errores como `{"detail": {code, message}}`; `ErrorEnvelope` es el formato objetivo.
  - El `center` de Madrid usa `ST_PointOnSurface` (cae al norte del municipio). Si B centra el mapa con él, valorar usar el centroide cuando esté dentro.
  - La API depende ya de hi-domain, que arrastra scipy, shapely, pyproj y h3. C debe medirlo para el alojamiento.

## 02 — READY THIS SPRINT (en orden)
1. CORE-005 Fases 3 y 4 (ver 03) · G3 · 12–13 nov
2. GAP-001 Lista de lo que falta por zona: FALTA / JUSTO / CUBIERTO / SIN DATOS frente a la referencia regional por población, con confidence. Filas: escuela infantil, colegio, centro de salud, mayores, farmacia, vivienda (tamaño de los hogares frente a superficie de las viviendas) · G3/G4 · Fase 0 hecha el 11 nov (`2da5d4d`); completa el 13–14 nov · D-194
3. CORE-006 Affordability baseline: alquiler €/m² CM frente a presupuesto, con confidence · G4 · 14–15 nov
4. CORE-003 Residential Fit baseline + Reality Check: constraints PASS/FAIL/UNKNOWN → scoring → cuántas zonas aparecen al relajar cada condición · perfiles dorados · G4 · 15 nov
5. API-002 `POST /api/v1/search` sobre `ScenarioState` · 15–16 nov
6. MAP-004 / PUB-001: parte web en la línea B; la línea A da la API y la procedencia · 16 nov
7. OPS-001: el alojamiento es de la línea C. La línea A hace `make supabase-sync PROFILE=demo` el 17 nov y avisa a C para que vuelva a desplegar · G6
8. DATAMAD-FORM-01 Formulario (https://forms.gle/NyatKHN95aPxvQro8) · lo prepara la línea D y lo envía Mariano · 18 nov (límite real 19) · D-193

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
_(vacío)_

## 07 — DONE (con evidencia)
- CORE-001 Contrato ScenarioState mínimo (presupuesto, hogar, lugares de referencia, servicios cerca y prioridades), publicado con los contratos PUBLIC · G4 · `7541527` · `evidence/gate-04/2026-11-11/phase-contracts-f1.txt` · 2026-11-11
- DATAMAD-PUBLIC-01 Repo público en la misma URL, con el historial limpio de datos de contacto de los fixtures. El original queda en `housing-intelligence-archive` (privado y archivado, prueba de fechas). `pre-datamad` = `cf39459` (22 oct) · `evidence/gate-00/2026-11-11/public-repo.md` · D-195 · 2026-11-11
- DATA-016 Datasets CM nuevos: oficinas de farmacia (2.953 puntos, sin nombres de titulares), farmacias por municipio, unidades escolares (desde 2015), nacidos vivos y viviendas por régimen de tenencia. `cm_stat_table` gana `period_min` y `points_csv` gana `subcategory_value`/`name_template`. Total: 21 datasets del portal CM · G1 PASS `evidence/gate-01/2026-11-10` · 2026-11-10
- DATA-007 Transporte CRTM nivel A: 6 GTFS (también en el portal CM) → 14.982 paradas y estaciones con salidas/día, salidas en punta, headway, primer/último servicio y líneas · G1 `evidence/gate-01/2026-11-10/crtm_gtfs_*` · G2 PASS `evidence/gate-02/2026-11-10` (10/10 golden) · D-196 · 2026-11-10
- DATAMAD-PLAN-01 Plan de competición y criterios del jurado (`docs/09_datamad/25_plan_competicion.md`) · D-194/D-195 · 2026-11-10
- DATAMAD-TAG-01 Tag `pre-datamad` en `08cc526` (22 oct) y merge de PR #2 y #3 en `main` · 2026-11-10. Hoy el tag apunta a `cf39459` (D-198); `08cc526` solo existe en el repo archivado
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
