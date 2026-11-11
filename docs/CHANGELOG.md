# Changelog

## v0.5.23 — Lista de lo que falta: cinco filas (2026-11-11)
- `04_technical_architecture/31_public_api_routes.md`: `/gaps` trae escuela infantil, mayores y farmacia por municipio y por los 21 distritos (GAP-001 F3a), además de colegio y centro de salud. La fila de colegios cuenta colegios con primaria, públicos o concertados (F2). Extras: la ratio oficial de farmacias de la CM y las plazas de residencia.

## v0.5.22 — Lista de lo que falta: minutos a pie (2026-11-11)
- `04_technical_architecture/31_public_api_routes.md`: `GET /api/v1/gaps/{level}/{code}` trae en `extra_indicators` los minutos a pie hasta el colegio y el centro de salud más cercanos (GAP-001 F1). Son indicadores que acompañan a la fila, sin estado propio, y sus datasets se suman a la procedencia de la fila.

## v0.5.14 — Vida Fácil y contratos v2 (2026-11-11)
- D-199 a D-207: nombre «Vida Fácil», escala (municipios + 21 distritos de Madrid), mapa 2D/3D y estilo, % de encaje con hechos, presupuesto de alquiler o compra, prioridades, extras con sus reglas de seguridad y accesibilidad, orden núcleo/extras y contratos PUBLIC v2.
- `09_datamad/25_plan_competicion.md` §1, §6 y §8 con el nombre y el estilo nuevos.
- `04_technical_architecture/31_public_api_routes.md`: contratos v2, nivel `distrito` en la lista, `GET /api/v1/datasets` y CORS con `POST`.

## v0.5.13 — Lista de lo que falta: esqueleto andante (2026-11-11)
- `04_technical_architecture/31_public_api_routes.md`: `GET /api/v1/gaps/{level}/{code}` ya responde con datos reales (colegio y centro de salud por municipio). La referencia regional es una fila `ccaa` del Feature Store: el total de la región dividido por su población. Las filas se declaran en el Feature Dictionary (`gap_row`). Con la migración 0004, `dataset_registry` guarda el enlace al portal CM e `is_cm_open_data`.

## v0.5.12 — Contratos PUBLIC de la demo (2026-11-11)
- `04_technical_architecture/31_public_api_routes.md`: contratos `ScenarioState`, `SearchResult` (ranking, motivos y Reality Check) y `ZoneGapList` (FALTA / JUSTO / CUBIERTO / SIN DATOS), sus JSON Schema en `data/schemas/api/` y las rutas previstas. La web (línea B) genera sus tipos desde ahí.

## v0.5.11 — Supabase configurado (2026-11-11)
- D-197: RLS en todas las tablas públicas, sin políticas (migración 0003). Supabase queda con el esquema en head y el perfil demo cargado (100 MB). La Data API no expone filas.
- D-198: repo público con el historial limpio; completa D-195.

## v0.5.10 — Repo público (2026-11-11)
- `09_datamad/25_plan_competicion.md` §7: el historial se publica limpio en la misma URL. El original queda en `housing-intelligence-archive` (privado). El tag `pre-datamad` pasa a `cf39459` y mantiene la fecha del 22 oct.

## v0.5.9 — Preparación del repo público (2026-11-11)
- `09_datamad/25_plan_competicion.md` §7: OK de Mariano al email de autor y a `docs/` visibles. Los fixtures de equipamientos se redactan (contacto, NIF y titulares). Queda pendiente decidir qué se hace con el historial.

## v0.5.8 — Datasets CM nuevos (2026-11-10)
- DATA-016: farmacias (registro y tabla municipal), unidades escolares, nacidos vivos y viviendas por régimen de tenencia. El plan pasa a 21 datasets del portal CM con Quality Gate.

## v0.5.7 — Transporte CRTM nivel A (2026-11-10)
- D-196: los 6 GTFS del CRTM (también publicados en el portal CM) pasan a paradas y estaciones con frecuencias en `place_master`; día de referencia y punta declarados.
- `02_data/32_transport_ingestion_spec.md`: estado de la implementación y pendientes.

