# Gate 00 — PASS

- Fecha: 2026-10-20
- Commit: `0337d620b81f9c73aaff5b8e8a78b10e7654a18b` (claude/sprint-p0)
- Generado: 2026-10-20T11:06:20.485800+00:00 por `scripts/evidence.py`

| Check | Criterio | Resultado |
|---|---|---|
| lint | lint (ruff + eslint) | PASS |
| typecheck | typecheck (pyright + tsc) | PASS |
| unit | unit test scaffold | PASS |
| web-unit | web unit tests | PASS |
| migrations | migrations up/down + no model drift | PASS |
| docker-boot | Docker/local boot (db + redis healthy) | PASS |
| db-extensions | PostGIS + pgvector available | PASS |
| secret-scan | secret scan (gitleaks, full history) | PASS |
| ci | CI green for HEAD | PASS |

Cada fila tiene su salida completa en `<check>.txt`. Entorno en `environment.json`.
