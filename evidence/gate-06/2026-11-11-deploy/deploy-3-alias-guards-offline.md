# OPS-001 (line C) · demo URL vidafacil-madrid.vercel.app, deploy guards and offline package (2026-11-11 ~12:25 UTC)

## Alias
- `vercel domains add vidafacil-madrid.vercel.app vida-facil` → assigned to the project. `vida-facil-eight.vercel.app` stays as a secondary alias.
- `NEXT_PUBLIC_API_URL=https://vidafacil-madrid.vercel.app`. `CORS_ORIGINS` lists both domains. Checked with `vercel env pull` to a scratch file, deleted afterwards.
- The web bundle embeds `https://vidafacil-madrid.vercel.app`. A request from origin `vida-facil-eight` gets `access-control-allow-origin: https://vida-facil-eight.vercel.app`.
- Both domains: `/` 200 and `/api/v1/health` 200.

## Deploy guards (R-07, R-08)
```
$ make deploy-demo   # from claude/s1-deploy
branch 'claude/s1-deploy' is not a demo branch (claude/sprint-1-public main); ALLOW_BRANCH=1 to force

$ ALLOW_BRANCH=1 make deploy-demo   # 100 s
warning: deploying branch 'claude/s1-deploy' (ALLOW_BRANCH=1)
note: these local files match .vercelignore and are NOT uploaded:
  ./.env
  ./.env.local
-> deploying c825f5f (claude/s1-deploy) to production
-> smoke test against https://vidafacil-madrid.vercel.app
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T12:23:19Z)
OK   web         0.97s      5596 B  /
OK   health      3.06s       225 B  /api/v1/health  process up
FAIL ready       0.35s        70 B  /api/v1/health/ready  HTTP 503
FAIL zone        0.34s        21 B  /api/v1/gaps/municipio/28079  HTTP 500
FAIL geography   0.23s        21 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  HTTP 500
FAIL layer       0.37s        21 B  /api/v1/places?category=education  HTTP 500
smoke: 2/6 OK
roll back to the previous one: npx vercel@65.12.1 rollback
```
Smoke 2/6, as expected: `DATABASE_URL` is still pending (Mariano).

## Offline package (make demo-offline-prepare / demo-offline / demo-offline-stop)
- prepare: 21 s. 41 MB dump of the 9 demo tables, read-only from the dev DB. Row counts in the offline DB equal the source (`manifest.txt`: source_registry 10, dataset_registry 33, dataset_version 31, metric_registry 13, feature_registry 13, geo_admin_unit 4973, place_master 24334, place_source_alias 24334, feature_value 2151).
- The source DB was at 0005 and the checkout at 0004 at test time. 0005 only adds the vf_api_ro role, so the run used `DEMO_OFFLINE_ALLOW_HEAD_MISMATCH=1`. After the rebase both are at 0005.
- start: 6–7 s, smoke 5/5 against :8012. Headless Chromium on http://localhost:3012/map: 0 requests to external hosts, no console errors, map drawn with data (`offline-map-desktop.png`, `offline-map-mobile.png`).
- stop: no listeners left on 3012, 8012 or 5441. A restart afterwards also takes 6 s, smoke 5/5.
- The first version used `next start`, which left an orphan `next-server`. It now runs the standalone `server.js`, a single process.
