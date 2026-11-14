# OPS-001 (line C) · deploy of d5fe735, batch 2b (#59 D-234 estimated purchase price, #60 D-240 office days, telework and family place, `fit-0.8`) and the D-234 sync · 2026-11-14 (Madrid)

## Order (D-234 §8)
1. Deploy the code. d5fe735 reads the new fit role `price_m2_estimate`, and the code before it ignores that role.
2. Smoke and e2e with the old data.
3. datamad-10 recalculated in `housing` (the panel with parser 1.4.0, `precio_compra_estimado_m2` and `valor_tasado_vivienda_m2`) and ran `make supabase-sync PROFILE=demo` from d5fe735.
4. Smoke, e2e, the purchase case and the logs again.

## Deploy · `dpl_G5sos4HUNhHsThkgLxqfoMbtoFCU` · 23:12
- **CI:** green on d5fe735, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-29/deploy-output.txt](deploy-29/deploy-output.txt).
- **Verification:** on round 0. The smoke passed 13/13, and all 13 of its requests came from the new deployment.
- **`telework`, the new check:** 200 with `fit-0.8`. Just before the deploy, the same body got 422 («days_per_week … greater than or equal to 1»).

## Before the sync
API details in [deploy-29/search.txt](deploy-29/search.txt). Web details in [deploy-29/web-checks.txt](deploy-29/web-checks.txt).
- **e2e:** 69/69 at 1440 px and 43/43 at 390 px, with the new labels ([deploy-29/e2e-report-presync.json](deploy-29/e2e-report-presync.json)).
- **The example is unchanged.**
  - It gives 27 of 199, with Latina 98 %, the same top 10 and the same «casi».
  - Against f1b6f5a: the same %, `passes_all` and failed constraints in all 199 zones, and the same order and facts.
  - On screen: «Latina · 98 % · ≈ 1.101 €/mes».
- **«Comprar 400.000 €, pareja»:**
  - 27 of 199 fit, all of them municipios, each with its price («≈ 196.000 €»);
  - none of the 21 districts has a price;
  - the Reality Check no longer offers to relax the budget; before the deploy it offered «+40.000 € +0»;
  - the web says «En 172 zonas no podemos comprobarlo todo: sin precio de compra en 172 zonas (…)». It says «zonas», never «municipios».
  - The district cards (Moratalaz at 1440, Tetuán at 390) say «Sin precio de compra en esta zona: el valor tasado del Ministerio de Vivienda se publica para Madrid entero, no por distrito ni por barrio.», with no price in their header.
  - Screenshots: [list](deploy-29/presync-1440-2-compra-400k.jpg) · [Moratalaz](deploy-29/presync-1440-3-tarjeta-moratalaz.jpg) · [Tetuán 390](deploy-29/presync-390-3-tarjeta-tetuan.jpg).
- **Tetuán by barrio:** 0 of 6, all 6 without data.

## After the sync
- **Supabase** ([deploy-29/supabase-postsync.txt](deploy-29/supabase-postsync.txt)):
  - `feature_registry` 50 (+1), `feature_value` 95,263 (+283) and `metric_registry` 38 (+3);
  - `precio_compra_estimado_m2` has 152 rows: 21 districts and 131 barrios.
- **Smoke:** 13/13 ([deploy-29/smoke-postsync.txt](deploy-29/smoke-postsync.txt)). **e2e:** 69/69 and 43/43 ([deploy-29/e2e-report-postsync.json](deploy-29/e2e-report-postsync.json)).
- **The example is unchanged.** Zones, order, %, costs and facts are identical. `datasets` gains the Ayuntamiento panel the estimate comes from.
- **«Comprar 400.000 €, pareja»** gives the same as D-234 §7:
  - 41 of 199 fit: 14 districts and 27 municipios;
  - the top 10 is Puente de Vallecas (≈ 202.000 €), Usera, Carabanchel, Latina, Villaverde, Coslada, Parla, Móstoles, San Blas-Canillejas and Leganés;
  - «Casi encajan» is Arganzuela (≈ 406.000 €), **Tetuán (≈ 411.000 €)**, Centro, Retiro and Chamberí;
  - the Reality Check offers «+40.000 € saldrían 44 zonas, 3 más»;
  - the rest without data are 151 municipios, and the notice now says «municipios».
- **Tetuán's district card**, at 1440 and 390:
  - «Comprar ≈ 411.000 € · Dato aproximado» under the name;
  - «No cumple: Compra hasta 400.000 €»;
  - the fact «Comprar ≈ 411.000 € por 68 m² (6.051 €/m², precio estimado: valor tasado de Madrid repartido según el valor catastral del distrito; Ministerio de Vivienda y Catastro vía Ayuntamiento) · Dato aproximado».
  - Screenshots: [1440](deploy-29/postsync-1440-3-tarjeta-tetuan.jpg) · [390](deploy-29/postsync-390-3-tarjeta-tetuan.jpg) · [list](deploy-29/postsync-1440-2-compra-400k.jpg).
- **Tetuán → barrios** («Ver la zona»; `/search/barrios` 200):
  - «4 de sus 6 barrios encajan»: **Valdeacederas (≈ 348.000 €) and Berruguete (≈ 378.000 €)**, then Almenara and Bellas Vistas;
  - each one's fact says «… del barrio».
  - Screenshots: [1440](deploy-29/postsync-1440-4-barrios-tetuan.jpg) · [390](deploy-29/postsync-390-4-barrios-tetuan.jpg).
- **Errors:** 0 console errors and 0 HTTP ≥ 400, before and after the sync, at both widths.

## Logs, 22:10–22:21 UTC, through the sync
Details in [deploy-29/logs-summary.txt](deploy-29/logs-summary.txt).
- **Runtime:** 348 lines, all info, with 7 instances started.
  - **0 `fit bindings ignored`**, 0 `WARNING`, and 0 pool, prepared-statement, authentication, validation or traceback lines.
- **CDN:** 1,477 records, 1,475 × 200 and 2 × 304, with **no 4xx or 5xx**. That includes the sync window: no 404 from the hospital note this time.

## Two readings for review, not blocking
1. **A zone in «Casi encajan» can show 0 %.** With only a purchase budget, a zone over the budget scores 0 % (D-234 §6). Tetuán appears under «Casi encajan» and its card reads «0 % de encaje».
2. **A barrio can «encajar» at 5 %.** With only a budget, the % falls as the price nears the budget: Valdeacederas 52 %, Berruguete 22 %, Almenara 10 % and Bellas Vistas 5 %, and all four «encajan».

## Rollback
- **If needed:** `dpl_59jvNLYJAitb5mopLmjGMmpXuogg` (f1b6f5a). It is safe after this sync without deleting anything, because it ignores `price_m2_estimate`.
  - Web and API go back together.
  - The old API answers 422 to `days_per_week: 0`, and the new smoke's `telework` check fails against it.
- **The D-233 rule still applies:** nothing before ad4a8f2 without first deleting the 2 `feature_registry` rows.

## Not done in this batch
The offline package was not rebuilt, as asked. It is still at 39644a9, without `scope`, telework or the estimate.
