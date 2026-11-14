# Board — Vida Fácil · Sprint 1 comprimido (10–18 nov 2026) · Demo para el formulario

Listas según `docs/11_engineering/24_trello_board_blueprint.md`. Una card pasa a DONE solo con gate + evidence.
Plan y criterios del jurado: `docs/09_datamad/25_plan_competicion.md`. Decisiones desde D-191. Protocolo de trabajo: `~/Desktop/DATAMAD/prompts/LINEAS.md` (4 líneas paralelas desde el 11 nov; este board lo escribe solo la línea A).
Última actualización: 2026-11-13 (A v15: D-232 barrios dentro de un distrito, `fit-0.7`, `POST /api/v1/search/barrios`; pendiente: sync y despliegue, y decidir con Mariano la fase 2 de barrios). **Formulario enviado (12 nov).**

## Líneas paralelas (LINEAS.md)
| Línea | Rama | Alcance | Estado (11 nov, tarde) |
|---|---|---|---|
| **A** · datos, motor y API · integradora | `claude/sprint-1-public` | Contratos, DATA-012, CORE-005, GAP-001, CORE-006, CORE-003, rutas de la API, Supabase | **DATA-012 hecha** (`f62f0d0`…`be40c2f`): `/gaps/distrito` con filas reales en los 21 distritos (población del padrón, D-209). Contratos v2 en `2bcc35e`. Siguiente: peticiones de B para la API (warnings de `/gaps`, `/places` y `/geo/admin-units`) y CORE-005 F3 |
| **B** · web de la demo | `claude/s1-web` | MAP-004 y PUB-001 (parte web) | PR #2 (borrador): F1 hecha (`4402edd`). **Antes de su F2, rebase sobre `2bcc35e` y tipos desde `data/schemas/api/` (v2)** |
| **C** · despliegue | `claude/s1-deploy` | OPS-001 (alojamiento) | **PR #7 fusionado** (`93af627`): el README cuenta el reintento del smoke y el smoke mide la página 1 de transporte (7/7 en producción con `879101a`; offline 6/6). Pendiente menor: exigir también `.data.pages >= 1` en el check `largest`. **PR #6 fusionado** (`877d4fd`): demo pública sobre Supabase con smoke 6/6 y reintento del smoke en `deploy.sh`. Antes, **PR #4 y PR #5 fusionados** (`c8ae262`, `d917162`): Vercel (web + API) en `vidafacil-madrid.vercel.app` (`vida-facil-eight` sigue de alias), readiness, smoke diario, guardas de deploy, paquete offline (5441/8012/3012) y rol `vf_api_ro` (migración 0005). Supabase en 0005 y sincronizado; Mariano ya puso `DATABASE_URL`. C despliega y pasa el smoke público |
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
| 14 nov | A+B | W1 · comprar en Madrid capital (D-234, `fit-0.8`) | verde | (este PR) | `evidence/gate-04/2026-11-14/compra-estimada.md`, `golden-search-compra-estimada.txt` (9/9), `evidence/gate-01/2026-11-14/ayto_panel_indicadores_distritos_barrios/`, `evidence/gate-06/2026-11-14-buy-estimate/` | Precio de compra estimado en los 21 distritos y 131 barrios: el valor tasado de Madrid repartido por valor catastral/m² (confidence 0,5, «Dato aproximado», «precio estimado» en cada texto). Validado frente a anuncios: Spearman 0,95 en 12 distritos, ningún error > 30 %. El Reality Check solo culpa a lo que FALLA (`unknown_by_constraint` aparte): con «Comprar» ya no ofrece «+40.000 €» por falta de precio, y la web dice el motivo. El precio de cada zona va a la vista en las filas y en la tarjeta. Pareja con 400.000 €: Tetuán «casi» (≈ 411.000 €), Valdeacederas y Berruguete cumplen. Invariante: 27 zonas, Latina 98 %. **Desplegar → recalcular en `housing` → sincronizar → smoke** |
| 13 nov | A | BARRIO-001 · Fase 2b (revisión con `reviewer`) | verde | `01fbf1e` | `evidence/gate-04/2026-11-12/barrios-gate.txt` | Sin bloqueantes. Un trayecto prestado del distrito nunca decide un límite (`UNKNOWN`); el texto del alquiler que falta sigue al motivo real (`SOURCE_NO_COVERAGE` sin lugares, `SOURCE_MISSING` sin alquiler publicado); tope 0,3 por lugares con valor; distrito sin barrios con aviso. Sin cambio de datos. |
| 12 nov | A | BARRIO-001 · Fase 2 (ruta, `fit-0.7`, D-232) | verde | `788f938` | `evidence/gate-04/2026-11-12/golden-search-barrios.txt` | `POST /api/v1/search/barrios {scenario, distrito}` → `BarrioSearchResult` (= `SearchResult` + `distrito`). Familia demo en San Blas-Canillejas: 7 de 8 barrios cumplen, Simancas 97 %, Rejas «casi» (colegio a 35 min). Golden 9/9; la búsqueda regional no cambia. Tipos TS generados para B |
| 12 nov | A | BARRIO-001 · Fase 1 (datos de barrio, D-232) | verde | `19bf8bd` | `evidence/gate-03/2026-11-12/barrios-datos.md`, `evidence/gate-01/2026-11-12/official_names/` | 131 barrios: nombres oficiales del panel del Ayuntamiento (17 cambios, Ambroz → Valdebernardo y los 3 sin nombre), minutos a pie (15 features, 131/131), alquiler por sus códigos postales (130/131, Sol sin dato) y trayectos (+75.849 filas). Base local recalculada |
| 12 nov | A | MEJORA-10 · Fase 4b (fixture de datasets con la AEAT) | verde | `983d225` | — | Petición de `datamad-10` para el `pie.aeat` de B (ya fusionado en `e7d4fa3`) |
| 12 nov | A | MEJORA-10 · Fase 4 (fuentes, D-231) | verde | (este commit) | `evidence/gate-04/2026-11-12/fuentes-gate.txt` | `source_name` en cada `DatasetRef` (padrón y panel: «Portal de Datos Abiertos del Ayuntamiento de Madrid»; OSM: «OpenStreetMap (extracto Geofabrik Madrid)»; CM y CRTM vía portal CM). Las 2 tablas de camas (solo total regional) pasan a features de región `camas_instaladas_por_1000_hab` (3,0) y `hospitales_total` (85). **B:** «en {source_name}» en vez de «en el portal de datos» y la línea de camas en la nota del hospital. Sync en cualquier orden (2 features nuevas). |
| 12 nov | A | MEJORA-7 · Fase 3 (zonas pequeñas, D-230) | verde | (este commit) | `evidence/gate-04/2026-11-12/zonas-pequenas.md`, `zonas-pequenas-gate.txt` | «No comparable: aquí viven muy pocos … para saber si falta» en zonas poco fiables sin grupo (La Acebeda, colegio: 0,0 frente a 28,0). Vivienda: el denominador (hogares de 4+) también necesita 3,69 → La Acebeda y otro municipio pasan a poco fiables; ninguna FALTA cambia. 0 niños → `NOT_APPLICABLE` con «No viven niños de 0 a 4 años…». Recalculadas las 5 features 2SFCA (mismos valores). **B:** pintar «No comparable» con `reliable: false` sin grupo y la `explanation` de `NOT_APPLICABLE`. Sync en cualquier orden. |
| 12 nov | A | MEJORA-8 · Fase 2b (revisión con `reviewer`) | verde | (este commit) | `evidence/gate-04/2026-11-12/alquiler-nuevo-review-gate.txt` | Sin bloqueantes. Valor y factor del mismo año (si no, el cálculo se para) y test de que la nota dice el año de la AEAT; página con un solo «Ejercicio» y fila de la Comunidad obligatoria; golden familia a 41 min. Sin cambio de datos. |
| 12 nov | A | MEJORA-8 · Fase 2 (alquiler de contratos nuevos, opción A de D-228; `fit-0.6`) | verde | (este commit) | `evidence/gate-04/2026-11-12/alquiler-nuevo-gate.txt`, `golden-search-alquiler-nuevo.txt`, `evidence/gate-01/2026-11-12/aeat_alquiler_nuevos_contratos_*` | Fuente complementaria `agencia_tributaria` (no CM) y pipeline `aeat_rent_comparison` (HTML; 37 municipios y 54 códigos postales). `alquiler_m2_mensual` v3 = €/m² CM × factor de contratos nuevos de la misma zona (fallback declarado: Comunidad o Madrid). Fuencarral 1.107 → 1.276 €, Salamanca 1.465 → 1.797 € (77 m²); +150 € añade 3 zonas en el caso demo. Nota «contratos firmados en 2024» en `fit.note` (viaja con el dato). Hechos a pie: «a unos N min andando». Golden 8/8 (dos límites de minutos a 45, con dos comprobaciones nuevas). **Desplegar `fit-0.6` y después sincronizar.** |
| 12 nov | A | MEJORA-3 · Fase 2b (revisión con `reviewer`) | verde | (este commit) | `evidence/gate-04/2026-11-12/impact-review-gate.txt` | Sin bloqueantes. El % del resumen sale de la misma cuota acotada que `share_in_falta`; `p_value` se redondea hacia abajo (nunca 0,025 en una FALTA); `zones` documentado (incluye SIN DATOS). |
| 12 nov | A | MEJORA-3 · Fase 2 (cifras de impacto, D-229) | verde | (este commit) | `evidence/gate-04/2026-11-12/impact-cifras.txt`, `impact-gate.txt` | `GET /api/v1/gaps/impact` (`impact-0.1`): por fila, la gente que vive donde falta y el ranking «dónde invertir primero» con su ratio y `p_value`; `people` en cada fila de `/gaps`. Escuelas infantiles: 25.551 niños de 0–4 (9,8 %) en Puente de Vallecas, Carabanchel y Villaverde. Farmacias: 667.172 personas (9,4 %) en 5 municipios. Mayores: 54.581 (4,1 %) en 6. Vivienda: 99.483 hogares de 4+ (14,8 %) en 25. Tipos de la web regenerados (`src/contracts`). Sin sync: los datos ya están. |
| 12 nov | A | MEJORA-8 · Fase 1 (alquiler de contratos nuevos, D-228) | verde (sin código) | (este commit) | `evidence/gate-01/2026-11-12/alquiler-contratos-nuevos/evaluacion.md` | El índice CM 1934428 es el IPVA del INE para la CM (2015 = 100, nuevo y existente, 2021–2024, sin municipios): no da el nivel de un contrato nuevo. Alternativa oficial: la tabla de nuevos contratos de la AEAT (IRPF 2024, 37 municipios y 54 códigos postales de Madrid, factor de 1,05 a 1,26). **Pendiente de Mariano: opción A (factor) o B (aviso).** |
| 12 nov | A | DATA-021 · Fase 1b (revisión con `reviewer`) + README | verde | `f29ebec` | `evidence/gate-04/2026-11-12/data021-f1b-gate.txt` | README (petición de `datamad-10`): 26 datasets CM en la demo y 27 en el código, extras ya desplegados, comprar y seguridad sin promesas, MCP local. Revisión sin bloqueantes. `explicar_zona` cita el valor tasado al comprar y el alquiler si no. Test de integración con un valor tasado sembrado (PASS, FAIL, coste en € y dataset citado), más el redondeo y el tope del Reality Check. Solo código; **el orden no cambia: primero desplegar, después sincronizar**. **Pendiente de B:** quitar «Aún no tenemos precios oficiales de compra por zona» de `SearchCard.tsx` y `FitDetails.tsx` donde haya precio (D-227 §8) |
| 12 nov | A | DATA-021 · Fase 1 (comprar con el valor tasado, D-227) | verde | `d2282aa` | `evidence/gate-01/2026-11-12/cm_valor_tasado_vivienda_municipios/`, `evidence/gate-04/2026-11-12/golden-search-compra.txt`, `data021-f1-gate.txt` | Dataset CM nuevo (id 1004050, CC BY 4.0, Ministerio de Vivienda): valor tasado medio de la vivienda libre en €/m², 28 municipios en 2025. Feature `valor_tasado_vivienda_m2` (`fit: price_m2`); los 21 distritos de Madrid quedan `SOURCE_MISSING`, sin repartir la media de la ciudad. Comprar sale PASS/FAIL con «Comprar ≈ … € por N m² (… €/m², valor tasado…)» y UNKNOWN sin precio; `estimated_cost_eur` en €; Reality Check «+30.000 €». `fit-0.5`. Golden 8/8 (`golden_couple`: 10 resultados con precio). **Primero desplegar y después sincronizar**: `fit-0.4` no entiende `price_m2` |
| 12 nov | A | DATA-020 · Fase 2b (revisión con `reviewer`) | verde | `3076f3c` | `evidence/gate-03/2026-11-12/seguridad-percibida-revision-gate.txt` | Sin bloqueantes. El panel solo funde fechas repetidas **entre** ediciones: un duplicado dentro de una edición vuelve a hacer fallar `unique_keys` (test); edición no numérica a cuarentena; la fila de la ciudad sin nombre de distrito (parser 1.2.1). Limitaciones públicas sin cifras que caducan ni la frase sobre renta (sin evidencia). Confidence de la ciudad 0,95 (juicio editorial, D-226 §6). Datos: mismos valores; cambian confidence de Madrid, `territory_name` y versión del panel → **sync menor** |
| 12 nov | A | DATA-020 · Fase 2 (seguridad percibida como contexto, D-226 §6) | verde | `70f0b7c` (sincronizado por `datamad-10`) | `evidence/gate-03/2026-11-12/seguridad-percibida.md`, `seguridad-percibida-gate.txt`, `evidence/gate-01/2026-11-12/ayto_panel_indicadores_distritos_barrios/` | Features `seguridad_percibida_noche` y `_dia` (0–10, encuesta municipal 2025): 21 distritos (de noche, de 4,9 en Villaverde a 7,7 en Chamberí y Barajas) y Madrid como referencia (6,4); los otros 178 municipios con `SOURCE_MISSING`. Dominio `safety` sin `fit` ni `gap_row` (test). El panel guarda la fila de la ciudad de esos indicadores (`city_indicators`) y una sola observación por fecha (parser 1.2.0). **Se sirven ya por `GET /features/{id}/values` (código desplegado)**. El hecho de la prioridad «Seguridad» pasa a «no la puntuamos…» (código; va con el próximo despliegue). Policía Municipal mensual: pendiente |
| 12 nov | A | DATA-020 · Fase 1 (fuentes de seguridad de Madrid capital, D-226) | verde (sin código) | `5f45517` | `evidence/gate-01/2026-11-12/seguridad-fuentes.md` | Petición de Mariano. Comprobadas en CKAN (CC BY 4.0, solo la capital): actuaciones mensuales de la Policía Municipal por distrito, encuesta de calidad de vida 2025 (unas 400 personas por distrito), panel de indicadores y accidentes de tráfico. **Percepción vecinal de su barrio (de noche y de día) como contexto** en los 21 distritos (el panel coincide con la encuesta). **Policía Municipal: la copia del panel repite valores entre distritos**; si entra, desde la fuente mensual, solo personas y patrimonio por 1.000 habitantes y con aviso. **Atropellos: no puntúan** (sin exposición peatonal; uno cada dos años por sección). DGT sin verificar |
| 12 nov | A | MCP-001 · Fase 1b (revisión con `reviewer`; fixture de búsqueda) | verde | `4befe22` | `evidence/gate-11/2026-11-12/mcp-review-gate.txt`, `api-image-sync.txt` | Sin bloqueantes. R-01: `explicar_zona` da los mismos avisos que `/search` (trabajo fuera de toda zona; `load_warnings` compartido). R-02: la caché de mapas de «Qué falta» de la búsqueda ya no puede dar `KeyError` entre hilos (también en la API: **código, sin sync**). R-06: `encontrar_zona` con `total` y aviso si deja coincidencias fuera. R-05: registros INFO a stderr. R-07: el Dockerfile de la API copia `services/mcp` como los demás miembros, sin instalarlo (comprobado). R-08: tests en 3 escenarios con avisos y stdout solo JSON-RPC. Petición de `datamad-10`: `search_result.familia_presupuesto.fixture.json` regenerado con la atribución actual del CRTM (solo ese fixture; web 286/286) |
| 12 nov | A | MCP-001 · Fase 1 (servidor MCP local, D-225) | verde | `3ab2f92` | `evidence/gate-11/2026-11-12/mcp-gate.txt`, `mcp-smoke.txt`, `api-image-sync.txt` | `services/mcp` (`hi-mcp`, SDK oficial `mcp` 2.3.0) con 5 herramientas de solo lectura por stdio: `buscar_zonas` (= `POST /search`; sin `include_map`, `all_zones` vacío), `que_falta` (= `/gaps`), `explicar_zona` (la tarjeta de `/search` con indicadores y datasets con `attribution_text`), `encontrar_zona` (nombre → código INE) y `fuentes_de_datos` (= `/datasets`). Sin SQL en el servidor: llaman a `hi_api.services`; transacción `READ ONLY`. `make mcp`; uso y configuración de clientes en `docs/04_technical_architecture/32_mcp_server.md`. Tests: 18 unitarios (contratos, entradas inválidas, base caída, stdio) y 11 de integración (cada herramienta = su ruta). **Sin sync ni despliegue:** no cambia datos ni rutas; la imagen de la API sigue igual (`uv sync --package hi-api` no instala `mcp`, comprobado) |
| 12 nov | A | DATA-020 · Fase 0 (evaluación de la fuente) | verde (sin código) | (este commit) | `evidence/gate-01/2026-11-12/seguridad-evaluacion.md` | **D-224:** la tasa oficial de hechos conocidos (portal CM, Interior) no entra en el buscador. El denominador es el padrón y los hechos se cuentan donde se denuncian (Humanes 116,2 y Madrid 58,6 por 1.000, con una referencia de 47,9). Solo cubre 36 de 199 zonas y no tiene distritos de Madrid. «Seguridad» sigue «aún sin datos oficiales». La opción de contexto (sin puntuar) queda para Mariano. |
| 12 nov | A | DATA-019 · Fase 1b (atribución del CRTM, petición de D) | verde | `555c2b4` | `tests/data/test_catalog.py` | `attribution_text` dice qué es en bruto (nombres de estaciones) y qué explotado (minutos). Sincronizado por `datamad-10` junto con DATA-019. B cambia `ATTRIBUTIONS_FALLBACK` y el fixture a la vez. |
| 12 nov | A | DATA-019 · Fase 1 («sin escaleras», revisado con `reviewer`) | verde | `d6c6f0f` | `evidence/gate-01/2026-11-12/estaciones-accesibles.md`, `evidence/gate-04/2026-11-12/sin-escaleras-gate.txt`, `golden-search-sin-escaleras.txt` | **D-223:** topología del CRTM (portal CM) con el grado de accesibilidad de cada estación; T = total, contrastado con «Metro Ligero 100 % accesible» (CM y CRTM). El `wheelchair_boarding` del GTFS del CRTM no sigue el estándar (2 = T en metro y Metro Ligero): se guarda en bruto y no se usa. Feature `min_a_pie_estacion_sin_escaleras`; la prioridad «sin escaleras» puntúa (`fit-0.4`). Golden 8/8 con `golden_reduced_mobility`. Sincronizado y verificado por `datamad-10` (smoke 8/8). `fit-0.4` sale con el próximo PR de B, que además enciende el chip. |
| 12 nov | A | DATA-018 · Fase 3b (revisión con `reviewer`) | verde | `8330771` | `evidence/gate-04/2026-11-12/zonas-verdes-revision-gate.txt`, `golden-search-parques.txt` | **Sin parque a un paseo pasa de UNKNOWN a 0 con confidence ≤ 0,5** (el texto sigue diciendo «el campo no cuenta»): con UNKNOWN un pueblo sin parque adelantaba a una ciudad con el parque a 25 min (test de propiedad de monotonía). Quality Gate `every_inclusion_published`; de un contorno inválido solo quedan sus polígonos; golden 7/7 con un escenario de zonas verdes; 78 de los 101 municipios lejos de un parque son rurales (Ley 45/2007). Mismos parques y features (sync opcional: solo cambia el parser de la versión); **C puede desplegar `fit-0.3` con este commit** |
| 12 nov | A | DATA-018 · Fase 3 (la prioridad «Zonas verdes» puntúa, `fit-0.3`) | verde | `f7e29ab` | `evidence/gate-04/2026-11-12/golden-search-parques.txt`, `zonas-verdes-gate.txt` | `FitBinding` admite una prioridad: «Zonas verdes» lee `min_a_pie_parque` (1 hasta 10 min, 0 a 30; «Parque urbano a N min…»). **Sin parque a un paseo (> 30 min) es UNKNOWN**, con «Sin parque urbano de 1 ha o más a un paseo (el campo no cuenta)»: los pueblos no salen como si les faltara verde (D-222 §7). No entra en «Qué falta». Golden 6/6. **Necesita sync y redespliegue de la API** (B no tiene que cambiar nada: los hechos llegan como texto) |
| 12 nov | A | DATA-018 · Fase 2 (a pie hasta el parque; Casa de Campo) | verde | `70b112c` | `evidence/gate-03/2026-11-12/parques-features.md`, `parques-features-gate.txt`, `evidence/gate-01/2026-11-12/parques.md` | Petición de `datamad-10`: comparada la lista oficial de parques del Ayuntamiento con OSM; **Casa de Campo y Quinta de Torre Arias** entran con fuente oficial (`data/catalog/corrections/parks.yaml`, D-222 §5). Features `min_a_pie_parque` y `pct_calle_parque_5min` hasta **cualquier punto del borde** del parque (Moratalaz 1,8 min, Chamberí 8,4). 101 municipios a más de 30 min: pueblos rodeados de campo (el indicador no mide ese verde). **Necesita sync** |
| 12 nov | A | DATA-018 · Fase 1 (parques de OSM, D-222) | verde | `91aeea1` | `evidence/gate-01/2026-11-12/parques.md`, `parques-gate.txt` | Pipeline `osm_parks` sobre el extracto de Geofabrik (ODbL): áreas `leisure=park` abiertas al público de 1 ha o más (umbral del indicador de la OMS). **1.402 parques** (8.423 ha, 80 municipios) como lugares `green` con los puntos de su borde cada 50 m; `/places?category=green` ya responde (507 en Madrid capital). La Casa de Campo falta: OSM la etiqueta como bosque. **Necesita sync** (lugares nuevos) |
| 12 nov | A | HOSP-001 · Fase 5b (revisión con `reviewer`) | verde | `e7102b0` | `evidence/gate-01/2026-11-12/nombres-tildes-revision-gate.txt` | El nombre corregido tiene que ser palabras completas de su fuente (NFC, sin espacios de más); D-221 §5 declara que se toma el nombre entero de la fuente («Dr.», «Don», «Consultorio») y §3 la excepción del Beata María Ana (decreto sin dirección: por nombre y titularidad). Parser `places-1.7.1`, recargado en local. **Necesita sync** (solo `attributes.correction.reason` de CH0024 y CS12162) |
| 12 nov | A | HOSP-001 · Fase 5 (nombres con tilde, D-221) | verde | `a04467d` | `evidence/gate-01/2026-11-12/nombres-tildes.md`, `nombres-tildes-gate.txt` | `name` en las correcciones, igual al texto de su fuente (el contrato rechaza una tilde que la fuente no escribe). **11 nombres recuperan tildes:** Ramón y Cajal, Fundación Alcorcón, La Fuenfría, Rodríguez Lafora, Fundación Jiménez Díaz, Infanta Sofía, Beata María Ana, Fundación Instituto San José, Lavapiés, Dr. Pedro Laín Entralgo e Infante Don Luis de Borbón (BOCM por número de registro o comunidad.madrid). Revisión sistemática con `scripts/audit_name_accents.py` + lectura a mano; declarados sin fuente: HM Nuevo Belén, HM Montepríncipe, Quirónsalud ×3. **Necesita sync** |
| 12 nov | A | HOSP-001 · Fase 4 (correcciones con fuente oficial, D-218 §10) | verde | `2ef95ca` | `evidence/gate-01/2026-11-12/correcciones.md`, `correcciones-gate.txt` | Decisión de Mariano (delegada en `datamad-10`): `data/catalog/corrections/places.yaml`, una corrección por registro con URL, fecha y texto de la fuente oficial, aplicada con linaje (input `corrections` de la carga) y `attributes.correction`. **El Ramón y Cajal ya sale con nombre y 886 camas**; 4 centros de salud «S/N» ubicados y con nombre (Orcasur, Campamento, Miguel de Cervantes, María de Guzmán). Features recalculadas (Alcalá: centros de salud a pie 0,395 → 0,494). Declarados sin fuente: Villar del Olmo, CEIP Navalafuente, CS12766. **Necesita sync** |
| 12 nov | A | CI · `/places` sin base | CI verde | `9cb54fe` | `evidence/gate-04/2026-11-12/ci-places-fix-gate.txt` | La CI estaba en rojo desde `b2b688b` (se validaba `category` dentro de la conexión). Ahora se valida antes y `make test-unit` corre sin base, como la CI |
| 12 nov | A | CORE-009 · Fase 3c (desempates estables) | verde | `f664a4f` | `evidence/gate-04/2026-11-12/golden-search-commute.txt` | Encaje sin redondear → confidence → menos minutos → id de zona; test de propiedad y golden con las zonas al revés |
| 12 nov | A | API para B · `attribution_text` y varias capas en `/places` | verde | `71cfdf2`, `b2b688b` | `evidence/gate-04/2026-11-12/attribution-gate.txt`, `places-categories-gate.txt` | Cada `DatasetRef` (en `/datasets`, `/gaps` y `/search`) trae `attribution_text` desde el catálogo de fuentes: Ministerio de Sanidad con las fechas de actualización, CC BY 4.0 de la CM y del Ayuntamiento, «Powered by CRTM», ODbL; los 4 datasets con lugares geocodificados añaden la cita de CartoCiudad. **B puede quitar el texto fijo** (tipos regenerados en `apps/web/src/contracts`). `/places?category=education,health,pharmacy` en una sola llamada. Sin sync (código de la API: va en el próximo despliegue de C) |
| 12 nov | A | CORE-009 · Fase 3 + 3b (la búsqueda usa el transporte público, `fit-0.2`) | verde | `b0222af`, `7e4aa7c` | `evidence/gate-04/2026-11-12/golden-search-commute.txt`, `core009-f3b-gate.txt`, `evidence/gate-03/2026-11-12/commute-matrix.md` | El trabajo puntúa por **minutos en transporte público llegando a las 9:00** (hecho: «33 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00»). Límite de trayecto PASS/FAIL; UNKNOWN donde no se llega con los horarios publicados. Sitio → estación a ≤ 600 m o centro de la zona que lo contiene. Revisado con `reviewer` (3b: transbordo a pie mínimo de 2 min). Golden 6/6 (expectativas del trabajo en minutos). **Caso demo: Fuencarral-El Pardo 100 % (29 min) y Ciudad Lineal 99 % (33 min)**. **Necesita sync** (matriz recalculada) **y redespliegue de la API** |
| 12 nov | A | CORE-009 · Fase 2 (matriz de trayectos, D-220) | verde | `c4173ef` | `evidence/gate-03/2026-11-12/commute-matrix.md`, `core009-f2-gate.txt` | Minutos en transporte público para **llegar a las 9:00** desde las 200 zonas a las 379 estaciones y los 200 centros de zona, con los 6 GTFS del CRTM (`hi-features commute`, 107 s). Sol: Centro 9 min, Getafe 38, Alcalá 67, Aranjuez 75. Limpieza declarada de los GTFS de autobuses (horas repetidas, expediciones que retroceden). 50 zonas sin dato (Sierra Norte; las líneas 720–726 de Colmenar faltan en el GTFS). Migración **0007** (`transit_hub`, `commute_time`). **Necesita migrate + sync** |
| 12 nov | A | CORE-009 · Fase 1 (búsqueda «llegar a las…») | verde | `a51b159` | `evidence/gate-03/2026-11-12/core009-f1-gate.txt` | Dominio puro: red expandida en el tiempo y búsqueda hacia atrás; tests de propiedades |
| 12 nov | `datamad-10` | Supabase · sync de HOSP-001 F3 | — | `56e846f` | MCP | 17 centros de salud genéricos, 399 alias de atención primaria, CS7368 = «Centro de salud Palma Norte» |
| 12 nov | A | HOSP-001 · Fase 3 + 3b (nombres, D-218 §9) | verde | `e418a18`, `56e846f` | `evidence/gate-01/2026-11-12/nombres-segunda-pasada.md`, `hosp001-f3b-gate.txt` | Notas de C desde producción. Centros de salud con nombre de 228 a 255 (genéricos de **44 a 17**) y consultorios de 128 a 144: reglas `direccion_municipio` y `municipio`, municipio y tipo obligatorios por debajo de la dirección completa, y grafías del catálogo del Ministerio («SAN CALLEAUDIO», «Mª», plurales, esquinas). Ningún cruce anterior cambia de pareja; 3 se pierden con motivo. Revisado con `reviewer` (3b). **El hospital sin nombre de Fuencarral es el Ramón y Cajal (CH0049):** el catálogo lo pone en la calle de Ayala 38; solo lo arregla el fichero de correcciones (Mariano). **El de Chamartín (CH0113) es de una mutua:** el catálogo da el nombre de la mutua, no del centro (D-218 §5). **Necesita sync** |
| 12 nov | A | OPS-001 · pooler en modo transacción (D-219) | verde | `de9ad4b` | `evidence/gate-06/2026-11-12-pool/transaction-mode-gate.txt`, `prepared-statements-local.txt` | `DB_PREPARED_STATEMENTS=false` pasa `prepare_threshold=None` a psycopg (el pooler de Supabase en modo transacción no admite prepared statements); por defecto nada cambia. En local: 1 prepared statement tras 8 ejecuciones con el valor por defecto y 0 con `false`. `vf_api_ro` ya trae `search_path` a nivel de rol (comprobado por MCP). D-219 recoge también el pool por entorno (`4645326`). **C: variables en Vercel abajo** |
| 12 nov | A | DATA-AUDIT · Fase 5 (CI y Gate 3) | verde · G3 PASS | `927af98` | `evidence/gate-03/2026-11-12/summary.md`, `phase-5-gate.txt`, `golden-search.txt` | CI de nuevo en verde: el test de propiedades del 2SFCA ya no genera floats subnormales y `gapMap.test.ts` (web, cambio mínimo pedido por `datamad-10`) lee Centro del fixture regenerado. El Gate 3 cuenta lo que dice el catálogo (38 features, 13 a pie, 17 por distrito) y toda feature municipal tiene fila en los 179 municipios (nulo explícito si la fuente no lo publica: Zarzalejo en tenencia) |
| 12 nov | A | PUBLIC · Fase 4 (README) | verde | `6c4dd4b` | `README.md` | README de la raíz desde el borrador de D: Vida Fácil, 23 datasets CM, capacidad a pie, licencias (CartoCiudad incluido), sin apellidos ni rutas locales; el tag `pre-datamad` con enlace relativo |
| 12 nov | A | DATA-AUDIT · Fase 3 (revisión) | verde | `e7864bd` | `evidence/gate-04/2026-11-12/phase-t2-review-gate.txt` | Ajustes del `reviewer`: la calle geocodificada tiene que coincidir (40 lugares geocodificados, no 42), aulas públicas también para «público-titularidad privada», caché atómica, filtros de `/places` más robustos |
| 12 nov | A | DATA-AUDIT · Fase 2 (T2a + T2b, D-217) | verde | `b88c4fb` | `evidence/gate-04/2026-11-12/gap-status-gap03.md`, `evidence/gate-03/2026-11-12/fca-sensitivity.md` | **`gap-0.3`:** las 5 filas de servicios miden capacidad al alcance a pie (2SFCA, 15 min a 4 km/h): aulas de primaria, escuelas infantiles, centros de salud del SERMAS, plazas de mayores y farmacias. Municipios pequeños comparados con vecinos del mismo tipo a ≤ 15 km (`comparison_group`): «poco fiable» en colegios de 140 a 65. Madrid salud FALTA → JUSTO (0,95). Hospitales y camas de la CM solo regionales (cargados); `min_a_pie_hospital` como extra. **Cambia el contrato** |
| 12 nov | A | DATA-AUDIT · Fase 1 (T1, D-216) | verde | `1913393` | `evidence/gate-01/2026-11-12/audit-places.md` | Auditoría frente a totales oficiales. Los 1.001 «Centro Polivalente» eran clínicas privadas (no mayores): fuera. Farmacias en categoría `pharmacy` (migración 0006). Coordenadas reparadas con CartoCiudad (IGN). `/places` con contrato `places-1` (titularidad, `gap_rows`, `capacity`) |
| 11 nov | A | CORE-003 · Fase 2 (`POST /api/v1/search`) | verde | `915be3c`, `5f373b6` | `evidence/gate-04/2026-11-11/phase-core003-f2.txt` | **El buscador funciona con datos reales** (método `fit-0.1`, D-215): 199 zonas (178 municipios y 21 distritos), los rasgos `fit` del Feature Dictionary (sin ids en el código), `gap_highlights` iguales que `/gaps`, Reality Check con `relaxed_scenario` y procedencia (16 datasets, 14 CM). 6 tests de integración y 6 escenarios dorados en datos reales (`scripts/golden_search.py`). Caso demo: Ciudad Lineal 99 %, Tetuán, Hortaleza y Moratalaz 97 %; el colegio a 10 min es la condición que más quita (+17 zonas con 5 min más). Fixture de búsqueda real (ya no ilustrativo). **B puede conectar el buscador; encender `NEXT_PUBLIC_FEATURE_SEARCH` tras el sync** |
| 11 nov | A | CORE-003 · Fase 1 (dominio del encaje) | verde | `1507deb` | `evidence/gate-04/2026-11-11/phase-core003-f1.txt` | `hi_domain/fit.py`, `reality_check.py` y `search.py`: condiciones PASS/FAIL/UNKNOWN, pesos por rango, utilidades con saturación y Reality Check; tests de propiedades (UNKNOWN nunca PASS, relajar nunca quita zonas) |
| 11 nov | A | CORE-006 · Fase 2 (m² por hogar y presupuesto, D-214) | verde | `92eab6b`, `7311370` | `evidence/gate-04/2026-11-11/phase-core006-f2.txt` | `hi_domain/affordability.py`: condición de presupuesto PASS/FAIL/UNKNOWN (UNKNOWN sin alquiler publicado; compra siempre UNKNOWN con «Sin datos», D-203). m² supuestos = vivienda mediana de los hogares de ese tamaño en la CM (Censo 2021, INE tabla 59524): 61, 68, 71, 77 y 77 m² para 1, 2, 3, 4 y 5+ personas. El coste es una cota baja (contratos vigentes; m² catastrales), declarado en D-214. **CORE-006 DONE** a falta del sync |
| 11 nov | A | CORE-006 · Fase 1 (alquiler por distrito) | verde | `100cb29` | `evidence/gate-04/2026-11-11/phase-core006-f1.txt` | `alquiler_m2_mensual` v2 con nivel distrito: media de los códigos postales de cada distrito ponderada por los lugares que llevan ese código (proxy declarado, confidence ≤ 0,8). Conecta `cm_alquiler_m2_codigo_postal_madrid`: **21 de 21 datasets CM alimentan features**. Media de distritos ponderada por población 14,46 frente a 15,10 publicados para Madrid. `/features/{id}/values` da el linaje del nivel pedido. Necesita sync |
| 11 nov | A | GAP-001 · Fase 5 (ADR de los cortes, D-213) | verde | `d02574f`, `f626e1f` | `evidence/gate-04/2026-11-11/phase-gap001-f5.txt`, `-f5-review.txt` | Método `gap-0.2`: cada zona frente a los **demás municipios de su tipo** (rural o urbano, Ley 45/2007; χ² rechaza una tasa común en las 6 filas, centros de salud ×14,8). FALTA = ratio < 0,8 **y** falta significativa (Poisson exacto 95 %); CUBIERTO ≥ 1; `reliable: false` si se esperan menos de 3,69 casos (nunca FALTA). Las features por población guardan sus recuentos (`inputs.counts`). Chamartín salud: FALTA → **JUSTO** (0,84); Madrid capital salud **FALTA** (0,67). Revisado con `reviewer` (sin autoinclusión, tests de propiedad). Tipos TS de la web regenerados (`apps/web/src/contracts`, generados). **Aprobado por Mariano el 11 nov. Necesita sync** |
| 11 nov | B → coord | PUB-001 / MAP-004 · PR #2 fusionado | CI verde | `bd5b006` | comentario de revisión en el PR #2 | Web de Vida Fácil. Revisado por A con `reviewer` (fusionar con mejoras); el merge lo hizo `datamad-10` con autorización de Mariano (a A se lo bloqueó el clasificador). Buscador tras `NEXT_PUBLIC_FEATURE_SEARCH`, apagado hasta `POST /search` |
| 11 nov | Mariano | Supabase · sync | — | — | MCP (`datamad-10`) | Sincronizado hasta `c4f1bc0`/`b1f899e` (nombres oficiales): 61.935 filas en `feature_value`, 0 nombres con «/» o «Ð», 106 MB. Producción sirve `995f7ce` (smoke 7/7) |
| 11 nov | A | GAP-001 · Fase 4 (`/gaps?level=&row=`) | verde | `697dbaf` | `evidence/gate-04/2026-11-11/phase-gap001-f4.txt` | Contrato `GapRowMap` (JSON Schema `gap_row_map_response`): una fila en todas las zonas de un nivel, con estado, valor, ratio, confidence y `null_reason` por zona, `counts`, referencia, cortes y datasets. Mismo indicador, referencia y cortes que `/gaps/{level}/{code}`; un test comprueba el color de cada zona contra su fila. Municipio: 179 zonas (unos 32 KB); distrito: 21; vivienda por distrito, 21 `SIN_DATOS`; sección, `zones: []` con aviso. Fixtures regenerados (nombres con tilde). B puede pintar la coropleta |
| 11 nov | A | DATA-022 · Fase 1 (nombres oficiales, D-212) | verde | `c4f1bc0`, `b1f899e` | `evidence/gate-01/2026-11-11/phase-data022-f1.txt`, `-f1-review.txt`, `official_names/` | Los 179 municipios toman el nombre de la tabla CM `cm_poblacion_edad_nacionalidad_sexo` («Redueña», «Griñón», «Villanueva de la Cañada», «Piñuécar-Gandullas», «Álamo (El)» → «El Álamo») y los 21 distritos de Madrid, del panel del Ayuntamiento («Vicálvaro»). Paso `make admin-names` (también al final de `run-all`); check crítico que bloquea «/», «Ð» o cualquier carácter fuera de la ortografía española. 405 nombres cambiados en la base local, 0 rotos. Revisado con `reviewer`. **Necesita sync** |
| 11 nov | A | GAP-001 · Fase 3b (vivienda, 6 filas) | verde | `98b842a`, `ea8ee74` | `evidence/gate-04/2026-11-11/phase-gap001-f3b.txt`, `-f3b-review.txt` | Método `metric_ratio` (dos métricas) y `not_published` (SIN DATOS explícito). Vivienda: viviendas > 90 m² por cada 100 hogares de 4+ (Madrid 163, región 178; confidence 0,8), SIN DATOS por distrito. Extras: aulas de infantil, nacimientos, % en alquiler, tamaño medio del hogar. **20 de 21 datasets CM alimentan features** (falta alquiler por CP: CORE-006). Revisado con `reviewer`. Necesita sync |
| 11 nov | A | GAP-001 · Fase 3a (5 filas) | verde | `4523d69` | `evidence/gate-04/2026-11-11/phase-gap001-f3a.txt` | Escuela infantil (por 1.000 niños de 0 a 4), mayores (centros por 1.000 de 65+) y farmacia (por 10.000 hab.) por municipio y por los 21 distritos; cada fila cuenta los mismos lugares que sus minutos a pie. Extras: ratio oficial de farmacias de la CM (`cm_farmacias_municipios`, solo municipio) y plazas de residencia. Golden de farmacias frente a la ratio oficial: mediana 0,33 %, p90 1,6 %. Necesita sync |
| 11 nov | A | GAP-001 · Fase 2 (filtro de colegios) | verde | `21939dd` | `evidence/gate-04/2026-11-11/phase-gap001-f2.txt` | La fila de colegios cuenta colegios con primaria, públicos o concertados (v2; 1.241 en la región). Chamartín FALTA → CUBIERTO (1,04); Madrid FALTA → JUSTO (0,96); región 2,18 → 1,32. Invariante de catálogo: fila y minutos a pie cuentan los mismos lugares. Revisado con `reviewer`. Necesita sync |
| 11 nov | A | GAP-001 · Fase 1 (`extra_indicators`) | verde | `2d05d78` | `evidence/gate-04/2026-11-11/phase-gap001-f1.txt` | `/gaps` trae en `extra_indicators` los minutos a pie de colegio y centro de salud (municipio y distrito); los extras no tienen estado propio, null con `null_reason` y sus datasets (red OSM) en la procedencia de la fila. Chamartín: salud FALTA (0,79) a 9,5 min a pie. `data_version` solo con lo que se muestra. Revisado con `reviewer`. C puede redesplegar (sin sync) |
| 11 nov | A | DATAMAD-PUBLIC-01 · Fase 3 (rutas locales) | verde | `12bd103` | `evidence/gate-00/2026-11-11/phase-public01-f3.txt` | Ningún fichero versionado lleva la ruta del home ni la del scratchpad (llevan los apellidos); el historial no se reescribe. Se limpiaron 29 evidencias (la línea `RUN` de vitest). `scripts/redact_paths.py` sanea al escribir (`evidence.py` lo aplica a cada log) y `tests/data/test_no_local_paths.py` falla en la CI si vuelve a aparecer una. Revisado con `reviewer` |
| 11 nov | A | Supabase · sync único (Mariano) | — | — | MCP `supabase-datamad` | `make supabase-sync PROFILE=demo` tras los 4 km/h. Por MCP: las 12 features a pie con `feature_version` 2 y 4.843 filas cada una, y los valores de Chamartín iguales que en local. Las 25 features del registro son las 24 calculadas más `admin_unit_area_km2`, que tiene su propio pipeline y no tiene filas en `feature_value` |
| 11 nov | A | CORE-005 · Fase 5 (4 km/h) | verde · G3 PASS | `ad2129a` | `evidence/gate-03/2026-11-11/phase-core005-f5.txt`, `summary.md` | Las 12 features a pie pasan a 4 km/h y a la versión 2 (D-211, fuente: «El Madrid de los 15 minutos» del Ayuntamiento). Los minutos suben un 12,5 %. Los 15 golden cumplen sin tocar los límites y hay 0 desacuerdos entre mediana y %. Chamartín: centro de salud 9,5 min y farmacia 2,6 |
| 11 nov | C → A | OPS-001 · PR #7 integrado | CI verde + gate local verde | `93af627` | `evidence/gate-06/2026-11-11/merge-pr7.txt`, `evidence/gate-06/2026-11-11-deploy/deploy-6-paginated.md` | El README explica el reintento único del smoke a los 20 s. El smoke gana el check `largest` (página 1 de transporte, unos 1,4 MB): 7/7 en producción con `/places` paginada y 6/6 en el paquete offline. Revisado con `reviewer`: fusionar; pendiente menor de C: exigir `.data.pages >= 1` en el filtro |
| 11 nov | A | CORE-005 · Fase 4 (cierre) | verde · G3 PASS | `fc025b6` | `evidence/gate-03/2026-11-11/summary.md`, `phase-core005-f4.txt` | Ejecución real: 24 features en 29 s. 15 casos golden (Sol, Plaza de Castilla, Centro, Getafe, Alcalá, La Acebeda sin farmacia y la región) y coherencia mediana/% en 4.819 zonas por destino. D-210 con velocidad, ventanas, destinos y calles de origen. **CORE-005 DONE** |
| 11 nov | A | Mantenimiento CI | verde | `29a688e`, `bc60e1f` | `evidence/gate-04/2026-11-11/docs-manifest-0.5.19.txt` | La CI de la rama estaba en rojo desde `6d02abb` porque faltaba regenerar el manifest de docs. Ahora `make lint` comprueba también los schemas y el manifest, igual que la CI |
| 11 nov | A | API para B · Fase 3 (`/places` paginada) | verde | `879101a` | `evidence/gate-04/2026-11-11/phase-apib-f3-places-pages.txt` | Páginas de 5.000 lugares (1,4 MB como máximo, frente al límite de 4,5 MB de Vercel), con `total`, `page` y `pages`. Si quedan páginas, `warnings` dice cómo pedir la siguiente; una página fuera de rango → 422. Riesgo detectado por el smoke de C |
| 11 nov | A | CORE-005 · Fase 3 | verde | `23b7531` | `evidence/gate-03/2026-11-11/phase-core005-f3.txt` | 12 features a pie por sección, municipio y distrito: mediana de minutos y % de calle a ≤ 10 min (salud 15, transporte 5) hasta escuela infantil, colegio, centro de salud, farmacia, centro de mayores y parada. Zona sin calles = SIN DATOS; calles aisladas = desconocido; nunca 0 |
| 11 nov | A | API para B · Fase 2 (`/geo/admin-units`) | verde | `12c834a` | `evidence/gate-04/2026-11-11/phase-apib-f2-geo.txt` | Nombres legibles («Las Rozas de Madrid»), como en `/gaps`, y `?parent=`: `ES.28.MUN.28079` devuelve los 21 distritos (0,03 MB frente a 0,54 MB). Las tildes que faltan en la fuente siguen faltando («Vicalvaro») |
| 11 nov | A | API para B · Fase 1 (`/places`) | verde | `d7037b7` | `evidence/gate-04/2026-11-11/phase-apib-f1-places.txt` | `/places` filtra por `?admin_unit_id=` (municipio, distrito o sección, con la misma regla que los features) y por `?subcategory=` repetible. Transporte sale entero (14.982, 4,2 MB); Chamartín con metro y cercanías son 15 puntos. Tope 20.000 con aviso si se alcanza |
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
| 18 nov | **Formulario** | **Formulario enviado (12 nov)** por Mariano: resumen de 98 palabras (`pitch/formulario.md`) y enlaces a la demo, al repo y a `datasets_cm.md` |
| 19–22 nov | Mejoras | Tiempo a polos de empleo, MCP 3–5 tools, más datasets, accesibilidad · 22: cut review 2 |
| 23 nov | Freeze | Solo fixes, manifest final de fuentes, README |
| 24–25 nov | Pitch | 4 slides (§8), guion, vídeo de respaldo, banco de preguntas, 5 ensayos |
| 26 nov | Final | Slides antes de las 14:00 · presentaciones de 17:00 a 19:00 en URJC Vicálvaro |