## v0.5.6 — Plan de competición (2026-11-10)
- `09_datamad/25_plan_competicion.md`: fases, criterios del jurado, calendario con responsables, formulario, repo público, pitch y día 26.
- D-194: la demo se centra en el buscador para personas y la lista de lo que falta por zona. D-195: repo público como tarde el 18 nov.
- `CLAUDE.md` §7: prioridad actual = fase de competición; regla de una sola sesión escribiendo en la carpeta principal.

## v0.5.5 — Arranque de la fase de competición (2026-11-10)
- D-191: licencia Apache-2.0 (código) + CC BY 4.0 (docs y catálogo); cierra LEGAL-001.
- D-192: replan comprimido hasta el 26 nov; tag `pre-datamad` y merge de P0, P1 y POIs abiertos en `main`.
- D-193: formulario de presentación obligatorio antes del 20 nov; despliegue y repo público adelantados.
- Roadmap del doc 19 marcado como superado por D-192 en las fechas de competición.

## v0.5.4 — Sprint P1: datos de la Comunidad de Madrid (2026-10-22)
- Decisiones D-186 a D-190: protección de personas vulnerables, modelo de observaciones, pipelines declarativos, Supabase, features, search_path.
- 9 datasets nuevos de la Comunidad de Madrid ingeridos con Quality Gate; 12 features municipales en el Feature Store.

## v0.5.3 — POIs abiertos (2026-10-20)
- D-185: Gosom descartado definitivamente; registradas Overture Places y FSQ OS Places.
- Estrategia de enriquecimiento ampliada con POIs abiertos (sección 6b).

## v0.5.2 — Sprint P0 en ordenador (2026-10-20)
- Leídas las bases oficiales DATAMAD 2026: añadido `09_datamad/24_bases_oficiales_2026.md`; blocker de trabajo previo cerrado.
- Añadida source review de Google Maps/Gosom (`07_privacy_legal/source_reviews/`), estado REJECTED.
- Decisiones D-174 a D-184 (entornos, toolchain, imagen DB, capa de datos, geografía canónica, scorecard, idempotencia).
- Calendario actualizado con criterios ponderados, formato de entrega y jornada final.
- Documentación movida a `docs/` del monorepo `housing-intelligence`; `CLAUDE.md` vive en la raíz.

## v0.5.1 — Computer handoff
- Última auditoría de falsos pendientes/TODOs.
- Marcados documentos de preguntas históricas como superados.
- Aclarado qué pendientes son deliberadamente dependientes de datos, legal o validación comercial.
- Añadido `START_HERE_ON_COMPUTER.md`.
- Añadido plan operativo de primeras 72 horas.
- Definido orden exacto de arranque: Control Tower → Data Foundation → first real pipeline → map proof.

## v0.5.0 — DATAMAD execution roadmap
- Verificado calendario oficial DATAMAD 2026.
- Añadido blocker para confirmar si la implementación específica previa al 7 de noviembre está permitida.
- Creada hoja de ruta por sprints del 20 de octubre al 26 de noviembre.
- Mapeados Sprints a Quality Gates.
- Definida estructura Trello/kanban.
- Creado protocolo operativo para Claude Code.
- Añadida Definition of Ready.
- Añadido template de daily/sprint review.
- Añadidos milestones internos, feature freeze y final freeze.

## v0.4.0 — Auditoría integral de completitud
- Auditoría completa de producto, datos, ML/AI, mapa, seguridad, privacidad, negocio, validación e ingeniería.
- Actualizado índice y eliminado backlog conceptual obsoleto.
- Añadidos account lifecycle, alerts, reports, roles PRO y listing analysis.
- Añadidos geocoding, geospatial QA, data drift, source onboarding y demo snapshots.
- Añadidas especificaciones de affordability, Housing Gap, calibration, uncertainty, spatial validation, JEV/RAG/LLM gates, fairness y model drift.
- Añadidos auth, tenancy, jobs, object storage, backup/restore, release/rollback, threat model, SLO/cost budgets, billing, API/MCP security y offline resilience.
- Añadidos requisitos WCAG, responsive map, performance budget y visual regression.
- Completado framework financiero, TAM/SAM/SOM y unit economics.
- Añadidos GDPR lifecycle, sensitive-data assessment, analytics consent, license workflow y open-source policy.
- Añadidos planes de validación de UX, datos, modelos, PRO y pricing.
- Añadidos submission checklist, demo runbook, jury evidence matrix, offline pack y open-source pack para DataMad.
- Creado sistema obligatorio de 14 Quality Gates, Master Test Catalog, CI/CD gates y planes de test especializados.
- Actualizada Definition of Done: ninguna fase puede cerrarse sin evidence artifact.

