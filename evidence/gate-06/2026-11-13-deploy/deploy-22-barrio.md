# OPS-001 (line C) · deploy of d12c67a (BARRIO-001, fit-0.7: the barrios of a district) · 2026-11-13 01:05 (Madrid)

## Deploy
- **Code:** `d12c67a`, the HEAD of `claude/sprint-1-public`, CI green on both runs (push and pull_request, all five jobs each).
  - It carries A's BARRIO-001 (fit-0.7, D-232), with the new route `POST /api/v1/search/barrios`. That is the start of Mariano's feedback, «que te recomiende directamente esos barrios».
  - The rest are D's pitch commits.
- **Data:** D synced and checked it before the deploy:
  - barrios in `feature_value`;
  - `commute_time` with 191,649 rows and 131 barrios;
  - official names;
  - Supabase at 185 MB;
  - smoke 8/8 before.
- **Deployed from a detached checkout.** Migration 0007; the variables are unchanged.
- **`ALLOW_BRANCH=1 make deploy-demo`:** `dpl_2r7MzYbbHY7jCSaTwtej5FdMHhNv`, verified on round 1. Output: [deploy-22/deploy-output.txt](deploy-22/deploy-output.txt).
  - Round 0 had 2 requests from `dpl_JCgqN…`.
  - Round 1 was 8/8, all from the new deployment.

## Checks
- **Regional `/search`** (demo case): `fit-0.7`, **27 of 199 zones, 1st Latina 98 %**, the same as before ([deploy-22/search-regional.txt](deploy-22/search-regional.txt)).
- **`POST /api/v1/search/barrios`** with the demo case and `distrito: "2807920"` (San Blas-Canillejas): HTTP 200, `fit-0.7`, `warnings: []`.
  - Request: [deploy-22/search-barrios-request.txt](deploy-22/search-barrios-request.txt). Response: [deploy-22/search-barrios-2807920-response.json](deploy-22/search-barrios-2807920-response.json).
  - **8 barrios evaluated, 7 pass.** The binding constraint is `near:colegio`.

| Rank | Barrio | Match |
|---|---|---|
| 1 | Canillejas | 97 % |
| 2 | Arcos | 97 % |
| 3 | **Simancas** | **97 %** |
| 4 | Rosas | 96 % |
| 5 | Amposta | 96 % |
| 6 | El Salvador | 95 % |
| 7 | Hellín | 93 % |
| near miss | **Rejas** | 55 %: «near:colegio FAIL: La mitad de sus calles está a 35 min andando o menos de un colegio con primaria» |

- **Simancas** (barrio `28079201`):
  - «Colegio con primaria a unos 7 min andando»;
  - «Parada de transporte público a unos 2 min andando»;
  - «Centro de salud a unos 13 min andando»;
  - «37 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00»;
  - «Alquiler ≈ 1.228 €/mes por 77 m² (15,9 €/m², contratos firmados en 2024; un anuncio de hoy puede pedir más)».
- **The web does not show the barrios yet.** B adds them in PR #37.

## Watch, 00:06–00:11 UTC
- **Load:** 8 zone view loads of Fuencarral-El Pardo and Chamartín, with 80 API requests and 0 5xx, plus 5 `/search`, all 200 in 0.40–0.84 s. Output: [deploy-22/watch.txt](deploy-22/watch.txt).
- **Logs, 00:02–00:11 UTC:** [deploy-22/logs-summary.txt](deploy-22/logs-summary.txt).

| Measure | Value |
|---|---|
| `EMAXCONNSESSION`, «prepared statement», authentication, connection, timeout | 0 |
| Tracebacks, `ValueError` or `KeyError` | 0 |
| API access lines | 129, all 200, 2 of them `POST /api/v1/search/barrios` |
| Instances started | 7 |
| CDN records | 420, all 200 |

## Offline package
It waits for B's PR #37: labels (with the fonts of #36, wired on `claude/s1-offline-glyphs`), the first view and the barrios.
