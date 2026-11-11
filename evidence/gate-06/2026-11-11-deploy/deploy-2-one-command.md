# OPS-001 (line C) · redeploy with the single command (2026-11-11 12:04 UTC)

Command: `make deploy-demo` (= `infra/deploy/deploy.sh`) at 9623288, clean tree, pushed. Total 100 s including the smoke.

```
-> deploying 9623288 (claude/s1-deploy) to production
-> smoke test against https://vida-facil-eight.vercel.app
smoke: https://vida-facil-eight.vercel.app (2026-11-11T12:04:28Z)
OK   web         1.40s      5596 B  /
OK   health      2.95s       225 B  /api/v1/health  process up
FAIL ready       0.37s        70 B  /api/v1/health/ready  HTTP 503
FAIL zone        0.12s        21 B  /api/v1/gaps/municipio/28079  HTTP 500
FAIL geography   0.23s        21 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  HTTP 500
FAIL layer       0.24s        21 B  /api/v1/places?category=education  HTTP 500
smoke: 2/6 OK
smoke failed and production already serves this deploy.
roll back to the previous one: npx vercel@65.12.1 rollback
make: *** [deploy-demo] Error 1
exit=2 in 100s
```

- Deployment `vida-facil-8w9wsegbz` READY; production domain https://vida-facil-eight.vercel.app.
- First API request after the deploy: 2.95 s (container start). Warm requests: 0.11–0.25 s (11:53 UTC).
- The web bundle now embeds `https://vida-facil-eight.vercel.app` as the API URL (checked in the `/map` JS chunks).
- As expected the smoke fails on the 4 database checks: `DATABASE_URL` is not set yet (Mariano) and Supabase is at Alembic 0003 (line A must migrate to 0004 and sync). The script printed the rollback command and exited 1.
