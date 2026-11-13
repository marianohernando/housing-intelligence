# OPS-001 (line C) · deploy of 310056b (fit-0.6, rent of leases signed in 2024), then the rent sync · 2026-11-12 23:15 (Madrid)

## Order: code first, then data
- **What D asked:** deploy before syncing. The new code with the old data is correct, because the note travels with the value.
- **The other way round:** the web would say «contratos vigentes» next to the new figure.

## Deploy
- **Code:** `310056b`, the HEAD of `claude/sprint-1-public` (MEJORA-8 Fase 2, fit-0.6, D-228 option A).
  - CI green on both runs, push and pull_request, all five jobs each.
  - Deployed from a detached checkout. Migration 0007; the variables are unchanged.
- **`ALLOW_BRANCH=1 make deploy-demo`:** `dpl_4P9B8j15b8pzTHugitgyeFxAaq94`, verified on round 1. Output: [deploy-20/deploy-output.txt](deploy-20/deploy-output.txt).
  - Round 0 had 4 requests from `dpl_2eR98…`.
  - Round 1 was 8/8, all from the new deployment.
  - «Desplegado» was sent to D.
- **The later HEAD, `861af7b` (Fase 2b),** changes neither `apps`, `packages` nor `infra`, so it needs no deploy.

## During the sync
- **What the API returned:** `/datasets` (total 0) and the gaps of Madrid (0 rows, `INSUFFICIENT_DATA`) came out empty around 22:04 UTC. `ready` was `ok`.
- **Why:** the sync's `TRUNCATE` empties the tables while it copies them, as the guide warns («Día de la final», never sync in the hour before presenting).
- **No baseline:** for that reason there is no reading from just before the sync, only the one after it.

## Checks after the sync
Output: [deploy-20/checks-after-sync.txt](deploy-20/checks-after-sync.txt).

| Check | Result |
|---|---|
| Smoke (tag `postsync-fit06`) | 8/8, «27 of 199 zones, 1st Latina» |
| `methodology_version` | `fit-0.6` |
| Rent text | **10 of 10** results say «contratos firmados en 2024» |
| Fuencarral-El Pardo | 97 %: «Alquiler ≈ 1.276 €/mes por 77 m² (16,6 €/m², contratos firmados en 2024; un anuncio de hoy puede pedir más)» |
| «+150 €/mes» | **+3 zones** (27 → 30). Before, it added none |
| «+5 min a pie hasta colegio con primaria» | +17 zones (27 → 44) |
| `/datasets` | the 2 Agencia Tributaria datasets have `is_cm_open_data=false`; `cm_open_data_count` stays at **27**, with 35 in total |
| Pitch journeys (`make e2e-prod`) | **66/66 and 40/40**: every figure on screen equals the API ([report](deploy-20/e2e/e2e-report.json)) |

- **The run with screenshots** ([report](deploy-20/e2e/e2e-shots-report.json)) has 36 and 30 checks. With `--shots`, J3 only goes through the first row; it is not missing anything.
- **The demo case, in full for the pitch and the screenshots:** [caso-demo-fit06.md](caso-demo-fit06.md).

## Watch, 22:06–22:11 UTC
- **Load:** 8 zone view loads of Fuencarral-El Pardo and Chamartín, with 80 API requests and 0 5xx, plus 5 `/search`, all 200 in 0.41–0.49 s. Output: [deploy-20/watch.txt](deploy-20/watch.txt).
- **Logs, 22:02–22:12 UTC:** [deploy-20/logs-summary.txt](deploy-20/logs-summary.txt).

| Measure | Value |
|---|---|
| `EMAXCONNSESSION`, «prepared statement», authentication, connection, timeout | 0 |
| Tracebacks, `ValueError` or `KeyError` | 0 |
| API access lines | 387, all 200 |
| Instances started | 6 |
| CDN records | 1,369: 1,363 × 200 and 6 × 304 |

## Offline package
Not regenerated, at D's request. It waits for B's PR #32.
