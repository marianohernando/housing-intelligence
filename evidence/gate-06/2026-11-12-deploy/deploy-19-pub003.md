# OPS-001 (line C) · deploy of eca4a30 (fit-0.5 buy, parks in green, perceived safety, /gaps/impact), then the buy-data sync · 2026-11-12 21:15 (Madrid)

## Order: code first, then data
- **What D asked:** deploy before syncing the buy data (`d2282aa` + `3076f3c`). With the data first, `/search` would return 500.
- **What happened:** the new code with the old data works, and Comprar comes out UNKNOWN until the sync.

## Deploy
- **Code:** `eca4a30`, the HEAD of `claude/sprint-1-public`, CI green on all five jobs (checked by line C). It carries:
  - B's PR #28: parks in green, perceived safety in the districts, Comprar without «Aún no tenemos precios», the 100 % line and the TrainFront icon;
  - A's fit-0.5 (DATA-021, Comprar with the valor tasado);
  - the new route `GET /api/v1/gaps/impact` (D-229);
  - A's `services/mcp` line in the API Dockerfile, reviewed before: build fine, `hi_mcp` not installed, 699 MB.
- **Deployed from a detached checkout.** Migration 0007; the variables are unchanged.
- **`ALLOW_BRANCH=1 make deploy-demo`:** `dpl_2eR98j8fXyiboV1F6Nb1Xa1TBdn8`, verified on round 1. Output: [deploy-19/deploy-output.txt](deploy-19/deploy-output.txt).
  - Round 0 had 2 requests from `dpl_5QyHV…`.
  - Round 1 was 8/8, all from the new deployment.
  - «Desplegado» was sent to D before the watch.

## Checks before and after the sync
The search is the demo case with `budget: {kind: buy, amount_eur: 300000}` ([deploy-19/search-buy-budget.json](deploy-19/search-buy-budget.json)).

| Check | Before the sync | After the sync |
|---|---|---|
| `methodology_version` | `fit-0.5` | `fit-0.5` |
| Zones passing | 0 of 199 (everything UNKNOWN) | **15 of 199** |
| Leganés | `match_pct` null | **1st, 95 %, `budget=PASS`, `near:colegio=PASS`** |
| `GET /api/v1/gaps/impact` | 200, `impact-0.1` | 200: escuelas infantiles **25,551** niños de 0 a 4 años in FALTA, of 260,310 (3 zones) |
| `/datasets` `cm_open_data_count` | 26 | **27** |
| Smoke | 8/8 | 8/8 (line C, tag `postsync-pub003`) |

- **Outputs:** [checks-before-sync.txt](deploy-19/checks-before-sync.txt) · [checks-after-sync.txt](deploy-19/checks-after-sync.txt).
- **D's `curl` test:** its 422 at 20:07:14 UTC came from its own request body. The demo case's body returns 200.

## Villaverde by hand: parks in green and perceived safety
- **Pages:** `/zona/distrito/2807917`, at desktop 1440 × 900 and mobile 390 × 844, with no console errors and no HTTP errors. Output: [deploy-19/villaverde.txt](deploy-19/villaverde.txt).
- **Parks:** the «Parques 34» chip, once pressed, lights the parks up in green with their green dots: [desktop](deploy-19/villaverde-desktop-parques.jpg) · [mobile](deploy-19/villaverde-mobile-parques.jpg).
- **Perceived safety:** the card «Seguridad del barrio según sus vecinos» reads «Así valoran sus vecinos la seguridad de su barrio: 4,9 de noche y 6,8 de día, de 0 a 10 (en todo Madrid, 6,4 y 7,8)», with the source «Encuesta de calidad de vida del Ayuntamiento de Madrid, 2025, unas 400 personas por distrito»: [desktop](deploy-19/villaverde-desktop-seguridad.jpg) · [mobile](deploy-19/villaverde-mobile-seguridad.jpg).

## Watch, 20:07–20:12 UTC
- **Load:** 8 zone view loads of Fuencarral-El Pardo and Chamartín, now 10 API requests each (perceived safety and parks), 80 in total with 0 5xx. Plus 5 `/search` with the demo case, all 200 in 0.38–0.63 s. Output: [deploy-19/watch.txt](deploy-19/watch.txt).
- **Logs, 20:03–20:12 UTC:** [deploy-19/logs-summary.txt](deploy-19/logs-summary.txt).

| Measure | Value |
|---|---|
| `EMAXCONNSESSION`, «prepared statement», authentication, connection, timeout | 0 |
| Tracebacks or `KeyError` | 0 |
| API access lines | 286 × 200 and D's 422 |
| Instances started | 7 |

## LCP, one pass on a phone with slow 4G
Report: [deploy-19/perf-report.json](deploy-19/perf-report.json). Elements: [deploy-19/lcp-elements.txt](deploy-19/lcp-elements.txt).

| Page | LCP |
|---|---|
| zone Chamartín | **1.98 s**, the lead text |
| home | 1.12 s |
| «Qué falta» Madrid | 1.12 s |

## Offline package
Not regenerated, at D's request. It will be done once, after A's fit-0.6 and B's «dónde invertir primero» are deployed.