## 03 — CLAUDE CODE (en curso, línea A)
- **CONTRACTS** Contratos PUBLIC: `ScenarioState`, `SearchResult` (ranking, motivos y Reality Check) y `ZoneGapList` (FALTA / JUSTO / CUBIERTO / SIN DATOS). JSON Schema en `data/schemas/api/`, rutas en `docs/04_technical_architecture/31_public_api_routes.md` y fixtures reales en `data/fixtures/contracts/`. **Contratos publicados: `7541527`** · `evidence/gate-04/2026-11-11/phase-contracts-f1.txt`
- **CORE-005** Distancia a pie por sección censal y H3:
  - Fase 1 `4cdee28`: red peatonal OSM como dataset `osm_red_peatonal` (solo Silver; 2,38 M nodos y 57.659 km; componente principal del 98,25 %). Evidencia en `evidence/gate-01/2026-11-11`.
  - Fase 2 `e31770b`: dominio puro de accesibilidad con tests de propiedades (`evidence/gate-03/2026-11-11`).
  - Fase 3 `23b7531`: método `network_walk_time` y 12 features (6 destinos × mediana de minutos y % de calle dentro de la ventana) en sección, municipio y distrito, con referencia regional. Evidencia en `evidence/gate-03/2026-11-11/phase-core005-f3.txt`. El H3 r9 queda para cuando lo pida la vista 3D (serían unas 300.000 filas más en Supabase).
  - Fase 4 `fc025b6`: ejecución real (24 features en 29 s), 15 casos golden y coherencia mediana/% en todas las zonas, **Gate 3 PASS** (`evidence/gate-03/2026-11-11/summary.md`) y **D-210**. **CORE-005 DONE.**
  - Fase 5 `ad2129a` (decisión de Mariano): **4 km/h** en las 12 features, que pasan a la versión 2 (**D-211**). Recálculo en 28 s; los 15 golden cumplen sin tocar los límites; **Gate 3 PASS** otra vez. Evidencia: `evidence/gate-03/2026-11-11/phase-core005-f5.txt`.

