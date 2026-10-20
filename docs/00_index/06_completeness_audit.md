# Auditoría Integral de Completitud — v0.4.0

## Objetivo
Revisar el proyecto como si mañana fuese a pasar de documentación a construcción real.

La auditoría busca huecos en:
- producto;
- datos;
- inteligencia;
- ingeniería;
- seguridad;
- privacidad;
- UX;
- negocio;
- validación;
- operación;
- DATAMAD.

## Huecos encontrados y cerrados en v0.4.0

### Producto
- lifecycle de cuenta/sesión;
- objetos guardados y escenarios;
- alertas/notificaciones;
- informes/exportes;
- Home/Listing analysis detallado;
- roles PRO;
- estados loading/error/empty.

### Datos
- geocoding/address resolution;
- QA geoespacial;
- source onboarding;
- clasificación/retención de datos;
- drift;
- snapshots reproducibles para demo.

### Intelligence
- especificación de affordability;
- Housing Gap matemático;
- calibración de scores;
- uncertainty calibration;
- spatial cross-validation;
- JEV evaluation;
- RAG evaluation;
- LLM/tool guardrails;
- fairness/model drift.

### Arquitectura
- auth;
- multi-tenancy;
- RBAC;
- jobs/scheduler;
- object storage;
- backup/restore/DR;
- release/rollback;
- SLOs/performance budgets;
- threat model;
- billing/entitlements;
- API/MCP auth/rate limiting;
- offline/demo resilience.

### UX / Map
- WCAG del propio producto;
- responsive/mobile;
- keyboard/screen reader;
- performance budgets;
- search/geocoding;
- state/share links;
- map visual regression;
- loading/error states.

### Legal
- GDPR data lifecycle;
- sensitive-data assessment;
- cookie/analytics consent;
- source license review workflow;
- open-source publication policy.

### Validation
- usability/accessibility tests;
- data validation;
- model validation;
- PRO pilot acceptance;
- pricing validation.

### DATAMAD
- final submission checklist;
- demo runbook;
- jury evidence matrix;
- offline demo pack;
- open-source submission pack.

### Ingeniería / Testing
- Quality Gates por fase;
- Master Test Catalog;
- CI/CD gates;
- security test plan;
- data test plan;
- model eval gate;
- map E2E;
- MCP/API contract tests;
- demo smoke tests;
- release checklist;
- migration/rollback;
- test fixtures.

## Resultado
No se han encontrado huecos conceptuales de primer orden que impidan construir la hoja de ruta.

Lo que permanece abierto está clasificado como:
1. `EXTERNAL_RESEARCH`
2. `DATA_DEPENDENT`
3. `IMPLEMENTATION_CALIBRATION`
4. `USER_VALIDATION`
5. `LEGAL_REVIEW`
6. `COMMERCIAL_VALIDATION`

## Regla de no-olvido
Toda fase futura debe cerrar su Quality Gate y producir un `evidence/phase-X/` antes de considerarse completada.
