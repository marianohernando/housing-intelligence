# OPS-001 (line C) · per-instance pool (D-219 option b) in production: not enough · 2026-11-12 10:52 (Madrid)

## Deploy
- **Code:** `0e50ead` (D-219: `DB_POOL_SIZE`, `DB_MAX_OVERFLOW` and `DB_PREPARED_STATEMENTS` in `make_engine`), plus the guide of PR #15. CI green on all five jobs; local gate green, with 479 Python tests and 256 web tests.
- **Vercel, Production, Config:** `DB_POOL_SIZE=2`, `DB_MAX_OVERFLOW=1`, `DB_PREPARED_STATEMENTS=false`. `DATABASE_URL` is unchanged, still on port 5432 (session mode).
- **`make deploy-demo`:** 135 s, `dpl_CB8UdJvLoPzRXU4ZQsjsjVQsuK2B`, verified on round 1: smoke 8/8, all 8 requests from the new deployment. Output: [deploy-14/deploy-output.txt](deploy-14/deploy-output.txt).

## Watch, 09:41–09:51 UTC
- **Load:** the zone views of Fuencarral-El Pardo and Chamartín, one page at a time, every 90 s; 14 loads in total. Output: [deploy-14/watch-zone-views.txt](deploy-14/watch-zone-views.txt).

| Measure | Value |
|---|---|
| API requests | 128 |
| Responses 5xx | 9 |
| Loads stuck in «Algo ha fallado por nuestra parte» | 5, the last ones (rounds 6 and 7) |
| `EMAXCONNSESSION` in the deployment's `vercel logs` | 80 |
| Access lines with 5xx / with 2xx | 17 / 151 |
| Instances started in 10 min | 11 |
| «prepared statement» errors | 0 |

**Reading:**
- `DB_PREPARED_STATEMENTS=false` works on port 5432 with no errors, so moving to 6543 is now safe (D-219 §5).
- The pool of 2 + 1 per instance is not enough. Vercel starts close to one instance per concurrent request: a zone view makes about 12 API requests and 11 instances came up.
- With 2 fixed connections each, that is 22, over the 15 clients that session mode allows on the current plan. The previous deployment's instances, with the default 5 + 10, also stayed alive a few minutes after the switch.

## Options sent to the orchestration
- **(a)** Mariano moves `DATABASE_URL` to port 6543 (transaction mode), then a redeploy with smoke and a watch.
- **(b2)** Meanwhile, `DB_POOL_SIZE=1` and `DB_MAX_OVERFLOW=0` (1 connection per instance) and a redeploy.

## (b2) applied: 1 connection per instance · green
- **Change:** `DB_POOL_SIZE=1` and `DB_MAX_OVERFLOW=0` (Config, overwritten with `--force`); `DB_PREPARED_STATEMENTS=false` unchanged.
- **Deploy:** the same code (`e2e8336` = `0e50ead` + guide), from a detached checkout so B's web stays out. `dpl_FrpvQbWWLvhXRm8XdzaCsfWYa2oq`, 130 s, verified on round 2 (round 1 had 2 of 8 requests from `dpl_CB8U…`), smoke 8/8. Output: [deploy-14/deploy-b2-output.txt](deploy-14/deploy-b2-output.txt).
- **Watch:** 10:01–10:06 UTC, 8 zone view loads, 96 API requests. Output: [deploy-14/watch-b2-zone-views.txt](deploy-14/watch-b2-zone-views.txt).

| Measure | Value |
|---|---|
| Responses 5xx | 0 |
| Loads in the error state | 0 |
| `EMAXCONNSESSION` in the deployment's logs | 0 |
| «prepared statement» errors | 0 |
| Tracebacks | 0 |
| Responses 2xx | 127 |
| Instances | 10, one connection each: 10 of 15 |

- **Still tight:** with more than one person, or more than about 15 instances, it would fail again. The real fix is port 6543 (D-219 §5).