- **GAP-001** Fases 2–3b `21939dd` `4523d69` `98b842a` `ea8ee74`: las 6 filas (escuela infantil, colegio, centro de salud, mayores, farmacia, vivienda) por municipio y por los 21 distritos; cada fila cuenta los mismos lugares que sus minutos a pie (invariante de catálogo). Evidencias `evidence/gate-04/2026-11-11/phase-gap001-f2.txt`, `-f3a.txt`, `-f3b.txt`.
- **GAP-001** Fase 1 `2d05d78`: los minutos a pie (CORE-005) salen en `extra_indicators` de colegio y centro de salud, en municipio y distrito. Evidencia: `evidence/gate-04/2026-11-11/phase-gap001-f1.txt`.
- **GAP-001** Fase 0 `2da5d4d`, esqueleto andante (y por distrito desde DATA-012 F2, `83c74dd`). `GET /api/v1/gaps/{level}/{code}` responde con datos reales: filas de colegio y centro de salud por municipio, frente a la referencia regional (fila `ccaa` del Feature Store: total de la región / población). Las filas se declaran en el Feature Dictionary (`gap_row`). La migración 0004 guarda el enlace al portal CM e `is_cm_open_data`. Evidencia: `evidence/gate-04/2026-11-11/phase-gap001-f0.txt`. **Checkpoint del 13 nov adelantado para 2 filas: B ya puede integrar contra la API real.**