## v0.3.1
- Cambiada la estrategia a final-product-first.
- Añadida clasificación Tier 0–3 de capabilities.
- Añadidos capability flags y fallbacks.
- Añadido Scope Cut Registry.
- Prohibida conceptualmente una arquitectura paralela desechable para DATAMAD.

## v0.3.0
- Cerrada ronda 09: PRO, DATA y monetización.
- Definido ICP inicial de promotoras/inmobiliarias medianas.
- Añadida escalera de oferta desde informes hasta Enterprise.
- Definida arquitectura de pricing FREE/PLUS/PRO/DATA.
- Añadido flywheel PUBLIC → PRO → DATA.
- Añadido PRO Project Workspace.
- Añadido Opportunity Finder y Price Sensitivity Engine.
- Añadido modo manual de investigación de anuncios para DATAMAD cuando no exista acceso automatizado autorizado.

## v0.2.9
- Cerrada ronda 08 de Data Foundation operativa.
- Formalizada arquitectura Bronze/Silver/Gold.
- Añadido contrato de null/missingness.
- Añadida resolución de conflictos entre fuentes.
- Definidos feature stores por dominio y ventanas multiescala.
- Formalizada política de adquisición de anuncios y limitación de scraping no autorizado.
- Añadidas especificaciones de ingestión Catastro, CRTM, comercio y ambiente.
- Añadido pipeline de feature selection/redundancia.
- Añadido Feature Dictionary machine-readable.
- Añadidas reglas de adquisición para Claude Code.
- DATAMAD: 30–50 datasets profundamente integrados como objetivo MVP.

## v0.2.8
- Cerrada ronda 07 del Residential Fit.
- Especificado pipeline multi-stage.
- Formalizado hard/soft constraints con PASS/FAIL/UNKNOWN.
- Añadido Pareto/Trade-off Engine.
- Añadido contrato de componentes de score.
- Definida curva de presupuesto.
- Añadida diversificación de resultados.
- Añadida adaptación en sesión.
- Añadidos invariantes algorítmicos.
- Formalizada política de web enrichment subjetivo.

## v0.2.7
- Cerrada ronda 06 de onboarding y perfil.
- Sustituido formulario tradicional por experiencia map-first.
- Añadida capa Inclusive Living / Accessibility.
- Formalizado Accessibility Needs Model basado en necesidades, no diagnósticos.
- Añadidos modelos sensorial/cognitivo y reglas anti-inferencia sensible.
- Incorporadas fuentes reales de Madrid para accesibilidad visual, aceras, cruces y aforos.
- Añadidos modos de mapa de accesibilidad y confidence de cobertura.

## v0.2.6
- Añadida ronda 06 de decisiones sobre onboarding, perfil y semántica.
- Preparado bloque para convertir lenguaje natural en variables estructuradas y scoring.

## v0.2.5
- Cerrada ronda 05: contextual scoring, clustering, movilidad temporal y calidad.
- Añadido Active Questioning Engine.
- Añadido Service Pressure Model con fallback.
- Añadidos submodelos por etapa de vida.
- Añadido Data Coverage Map.
- Formalizado versionado temporal y correcciones históricas.
- Añadido pipeline de anomalías con reglas + estadística + JEV.
- Añadido Lineage & Dependency Graph.
- Knowledge Graph marcado como opcional.
- Scenario Engine DATAMAD definido como parcial y explícito.

