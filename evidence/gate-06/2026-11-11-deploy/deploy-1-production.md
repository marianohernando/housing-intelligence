# OPS-001 (line C) · first production deploy (2026-11-11 ~11:50 UTC)

Command: `npx vercel@65.12.1 deploy --prod --yes` from `claude/s1-deploy`, at 72f5d90 plus the deploy config. It was not deployed from a clean tree because `deploy.sh` did not exist yet. Exit 0 in **94 s**, covering the API container build and the Next.js build.

| Field | Value |
|---|---|
| Project | `mariano-hernando-s-projects/vida-facil` (preset Services: `web` Next.js, `api` container) |
| Deployment | `dpl_DDUofMsMnv7rRtBeWh838R5j48rA` · READY · target production |
| Production URL | **https://vida-facil-eight.vercel.app** |
| Build machine | 4 cores, 8 GB |
| Protection | `vercel_authentication` on generated deployment URLs. The production domain is public: the web answers 200 without login |

`vida-facil.vercel.app` could not be used: `vercel domains add` → 403 «The chosen alias "vida-facil.vercel.app" is already in use». Vercel assigned the `-eight` suffix.

## Smoke against the public URL, without `DATABASE_URL` (secret not loaded yet)
```
smoke: https://vida-facil-eight.vercel.app (2026-11-11T11:50:38Z)
OK   web         0.57s      5596 B  /
OK   health      4.28s       225 B  /api/v1/health  process up
FAIL ready       0.35s        70 B  /api/v1/health/ready  HTTP 503
FAIL zone        0.35s        21 B  /api/v1/gaps/municipio/28079  HTTP 500
FAIL geography   0.12s        21 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  HTTP 500
FAIL layer       0.23s        21 B  /api/v1/places?category=education  HTTP 500
smoke: 2/6 OK
```
- The hosting works: the web is served and the API container starts. The first request to the API took 4.28 s, which includes the cold start.
- `ready` → 503 `{"code":"SOURCE_DEGRADED","message":"Database unreachable"}`. That is expected without `DATABASE_URL`: the API falls back to its local default URL. The body does not leak the cause.
- Supabase, checked with the read-only MCP: the schema is at Alembic **0003**. It lacks the 0004 columns (`dataset_registry.portal_url`, `is_cm_open_data`) that `/api/v1/gaps` reads, so line A has to run `make supabase-migrate` and then `make supabase-sync PROFILE=demo`. `vf_api_ro` does not exist yet. `PUBLIC` has no CREATE on schema `public`.

## Environment (names only)
Production values for `PORT`, `CORS_ORIGINS` and `NEXT_PUBLIC_API_URL` were checked with `vercel env pull` to a scratch file, which was deleted afterwards. `DATABASE_URL` is pending: Mariano enters it.
