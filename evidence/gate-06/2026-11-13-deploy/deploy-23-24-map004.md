# OPS-001 (line C) · deploys of e7025fb (MAP-004: labels, first view, barrios in a district) and 5101c93 (the search kept from /zonas); offline package with labels, fonts and barrios · 2026-11-13 (Madrid)

## Deploy of e7025fb (B's PR #37) · `dpl_3ccokRv4tfFNoq4u6V9cfuE9UUSe` · 11:52
- **CI:** green on all five jobs.
- **Verification:** round 1, all 8 requests from the new deployment. Output: [deploy-23/deploy-output.txt](deploy-23/deploy-output.txt).
- **Smoke 9/9,** with the new barrios check: «27 of 199 zones, 1st Latina» and «7 of 8 barrios, 1st Canillejas» ([deploy-23/smoke-9.txt](deploy-23/smoke-9.txt)).
- **By hand at 1440 and 390,** with no console errors ([deploy-23/manual-checks.txt](deploy-23/manual-checks.txt)). The 5 glyph requests to `tiles.openfreemap.org` all returned 200.
  - **First view on Madrid** with the names of districts and municipios, the M-30, the M-40, the A-2 and the A-5: [desktop](deploy-23/desktop-1-primera-vista.jpg) · [mobile](deploy-23/mobile-1-primera-vista.jpg).
  - **Zoomed:** Chamartín, Salamanca and Ciudad Lineal; in San Blas, the station names ([desktop](deploy-23/desktop-2-zoom-chamartin.jpg)).
  - **San Blas after the example** (results list → San Blas → «Ver la zona»): «Los barrios que mejor encajan: 7 de sus 8 barrios…».
    - Canillejas, Arcos and Simancas come out at 97 %.
    - Tapping Simancas sets `aria-pressed=true` and draws its dashed outline: [desktop](deploy-23/desktop-3-simancas-mapa.jpg) · [mobile](deploy-23/mobile-3-simancas-mapa.jpg).
    - Rejas is under «Casi encajan», at 55 %: «No cumple: Colegio con primaria a 10 min andando como mucho».
  - **Hospital note:** «En toda la Comunidad hay 85 hospitales … y 3,0 camas instaladas por cada 1.000…» ([desktop](deploy-23/desktop-4-nota-hospital.jpg)).
- **Watch, 10:53–10:57 UTC:** 8 zone view loads with 80 API requests, plus 5 `/search`, all 200 in 0.46–0.60 s, with 0 5xx ([deploy-23/watch.txt](deploy-23/watch.txt)).
- **Logs, 10:50–11:14 UTC** ([deploy-23/logs-summary.txt](deploy-23/logs-summary.txt)):
  - 0 `EMAXCONNSESSION`, 0 «prepared statement», 0 pooler or authentication errors, 0 tracebacks;
  - 337 API lines, all 200, 9 of them `/search/barrios`.
- **LCP on a phone with slow 4G:** zone 2.02 s, home 1.53 s ([deploy-23/perf-report.json](deploy-23/perf-report.json)).
- **`/search/barrios` warm:** 0.20–0.28 s ([deploy-23/barrios-warm.txt](deploy-23/barrios-warm.txt)).
- **Found for B:** entering a district from «Ver las zonas en una lista» lost the search, because `ScenarioProvider` only wrapped the (mapa) group. B fixed it in PR #43.

## Deploy of 5101c93 (B's PR #43) · `dpl_7puMwXSMefAzT3tBNpkehJ1w7ZSV` · 12:35
- **What changed:** web only, plus D's pitch files.
- **CI and verification:** CI green. Verified on round 0, with all 8 requests from the new deployment ([deploy-24/deploy-output.txt](deploy-24/deploy-output.txt)).
- **Smoke:** 9/9 ([deploy-24/smoke-9.txt](deploy-24/smoke-9.txt)).
- **The path that lost the search,** example → «Ver las zonas en una lista» → San Blas-Canillejas: now it shows «Los barrios que mejor encajan. 7 de sus 8 barrios… Toca uno para verlo en el mapa», with `/search/barrios` 200, at 1440 and 390, with no console errors ([desktop](deploy-24/desktop-zonas-sanblas-barrios.jpg) · [mobile](deploy-24/mobile-zonas-sanblas-barrios.jpg)).
- **e2e in production:** 66/66 and 40/40 ([deploy-24/e2e-report.json](deploy-24/e2e-report.json)), with the suite fixed for D-230 (below).

## The e2e follows D-230
- **The old check:** the suite expected «Zona pequeña para comparar» for any `reliable: false`.
- **What the web does now:** «No comparable» only for a small zone with no group of 2 or more neighbours, and never for SIN DATOS (`apps/web/src/lib/gaps.ts`, `notComparable`). A small zone with such a group keeps its status.
- **The fix:** `infra/deploy/e2e/e2e_prod.mjs` now applies the same rule to the rows (J2) and to the map legend (J3).
- **Effect:** before the fix, J3 failed its 6 legend checks for that category, in production and in the package alike. With it, they pass.

## Offline package with 5101c93
Checkout `fc80718`: `5101c93` plus this branch.
- **Row counts:** the 11 tables are identical to Supabase (`feature_value` 85,032, `commute_time` 191,649), with migration 0007 on both sides.
- **Manifest:** «basemap local, madrid-261111.osm.pbf, label fonts local» ([package-manifest](offline-map004/package-manifest.txt), [prepare](offline-map004/prepare-output.txt)).
- **Web build:** `NEXT_PUBLIC_MAP_TILES_URL=/tiles/tiles.json` and `NEXT_PUBLIC_MAP_GLYPHS_URL=/tiles/fonts/{fontstack}/{range}.pbf`.
- **Smoke:** `make demo-offline`, **8/8 with `/search/barrios`** ([start](offline-map004/start-output.txt)).
- **API against production,** rounded to 1e-9, with `meta` left out: **identical** for `/search`, `/search/barrios`, the gaps of Madrid and San Blas-Canillejas, `/datasets` and `/gaps/impact`.
- **Without network** (every host other than localhost blocked):
  - **e2e:** 66/66 and 40/40, with **0 blocked hosts and 0 console errors** ([report](offline-map004/e2e-nonet/e2e-report.json)).
  - **Labels, served by the package:** the 5 glyph requests go to `localhost:3012`, all 200 ([probe-sin-red.txt](offline-map004/probe-sin-red.txt)).
  - **Barrios:** `/search/barrios` 200, Simancas pressed, and the hospital note present.
  - **Screenshots:** [first view on mobile with labels](offline-map004/mobile-1-primera-vista.jpg) (Madrid, Chamartín, Salamanca, Latina, Usera, Arganzuela, Vicálvaro, Coslada, A-2, A-3, A-6, M-12) · [Simancas](offline-map004/desktop-3-simancas-mapa.jpg).
  - **The `/zonas` path:** San Blas shows its barrios in the package too.
