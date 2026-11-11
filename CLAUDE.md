# CLAUDE.md — Housing Intelligence Platform

Este archivo es la puerta de entrada para Claude Code.

## 1. Qué estás construyendo

Una plataforma de inteligencia residencial con tres productos:

1. **PUBLIC** — gratuita para ciudadanía.
2. **PRO** — inteligencia territorial para empresas y administraciones.
3. **DATA** — API + MCP para software y agentes.

La tesis es:

> No queremos saber únicamente qué vivienda hay. Queremos saber qué vivienda necesita una persona y qué vivienda necesita un territorio.

## 2. Antes de programar

Lee en este orden:

1. `README.md` (repo) y `docs/README.md`
2. `docs/00_index/00_master_index.md`
3. `docs/00_index/01_decisions_log.md`
4. `docs/01_product/01_vision_product_master.md`
5. `docs/01_product/02_functional_spec.md`
6. `docs/02_data/01_data_strategy.md`
7. `docs/02_data/10_external_enrichment_strategy.md`
8. `docs/03_intelligence/01_intelligence_engine.md`
9. `docs/04_technical_architecture/01_global_architecture.md`
10. `docs/04_technical_architecture/07_repository_blueprint.md`
11. `docs/11_engineering/01_engineering_rules.md`
12. El documento específico de la tarea.

No comiences una implementación relevante si no entiendes:
- qué capa del producto afecta;
- qué fuente de datos utiliza;
- qué servicio es responsable;
- qué contrato de entrada/salida existe;
- cómo se prueba;
- cómo se explica el resultado.

## 3. Reglas no negociables

### Datos
- PostgreSQL/PostGIS es la fuente de verdad para datos exactos.
- pgvector sirve para embeddings y recuperación semántica, no para guardar cifras exactas como población o alquiler.
- Todo dato debe conservar `source_id`, `source_version`, `observed_at` o `valid_at` cuando aplique.
- Nunca ocultes una transformación: registra lineage y versión.
- Nunca mezcles fuentes duplicadas sin pasar por Entity Resolution.

### IA
- El LLM no calcula si existe una función determinista o un modelo.
- El LLM no ejecuta SQL libre.
- El LLM no inventa cifras faltantes.
- JEV se usa para decisiones tipadas, clasificación, routing, QC y reranking.
- Claude/Fable se usa para razonamiento complejo, conversación, informes y fallback.
- Toda respuesta importante debe ser explicable.

### Producto
- PUBLIC no debe degradarse artificialmente para forzar pago.
- PRO monetiza inteligencia agregada, análisis y workflow profesional.
- No vender ni exponer perfiles personales identificables.
- No usar características protegidas para discriminación residencial.

### Arquitectura
- Empezar como monolito modular.
- Evitar microservicios prematuros.
- Frontend nunca accede directamente a DB.
- MCP llama a servicios del dominio, no a SQL.
- API pública versionada.
- Todo modelo y score tiene versión.

### Código
- Tipado fuerte.
- Funciones pequeñas.
- Módulos por dominio.
- Tests para reglas y cálculos.
- No hardcodear IDs de datasets, zonas o fórmulas.
- Configuración por entorno.
- Nada de secretos en repo.

## 4. Qué hacer si falta una decisión

No improvises silenciosamente.

1. Comprueba `docs/00_index/02_open_questions.md`.
2. Si es una decisión reversible y de bajo riesgo, elige una opción razonable y documenta un ADR.
3. Si cambia producto, privacidad, negocio o modelo matemático, deja TODO explícito y no cierres la decisión sin validación.
4. Añade la decisión a `docs/00_index/01_decisions_log.md`.

## 5. Definición de “hecho”

Una funcionalidad no está terminada hasta que tenga:
- implementación;
- tests;
- contrato;
- manejo de errores;
- observabilidad mínima;
- documentación;
- datos de ejemplo;
- criterio de aceptación cumplido.

## 6. Estructura mental del sistema

```text
Sources
  ↓
Ingestion
  ↓
Bronze / Raw
  ↓
Normalization + Data Quality
  ↓
Canonical Entities + Geospatial Alignment
  ↓
Feature Store
  ↓
Rules + Statistical Models + ML + JEV
  ↓
Domain Services
  ↓
API / MCP
  ↓
PUBLIC / PRO / DATA
  ↓
LLM explanation and interaction
```

## 7. Prioridad actual

Estamos en **fase de competición DATAMAD 2026** (hasta el 26 nov 2026).

- Plan vigente: `docs/09_datamad/25_plan_competicion.md`. Cards y calendario: `board/BOARD.md`. Decisiones D-191 a D-195.
- Objetivo inmediato: demo desplegada el 17 nov con datos reales de la Comunidad de Madrid (buscador para personas + lista de lo que falta por zona) para el formulario del 18 nov.
- La base de DATA FOUNDATION ya existe (source registry, inventario, métricas, entidades, contratos de features, ingestión y geografía común): se amplía, no se rehace.
- Solo la sesión de desarrollo escribe en la carpeta principal (rama `claude/sprint-1-public`); cualquier otra sesión usa un worktree propio. Commits de rutas explícitas, nunca `git add -A`.

