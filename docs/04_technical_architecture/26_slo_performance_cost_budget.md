# SLOs, Performance & Cost Budgets

## Initial product targets
### API
- simple/cached p95 < 500 ms;
- complex synchronous analysis p95 < 2 s where feasible;
- heavy jobs async.

### Map
- first useful map < 4 s on representative connection/device;
- interaction target ~60 fps during normal pan/zoom;
- layer toggle feedback < 500 ms.

### AI
Show progressive state for calls > 2 s.
Timeout/fallback mandatory.

## Cost
Track per:
- LLM call;
- routing;
- tiles;
- storage;
- report;
- user/session.

## Budget guardrails
- token limits;
- query limits;
- caching;
- batch jobs;
- PLUS/PRO entitlements.
