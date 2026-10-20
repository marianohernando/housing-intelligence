# Testing Strategy — v0.4.0

Testing is not a final phase. Every capability ships with tests and must pass a Quality Gate.

## Layers
1. static: lint/types/secrets/dependencies
2. unit
3. data contract
4. geospatial
5. integration
6. API/MCP contract
7. model/JEV/RAG eval
8. E2E
9. accessibility
10. security
11. performance/load
12. operations/restore/release
13. demo smoke

## Golden fixtures
Use stable Madrid fixtures and synthetic user profiles.

## Critical invariant
A feature is not “done” if only its happy path works.

See:
- `11_engineering/11_phase_quality_gates.md`
- `11_engineering/12_master_test_catalog.md`