### Estado de la sesión del 13 nov (madrugada, línea A v15)
- **Done (A v15), BARRIO-001 = fase 1 del diseño de barrios (D-232, `fit-0.7`):**
  - `983d225`: fixture de datasets con la AEAT, para el `pie.aeat` de B.
  - `19bf8bd` (datos), `788f938` (ruta) y `01fbf1e` (revisión con `reviewer`, sin bloqueantes).
  - **Ruta:** `POST /api/v1/search/barrios {scenario, distrito}` devuelve los barrios del distrito con el mismo motor que `/search`.
  - **Contrato:** `BarrioSearchRequest`/`BarrioSearchResult`, schemas en `data/schemas/api/barrio_search_*` y tipos TS generados en `apps/web/src/contracts/`. Fixture real: `barrio_search_result.san_blas`.
  - **Datos:** nombres oficiales de barrio (panel del Ayuntamiento), minutos a pie, alquiler por sus códigos postales (confidence 0,6/0,3; Sol sin dato) y trayectos propios (mediana de sus secciones). Si falta el trayecto propio, usa el del distrito con aviso y nunca decide un límite.
  - **Desviación del diseño, declarada en D-232 §5:** el trayecto se mide desde las secciones del barrio, no desde un único «centro», igual que los distritos.
- **Sync y despliegue (pedido a `datamad-10`):**
  - Los datos nuevos son compatibles con el código desplegado (`fit-0.6`): todas sus lecturas filtran por nivel.
  - Orden recomendado: primero `make supabase-sync PROFILE=demo` (sin migración nueva) y después desplegar `01fbf1e` o posterior. Así la ruta sale con nombres y datos desde el primer momento.
  - Si se despliega antes del sync, la ruta responde, pero con todo `UNKNOWN`, trayectos prestados y 3 barrios con su código en vez de nombre.
