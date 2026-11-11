# OPS-001 (line C) · deploy.sh verifies which deployment served the smoke · 2026-11-11 17:48 UTC

Follows [deploy-7-gap001.md](deploy-7-gap001.md): a 7/7 smoke right after a deploy had several of its requests served by the previous deployment. The orchestration chose option (a): verify with `vercel logs`.

## How it works
- `scripts/smoke_demo.sh` sends `User-Agent: vida-facil-smoke`, plus `/<SMOKE_TAG>` when the variable is set. The tag may only contain letters, digits, `.`, `_` and `-`.
- `infra/deploy/deploy.sh`:
  1. Deploys with `vercel deploy --prod --yes --json` and reads `.deployment.id`.
  2. Runs the smoke with the tag `<deployment id>-<round>`.
  3. Polls `vercel logs requests --query 'clientUserAgent:"vida-facil-smoke/<tag>"'` every 5 s, for at most 60 s, until every request of the smoke shows up. These are the CDN records, one per request, web included, each with its `deploymentId`.
  4. Accepts only if all of them came from the new deployment. Otherwise it waits 20 s and repeats smoke and check, at most 3 times.
- Exit codes:
  - 0: verified.
  - 1: the deploy failed, or the smoke failed every round. It prints the rollback command.
  - 2: refused before deploying.
  - 3: deployed but not verified.
- It prints only deployment ids, tags and counts. The CDN records it reads carry no secrets, and its stderr is discarded.

## Measured before writing it
- A probe of 3 tagged requests appeared in `vercel logs requests` after 12–20 s: 2 records at t+12 s and 3 at t+20 s. The server-side `--query` on `clientUserAgent` works.
- The CDN records of the 17:37 smoke show that 4 of its 7 requests came from the previous deployment `dpl_3EwQ…`. The runtime logs had shown 3 of 6, because the web is not in them.

## Paths tested with a fake `npx`/`vercel` and `sleep` (real smoke against production)
| Scenario | Rounds | Exit |
|---|---|---|
| 7/7 records from the new deployment | 1 | 0 |
| 3 old + 4 new in round 0, then 7 new | 2 | 0 |
| 3 old + 4 new in every round | 4 | 3, «NOT VERIFIED» |
| Only 4 of 7 records ever show up | 4 | 3, «only 4/7 smoke requests in vercel logs after 60 s» |
| Deploy output without an id | 0 | 3 |
| Smoke fails (`DEMO_URL=http://127.0.0.1:9`) | 4 | 1, rollback command |

## Real deploy: 53640d6 (= origin/claude/sprint-1-public dc2c86a, with GAP-001 F4, + line C) · 157 s · exit 0
```
-> deploying 53640d6 (claude/s1-deploy) to production
-> deployment dpl_3NckziR5jkhxJX6Luv31zzzaHhTJ is ready: <despliegue>
-> smoke test against https://vidafacil-madrid.vercel.app
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T17:50:25Z) tag dpl_3NckziR5jkhxJX6Luv31zzzaHhTJ-0
OK   web         0.09s      5596 B  /
OK   health      0.12s       225 B  /api/v1/health  process up
OK   ready       4.15s       225 B  /api/v1/health/ready  database and geography visible
OK   zone        0.16s     20640 B  /api/v1/gaps/municipio/28079  Madrid: 6 rows
OK   geography   0.71s    331914 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.51s   1156882 B  /api/v1/places?category=education  3851 places
OK   largest     0.53s   1407222 B  /api/v1/places?category=transport  14982 stops, page 1/3
smoke: 7/7 OK
-> which deployment served the smoke (vercel logs requests, tag dpl_3NckziR5jkhxJX6Luv31zzzaHhTJ-0)
   3 from dpl_25X3tSgAWMQVgsazzPUzWt148rei (another deployment)
   4 from dpl_3NckziR5jkhxJX6Luv31zzzaHhTJ (this deploy)
-> the smoke did not come entirely from dpl_3NckziR5jkhxJX6Luv31zzzaHhTJ; repeating the smoke in 20 s (1/3)
-> smoke test against https://vidafacil-madrid.vercel.app
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T17:51:06Z) tag dpl_3NckziR5jkhxJX6Luv31zzzaHhTJ-1
OK   web         0.59s      5596 B  /
OK   health      0.25s       225 B  /api/v1/health  process up
OK   ready       0.37s       225 B  /api/v1/health/ready  database and geography visible
OK   zone        0.18s     20640 B  /api/v1/gaps/municipio/28079  Madrid: 6 rows
OK   geography   0.51s    331914 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.63s   1156882 B  /api/v1/places?category=education  3851 places
OK   largest     1.48s   1407222 B  /api/v1/places?category=transport  14982 stops, page 1/3
smoke: 7/7 OK
-> which deployment served the smoke (vercel logs requests, tag dpl_3NckziR5jkhxJX6Luv31zzzaHhTJ-1)
   7 from dpl_3NckziR5jkhxJX6Luv31zzzaHhTJ (this deploy)
-> verified: https://vidafacil-madrid.vercel.app serves dpl_3NckziR5jkhxJX6Luv31zzzaHhTJ, and the smoke passed against it
```
- The first round shows the problem the change is for: a 7/7 smoke with 3 of its 7 requests still served by the previous deployment. The script caught it and verified the next round, 20 s later.
- The deploy also published GAP-001 Fase 4:
  - `GET /api/v1/gaps?level=distrito&row=colegio`: 200, 21 zones, 5,516 B.
  - `GET /api/v1/gaps?level=municipio&row=farmacia`: 200, 179 zones, 31,972 B.
