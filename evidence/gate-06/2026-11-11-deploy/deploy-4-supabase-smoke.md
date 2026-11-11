# OPS-001 (line C) · deploy with Supabase: public smoke 6/6 (2026-11-11 14:36 UTC)

Preconditions, confirmed by datamad-10 over MCP:
- `DATABASE_URL` is in Vercel (Production, Secret) with the role `vf_api_ro`.
- Supabase is at Alembic 0005; `vf_api_ro` has LOGIN and 7 policies.
- Data: `feature_value` 2298, `place_master` 24334, `geo_admin_unit` 4973.

## make deploy-demo (be40c2f = origin/claude/sprint-1-public, ALLOW_BRANCH=1 from the worktree branch) · 84 s
```
warning: deploying branch 'claude/s1-deploy' (ALLOW_BRANCH=1)
note: these local files match .vercelignore and are NOT uploaded:
  ./.env
  ./.env.local
-> deploying be40c2f (claude/s1-deploy) to production
-> smoke test against https://vidafacil-madrid.vercel.app
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T14:36:42Z)
OK   web         0.19s      5596 B  /
OK   health      2.92s       225 B  /api/v1/health  process up
OK   ready       3.66s       225 B  /api/v1/health/ready  database and geography visible
FAIL zone        0.25s        21 B  /api/v1/gaps/municipio/28079  HTTP 500
OK   geography   0.99s    331893 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.56s   1156850 B  /api/v1/places?category=education  3851 places
smoke: 5/6 OK
roll back to the previous one: npx vercel@65.12.1 rollback
```

### Why `zone` failed once
Production logs (`vercel logs --json`):
- The 500 at 14:36:49.782Z came from deployment **`dpl_3TNW4u6sLZBPyZBQFh8AzT9dLjxt`**, the previous one. It was deployed before `DATABASE_URL` existed, so it fell back to the default `127.0.0.1:5440` and got `psycopg.OperationalError: connection refused`.
- Every request to the new deployment **`dpl_Hj9n6Fup7Uy5Y9TUStzHCG6nFLad`** returned 200.
- This was a few seconds of overlap while the domain switched, not a GRANT or policy problem.
- Fix: `deploy.sh` now retries the smoke once after 20 s before reporting a failure.

## Smoke repeated after the switch: 3 × 6/6
```
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T14:38:28Z)
OK   web         0.09s      5596 B  /
OK   health      0.12s       225 B  /api/v1/health  process up
OK   ready       0.13s       225 B  /api/v1/health/ready  database and geography visible
OK   zone        0.14s      4750 B  /api/v1/gaps/municipio/28079  Madrid: 2 rows
OK   geography   0.84s    331893 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.26s   1156850 B  /api/v1/places?category=education  3851 places
smoke: 6/6 OK
```

## Manual check: Chamartín (`/api/v1/gaps/distrito/2807905`)
```
zone: Chamartín (distrito 2807905)
  colegio | FALTA | 0.8793 centros/1000 menores vs reference 2.178 | confidence 1.0 | 3 datasets
  centro_salud | FALTA | 0.469 centros/10000 hab vs reference 0.5918 | confidence 1.0 | 3 datasets
warnings: []
```

## The API reads as `vf_api_ro`
`pg_stat_activity` on Supabase, read-only MCP query: one `vf_api_ro` session from `Supavisor`, backend_start 14:36:49Z, the new deployment. No API sessions as `postgres`, so the RLS policies are actually in use.