- **Pendiente de otros:**
  - **B:**
    - selector de barrios dentro de un distrito: llamar a `/search/barrios` con el distrito elegido y pintar sus barrios con `GET /api/v1/geo/admin-units?level=barrio&parent=ES.28.DIS.<código>`;
    - mismos componentes de tarjeta, % y «casi»; `gap_highlights` viene vacío;
    - el `relaxed_scenario` se reenvía a `/search/barrios` con el mismo `distrito`;
    - la nota «(trayecto medido para todo el distrito…)» ya va en el texto.
  - **Mariano y `datamad-10`:** decidir la fase 2 del diseño (los 131 barrios en el ranking regional) antes del 18 nov. «Qué falta» por barrio, después del freeze.
- **Next (línea A):** nada de barrios sin decisión. Lo que mande `datamad-10`.
- **Gate status:** `make lint typecheck test` en verde en `01fbf1e`: 704 unit, 354 web y 133 integración. Golden de búsqueda 9/9 (8 regionales sin cambios + San Blas).
- **Relevo:** A v15 cierra tras BARRIO-001. Continuar con `~/Desktop/DATAMAD/prompts/RELEVO.md`.

### Estado de la sesión del 12 nov (madrugada, línea A v14)
- **Done (A v14), las 4 fases de `FASE_MEJORA.md` para A:**
  1. **Alquiler (D-228, `fit-0.6`):**
     - el índice CM 1934428 no sirve (es el IPVA del INE para toda la CM, en base 2015 por serie);
     - Mariano eligió la opción A: €/m² de la CM × el factor de contratos nuevos de la Agencia Tributaria de la misma zona (fuente complementaria, no CM). Commits `a400223`, `310056b` y `861af7b`;
     - **desplegado y sincronizado** (`310056b`). `861af7b` (revisión, solo código) va en el próximo despliegue.
  2. **Impacto (D-229):** `GET /api/v1/gaps/impact` y `people` en cada fila (`5655b76`, `c1ad3ed`). Por ejemplo, 25.551 niños de 0–4 años en 3 distritos con FALTA de escuela infantil.
  3. **Zonas pequeñas (D-230, `195ff6d`):** «No comparable» en la explicación, suelo de 3,69 para los hogares de la vivienda y `NOT_APPLICABLE` con su motivo cuando no vive nadie de esa edad. Sincronizado por `datamad-10`.
  4. **Fuentes (D-231, `c269100`):** `source_name` en cada `DatasetRef` y las 2 tablas de camas servidas como features de región. **Sync pendiente, en cualquier orden.**
  - Textos de D aplicados: «a unos N min andando».
- **Pendiente de otros:**
  - **B:**
    - pintar `/gaps/impact` y `people`, y «{n} por cada 100» con `ratio_to_reference` (el del grupo si lo hay);
    - «No comparable» cuando `reliable` es `false` y no hay grupo;
    - la `explanation` de `NOT_APPLICABLE`;
    - «en {source_name}» en vez de «en el portal de datos»;
    - la línea de camas en la nota del hospital (`camas_instaladas_por_1000_hab`, `hospitales_total`);
    - el hospital a más de 30 min como distancia;
    - la atribución de la Agencia Tributaria.
  - **D:** retirar «el colegio, no el dinero» y contar las camas solo si la web las enseña.
- **Next (línea A), aprobado por `datamad-10` y Mariano:** **barrios, fase 1 (`fit-0.7`, `POST /api/v1/search/barrios {scenario, distrito}`)**, unas 8–9 h:
  - **Asignación:** cada una de las 2.443 secciones de Madrid va a uno de los 131 barrios por su punto interior (comprobado: las 131 tienen secciones).
  - **Minutos a pie:** con `network_walk_time` en el nivel barrio (mediana de las calles del barrio, no mediana de medianas).
  - **Alquiler:** por los códigos postales del barrio (D-214 + D-228), con la confidence más baja. Si queda UNKNOWN, el motivo va en llano.
  - **Trayecto:** desde el centro del barrio. Si falta, el del distrito, y el hecho lo dice: «trayecto medido desde el centro del distrito».
  - Contrato, tests, golden y ADR.
  - **Fase 2** (ranking de los 131 barrios) solo si la fase 1 queda en verde y desplegada antes del 18 nov.
  - «Qué falta» por barrio, no antes del freeze.
- **Gate status:** `make lint typecheck test` en verde en `c269100`: 670 unit, 308 web y 126 integración. Golden de búsqueda 8/8.
- **Relevo:** A v14 cierra aquí por contexto, tras 4 fases. Continuar con `~/Desktop/DATAMAD/prompts/RELEVO.md`.

### Estado de la sesión del 12 nov (noche, línea A v13)
- **Done (A v13):**
  - **MCP-001 F1–F1b** (`3ab2f92`, `4befe22`, **D-225**): servidor MCP local por stdio con el SDK oficial `mcp` 2.3.0 (`make mcp`).
    - 5 herramientas de solo lectura sobre `hi_api.services`, sin SQL y en transacción `READ ONLY`: `buscar_zonas`, `que_falta`, `explicar_zona`, `encontrar_zona` y `fuentes_de_datos`.
    - Los tests comprueban que cada herramienta devuelve lo mismo que su ruta.
    - Docs en `docs/04_technical_architecture/32_mcp_server.md`. No se despliega.
    - Arreglo que también afecta a la API: la caché de mapas de la búsqueda era insegura entre hilos.
  - **DATA-020 F1–F2b** (`5f45517`, `70f0b7c`, `3076f3c`, **D-226**):
    - fuentes de seguridad de Madrid capital evaluadas;
    - la percepción vecinal de su barrio (de día y de noche) entra como contexto en los 21 distritos y Madrid, sin puntuar;
    - la copia del panel de la Policía Municipal tiene errores;
    - los atropellos no puntúan;
    - hecho nuevo de la prioridad «Seguridad: no la puntuamos…» (texto provisional b, a la espera de Mariano).
  - **DATA-021 F1–F1b** (`d2282aa`, `f29ebec`, **D-227**, `fit-0.5`): comprar puntúa con el valor tasado de la vivienda libre por municipio.
    - Es un dataset CM: el nº 27 en el código y el 26 en la demo hasta el despliegue.
    - Hay 28 municipios con valor. Los distritos de Madrid quedan SIN DATOS.
  - README de la raíz actualizado para el jurado. Fixture `search_result.familia_presupuesto` regenerado (atribución del CRTM y `fit-0.5`).
- **Pendiente de otros:**
  - **C, en este orden:**
    1. desplegar `f29ebec`, con `fit-0.5`, el hecho de seguridad, la caché segura y el `COPY services/mcp` del Dockerfile;
    2. después, el sync de `d2282aa` y `3076f3c`.

    Si se sincroniza antes, `/search` da 500, porque `fit-0.4` no conoce `price_m2`.
  - **B:**
    - Comprar: quitar «Aún no tenemos precios oficiales de compra por zona» donde haya precio (`SearchCard.tsx`, `FitDetails.tsx`; D-227 §8);
    - pintar la seguridad percibida desde `GET /features/seguridad_percibida_{noche,dia}/values` (`31_public_api_routes.md`);
    - cambiar el «Muy pronto» de seguridad.
  - **Mariano:** el texto definitivo de la seguridad.
- **Next (línea A), en orden:**
  1. Actuaciones de la Policía Municipal desde la fuente mensual (D-226 §2): pipeline nuevo para los 12 XLSX de cada año; solo personas y patrimonio, por 1.000 habitantes y con aviso. Solo si Mariano lo sigue queriendo después de ver la percepción vecinal.
  2. Comprar en los distritos de Madrid: buscar una fuente oficial por distrito o código postal que sea un precio. El valor de referencia del Catastro por código postal está evaluado y descartado (D-227 §6).
  3. Deuda:
     - `drop_off_type` del GTFS (M-3 de CORE-009);
     - Gate 3 completo;
     - script de comparación de parques sin versionar;
     - `make help` muestra «Makefile» como nombre de cada objetivo cuando existe `.env` (el `grep` recibe dos ficheros).