## v0.2.4
- Cerrada ronda 04 del feature universe.
- Formalizado el principio micro-location: barrio no homogéneo.
- Especificado modelo de accesibilidad multimodal completo.
- Añadido 15-Minute Living Model y Car Dependency Model.
- Añadida política de seguridad objetiva y no estigmatizante.
- Añadido Urban Activity Model y Emerging Opportunity Model.
- Ratificado Total Housing Cost completo.
- Añadido blueprint de 300–500 features.
- Añadido Timeline/SimCity Mode.
- Especificado motor híbrido GIS + RAG + métricas.
- Añadido fallback de Building Intelligence.

## v0.2.3
- Cerrada ronda 03: privacidad, perfil, precisión, ML y forecasting.
- Formalizada política Madrid-first para DATAMAD.
- Añadido modelo de datos de usuario con separación de identidad, finanzas y necesidades sensibles.
- Añadida política de missing data y confidence.
- Definida evolución del Residential Fit desde baseline experto a Learning-to-Rank.
- Añadida explicabilidad ultra-simple orientada a consecuencias reales.
- Definida estrategia temporal 3–5 años + forecast 1–3 y escenarios posteriores.
- Añadida estrategia de cold start con perfiles sintéticos.
- Especificado simulador PRO de proyectos residenciales.
- Añadida narrativa de datos para el jurado DATAMAD.

## v0.2.2
- Añadida ronda de decisiones sobre perfil, privacidad, ML, confidence, fairness y simulación.
- Añadido documento de decisiones pendientes del ML core.
- Bloqueado conceptualmente el inicio de modelos productivos hasta cerrar esta ronda.

## v0.2.1
- Cerradas 19 decisiones técnicas/producto de la segunda ronda.
- Definido plan FREE/PLUS/PRO y monetización de particulares.
- Especificado Natural Language GIS y MapState estructurado.
- Añadido lenguaje visual SimCity/Jarvis.
- Definido Reality Check como optimizador.
- Añadida estrategia de aprendizaje por comportamiento.
- Especificado Housing Gap Product Recommender.
- Añadidas fases de adquisición de datos y scraping.
- Definido contrato para capas dinámicas generadas vía MCP.
- Añadidos escenarios completos de demo DATAMAD.

## v0.2.0
- Convertida la documentación en un paquete ejecutable para Claude Code.
- Añadido `CLAUDE.md` raíz con reglas no negociables.
- Añadidos contratos de fuentes, datasets, métricas y Entity Resolution.
- Especificado pipeline de ingestión y política geoespacial.
- Detallada orquestación IA, JEV, RAG, Place Embeddings y model registry.
- Añadidos contratos API/MCP, telemetría, observabilidad y testing.
- Añadida estructura recomendada del repositorio.
- Añadidas reglas de ingeniería, desarrollo local, secretos y ADRs.
- Añadido backlog y criterios de aceptación DATAMAD.
- Ampliada la documentación para minimizar decisiones implícitas durante implementación.

## v0.1.2
- Añadida estrategia de enriquecimiento externo multi-fuente.
- Definida jerarquía de confianza A/B/C/D.
- Añadida estrategia de Entity Resolution y place_master.
- Definido enfoque de POIs basado en accesibilidad, cobertura y diversidad.
- Documentado uso de Catastro, OSM, APIs comerciales y scraping selectivo.

## v0.1.1
- Iniciada Fase 1: Data Foundation.
- Añadida primera cartografía validada de fuentes oficiales de Madrid.
- Clasificación P0/P1 de datasets.
- Añadido plan para diccionario de 200–400 features.
- Actualizados índice y registro de decisiones.

## v0.1.0
Primera estructura completa del repositorio de documentación.

Incluye:
- visión de producto;
- especificación funcional;
- arquitectura técnica;
- estrategia de datos;
- PostGIS + pgvector + H3;
- IA generativa + JEV + ML;
- MCP/API;
- mapa 3D tipo digital twin;
- capa pública, PRO y DATA;
- modelo de negocio bootstrapped;
- privacidad;
- validación;
- estrategia DATAMAD;
- inventario de áreas pendientes.
