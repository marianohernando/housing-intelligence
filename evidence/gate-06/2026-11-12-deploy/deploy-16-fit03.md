# OPS-001 (line C) · `/search` 500 after a data sync, fixed by deploying fit-0.3 · 2026-11-12 13:55 (Madrid)

## Incident
- **What happened:** D synced to Supabase the new park feature of DATA-018, the «Zonas verdes» priority without a `need`.
- **Effect:** the deployed code, `dpl_5efz…` (`a04467d`, fit-0.2), failed to read it.
  - `/search` returned 500 with `ValueError: None is not a valid NeedKey` (`hi_api/services/search.py:111`).
  - The smoke gave 7/8.
- **The fix:** the HEAD of `claude/sprint-1-public`, whose fit-0.3 (`f7e29ab`, D-222 §7) understands that feature.

## Deploy
- **Code:** `50d4b28`, which is `f7e29ab` plus line C's evidence. CI green.
  - Deployed from a checkout detached from the work branch, so line C's work in progress stayed out.
  - Migration 0007. Config unchanged: `DB_POOL_SIZE=1`, `DB_MAX_OVERFLOW=0`, `DB_PREPARED_STATEMENTS=false`.
- **`ALLOW_BRANCH=1 make deploy-demo`:** `dpl_AtNd6uYPahHmYPyHMp3SwRepcck8`, verified on round 1. Output: [deploy-16/deploy-output.txt](deploy-16/deploy-output.txt).
  - **Round 0: 8/8,** but 3 of its 8 requests came from `dpl_5efz…`.
  - **Round 1: 8/8,** all from the new deployment.
- **Demo case:** 33 of 199 zones.

| Rank | Zone | Match |
|---|---|---|
| 1 | Fuencarral-El Pardo | 100 % |
| 2 | Ciudad Lineal | 99 % |
| 3 | Hortaleza | 99 % |

- **CDN records of `/search`:** the last 500 came from `dpl_5efz…` at 12:54:41 UTC. From 12:55:05 every one is a 200 from `dpl_AtNd6…`.

## Watch, 12:56–13:01 UTC
- **Load:** 8 zone view loads of Fuencarral-El Pardo and Chamartín, with 48 API requests, plus one `/search` with the demo case every minute. Output: [deploy-16/watch.txt](deploy-16/watch.txt).
- **Result:**
  - 0 responses 5xx and 0 loads in the error state.
  - The 5 searches all returned 200, in 0.35–0.59 s.
- **The new deployment's logs, 12:53–13:49 UTC:** [deploy-16/logs-summary.txt](deploy-16/logs-summary.txt).

| Measure | Value |
|---|---|
| `EMAXCONNSESSION` | 0 |
| «prepared statement» | 0 |
| «password authentication», «connection» or «timeout» | 0 |
| `ValueError`, `NeedKey` or tracebacks | 0 |
| API access lines | 119, all 200, 10 of them `POST /api/v1/search` |
| Instances started | 8 |
| CDN records | 445, all 200 |

## Consequences for the guide
- **Rollback:** `dpl_5efz…` no longer serves for one, because it does not understand the current data. Since this deploy, a rollback is only valid to `dpl_AtNd6…` or later.
- **Order when code and data change together:** deploy the code that understands the new data first, then sync.