- **Gate status:** `make lint typecheck test` en verde en `f29ebec`: 623 unit, 286 web y 119 integración. Golden de búsqueda 8/8. Smoke del MCP por stdio en `evidence/gate-11/2026-11-12/mcp-smoke.txt`.
- **Relevo:** A v13 cierra aquí tras 3 cards. Continuar con `~/Desktop/DATAMAD/prompts/RELEVO.md`.

### Estado de la sesión del 12 nov (tarde-noche, línea A v12)
- **Done (A v12):**
  - **DATA-019 F1–F1b** (`d6c6f0f`, `555c2b4`, **D-223**): «sin escaleras» puntúa los minutos a pie hasta una estación de metro, Metro Ligero o Cercanías con accesibilidad total (grado T de la topología del CRTM, portal CM). Pipeline nuevo `station_topology`; los GTFS de tren enlazan sus estaciones por código oficial (los intercambiadores toman la menos accesible). El `wheelchair_boarding` del CRTM no sigue el estándar GTFS: se guarda en bruto y no se usa. `local_file` conserva la URL oficial de lo que ya está en Bronze. Golden 8/8 con `golden_reduced_mobility`. Revisado con `reviewer` (R-01 y R-02 resueltos). Sincronizado; la atribución del CRTM dice qué es en bruto y qué explotado.
  - **DATA-020 F0** (**D-224**): la tasa oficial de hechos conocidos no entra en el buscador (denominador, cobertura y modelo). Sin código.
- **Pendiente de otros:**
  - B: encender el chip «sin escaleras». Cambiar a la vez `ATTRIBUTIONS_FALLBACK` y `data/fixtures/contracts/dataset_list.all.fixture.json`. Con su próximo PR se despliega `fit-0.4`.
  - Mariano: si la tasa de seguridad va como dato de contexto sin puntuar (D-224 §3).
- **Next (línea A), en orden:**
  1. **MCP-001: 3–5 herramientas sobre los servicios de dominio**, sin SQL libre (CLAUDE.md §3). `services/mcp/` solo tiene un README. Propuesta:
     - `buscar_zonas(ScenarioState)`, que llame a `hi_api.services.search.search`;
     - `que_falta(level, code)`, sobre el servicio de `/gaps`;
     - `explicar_zona(level, code)`, con indicadores y datasets citados (`dataset_refs`, atribuciones);
     - opcional: `lugares_cerca(categoría, zona)`.
     Con tests y documentación de uso.
  2. DATA-021: precio de compra con fuente oficial, o SIN DATOS declarado.
  3. Deuda:
     - `drop_off_type` del GTFS (M-3 de CORE-009);
     - Gate 3 completo tras las correcciones;
     - script de comparación de parques sin versionar;
     - los recuentos del GTFS de autobuses siguen con la versión de `gtfs-1.2.0` recargada desde Bronze (mismos lugares).
- **Gate status:** `make lint typecheck test` en verde en `d6c6f0f`: 570 unit, 282 web y 102 integración. Tras el rebase, `555c2b4`: 571 unit y 286 web. Golden de búsqueda 8/8.
- **Relevo:** A v12 cierra aquí por contexto, tras 2 cards. Continuar con `~/Desktop/DATAMAD/prompts/RELEVO.md`.

### Estado de la sesión del 12 nov (tarde, línea A v11)
- **Done (A v11):**
  - **HOSP-001 F5–F5b** (`a04467d`, `e7102b0`, **D-221**): `name` en las correcciones, igual palabra por palabra al texto de su fuente (NFC). 11 nombres recuperan tildes con el BOCM por número de registro o con comunidad.madrid: Ramón y Cajal, Fundación Alcorcón, La Fuenfría, Rodríguez Lafora, Fundación Jiménez Díaz, Infanta Sofía, Beata María Ana, Fundación Instituto San José, Lavapiés, Dr. Pedro Laín Entralgo e Infante Don Luis de Borbón. Declarados sin fuente: HM Nuevo Belén, HM Montepríncipe y Quirónsalud ×3. Sincronizado.
  - **DATA-018 F1–F3b** (`91aeea1`, `70b112c`, `f7e29ab`, `8330771`, **D-222**): 1.404 parques de OSM de 1 ha o más (umbral de la OMS) como lugares `green` con los puntos de su borde. Casa de Campo y Quinta de Torre Arias entran por `data/catalog/corrections/parks.yaml` con la lista oficial del Ayuntamiento. Features `min_a_pie_parque` y `pct_calle_parque_5min` hasta el borde. La prioridad «Zonas verdes» puntúa (`fit-0.3`); sin parque a un paseo vale 0 con confidence ≤ 0,5 y el texto «el campo no cuenta». No entra en «Qué falta». Revisado con `reviewer` dos veces.
- **Pendiente de otros:**
  - C despliega `8330771`: el arreglo de monotonía de la revisión. Es solo código, sin sync.
  - B, cuando regenere los fixtures de contrato: `apps/web/src/lib/__tests__/facilities.test.ts:154` tiene que buscar «Hospital Universitario Fundación Jiménez Díaz». Los fixtures siguen en `fit-0.2` a propósito.
- **Regla de sync (`datamad-10`, 12 nov):** cada petición dice si añade o cambia features o specs que el código desplegado no entienda. En ese caso se despliega antes y se sincroniza después. Hoy, el sync de DATA-018 F2 (`fit.priority`) rompió `/search` 12 min.
- **Next (línea A), en orden:**
  1. **DATA-019 accesibilidad física.** Antes de usar `wheelchair_boarding` del CRTM, comprobar su codificación con una fuente oficial. Metro trae 0: 762, 1: 6, 2: 282. Metro Ligero, 2: 71 y 0: 25, aunque sus paradas son a nivel. Cercanías, 1: 74 y 2: 21. EMT no trae el campo. Parece que el CRTM no usa el estándar GTFS (2 = no accesible). Si no hay fuente que lo aclare, SIN DATOS. Complemento previsto: instalaciones accesibles del Ayuntamiento (D-205). La prioridad «sin escaleras» ya existe en la web («aún sin datos»), con `PRIORITY_WALK` y `FitBinding.priority` como patrón.
  2. **DATA-020 seguridad.** Hay un dataset CM candidato sin características de personas: `hechos_conocidos_penales_por_tipologia_municipios_mayores_20000_por_municipio`, el Balance de Criminalidad por municipio de más de 20.000 habitantes. Encaja con §11 (oficial y agregado) si se usa por 1.000 habitantes, sin etiquetas y con SIN DATOS por debajo de 20.000. Revisar D-205, que descartó los «delitos» del portal CM por la nacionalidad: este no la lleva.
  3. DATA-021 precio de compra y MCP-001 (3–5 herramientas).
  4. Deuda: `drop_off_type` del GTFS (M-3 de CORE-009); la segunda pasada de osmium para inclusiones ensambla todas las áreas (unos 2 s, aceptado); el script de comparación con la lista del Ayuntamiento no está versionado (resultado en `evidence/gate-01/2026-11-12/parques.md`); Gate 3 completo tras las correcciones.
- **Gate status:** `make lint typecheck test` en verde en `8330771`: 553 unit, 282 web y 102 integración. Golden de búsqueda 7/7.
- **Relevo:** A v11 cierra aquí tras 2 cards; continuar con `~/Desktop/DATAMAD/prompts/RELEVO.md`.

### Estado de la sesión del 12 nov (mañana, línea A v10)
- **Done (A v10):** D-219 (pooler en modo transacción, `de9ad4b`); HOSP-001 F3–F4 (nombres de atención primaria y fichero de correcciones, D-218 §9–§10); CORE-009 F1–F3c (transporte público al trabajo, D-220, `fit-0.2`, desempates estables); API para B (`attribution_text`, `/places` con varias categorías); CI de nuevo en verde (`9cb54fe`).
- **Next (línea A), en orden:** (1) confirmar el sync de `2ef95ca` por MCP; (2) DATA-018 a DATA-021 (zonas verdes, accesibilidad, seguridad con salvaguardas, precio de compra), cada una con su fase; (3) MCP-001: 3–5 herramientas sobre los servicios de dominio; (4) deuda: `drop_off_type` en el GTFS (M-3 de la revisión de CORE-009), matriz con aristas por pareja evento-footpath (memoria) si se amplía la ventana, y Gate 3 completo tras las correcciones.
- **Gate status:** `make lint typecheck test` verde en `2ef95ca` (531 unit, 277 web, 102 integración); CI verde en `9cb54fe`; golden de búsqueda 6/6 con orden estable.
- **Relevo:** la sesión A v10 cierra aquí por contexto; continuar con `~/Desktop/DATAMAD/prompts/RELEVO.md`.
- **Variables de la API en Vercel (para C, D-219).** C las documenta en `infra/deploy/README.md`:
  | Variable | Valor en producción | Cuándo |
  |---|---|---|
  | `DB_POOL_SIZE` | `2` | ya (mitigación del incidente, `4645326`) |
  | `DB_MAX_OVERFLOW` | `1` | ya |
  | `DB_PREPARED_STATEMENTS` | `false` | **antes** de que Mariano cambie el puerto; funciona también en 5432 |
  | `DATABASE_URL` | mismo valor con el puerto `6543` en vez de `5432` | lo cambia Mariano, después de desplegar `DB_PREPARED_STATEMENTS=false` |

  Orden: (1) C pone `DB_PREPARED_STATEMENTS=false` y redespliega (smoke en verde); (2) Mariano cambia el puerto de `DATABASE_URL` a 6543; (3) C redespliega y pasa el smoke. Al revés, las consultas repetidas fallan con «prepared statement … already exists». Las migraciones y el sync siguen en 5432 (`SUPABASE_DATABASE_URL`): Alembic necesita el modo sesión. Valores no booleanos en `DB_PREPARED_STATEMENTS` hacen fallar el arranque.
- **Sync de HOSP-001 F3 hecho** por `datamad-10` (12 nov) y comprobado por MCP.
- **Migrate 0007 + sync de CORE-009 F2 hechos** por `datamad-10` (12 nov), comprobados por MCP.
- **Pendiente (CORE-009 F3b, `7e4aa7c`), sin migración:** `make supabase-sync PROFILE=demo` (la matriz cambia tras la revisión). Comprobación por MCP: `select count(minutes) from commute_time` → 73783; `select minutes from commute_time where hub_id = 'estacion:metro:puerta del sol' and origin_admin_unit_id = 'ES.28.MUN.28065'` → 38,6 (Getafe). Después C redespliega la API (`fit-0.2`). Avisar a D: el caso demo cambia de orden (Fuencarral-El Pardo 100 %, Ciudad Lineal 99 %) y el hecho del trabajo ya no es en línea recta.
- **Peticiones de B hechas:** `attribution_text` y `/places` con varias categorías (ver registro).
- **Pendiente (HOSP-001 F4, `2ef95ca`, y la atribución del IGN, `8aeba3f`), sin migración:** `make supabase-sync PROFILE=demo`. Comprobación por MCP: `select canonical_name, attributes->'directory'->>'capacity' from place_master where official_entity_id = 'CH0049'` → «Hospital Universitario Ramon y Cajal», 886; `select count(*) from place_master where attributes ? 'correction'` → 5; `select attribution_text from source_registry where source_id = 'ign_cartociudad'` → «Geocodificación: © Instituto Geográfico Nacional (CartoCiudad), CC BY 4.0 scne.es.».
- **Decisión pendiente de Mariano (ya estaba en el board):** fichero de correcciones versionado con fuente oficial por registro. Lo necesitan el Ramón y Cajal (CH0049, el Catálogo Nacional de Hospitales lo sitúa en la calle de Ayala 38, 28001), los centros de salud «S/N» y el CEIP de Navalafuente.

