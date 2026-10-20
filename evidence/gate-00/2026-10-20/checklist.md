# Gate 00 — checklist manual

- [x] `.env` no versionado; `.env.example` sin valores reales.
- [x] Token de Supabase solo en `.claude/settings.local.json` (gitignored); gitleaks con regla `sbp_` explícita y probada con token falso.
- [x] `CLAUDE.md` raíz adaptado a `docs/` y al entorno real (puertos, uv, npm).
- [x] Documentación v0.5.1 íntegra en `docs/` (272 ficheros verificados por sha256).
- [x] Quickstart del README probado: `make up`, `make migrate`, `make seed`, `make lint typecheck test`.
- [x] Puertos sin conflicto con otros proyectos locales (5440, 6390, 3010).
- [ ] Aprobación de Mariano del Gate 0 (revisar este summary).
