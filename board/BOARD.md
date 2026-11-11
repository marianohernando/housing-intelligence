# Board — Vida Fácil · Sprint 1 comprimido (10–18 nov 2026) · Demo para el formulario

Listas según `docs/11_engineering/24_trello_board_blueprint.md`. Una card pasa a DONE solo con gate + evidence.
Plan y criterios del jurado: `docs/09_datamad/25_plan_competicion.md`. Decisiones desde D-191. Protocolo de trabajo: `~/Desktop/DATAMAD/prompts/LINEAS.md` (4 líneas paralelas desde el 11 nov; este board lo escribe solo la línea A).
Última actualización: 2026-11-11 (tarde: DATA-012 completa con `/gaps` por distrito, D-209; PR #4 y PR #5 de C integrados; Supabase en 0005 y sincronizado).

## Líneas paralelas (LINEAS.md)
| Línea | Rama | Alcance | Estado (11 nov, tarde) |
|---|---|---|---|
| **A** · datos, motor y API · integradora | `claude/sprint-1-public` | Contratos, DATA-012, CORE-005, GAP-001, CORE-006, CORE-003, rutas de la API, Supabase | **DATA-012 hecha** (`f62f0d0`…`be40c2f`): `/gaps/distrito` con filas reales en los 21 distritos (población del padrón, D-209). Contratos v2 en `2bcc35e`. Siguiente: peticiones de B para la API (warnings de `/gaps`, `/places` y `/geo/admin-units`) y CORE-005 F3 |
| **B** · web de la demo | `claude/s1-web` | MAP-004 y PUB-001 (parte web) | PR #2 (borrador): F1 hecha (`4402edd`). **Antes de su F2, rebase sobre `2bcc35e` y tipos desde `data/schemas/api/` (v2)** |
| **C** · despliegue | `claude/s1-deploy` | OPS-001 (alojamiento) | **PR #6 fusionado** (`877d4fd`): demo pública sobre Supabase con smoke 6/6 y reintento del smoke en `deploy.sh`. Antes, **PR #4 y PR #5 fusionados** (`c8ae262`, `d917162`): Vercel (web + API) en `vidafacil-madrid.vercel.app` (`vida-facil-eight` sigue de alias), readiness, smoke diario, guardas de deploy, paquete offline (5441/8012/3012) y rol `vf_api_ro` (migración 0005). Supabase en 0005 y sincronizado; Mariano ya puso `DATABASE_URL`. C despliega y pasa el smoke público |
| **D** · formulario y pitch | `claude/coord` | DATAMAD-FORM-01, PITCH-00x | PR #3 (borrador): formulario de 98 palabras, slides, guion y banco de preguntas. «Vida Fácil» está libre (TMview) |

**Respuestas de A a lo que piden las líneas (11 nov, noche):**
- **B (PR #2):**
  1. Nivel distrito: `GET /api/v1/gaps/distrito/{2807901–2807921}` ya responde con nombre y zona; las filas llegan con DATA-012. El buscador siempre usa municipios + distritos (D-200).
  2. Compra: `ScenarioState.budget = {kind: rent|buy, amount_eur}` (D-203).
  3. `GET /api/v1/datasets?cm_only=true` funciona: 22 datasets, 21 CM.
  4. CORS: la API admite `GET` y `POST`; los orígenes van en `CORS_ORIGINS` al arrancar.

  Además: `match_pct` + `facts` (D-202), `gap_highlights`, `all_zones` para la coropleta y `relaxed_scenario` en cada opción del Reality Check. Rutas y reglas en `docs/04_technical_architecture/31_public_api_routes.md`. Hay fixtures v2 en `data/fixtures/contracts/`.
- **D (PR #3):**
  1. Plan §1, §6 y §8 actualizados con «Vida Fácil» y el estilo nuevo.
  2. Títulos oficiales en el catálogo para los 6 GTFS y las secciones censales.
  3. Los 12 datasets CM que aún no alimentan nada se conectan así: farmacias, unidades escolares y nacidos vivos en GAP-001; los 6 GTFS en CORE-005 (transporte a pie) y GAP-001; tenencia en GAP-001 (vivienda); alquiler por código postal en CORE-006. Si alguno no llega el 16 nov, A lo avisa aquí para bajar la cifra.
  4. DATA-012 y las 6 filas de GAP-001 están comprometidas para el 16 nov (checkpoint del 13: la lista con datos reales).
  5. `/datasets` funciona.
- **C:** A convierte `vf_api_ro` en migración en cuanto llegue el PR. La API ya depende de hi-domain (scipy, shapely, pyproj y h3): conviene medirlo para el alojamiento. Supabase necesita `make supabase-migrate` (0004) antes de la siguiente carga.

Checkpoints: **13 nov** la lista de lo que falta sale por la API con datos reales · **15 nov** el buscador funciona con un perfil dorado · **16 nov (noche)** todo integrado con la web de B.

## Registro de progreso (lo más reciente arriba)
Una línea por fase cerrada, con el formato de LINEAS.md: línea · card y fase · gate · commit · evidencia · qué deja hecho. La escribe la línea A al cerrar cada fase propia y al integrar un PR de B, C o D. Lo anterior al 11 nov está en «07 — DONE».

| Fecha | Línea | Card · fase | Gate | Commit | Evidencia | Qué deja hecho |
|---|---|---|---|---|---|---|
| 11 nov | C → A | OPS-001 · PR #6 integrado | CI verde + gate local verde | `877d4fd` | `evidence/gate-06/2026-11-11-deploy/deploy-4-supabase-smoke.md`, `evidence/gate-06/2026-11-11/merge-pr6.txt` | Demo pública sobre Supabase con `vf_api_ro` (smoke 6/6). `deploy.sh` repite el smoke una vez a los 20 s; un fallo real sigue saliendo con 1 y la sugerencia de rollback. Revisado con `reviewer`: fusionar; pendiente menor de C: contarlo en `infra/deploy/README.md` |
| 11 nov | A | GAP-001 · Fase 0b (avisos por fila) | verde | `d3127d3` | `evidence/gate-04/2026-11-11/phase-gap001-f0b.txt` | `/gaps` trae un aviso por cada una de las 6 filas que aún no está calculada a ese nivel (`INSUFFICIENT_DATA: row <fila> not computed at <nivel> level yet`). Responde al punto 5 del PR #2 de B |
| 11 nov | A | DATA-012 · Fase 4 (revisión) | verde | `be40c2f` | `evidence/gate-01/2026-11-11/phase-data012-f4-review.txt` | Ajustes del `reviewer`: confidence por lugares sin sección, guarda contra un padrón truncado (±10 % por distrito), tests más estrictos y cobertura por distrito en el Gate 3 |
| 11 nov | C → A | OPS-001 · PR #5 integrado | CI verde | `d917162` | `evidence/gate-06/2026-11-11-deploy/` | URL `vidafacil-madrid.vercel.app`, guardas de deploy (R-07/R-08) y paquete offline aislado. Revisado con `reviewer` y con los 7 ajustes de C |
| 11 nov | A | DATA-012 · Fase 3 | verde | `d87c561` | `evidence/gate-01/2026-11-11/phase-data012-f3.txt` | Hogares por distrito (panel del Ayuntamiento, 2019–2025): los 21 distritos suman los 1.411.646 hogares de la ciudad. `tamano_medio_hogar` por distrito |
| 11 nov | A | DATA-012 · Fase 2 | verde | `83c74dd` | `evidence/gate-04/2026-11-11/phase-data012-f2.txt` | **`/gaps/distrito` con filas reales en los 21 distritos.** Ejemplos: Centro sale colegios CUBIERTO y salud JUSTO; Fuencarral-El Pardo, FALTA en las dos. 7 features por distrito con procedencia por nivel |
| 11 nov | A | DATA-012 · Fase 1 | verde | `f62f0d0` | `evidence/gate-01/2026-11-11/phase-data012-f1.txt` | Padrón por distrito en las bandas de edad de la CM: 3.535.868 personas (+1,68 % frente al censo, declarado, D-209). Nacionalidad y sexo nunca se guardan |
| 11 nov | A | OPS-001 · Fase A (migración 0005) | verde | `ad16393` | `evidence/gate-06/2026-11-11/phase-ops001-0005.txt` | Rol `vf_api_ro` como migración (D-208): solo lectura y una política `FOR SELECT` en las 7 tablas de la API. Test unitario contra la migración y test de integración del rol real. Base local en 0005 |
| 11 nov | C → A | OPS-001 · PR #4 integrado | CI verde | `c8ae262` | `evidence/gate-06/2026-11-11-deploy/` | Despliegue en Vercel con un comando, `/api/v1/health/ready`, smoke diario (activo cuando llegue a `main`). Revisado con `reviewer`: sin bloqueantes |
| 11 nov | A | CONTRACTS · Fase 2 (v2) | verde | `2bcc35e` | `evidence/gate-04/2026-11-11/phase-contracts-f2.txt` | **Contratos v2 de Vida Fácil** (D-199 a D-207): compra o alquiler, hogar, 6 prioridades, distritos de Madrid, % de encaje con hechos y Reality Check aplicable. `/gaps` acepta distrito; nuevas `/datasets` y CORS con `POST`; títulos oficiales en el catálogo; plan §1, §6 y §8 |
| 11 nov | A | Mantenimiento | — | `d4a03dd` | — | Token `sbp_…` del MCP rotado (lo confirma Mariano). El MCP `supabase-datamad` sigue respondiendo: 14 tablas con RLS y perfil demo |
| 11 nov | A | GAP-001 · Fase 0 (esqueleto andante) | verde | `2da5d4d` | `evidence/gate-04/2026-11-11/phase-gap001-f0.txt` | `GET /api/v1/gaps/{level}/{code}` con datos reales: colegio y centro de salud por municipio frente a la referencia regional. Madrid: FALTA en los dos (1,56 frente a 2,18 y 0,37 frente a 0,59). Migración 0004 |
| 11 nov | A | Organización | — | `c0faef8` | — | Cuatro líneas paralelas (LINEAS.md); el board recoge las cuatro |
| 11 nov | A | CONTRACTS · Fase 1 | verde | `7541527` | `evidence/gate-04/2026-11-11/phase-contracts-f1.txt` | **Contratos publicados**: `ScenarioState`, `SearchResult` con Reality Check y `ZoneGapList`. JSON Schema en `data/schemas/api/`, rutas en docs/04/31 y fixtures reales. Cierra CORE-001 |
| 11 nov | A | CORE-005 · Fase 2 | verde | `e31770b` | `evidence/gate-03/2026-11-11/phase-core005-f2.txt` | Distancia a pie al servicio más cercano por zona (Dijkstra con scipy; 0,3 s para todas las farmacias). Tests de propiedades |
| 11 nov | A | CORE-005 · Fase 1 | verde | `4cdee28` | `evidence/gate-01/2026-11-11/phase-core005-f1.txt` | Red peatonal de OSM como dataset `osm_red_peatonal`: 2,38 M nodos, 57.659 km, componente principal del 98,25 % |
| 11 nov | A | DATAMAD-PUBLIC-01 · Fase 0 | verde | `9356b2d` | `evidence/gate-00/2026-11-11/phase-readme-f0.txt` | El README cita el tag `cf39459` y el repo archivado. PR #1 a `main` abierto (lo fusiona Mariano) |
| 11 nov | A | OPS-001 · parte Supabase | verde | `114023a` | `evidence/gate-06/2026-11-11` | RLS en todas las tablas (D-197) y perfil demo cargado (100 MB) |
| 11 nov | A | DATAMAD-PUBLIC-01 | verde | `6ac1cbc` | `evidence/gate-00/2026-11-11/public-repo.md` | Repo público con el historial limpio (D-198) |
| 10 nov | A | DATA-016 · Fase 4b | G1 PASS | `9180539` | `evidence/gate-01/2026-11-10` | 21 datasets CM con Quality Gate |
| 10 nov | A | DATA-007 · Fase 4b | G2 PASS | `b19869b` | `evidence/gate-02/2026-11-10` | Transporte CRTM: 14.982 paradas y estaciones con frecuencias (D-196) |

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

- **GAP-001** Fase 0 `2da5d4d`, esqueleto andante (y por distrito desde DATA-012 F2, `83c74dd`). `GET /api/v1/gaps/{level}/{code}` responde con datos reales: filas de colegio y centro de salud por municipio, frente a la referencia regional (fila `ccaa` del Feature Store: total de la región / población). Las filas se declaran en el Feature Dictionary (`gap_row`). La migración 0004 guarda el enlace al portal CM e `is_cm_open_data`. Evidencia: `evidence/gate-04/2026-11-11/phase-gap001-f0.txt`. **Checkpoint del 13 nov adelantado para 2 filas: B ya puede integrar contra la API real.**

### Estado de la sesión del 11 nov (tarde, relevo de la línea A)
- **Done (esta sesión):**
  - PR #4 de C integrado (`c8ae262`) y migración 0005 del rol `vf_api_ro` (`ad16393`, D-208).
  - **DATA-012 completa** (D-209). Commits:
    - F1 `f62f0d0`: padrón por distrito en bandas CM;
    - F2 `83c74dd`: features por distrito y `/gaps/distrito` con filas reales;
    - F3 `d87c561`: hogares por distrito;
    - F4 `be40c2f`: ajustes del `reviewer`.
  - PR #5 de C integrado (`d917162`): URL `vidafacil-madrid.vercel.app`, guardas de deploy y paquete offline, revisado con `reviewer`.
  - Supabase comprobado por MCP tras el sync de Mariano: alembic 0005, 7 políticas de `vf_api_ro`, `feature_value` 2.298 (147 de distrito = 7 features × 21) y los 2 datasets del Ayuntamiento como no CM.
  - La base local está en la 0005, con el padrón y el panel ingeridos y las features recalculadas.
- **Blocked:** nada. Mariano fusionó el PR #1 en `main` (`2107119`); el siguiente paso a `main` lo decide él.
- **Next (línea A), en orden:**
  1. ~~`/gaps`: un warning por cada fila esperada que no esté~~ → hecho en `d3127d3` (GAP-001 F0b).
  2. **Peticiones de B para la API** (PR #2), mejor antes del 14 nov:
     - `/places` corta en 10.000 resultados (transporte tiene 14.982) y no filtra: añadir `?admin_unit_id=` y `?subcategory=`;
     - `/geo/admin-units`: nombres de municipio con mayúsculas normales y filtro por padre (p. ej. los distritos de Madrid).
  3. CORE-005 Fase 3: método `network_walk_time` sobre `hi_domain.access`; 12 features (6 servicios × mediana de minutos y % de calle a ≤ N min) en sección, municipio y H3 r9, también por distrito con `formula.levels`; fixture OSM recortado.
  4. CORE-005 Fase 4: ejecución real, golden checks y Gate 3. ADR nuevo (D-199 ya es el nombre del producto): 4,5 km/h; ventanas: transporte 5 min, salud 15 min y el resto 10 min. D pide confirmar los 4,5 km/h.
  5. GAP-001 completo: filas de escuela infantil, mayores, farmacia y vivienda. Corregir el filtro de colegios (hoy incluye escuelas infantiles e IES). Añadir la distancia a pie como `extra_indicators`, la lista por sección y `GET /api/v1/gaps?level=&row=`. ADR de los cortes.
     - Por distrito: la vivienda queda SIN DATOS, porque no hay superficie de viviendas por distrito.
     - D pide, en lenguaje llano, qué mide cada fila nueva y si los cortes 0,8 / 1,0 cambian.
  6. CORE-006: D pide los m² que se suponen según el tamaño del hogar.
  7. CORE-003 con Reality Check: D pide cómo se reparten los pesos y cómo se pasa a %, con el caso de la Castellana, y el presupuesto con el que el caso de ejemplo hace aparecer el Reality Check.
  8. `POST /api/v1/search`; los distritos entran en `all_zones`.
- **Peticiones abiertas de otras líneas:**
  - **D:** conectar los 12 datasets CM que aún no alimentan nada (6 GTFS, 2 de farmacias, nacidos vivos, unidades escolares, viviendas por tenencia y alquiler por código postal) y la zona real para el bloque 3 del guion.
  - **B:** los JSON Schema se exportan en modo validación, así que `near_misses`, `meta` y `warnings` salen opcionales en TypeScript; valorar el modo serialización.
- **Para Supabase:** migrate y sync hechos por Mariano el 11 nov. Tras cada cambio de features o de lugares, pedir a Mariano `make supabase-sync PROFILE=demo` (las sesiones no pueden) y comprobarlo después por MCP.
- **Gate status:**
  - G1 PASS: 21 datasets CM y 2 complementarios del Ayuntamiento (padrón y panel); la red OSM pasa su calidad.
  - G2 PASS.
  - G3: fases de CORE-005 en verde, coverage `12|0|0|179` y la nueva comprobación por distrito (7 features × 21) en verde. El Gate 3 completo llega con CORE-005 F4.
  - G4: contratos y `/gaps` (municipio y distrito) en verde; fixture `zone_gap_list.centro` para B.
  - G6: Supabase en 0005 y sincronizado. C está desplegando con `vf_api_ro` en `vidafacil-madrid.vercel.app`.
- **Notas para las siguientes cards:**
  - `colegios_publicos_por_1000_menores` cuenta también escuelas infantiles e institutos públicos (corregir en GAP-001; el `proxy_note` ya lo avisa).
  - Las farmacias salen en la capa «health» del mapa: separarlas en MAP-004 (línea B).
  - Unidades escolares: elegir el nivel de enseñanza, nunca sumar miembros.
  - La API devuelve los errores como `{"detail": {code, message}}`; `ErrorEnvelope` es el formato objetivo.
  - El `center` de Madrid usa `ST_PointOnSurface` (cae al norte del municipio). Si B centra el mapa con él, valorar usar el centroide cuando esté dentro.
  - **Features por nivel** (DATA-012):
    - `formula.levels.<nivel>` es un override superficial (puede cambiar el método);
    - `FeatureSource.levels` dice qué datasets cita cada nivel;
    - los lugares llegan a un distrito por su sección censal, y si a un municipio le faltan secciones, la confidence baja;
    - la referencia regional sale solo del nivel base. CORE-005 y GAP-001 deben usar este mecanismo para los distritos.
  - `places_per_population` declara `geocoding_quarantine` en `confidence.inputs`, pero no lo aplica (deuda anterior a DATA-012).

## 02 — READY THIS SPRINT (en orden)
1. API para B: un warning por cada fila de `/gaps` que falte; `/places` con `?admin_unit_id=` y `?subcategory=` y sin el corte de 10.000; `/geo/admin-units` con nombres en mayúsculas normales y filtro por padre · G4 · 12 nov
2. CORE-005 Fases 3 y 4 (ver 03); los indicadores salen también por distrito · G3 · 12–13 nov
3. GAP-001 Lista de lo que falta por zona: FALTA / JUSTO / CUBIERTO / SIN DATOS frente a la referencia regional por población, con confidence. Filas: escuela infantil, colegio, centro de salud, mayores, farmacia, vivienda (tamaño de los hogares frente a superficie de las viviendas) · G3/G4 · Fase 0 hecha el 11 nov (`2da5d4d`); completa el 13–14 nov, también por distrito · D-194
4. CORE-006 Affordability baseline: alquiler €/m² CM frente a presupuesto, con confidence · G4 · 14–15 nov
5. CORE-003 Residential Fit baseline + Reality Check: constraints PASS/FAIL/UNKNOWN → scoring → cuántas zonas aparecen al relajar cada condición · perfiles dorados · G4 · 15 nov
6. API-002 `POST /api/v1/search` sobre `ScenarioState` · 15–16 nov
7. MAP-004 / PUB-001: parte web en la línea B; la línea A da la API y la procedencia · 16 nov
8. OPS-001: el alojamiento es de la línea C. La línea A hace `make supabase-sync PROFILE=demo` el 17 nov y avisa a C para que vuelva a desplegar · G6
9. DATAMAD-FORM-01 Formulario (https://forms.gle/NyatKHN95aPxvQro8) · lo prepara la línea D y lo envía Mariano · 18 nov (límite real 19) · D-193

## 01 — BACKLOG (19–22 nov, si el cut review 1 está en verde)
- DATA-018 Zonas verdes: inventario del Ayuntamiento (Madrid capital) + parques de OSM (ODbL) en el resto (D-205)
- DATA-019 Accesibilidad física: instalaciones accesibles del Ayuntamiento + `wheelchair_boarding` de metro y cercanías; el resto, SIN DATOS (D-205)
- DATA-020 Seguridad: actuaciones de la Policía Municipal por distrito por cada 1.000 habitantes; nunca características de personas ni «peligroso»; fuera de Madrid, SIN DATOS (D-205)
- DATA-021 Precio de compra: fuente oficial abierta por municipio (por ejemplo, el valor tasado del Ministerio de Vivienda), con confidence baja; si no hay una fiable, SIN DATOS (D-203)
- CORE-009 Tiempo en transporte público a 5 polos de empleo (nivel B de transporte)
- DATA-017 Transacciones inmobiliarias (libre/protegida y nueva/usada) por municipio: trimestrales y solo con nombre de municipio → tipo de pipeline nuevo (periodo trimestral + resolución de nombre a código INE). Recortado de DATA-016: el objetivo de datasets CM ya se superó (21)
- MCP-001 / API-001 API versionada + 3–5 tools MCP sobre servicios de dominio (nunca SQL)
- MAP-002 Resaltar selección, navegación por teclado y lista accesible (WCAG, Gate 6)
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
- DATA-012 Población por edad y hogares por distrito de Madrid (D-200, D-209): padrón municipal (21 distritos × 21 bandas CM + total; nacionalidad y sexo nunca se guardan) y panel de distritos (hogares, 2019–2025), complementarios y no CM. 7 features por distrito y `/gaps/distrito` con filas reales en los 21 distritos · G1 `evidence/gate-01/2026-11-11/phase-data012-f1.txt`, `-f3.txt` y `-f4-review.txt` · G4 `evidence/gate-04/2026-11-11/phase-data012-f2.txt` · `f62f0d0` `83c74dd` `d87c561` `be40c2f` · 2026-11-11
- OPS-001 (parte de A): PR #4 y PR #5 de C integrados con `reviewer`; migración 0005 del rol `vf_api_ro` (D-208) · `evidence/gate-06/2026-11-11/phase-ops001-0005.txt` · `c8ae262` `ad16393` `d917162` · 2026-11-11
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
