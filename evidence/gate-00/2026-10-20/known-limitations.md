# Gate 00 — limitaciones conocidas (2026-10-20)

- CI corre en la rama `claude/sprint-p0`; `main` aún no existe en el remoto. La integración en `main` la decide Mariano.
- La imagen de Postgres se construye en cada job de integración (sin GHCR). Coste ~30 s por run; aceptable en P0.
- `deps` (pip-audit, npm audit) era informativo en este Gate 0. Pasó a bloqueante el mismo día tras detectar GHSA-jrc7-96c5-q579 en MapLibre 5.24.
- Supabase remoto (`ilvbivfnqvfqslbbiuts`) no está migrado: falta la connection string y aprobar el MCP `supabase-datamad`.
- No hay `LICENSE` en el repo: decisión pendiente (card LEGAL-001).
- Sin despliegue de staging: no requerido por Gate 0.