### Estado de la sesión del 12 nov (madrugada, relevo de la línea A v8)
- **Done (A v8), fase de prueba (`prompts/FASE_PRUEBAS.md`, sección A):**
  - **T1** (`1913393`, `e7864bd`, **D-216**): auditoría de equipamientos frente a totales oficiales (`scripts/audit_places.py`). Farmacias como `pharmacy`; fuera los 1.001 «Centro Polivalente» (clínicas privadas); 40 lugares geocodificados con CartoCiudad (portal, calle y municipio declarados). Los 55 colegios en cuarentena: la fuente no publica coordenadas; 15 recuperados y los 40 restantes sin portal utilizable. Revisión de 10 zonas de D (D1–D7) respondida en el informe.
  - **T2a + T2b** (`b88c4fb`, `e7864bd`, **D-217**): 2SFCA en las 5 filas de servicios y agrupación de municipios pequeños con vecinos (≤ 15 km, mínimo de 3,69 casos esperados). Tablas CM de hospitales y camas (solo totales regionales). Sensibilidad 10/20 min: Spearman ≥ 0,995.
  - **T4** (`6c4dd4b`): README público.
  - **T5** (`927af98`): CI verde y **Gate 3 PASS** (`evidence/gate-03/2026-11-12/summary.md`); golden de búsqueda 6/6 y golden a pie OK.
