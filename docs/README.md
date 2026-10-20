# Plataforma de Inteligencia Residencial — Documentación v0.5.1

Repositorio maestro de documentación del proyecto.

## Objetivo
Construir una infraestructura de inteligencia residencial que conecte:
- necesidades reales de los hogares,
- capacidad económica,
- territorio,
- oferta de vivienda,
- servicios,
- inversión y planificación.

La plataforma tendrá tres capas:
1. **PUBLIC** — gratuita para ciudadanía.
2. **PRO** — inteligencia territorial para empresas y administraciones.
3. **DATA / API / MCP** — infraestructura consumible por software y agentes de IA.

## Principio rector
> Idealista sabe qué vivienda hay. Nosotros queremos saber qué vivienda hace falta.

## Estructura
- `00_index/` — índice, decisiones, preguntas abiertas, glosario.
- `01_product/` — visión y especificación funcional.
- `02_data/` — estrategia de datos, taxonomía, geografía, RAG.
- `03_intelligence/` — ML, JEV, scoring y evaluación.
- `04_technical_architecture/` — arquitectura, APIs, infraestructura y rendimiento.
- `05_map_ux/` — mapa 3D, UX y sistema visual.
- `06_business/` — modelo de negocio, bootstrap, pricing y GTM.
- `07_privacy_legal/` — privacidad, licencias y ética.
- `08_validation/` — investigación y validación con usuarios/B2B.
- `09_datamad/` — estrategia específica del concurso.
- `10_research/` — vivienda en España, referencias y proyectos comparables.

## Regla de actualización
Cada nueva decisión del proyecto debe:
1. actualizar el documento correspondiente;
2. registrar la decisión en `00_index/01_decisions_log.md`;
3. añadir cambios a `CHANGELOG.md`;
4. incrementar versión del ZIP.

## Fase actual
Data Foundation: inventario real de fuentes y diseño del feature dictionary.

## Claude Code
Usar `CLAUDE.md` como entrada principal antes de cualquier implementación.


## Quality Gates
Ninguna fase se considera completa sin pasar los gates definidos en `11_engineering/11_phase_quality_gates.md`.