## 8. Principio técnico central

> Haz que los datos sean inteligentes antes de pedirle inteligencia al LLM.


## 9. Decisiones de producto ya cerradas

- Geografía core: H3 + sección censal.
- Actualización de datos: frecuencia natural por fuente.
- Perfil persistente: sí, con cuenta/consentimiento y separación PII/analytics.
- Recomendación: híbrida, no ML puro.
- Prioridades: IA propone, usuario corrige.
- Mapa: 3D estilizado tipo SimCity/Jarvis.
- Natural Language GIS: sí, mediante tools y MapState; nunca SQL libre.
- Estimaciones: deben exponer confidence.
- Datos externos: oficial/open primero; scraping ampliado después y controlado.
- POIs: accesibilidad/cobertura/diversidad, no conteo bruto.
- Place Model: sí.
- Behavioral learning: sí, progresivamente.
- Housing Gap: debe recomendar producto residencial.
- Parcel analysis: incluye proyectos/parcelas de cliente.
- Private PRO data: aislada por tenant.
- JEV: desarrollo + producción.
- Vector DB: RAG + place embeddings.
- MCP: objetivo de capas dinámicas y control de mapa.
- PUBLIC: evaluación de anuncio/vivienda por URL cuando sea legal/viable.
- Reality Check: optimizador multidimensional.


## 10. Reglas de datos específicas para DATAMAD

- El MVP debe usar datos del Catálogo de Datos Abiertos de la Comunidad de Madrid en funcionalidades centrales.
- No sustituir fuentes regionales por externas solo por facilidad de implementación.
- Fuentes externas complementan; no deben convertir el proyecto en un producto ajeno a DATAMAD.
- Toda recomendación importante debe poder trazar datasets de Comunidad de Madrid usados.
- Para PUBLIC, explicar resultados en lenguaje cotidiano y tangible; no obligar al usuario a interpretar scores abstractos.
- Para datos faltantes, degradar confidence antes que inventar precisión.


## 11. Reglas de micro-localización y feature universe

- No asumir que un barrio es homogéneo.
- Calcular lo importante a nivel H3/sección censal y bajar a edificio/parcela solo con cobertura suficiente.
- Accesibilidad se calcula por red/tiempo cuando sea posible, no por círculos.
- Movilidad debe ser multimodal y considerar frecuencia/transbordos/anchors.
- 15-minute living y car dependency son modelos core.
- Seguridad puede incorporarse solo con datos oficiales/agregados y sin inferencias demográficas.
- Building Intelligence funciona best-effort: C si existen datos, B como fallback.
- Timeline debe distinguir observado, estimado, forecast y escenario.
- Objetivo del feature universe: 300–500 variables bien gobernadas, no 500 columnas por cantidad.


## 12. Reglas de calidad contextual

- Mantener dato absoluto + referencia relativa.
- Tipologías territoriales mediante clustering, pero naming interpretado por humanos.
- Movilidad puede depender de hora/día.
- Capacidad/saturación se calcula solo con datos fiables; si no, usar fallback.
- Progressive profiling + active questioning deben minimizar preguntas.
- Mantener Data Coverage Map para evitar falsa precisión.
- Históricos y correcciones son versionados.
- Knowledge Graph es opcional y NO debe bloquear DATAMAD.
- Scenario Engine MVP es parcial y debe declarar qué recalcula.
- Cada modelo usa solo features justificadas; no usar todas por defecto.

## 13. Reglas de accesibilidad e inclusión
- Modelar necesidades funcionales/ambientales, no diagnósticos.
- Nunca inferir discapacidad/autismo/salud mental del comportamiento.
- Necesidades sensibles son opt-in.
- No crear etiquetas “barrio para X diagnóstico”.
- Features de accesibilidad deben ser concretas y explicables.
- Si una feature es proxy, declararlo.
- Map-first UX: chat + chips + filtros comparten un único ScenarioState.
- No construir un formulario clásico como onboarding obligatorio.

## 14. Reglas del Residential Fit
- Pipeline: constraints → candidates → scoring → ML/JEV → diversification.
- Hard constraints usan PASS/FAIL/UNKNOWN.
- UNKNOWN nunca equivale a PASS.
- Mantener score personal separado de referencia territorial.
- Usar curvas de utilidad y saturación.
- Generar varias soluciones Pareto.
- Candidatos que violan constraints solo salen como alternativa explícita.
- Web enrichment termina en señales estructuradas con provenance.
- Implementar invariantes lógicos y property-based tests donde sea viable.

## 15. Reglas de adquisición y Feature Dictionary
- Conservar Bronze/Silver/Gold.
- No confundir 0 con unknown.
- Resolver conflictos por política de métrica.
- Para Catastro usar INSPIRE/servicios oficiales.
- Para CRTM usar GTFS/API/open data.
- No implementar scraping masivo de Idealista sin permiso/licencia adecuada.
- Cada feature productiva debe existir en catálogo machine-readable y pasar quality gate.
- Los modelos deben usar feature sets versionados y revisar redundancia/leakage.

