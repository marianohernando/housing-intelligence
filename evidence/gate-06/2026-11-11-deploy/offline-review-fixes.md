# OPS-001 (line C) · fixes to `demo_offline.sh` after line A's review of PR #5 (2026-11-11 ~14:15 UTC)

| Item | Fix | Test | Result |
|---|---|---|---|
| R-01 | `COMPOSE=(docker compose -p vida-facil-offline …)` | `COMPOSE_PROJECT_NAME=housing-intelligence make demo-offline-prepare` | exit 0 in 23 s; `housing-intelligence-db-1` and `-redis-1` still running |
| R-02 | The web is built from a private copy (`data/offline/web-build`, copied with rsync without `.next`, `node_modules` or `.env*`), with `NEXT_PUBLIC_*` unset except `NEXT_PUBLIC_API_URL=http://localhost:8012` | Same run with `NEXT_PUBLIC_API_URL=http://localhost:8010` (and earlier `NEXT_PUBLIC_LEAK_TEST`) in the environment | The bundle only contains `http://localhost:8012`; `NEXT_PUBLIC_LEAK_TEST` appears in 0 files; `apps/web/.next/BUILD_ID` still has its 13:16 CET timestamp |
| R-03 | The source is checked first (`select 1` and migration head); the dump and manifest are written to `.tmp`; they load into a `vidafacil_staging` database; counts are validated; only then the staging DB is renamed and the files are moved. The volume is never deleted | `SOURCE_DATABASE_URL` pointing at a closed port | exit 2 in 4 s; `shasum` of dump and manifest unchanged; `make demo-offline` straight after: smoke 5/5 |
| R-04 | `stop` only kills the pid if its command is `next-server`/`server.js` | Unrelated process (`perl -e 'sleep 60'`) written into `web.pid`, then `make demo-offline-stop` | The process survives |
| R-05 | `trap … ERR`: "failed at line N. Clean up with: make demo-offline-stop" (`set -E`, no false positives from the stderr filters) | Normal runs | No trap message; it only appears on real failures |
| R-06 | `start` checks the volume against `manifest.txt` and, if it does not match, restores from `demo-data.sql.gz` (staging + validation) | `docker volume rm vida-facil-offline_offline_pgdata`, then `make demo-offline` | "restoring it from …"; exit 0 in 11 s; smoke 5/5 |
| R-07 | Clear message when the source fails, with the password masked | Same run as R-03 | "cannot reach the source database postgresql://housing:***@host.docker.internal:5999/housing … start the development stack (make up) or set SOURCE_DATABASE_URL."; the password appears in 0 lines |

Normal cycle afterwards:
- `make demo-offline`: 8 s, smoke 5/5.
- Headless Chromium on `/map`: 0 external requests, no console errors (`offline-map-desktop.png` and `offline-map-mobile.png` regenerated).
- `make demo-offline-stop`: no listeners left on 3012, 8012 or 5441.