- **Blocked / a la espera de Mariano:**
  1. `make supabase-migrate` (**0006**: categoría `pharmacy`; sin ella el sync falla por la restricción de `place_master`).
  2. `make supabase-sync PROFILE=demo` (lugares, features 2SFCA y `min_a_pie_hospital`, registros). Comprobación por MCP: `select count(*) from place_master where category = 'pharmacy'` → 2.957; `select count(*) from feature_value where feature_id like '%\_a\_pie\_por\_%'` → 1.005.
  3. Después, C redespliega la API (código nuevo: `/places` `places-1`, `gap-0.3`, agrupación). B adapta la web a `comparison_group` y a los textos del 2SFCA (su PR #13).
- **Next (línea A), en orden:**
  1. Camas por hospital: Catálogo Nacional de Hospitales 2025 (Ministerio de Sanidad, XLSX, reutilizable con cita) como fuente complementaria, con resolución de entidades frente al registro CM (dirección + CP), para `capacity` en `/places` («Hospital La Paz · N camas») y nombres de hospitales.
  2. Los 4 centros de salud «S/N» (Alcalá 2, Madrid 2), el consultorio de Villar del Olmo y el CEIP de Navalafuente: sin coordenadas utilizables. Opciones: pedir la corrección al portal CM o un fichero de correcciones versionado con fuente oficial por registro (decisión de Mariano).
  3. Bug del runner: si una ingesta falla tras registrar la versión, la siguiente se la salta («same checksum and parser»); arreglar en `versions.register_version`.
  4. E2SFCA (decaimiento con la distancia) y tope a vecinos muy grandes en la agrupación (anotado por `reviewer`), si hay tiempo.
  5. Lo que seguía de A v7: CORE-009, extras DATA-018 a DATA-021, MCP 3–5 tools.
- **Gate status:** `make lint typecheck test` verde en `927af98` (426 unit, 226 web, 90 integración); CI verde; **G3 PASS** 12 nov (38 features, 13 a pie × 4.843 zonas, 17 por distrito); G1 PASS para los 4 registros reingeridos y las 2 tablas de hospitales.
- **Notas:**
  - Las features de recuento (centros por habitante) siguen como extras de cada fila; la primaria es la 2SFCA.
  - `inputs.counts` de las features 2SFCA está en centros equivalentes (capacidad / capacidad media por centro de la región): el ratio no cambia y la prueba de Poisson cuenta centros.
  - Radio de agrupación configurable con `GAP_POOL_RADIUS_M` (15000 por defecto, D-217 §6).
  - Para repetir la evidencia: `scripts/gap_status_summary.py`, `scripts/fca_sensitivity.py`, `scripts/audit_places.py`.

### Estado de la sesión del 11 nov (noche, relevo de la línea A v7)
- **Done (A v7):**
  - **CORE-006** (`100cb29`, `92eab6b`, `7311370`, **D-214**): alquiler €/m² en los 21 distritos desde el dataset CM de códigos postales (proxy por lugares, confidence ≤ 0,8; **21 de 21 datasets CM alimentan features**); condición de presupuesto PASS/FAIL/UNKNOWN; m² por hogar según el Censo 2021 (61, 68, 71, 77 y 77); compra «Sin datos» hasta DATA-021. Revisado con `reviewer`.
  - **CORE-003** (`1507deb`, `915be3c`, `5f373b6`, **D-215**): Residential Fit `fit-0.1`, Reality Check y **`POST /api/v1/search`** con datos reales (199 zonas, 0,2 s en local). 6 escenarios dorados en datos reales (`scripts/golden_search.py`); el fixture de búsqueda es ya la salida real. Revisado con `reviewer`.
  - D-213: ya figuraba como aprobada (pedido de `datamad-10`), sin cambios.
- **Blocked / a la espera de Mariano:**
  - `make supabase-sync PROFILE=demo`, **sin migración** (Alembic sigue en 0005): lleva `alquiler_m2_mensual` v2 (distritos) y los enlaces `fit` del Feature Dictionary. Comprobación por MCP: 21 filas de `alquiler_m2_mensual` por distrito con valor y 7 features con `spec->'fit'`. El sync de F5 (`inputs.counts`) ya está en Supabase: 1.744 filas, comprobado por MCP.
  - Después, C redespliega la API (la ruta `/search` es código nuevo) y `datamad-10` enciende `NEXT_PUBLIC_FEATURE_SEARCH`. B conecta el buscador con `max_minutes: null` en el trabajo (el límite de trayecto sale UNKNOWN hasta CORE-009).
- **Next (línea A), en orden:**
  1. Medir `POST /search` contra Supabase tras el sync (en local 0,2 s; los mapas de `/gaps` quedan en caché por proceso hasta que cambian las features).
  2. Repetir el Gate 3 (`make evidence GATE=03`) con las features actuales.
  3. Pendientes de D-215: diversificación/Pareto, tiempo de trayecto real (CORE-009) y los extras (zonas verdes, seguridad, «sin escaleras») del 19 al 22 nov.
- **Gate status:** `make lint typecheck test` en verde en `5f373b6` (367 unit, 172 web y 89 de integración). G4: `/gaps`, `/search` y `/datasets` con datos reales.
- **Notas:**
  - Los m² supuestos y el coste son orientativos y tiran a la baja (contratos vigentes; m² catastrales), D-214.
  - `scripts/build_contract_fixtures.py` usa ya el servicio real de búsqueda (el constructor ilustrativo se sustituyó).

### Estado de la sesión del 11 nov (noche, relevo de la línea A v6)
- **Done (A v6):**
  - **DATA-022 F1** (`c4f1bc0`, `b1f899e`, **D-212**): nombres oficiales de municipios (tabla CM) y de los distritos de Madrid (panel del Ayuntamiento), con el paso `make admin-names` y un check crítico contra «/», «Ð» y cualquier carácter fuera de la ortografía española. Ya está en Supabase y en producción (`995f7ce`).
  - **GAP-001 F4** (`697dbaf`): `GET /api/v1/gaps?level=&row=` (`GapRowMap`), coherente con la lista de cada zona.
  - **GAP-001 F5** (`d02574f`, `f626e1f`, `f1b487a`, **D-213, aprobado por Mariano**): método `gap-0.2`. Referencia de los demás municipios del mismo tipo (Ley 45/2007), FALTA material y significativa (Poisson al 95 %) y `reliable` para las zonas pequeñas. Las features por población guardan `inputs.counts`. **GAP-001 queda completa a falta del sync** (y de que B pinte «poco fiable»).
  - Revisiones con `reviewer`: PR #2 de B (lo fusionó `datamad-10` con autorización de Mariano, `bd5b006`) y PR #8 de C (comentario: antes de fusionar, quitar de `deploy-8-verified.md:36` el slug de Vercel con el apellido).
- **Blocked / a la espera de Mariano:**
  - `make supabase-sync PROFILE=demo`, sin migración: `feature_value` con `inputs.counts` (F5). Después, C redespliega la API para servir `gap-0.2`. Comprobación por MCP: `select count(*) from feature_value where inputs ? 'counts'` > 0 y, en la API pública, `method.version = gap-0.2`.
  - Fusiones de PRs: a la línea A se las bloquea el clasificador de permisos (`gh pr merge` y el merge local). PR #8 de C: revisado, pendiente del cambio de datos personales y del merge por `datamad-10`/Mariano.
- **Next (línea A), en orden:**
  1. **CORE-006, asequibilidad.** Datos ya cargados:
     - `alquiler_m2_mensual_municipio` (179 municipios, 2024; feature `alquiler_m2_mensual`);
     - `alquiler_m2_mensual_codigo_postal`: 54 códigos postales de Madrid capital, 2024. Es el dataset CM 21 de 21, `cm_alquiler_m2_codigo_postal_madrid`, y hoy no alimenta ninguna feature.

     No hay geometría de códigos postales (DATA-013 está en backlog). Propuesta para llevar el CP a los distritos sin geometría: una tabla de correspondencia hecha con los lugares geocodificados que traen código postal (colegios, centros de salud y farmacias tienen dirección). El distrito de cada CP sería el mayoritario y el peso, la parte de los lugares; la confianza, la parte del CP que cae en ese distrito. Hay que declararlo como proxy.

     Además:
     - el alquiler por distrito sería la mediana ponderada de sus CP;
     - la condición de presupuesto es PASS/FAIL/UNKNOWN: alquiler del m² × m² supuestos según el hogar frente a `budget.amount_eur`. D pidió los m² que se suponen por tamaño de hogar: hay que fijarlos con una fuente (por ejemplo, el tamaño medio de vivienda del censo o la norma de vivienda protegida) en un ADR;
     - compra: sin fuente oficial abierta fiable, `UNKNOWN` declarado (D-203).
  2. **CORE-003:** Residential Fit, Reality Check y `POST /api/v1/search` según `hi_contracts/public/search.py` (v2). Cuando esté en verde, avisar a `datamad-10` para encender `NEXT_PUBLIC_FEATURE_SEARCH`.
  3. Repetir el Gate 3 (`make evidence GATE=03`) con las features actuales.
- **Gate status:** `make lint typecheck test` en verde en `f1b487a` (327 unit, 172 web y 81 de integración). G4: `/gaps` (lista y mapa) con `gap-0.2`. G3 sin repetir desde el 11 nov a las 16:15.
- **Notas:**
  - Si cambias `data/schemas/api`, regenera también los tipos de la web (`npm run -w apps/web contracts`): su test de sincronía falla en la CI.
  - Un `apps/web/.next` local antiguo rompe `tsc`: bórralo, porque no se versiona.
  - Los nombres oficiales se pierden si se vuelve a publicar la geografía: después de las tablas estadísticas, `make admin-names` (el CLI lo avisa).

### Estado de la sesión del 11 nov (tarde-noche, relevo de la línea A v5)
- **Done (A v5):** GAP-001 F1 (`2d05d78`), F2 (`21939dd`), F3a (`4523d69`) y F3b (`98b842a`, `ea8ee74`), todas con gate verde, evidencia y `reviewer`. `/gaps` da las 6 filas por municipio y por los 21 distritos, con extras (minutos a pie, ratio oficial de farmacias, plazas de residencia, aulas de infantil, nacimientos, % en alquiler y tamaño medio del hogar). Vivienda por distrito sale `SIN_DATOS` (`SOURCE_MISSING`). 20 de los 21 datasets CM alimentan features.
- **Blocked / a la espera de Mariano:** `make supabase-sync PROFILE=demo` con F2–F3b (features nuevas y colegios v2; sin migración). Después, comprobarlo por MCP: 11 features nuevas o cambiadas, 21 filas `not_published` de vivienda por distrito y `colegios_publicos_por_1000_menores` en `feature_version` 2. C no necesita redesplegar: la API lee las filas de la base.
- **Next (línea A), en orden:**
  1. **Nombres de municipio con la ñ rota** (lo pide B a través de `datamad-10`): «REDUE/A», «GRIÐON», «CARABA/A», «COBE/A», «FUENTIDUEÐA DE TAJO», «MORATA DE TAJUÐA», «ORUSCO/PERALES DE TAJU/A», «PI/UECAR-GANDULLAS», «VILLANUEVA DE LA CA/ADA» y sus distritos censales. **La fuente está rota:** el CSV de `cm_secciones_censales` trae «/» o el byte 0xD0 en lugar de la Ñ, así que no se arregla con el encoding.
     - Propuesta: en `admin_boundaries`, tomar los nombres de municipio de una tabla estadística de la CM que ya ingerimos (`territory_name` de `cm_poblacion_edad_nacionalidad_sexo`: «Griñón», «Alcalá de Henares», «Álamo (El)»). Que `display_name` convierta «Álamo (El)» en «El Álamo», y añadir un check de calidad crítico, más un test, que falle si un nombre lleva «/», «Ð» o caracteres fuera de las letras españolas.
     - Resuelve también DATA-022 para los municipios. Los distritos de Madrid y los barrios vienen de otra columna: revisarlos.
     - Necesita otro sync.
  2. **F4:** nivel sección y `GET /api/v1/gaps?level=&row=` (estado por zona para la coropleta).
  3. **F5:** ADR de los cortes con criterio estadístico (sin mirar el 0,79 de Chamartín) y número D-xxx. Para D: qué mide cada fila, los cortes y el estado de Chamartín después del ADR. Ojo: con los indicadores v2, la mediana municipal de vivienda es 327 frente a 178 de la región, así que casi todos los municipios saldrían CUBIERTO. El ADR debe decir si la referencia regional sirve igual para todas las filas.
  4. CORE-006 (D pide los m² que se suponen según el tamaño del hogar; conecta `cm_alquiler_m2_codigo_postal_madrid`, el dataset CM 21 de 21) → CORE-003 → `POST /api/v1/search`.
- **Gate status:** G4 verde con `/gaps` de 6 filas (`ea8ee74`). G3 no se ha vuelto a pasar desde el 11 nov a las 16:15; hay que repetirlo (`make evidence GATE=03`) con las features nuevas cuando HEAD tenga la CI en verde.
- **Notas:** `metric_ratio` toma el periodo del denominador. `inputs.method` guarda el método efectivo de cada nivel. Los umbrales de población pequeña (infantil 200, mayores 300, farmacia y nacimientos 2.000) se pueden revisar en el ADR.

### Estado de la sesión del 11 nov (noche, relevo de la línea A v4; su Next ya está hecho o pasado a A v5)
- **Done (esta sesión, A v4):**
  - PR #7 de C integrado (`93af627`) con `reviewer`: el smoke mide la página 1 de transporte (7/7). Pendiente menor de C: exigir `.data.pages >= 1` en el check `largest`.
  - **CORE-005 Fase 5** (`ad2129a`, **D-211**): 4 km/h en las 12 features a pie, que pasan a la versión 2. Los 15 golden cumplen sin tocar los límites y el **Gate 3 da PASS**. Chamartín: centro de salud 9,47 min y farmacia 2,57 (enviados a D por `datamad-10`).
  - **Supabase** sincronizado por Mariano y comprobado por MCP.
  - **DATAMAD-PUBLIC-01 Fase 3** (`12bd103`): no quedan rutas locales en el árbol. `scripts/redact_paths.py` las sanea y `tests/data/test_no_local_paths.py` las vigila en la CI.
  - Antes (A v3): peticiones de B a la API cerradas (`d3127d3`, `d7037b7`, `12c834a` y `879101a`), CORE-005 DONE (`fc025b6`) y PR #6 de C (`877d4fd`).
- **Blocked / a la espera:** nada. **Supabase:** sincronizado por Mariano tras los 4 km/h y comprobado por MCP (12 features a pie en `feature_version` 2, con 4.843 filas cada una). La API pública no necesita redespliegue hasta que GAP-001 sirva las features a pie: entonces hay que avisar a `datamad-10`.
- **Next (línea A), en orden.** Las tres decisiones de Mariano del 11 nov por la noche están hechas: PR #7 de C (`93af627`), 4 km/h (D-211, `ad2129a`, ya en Supabase) y sin rutas locales en el árbol (`12bd103`).
  4. **GAP-001 completo** (checkpoint del 13 nov). Fases propuestas, cada una con su commit:
     - ~~F1 `extra_indicators`~~ **hecha** (`2d05d78`); avisado `datamad-10` para que C redespliegue.
     - ~~F2 filtro de colegios~~ **hecha** (`21939dd`). ~~F3a escuela infantil, mayores y farmacia~~ **hecha** (`4523d69`).
     - **F3b (siguiente):** vivienda (viviendas de más de 90 m² por cada 100 hogares de 4 o más personas; por distrito SIN DATOS explícito), unidades escolares de infantil, natalidad y % de viviendas en alquiler como extras. Hace falta un método `metric_ratio` (dos métricas). Conecta `cm_unidades_escolares`, `cm_nacidos_vivos_municipios` y `cm_viviendas_tenencia_censo_2021`.
     - **F2 filtro de colegios:** usar los mismos destinos que `min_a_pie_colegio` (primaria, público o concertado); hoy cuenta escuelas infantiles e IES. Nueva versión de la feature y del `proxy_note`.
     - **F3 filas nuevas por municipio y distrito**, con los tests primero:
       - farmacia: puntos de `cm_oficinas_farmacia` por población, con `places_per_population`; `cm_farmacias_municipios` publica la ratio oficial y sirve para contrastar;
       - mayores: centros de mayores (los mismos destinos que `min_a_pie_mayores`) por cada 1.000 mayores de 65; las plazas de residencia son otra medida;
       - escuela infantil: `cm_unidades_escolares` de un único nivel (nunca sumando miembros) frente a la población de 0 a 4 años o a `cm_nacidos_vivos_municipios`;
       - vivienda: tamaño de los hogares (`cm_hogares_tamano_censo_2021`) frente a la superficie de las viviendas (`cm_viviendas_superficie`); por distrito queda SIN DATOS.
     - **F4 nivel sección y `GET /api/v1/gaps?level=&row=`.**
     - **F5 ADR de los cortes** con criterio estadístico, golden y `reviewer`. Chamartín salud = 0,79: no mover los cortes por ese caso, y decirle a D si cambia de estado.
     - En la web, mejor mostrar los minutos muy altos (hasta 380 en pueblos sin colegio, a 4 km/h) como «más de 60 min»: proponérselo a B.
  5. CORE-006: D pide los m² que se suponen según el tamaño del hogar.
  6. CORE-003 con Reality Check: D pide cómo se reparten los pesos y cómo se pasa a %, con el caso de la Castellana, y el presupuesto con el que aparece el Reality Check.
  7. `POST /api/v1/search`; los distritos entran en `all_zones`.
- **Peticiones abiertas de otras líneas:**
  - **D:** el párrafo de metodología §1.5 (a pie) ya está enviado. Faltan los de GAP-001, CORE-006 y CORE-003. Conectar los datasets CM que aún no alimentan nada: unidades escolares, nacidos vivos, viviendas por tenencia, alquiler por código postal y farmacias por municipio. Los 6 GTFS y las oficinas de farmacia ya alimentan CORE-005.
  - **B:** los JSON Schema se exportan en modo validación (`near_misses`, `meta` y `warnings` salen opcionales en TypeScript); valorar el modo serialización. Pedir transporte filtrado o recorrer `pages`.
- **Para Supabase:** tras cada cambio de features o de lugares, pedir a Mariano `make supabase-sync PROFILE=demo` (las sesiones no pueden) y comprobarlo después por MCP.
- **Gate status:**
  - G1 PASS: 21 datasets CM y 2 complementarios del Ayuntamiento; la red OSM pasa su calidad.
  - G2 PASS.
  - G3 PASS (11 nov, `evidence/gate-03/2026-11-11/summary.md`, a 4 km/h): 24 features (`24|0|0|179`), 7 con los 21 distritos, 12 a pie con las 4.843 zonas y los golden de la red real.
  - G4: contratos, `/gaps`, `/places` y `/geo` en verde.
  - G6: Supabase en 0005; el sync único llega tras recalcular a 4 km/h. C sirve la demo desde `cf33a5b`, con `/places` paginada (smoke 7/7).
- **Notas para las siguientes cards:**
  - **Evidencia sin rutas locales:** guarda las salidas de los gates de fase a través del filtro: `set -o pipefail; { …; make lint typecheck test 2>&1; echo "exit=$?"; } | uv run python scripts/redact_paths.py > evidence/…`. `make evidence` ya sanea solo. `tests/data/test_no_local_paths.py` falla en la CI de cualquier línea si se cuela una ruta.
  - **Gate local = CI:** `make lint typecheck test`. `lint` incluye `export_schemas --check` y `check_docs_manifest`. Si cambias `docs/`, regenera con `uv run python scripts/check_docs_manifest.py docs --write <versión siguiente>`; hoy está en 0.5.22.
  - **Features a pie (D-210, D-211: 4 km/h y versión 2):**
    - `hi_features/walk.py` carga la red, los orígenes y las distancias una vez por proceso;
    - van con la clave `destination_category`, no `category`, para que `compute` no les aplique el ajuste de los conteos por sección;
    - en integración, una rejilla OSM sintética sobre la muestra de Madrid más la muestra GTFS (`tests/integration/conftest.py`).
  - 24 secciones pequeñas sin calle de origen salen SIN DATOS (15 en Moratalaz y Villa de Vallecas). Una mejora posible: usar cualquier vía transitable como origen en esas secciones.
  - Unidades escolares: elegir el nivel de enseñanza, nunca sumar miembros.
  - La API devuelve los errores como `{"detail": {code, message}}`; `ErrorEnvelope` es el formato objetivo.
  - El `center` de Madrid usa `ST_PointOnSurface` (cae al norte del municipio).
  - **Features por nivel** (DATA-012):
    - `formula.levels.<nivel>` es un override superficial;
    - `FeatureSource.levels` dice qué datasets cita cada nivel;
    - la referencia regional sale solo del nivel base.
  - `places_per_population` declara `geocoding_quarantine` en `confidence.inputs`, pero no lo aplica (deuda anterior).

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
- DATA-022 Nombres con tilde («El Álamo», «Vicálvaro», «Móstoles»): nombre oficial del INE o relación de municipios de la CM, con su fuente declarada, en los datos y no parcheado en la web (propuesta de `datamad-10`, prioridad baja)
- CORE-005b Distancia a pie por H3 r9, cuando la vista 3D de la zona lo necesite (vigilar el tamaño en Supabase)

## 01b — PITCH (23–25 nov)
- PITCH-001 4 slides de §8 con el estilo del PDF del 31 oct
- PITCH-002 Guion de 5 min y banco de preguntas (§8 del plan)
- PITCH-003 Vídeo de respaldo de 2 min y snapshot offline de la demo
- PITCH-004 5 ensayos cronometrados (Mariano)

## 06 — BLOCKED (decisión de Mariano)
_(vacío)_

## 07 — DONE (con evidencia)
- CORE-003 Residential Fit + Reality Check + API-002 `POST /api/v1/search` (D-215, `fit-0.1`): condiciones PASS/FAIL/UNKNOWN, % de encaje con hechos, Reality Check aplicable y 6 perfiles dorados en datos reales · G4 `evidence/gate-04/2026-11-11/phase-core003-f1.txt`, `-f2.txt`, `-f2-review.txt` · `1507deb` `915be3c` `5f373b6` · 2026-11-11 (falta el sync)
- CORE-006 Asequibilidad (D-214): alquiler €/m² por municipio y por los 21 distritos (CP → distrito), m² por hogar del Censo 2021, presupuesto PASS/FAIL/UNKNOWN y compra «Sin datos» · G4 `evidence/gate-04/2026-11-11/phase-core006-f1.txt`, `-f2.txt`, `-f2-review.txt` · `100cb29` `92eab6b` `7311370` · 2026-11-11 (falta el sync)
- CORE-005 Distancia a pie por la red de calles (D-210; 4 km/h desde D-211): 12 features (escuela infantil, colegio, centro de salud, farmacia, centro de mayores y parada × mediana de minutos y % de calle dentro de la ventana) por sección, municipio y distrito, con referencia regional; nunca 0 sin datos · G1 `evidence/gate-01/2026-11-11` (red OSM) · G3 PASS `evidence/gate-03/2026-11-11/summary.md` · `4cdee28` `e31770b` `23b7531` `fc025b6` · 2026-11-11
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