## 16. Reglas PRO / negocio
- ICP inicial: promotoras/inmobiliarias medianas.
- Vender informes/estudios antes del SaaS completo.
- PRO debe soportar site-first y thesis-first.
- DATA/API/MCP es producto independiente.
- FREE debe resolver el problema básico completo.
- PLUS cobra profundidad/automatización/volumen.
- Datos privados siempre por tenant.
- No vender perfiles personales.
- Muestras manuales de anuncios solo para investigación limitada y con respeto a condiciones/licencias.

## 17. Estrategia de ejecución final-product-first
- Construir arquitectura de producto final desde el inicio.
- DATAMAD no debe generar una rama técnica desechable.
- Usar capability flags y fallbacks para recortar scope.
- No iniciar capabilities avanzadas con deuda crítica en Tier 0.
- Un recorte desactiva o degrada una capability; no crea otra arquitectura.
- Priorizar máximo producto real estable antes que MVP artificialmente pequeño.


## 18. Quality Gates — mandatory
- No phase/capability is complete until its Quality Gate passes.
- Read `docs/11_engineering/11_phase_quality_gates.md`.
- Every significant task must identify which tests/gate it affects.
- Critical invariant, tenant isolation, privacy or data-lineage failure blocks progress.
- Evidence for completed gates goes under `evidence/gate-XX/`.
- “Works on my machine” is not acceptance.

## 19. Cross-cutting production rules
- Architecture supports auth/multi-tenant/security from the beginning.
- Heavy work runs in workers/jobs, not request threads.
- Backups are tested by restore.
- URL ingestion must defend SSRF.
- Uploaded files are untrusted.
- App itself targets WCAG 2.2 AA.
- Missing data and zero are different.
- Demo has an offline/snapshot mode.
- All enabled capabilities have fallback and observability.

## 20. Sprint execution
- Read the sprint roadmap and Trello card before implementation.
- A card is not DONE when code is written; it is DONE after acceptance tests and relevant Gate evidence.
- Do not take work from BACKLOG without Definition of Ready.
- During final week, feature freeze rules override opportunistic feature creation.

## 21. Entorno local verificado (2026-10-20)
- Documentación completa en `docs/` (v0.5.1 + addenda). Este `CLAUDE.md` es la única copia: no existe `docs/CLAUDE.md`.
- Bases oficiales DATAMAD 2026 resumidas en `docs/09_datamad/24_bases_oficiales_2026.md`. El trabajo previo está permitido si se identifica (§6 bases).
- Python 3.12 vía `uv` (workspace). Nunca `python3` directo: siempre `uv run`. No hay poetry.
- Node 24 + npm workspaces. No hay pnpm.
- Puertos locales: Postgres 5440, Redis 6390, API 8010, Web 3010 (configurables en `.env`). 3000/5432/8000 están ocupados por otros proyectos.
- Postgres 17 + PostGIS + pgvector en Docker (`infra/docker/postgres`). Extensiones en schema `extensions`.
- Supabase (proyecto free `ilvbivfnqvfqslbbiuts`) es entorno remoto/demo; sin h3-pg: **H3 se calcula siempre en Python**.
- MCP `supabase-datamad`: registrado por Mariano con scope local en `~/Desktop/DATAMAD` y `--read-only` (11 nov). `.mcp.json` es la plantilla y necesita `SUPABASE_DATAMAD_ACCESS_TOKEN`. No confundir con el conector claude.ai "Supabase" (otra cuenta).
- Supabase remoto (11 nov): esquema en head, RLS en todas las tablas (D-197) y perfil demo cargado. Para volver a cargar datos tras cambiar features o lugares: `make supabase-migrate` y después `make supabase-sync PROFILE=demo`.
- `make` es la entrada única: `make dev`, `make lint`, `make typecheck`, `make test`, `make ingest DATASET=...`.

## 22. Convenciones del repo
- Paquetes Python con prefijo `hi_` (`hi_contracts`, `hi_domain`, `hi_db`, `hi_ingestion`, `hi_api`).
- `packages/contracts`: Pydantic puro, sin I/O. `packages/domain`: lógica pura y testeable. `packages/db`: ORM + sesión. `services/*`: procesos/jobs. `apps/*`: entrypoints.
- Catálogo machine-readable en `data/catalog/{sources,datasets,features}/*.yaml`; los JSON Schema de `data/schemas/` se generan (`make schemas`), no se editan a mano.
- Bronze/Silver/Quarantine no se versionan; sus `manifest.json` sí.
- Markers pytest: `db` (requiere Postgres), `network` (llama a APIs externas, excluido por defecto), `slow`.
- Google Maps / Gosom: `REJECTED` para el proyecto DATAMAD (ver `docs/07_privacy_legal/source_reviews/google_maps_gosom.md`).
