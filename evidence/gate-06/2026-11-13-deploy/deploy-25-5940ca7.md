# OPS-001 (line C) · deploy of 5940ca7 (#45, #46 by A+B, #47 by D) and offline package with it · 2026-11-13 (Madrid)

## What changed
- **API (`hi_domain/fit.py`):**
  - The walking condition now reads «A unos N min andando de X (lo que tarda la mitad de la zona)». Before, it read «La mitad de sus calles está a…».
  - A priority walking fact that is out of range no longer carries `indicator`.
- **Web:**
  - `hasWalkingFact` now goes by the indicator (`min_a_pie_*`), not by the word «andando».
  - `style.ts` paints by fit and by row with `!= null` instead of `has`.
- **No sync.** The fit is computed on each request, and the Supabase data do not change.

## Deploy · `dpl_7SDGdC8Wtr5GAVHRTcyG871BFDLN` · 15:16
- **CI:** green on 5940ca7, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout of 5940ca7.
- **Verification:** round 0, all 9 smoke requests from the new deployment. Output: [deploy-25/deploy-output.txt](deploy-25/deploy-output.txt).
- **Smoke 9/9:** «27 of 199 zones, 1st Latina» and «7 of 8 barrios, 1st Canillejas».
- **New texts in the API** ([deploy-25/api-texts.txt](deploy-25/api-texts.txt)):
  - **`/search`, demo case:** all 15 walking conditions read «A unos N min andando de un colegio con primaria (lo que tarda la mitad de la zona)».
  - **Walk indicators:** 30 facts carry a `min_a_pie_*` indicator. The facts without one are the 10 commute facts, as before.
  - **`/search/barrios`, San Blas-Canillejas:** the same text for its 8 barrios, from «A unos 4 min» (Hellín) to «A unos 35 min» (Rejas, which fails, 55 %).
  - **Not seen in the demo case:** no priority walking fact out of range shows up in it, so change (2) is covered only by `tests/unit/fit/test_fit.py`.
- **e2e in production:** 66/66 at 1440 px and 40/40 at 390 px ([deploy-25/e2e-report.json](deploy-25/e2e-report.json)).
- **Logs, 14:10–14:22 UTC** ([deploy-25/logs-summary.txt](deploy-25/logs-summary.txt)):
  - 0 `EMAXCONNSESSION`, 0 «prepared statement», 0 pooler or authentication errors, 0 tracebacks;
  - 196 API lines, all 200, 12 of them `POST /search` and 15 `POST /search/barrios`;
  - 732 CDN records, all 200.

## The map after a search (style.ts), by hand at 1440 and 390
Details in [deploy-25/manual-checks.txt](deploy-25/manual-checks.txt). No console errors and no HTTP ≥ 400 in any step.
- **No search:** every zone is plain and light, and the streets show through ([desktop](deploy-25/desktop-0-sin-buscar.jpg)).
- **After «Ver un ejemplo»** ([desktop](deploy-25/desktop-1-busqueda-region.jpg) · [mobile](deploy-25/mobile-1-busqueda-region.jpg)):
  - zones that fit are in the violet ramp, those failing a condition are hatched, and those with no data are dashed;
  - the legend reads «Cumple todo 27 · No cumple todo 157 · Sin datos 15», the same as the API's `all_zones`.
- **«Colegios» with the search on** ([desktop](deploy-25/desktop-4-busqueda-fila-colegios.jpg) · [mobile](deploy-25/mobile-4-busqueda-fila-colegios.jpg)):
  - the map paints by row: CUBIERTO 59, JUSTO 75, No comparable 65, FALTA 0 and SIN DATOS 0, 199 zones in all;
  - back to «Encaje con tu búsqueda», the legend reads 27 again.
- **San Blas-Canillejas after the search** ([desktop](deploy-25/desktop-7-simancas-mapa.jpg) · [mobile](deploy-25/mobile-7-simancas-mapa.jpg)):
  - «7 de sus 8 barrios encajan»;
  - tapping Simancas sets `aria-pressed=true` and draws its dashed outline;
  - «Los minutos andando son los de la mitad de la zona…» shows under the list, now detected by the indicator.

## Offline package with 5940ca7
- **Prepare:** `make demo-offline-prepare` from the same checkout ([prepare](offline-5940ca7/prepare-output.txt)).
  - Manifest: `git_commit 5940ca7`, «basemap local, madrid-261111.osm.pbf, label fonts local» ([package-manifest](offline-5940ca7/package-manifest.txt)).
- **Row counts:** the 11 tables equal Supabase, checked after the prepare (`feature_value` 85,032, `commute_time` 191,649), with migration 0007 on both sides.
- **Smoke:** `make demo-offline`, 8/8 with `/search/barrios` ([start](offline-5940ca7/start-output.txt)).
- **API against production,** rounded to 1e-9, with `meta` left out: **identical** for the 6 answers, the new texts included ([api-vs-production](offline-5940ca7/api-vs-production.txt)). The 6 are `/search`, `/search/barrios`, the gaps of Madrid and San Blas-Canillejas, `/datasets` and `/gaps/impact`.
- **Without network** (every host other than localhost blocked):
  - **e2e:** 66/66 and 40/40, with **0 blocked hosts** ([report](offline-5940ca7/e2e-nonet/e2e-report.json));
  - **the same map probes as in production:** the same legends and counts, the walking note, and Simancas pressed, with 0 blocked hosts and 0 errors ([probe-sin-red.txt](offline-5940ca7/probe-sin-red.txt));
  - **screenshots:** [search on mobile](offline-5940ca7/mobile-1-busqueda-region.jpg) · [«Colegios» with local labels](offline-5940ca7/desktop-4-busqueda-fila-colegios.jpg) · [Simancas](offline-5940ca7/desktop-7-simancas-mapa.jpg).

## Rollback
Not needed. If it were, `dpl_7puMwXSMefAzT3tBNpkehJ1w7ZSV` (5101c93) understands the same data.
