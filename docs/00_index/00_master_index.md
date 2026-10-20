# Índice Maestro — v0.4.0

## Estado general tras auditoría integral

| Área | Estado |
|---|---|
| Visión / posicionamiento | Cerrado |
| PUBLIC | Cerrado a nivel funcional y de arquitectura |
| PRO / B2G | Cerrado a nivel funcional y de arquitectura |
| DATA / API / MCP | Cerrado a nivel funcional y de arquitectura |
| Onboarding / ScenarioState | Cerrado |
| Residential Fit | Cerrado conceptualmente + contrato matemático |
| Accessibility / Inclusive Living | Cerrado conceptualmente |
| Housing Gap / Product Recommender | Cerrado conceptualmente |
| Datos / lineage / quality | Cerrado a nivel de arquitectura |
| Feature universe | Blueprint cerrado; catálogo real se construye al adquirir fuentes |
| JEV / LLM / RAG | Cerrado a nivel de arquitectura y validación |
| Place Model / ML | Cerrado a nivel de arquitectura y gates |
| Mapa 3D / SimCity | Cerrado a nivel técnico/UX |
| Auth / multi-tenant / RBAC | Cerrado |
| Seguridad / threat model | Cerrado |
| Backups / restore / DR | Cerrado |
| Jobs / scheduler / workers | Cerrado |
| Observabilidad / SLOs | Cerrado |
| Privacidad / sensitive data | Cerrado a nivel de diseño; revisión jurídica externa antes de producción |
| Licencias de fuentes | Workflow cerrado; revisión dataset a dataset durante adquisición |
| App accessibility / WCAG | Cerrado a nivel de requisitos/test |
| Testing / quality gates | Cerrado y obligatorio por fase |
| Release / rollback | Cerrado |
| DATAMAD demo / evidence pack | Cerrado a nivel de procedimiento |
| GTM / pricing architecture | Cerrado como hipótesis |
| Financial model | Estructura cerrada; números se calibran con costes y validación comercial |
| Roadmap con fechas | **Siguiente bloque a construir con el usuario** |

## Estrategia actual
**FINAL-PRODUCT-FIRST.**

Se construye arquitectura de producto final. Si el tiempo obliga:
- se desactivan capabilities;
- se reduce cobertura;
- se usan fallbacks;
- no se crea una arquitectura paralela de hackathon.

## Principio de calidad
No avanzar de una fase a la siguiente porque “parece funcionar”.

Cada fase tiene:
1. entregables;
2. tests automáticos;
3. tests manuales;
4. métricas mínimas;
5. evidence artifact;
6. Quality Gate PASS.

## Documentos críticos antes de programar
- `CLAUDE.md`
- `00_index/06_completeness_audit.md`
- `11_engineering/11_phase_quality_gates.md`
- `11_engineering/12_master_test_catalog.md`
- `11_engineering/13_ci_cd_quality_gates.md`
- `02_data/36_feature_dictionary_contract.md`
- `09_datamad/13_final_submission_checklist.md`

## Próximo paso
Construir hoja de ruta fechada desde el día actual hasta DataMad y mapear cada bloque a sus Quality Gates.

## Roadmap 2026
- `09_datamad/18_official_calendar_2026.md`
- `09_datamad/19_master_roadmap_oct20_nov26.md`
- `09_datamad/20_weekly_sprint_gate_matrix.md`
- `11_engineering/24_trello_board_blueprint.md`
- `11_engineering/25_claude_code_execution_protocol.md`

## Handoff
- `START_HERE_ON_COMPUTER.md` — punto de entrada obligatorio al mover el proyecto al ordenador.
