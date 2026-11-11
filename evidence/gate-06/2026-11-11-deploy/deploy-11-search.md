# OPS-001 (line C) · CORE-006 and CORE-003 in production: POST /api/v1/search · 2026-11-11 21:08 UTC

Sync by Mariano before this deploy (orchestrator check by MCP): `feature_value` 61,956 rows, rent in the 21 districts, 134 MB.

## What was deployed
`20c59d8` = origin/claude/sprint-1-public `f479281` (CORE-006 F1–F2, CORE-003 F1–F2, D-214, D-215) + line C (PR #8).
- No new migration and no dependency change.
- CORS already allows `POST`.
- `services/search.py` reads only `feature_value`, `feature_registry` and `geo_admin_unit`, all granted to `vf_api_ro`.
- `NEXT_PUBLIC_FEATURE_SEARCH` is still not defined in Vercel, so the web keeps search off.

Gate: `make lint typecheck test-unit` green, with 367 Python tests and 172 web tests.

## make deploy-demo (ALLOW_BRANCH=1) · 145 s · exit 0 · verified on round 2
```
-> deploying 20c59d8 (claude/s1-deploy) to production
-> deployment dpl_G88JsCXfGKMCciDDopZKbTkW8bjr is ready
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T21:10:27Z) tag dpl_G88JsCXfGKMCciDDopZKbTkW8bjr-0
smoke: 7/7 OK
-> which deployment served the smoke (vercel logs requests, tag dpl_G88JsCXfGKMCciDDopZKbTkW8bjr-0)
   2 from dpl_5x37zAL3Rrsw4tAsnBkPjBmpiwcs (another deployment)
   5 from dpl_G88JsCXfGKMCciDDopZKbTkW8bjr (this deploy)
-> the smoke did not come entirely from dpl_G88JsCXfGKMCciDDopZKbTkW8bjr; repeating the smoke in 20 s (1/3)
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T21:11:14Z) tag dpl_G88JsCXfGKMCciDDopZKbTkW8bjr-1
smoke: 7/7 OK
-> which deployment served the smoke (vercel logs requests, tag dpl_G88JsCXfGKMCciDDopZKbTkW8bjr-1)
   7 from dpl_G88JsCXfGKMCciDDopZKbTkW8bjr (this deploy)
-> verified: https://vidafacil-madrid.vercel.app serves dpl_G88JsCXfGKMCciDDopZKbTkW8bjr, and the smoke passed against it
```

## POST /api/v1/search, demo case
Body: `data/fixtures/contracts/scenario_state.familia_castellana.fixture.json` (also `golden_family` in `data/fixtures/golden/search_scenarios.yaml`):
- a couple with 2 children aged 4 and 8;
- rent of 1,500 €/month;
- a school within 10 min on foot, required;
- work on the Castellana (Azca) with `max_minutes: null`.

Result, the same in all 8 calls apart from `meta`:
- `meta.methodology_version` is `fit-0.1`, and `data_version` is `2026-11-11`.
- `reality_check`:
  - `zones_evaluated` 199, `zones_passing` **32**, `zones_unknown` 15;
  - `binding_constraint` `near:colegio`, with 2 relaxations.
- `results`: 10 zones, led by **Ciudad Lineal 99 %**, then Tetuán 97, Hortaleza 97, Moratalaz 97 and San Blas-Canillejas 96. `near_misses`: 5.
- `all_zones`: 199. Warnings: none. Body: 109,156 B, about 2.4 % of the 4.5 MB response limit.

## Response times in production (curl from Madrid, total time)
| Call | Time | Instance state |
|---|---|---|
| 1st search on the new deployment, right after the smoke | 0.96 s | container up, search caches empty |
| Searches 2 to 6 | 0.29 · 0.36 · 0.29 · 0.44 · 0.34 s | warm |
| After 7 min without my traffic | 1.82 s | container still up: other requests hit the API at 21:17 and 21:18, and the logs show no startup before it; caches empty again |
| The next one | 0.36 s | warm |

- **A true cold start was not isolated:** other sessions kept the container up.
- **Estimate for a fully cold request:**
  - container start, about 3.8 s (the `health` and `ready` checks of the same deploy's smoke took 3.88 s and 3.76 s on fresh instances);
  - plus the first search, 1–1.8 s;
  - so about 5–6 s in total, against a 300 s limit per request.
- **Logs:** the runtime logs of `dpl_G88J…` have no errors, no warnings and no restarts, only the startup lines of new instances. Vercel does not report memory per request. Each instance has 2 GB.
- **Instances and caches:** several instances started during the session, and each one keeps its own search caches. So the first search on each instance costs about 1–2 s.
