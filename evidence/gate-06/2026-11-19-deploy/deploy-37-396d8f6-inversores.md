# OPS-001 (line C) · deploy of 396d8f6: the investor version, #95 (D-247, data) and #94 (D-248, viability and «Para inversores») · 2026-11-19 (Madrid)

## What the deploy brings
- **#94, D-248:**
  - the API `/api/v1/investors/zones`, `/api/v1/investors/zones/{admin_unit_id}` and `POST /api/v1/investors/viability` (residual method v0, `viability-0.1`);
  - the web «Para inversores»: `/inversores` (the 108 pilot barrios), `/inversores/<barrio>` (a barrio's sheet with its calculator and print view), and a link in the header and footer.
- **#95, D-247:** the investor data:
  - the M-40 pilot;
  - the padrón;
  - the census of premises;
  - VEDA's remaining buildable area;
  - the CM cadastre uses;
  - the PEM of the CM building permits.

  It is context that never scores. datamad-10 loaded it into `housing` and synced it. There are no migrations.
- **Nothing here touches `/search` or `/gaps`.**
- **Order:**
  1. the code, verified with the old data;
  2. the load and the sync;
  3. a second verification.

## Deploy · `dpl_GAcSQGpjuj7AKa178gFS2Yq1kNRU` · 10:40
- **CI:** green on 396d8f6, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-37/deploy-output.txt](deploy-37/deploy-output.txt).
- **Verification:** on round 0. All 13 smoke requests came from the new deployment.
- **Disk:** the build is remote. Free disk stayed between 3.9 and 4.7 GB, above the 1.5 GB floor.

## 1. With the old data, 09:41–09:47 UTC
1. **Smoke:** 13/13, `/search` included (the example gives 42 of 199, Puente de Vallecas 1st).
2. **API:** 51 answers identical to 747cb65's, without `meta` ([deploy-37/search.txt](deploy-37/search.txt)).
   - They are:
     - 11 search bodies;
     - `/gaps` of 21 districts and 10 municipios;
     - the feature list at 3 levels;
     - 6 value answers of context features.
   - Only `request_id` and `generated_at` change in `meta`, and every answer keeps its byte size.
3. **Golden:** 10/10 through the public API, identical line by line to before the deploy (and to deploy-36's after its sync).
4. **e2e:** 116/116 at 1440 px and 92/92 at 390 px, with 0 console errors ([report](deploy-37/e2e-antes-del-sync.json)). The public pages never ask for the new features, so there is no 404 before the sync this time.
5. **`check-ux-mobile.mjs`:**
   - 0 texts under 16 px and 0 targets under 44 px on 24 screens (12 at 390 px, 12 at 360 px), apart from the map's 3 attribution controls;
   - axe 0;
   - its output is identical to deploy-36's, so the header and footer link keeps every size and count.
6. **The investor routes, no 5xx** ([deploy-37/inversores-api.txt](deploy-37/inversores-api.txt)):
   - **`GET /investors/zones`:** 200.
     - It lists 108 barrios, pilot «Madrid capital dentro de la M-40».
     - `remaining_m2`, `remaining_shared_areas` and `commerce_per_1000` are null in all 108, as expected before the sync.
   - **Pinar del Rey's sheet (`ES.28.BAR.28079164`):** 200, with six `INSUFFICIENT_DATA: … not loaded yet` warnings, one per feature of A's that was not loaded yet.
   - **`POST /investors/viability`, 1.000 m² at 4.000 €/m², PEM 600 €/m², rent 15 €/m²:**
     - «Lo máximo que se puede pagar por el suelo: 2,06 millones de € (2.064 € por m² edificable)», with a rental yield of 6,25 %;
     - with land at 2.200 €/m² and an income of 40.000 €: «Ajustar: margen del 16,6 %».
   - **Errors:** a barrio outside the pilot gives 404; a municipio id, 49 m² and both land prices give 422.
   - **Web:** `/inversores` and `/inversores/28079164` give 200; `/inversores/99999999` and `/inversores/abc` give 404.
7. **#94's `check-inversores.mjs` against production:** 12/12 screens clean ([deploy-37/check-inversores-antes-del-sync.json](deploy-37/check-inversores-antes-del-sync.json)).
   - The run adds 360 px to the script's 390 and 1440 px.
   - The screens are the list, the sheet, the calculator with a land price and the print view.
   - On every screen: 0 texts under 16 px, 0 targets under 44 px, no horizontal overflow, axe 0 and 0 console errors.
   - The sheet says «Aún sin dato para este barrio» and «Suelo vacante (Catastro) · Sin dato · Fuente: Aún sin cargar» ([390](deploy-37/390-03-suelo-antes-del-sync.jpg)).
8. **Logs** ([deploy-37/logs-antes-del-sync.txt](deploy-37/logs-antes-del-sync.txt)):
   - **Runtime:** 594 lines, all info, with 7 instances started. 0 `WARNING`, and 0 pool, authentication or traceback lines.
   - **CDN:** 1,734 records, the whole window. 0 5xx.
   - **4xx:** only these checks' deliberate errors: 3 × 404 and 3 × 422.
   - **499:** 5, all static chunks that `check-inversores` cancelled when it navigated.

## The load and the sync (datamad-10)
- **`housing`:** loaded first, and all 7 quality checks passed: `osm_m40`, the padrón, the census of premises, VEDA, the two CM cadastre sets and the PEM.
- **Features:** `hi-features compute`, then golden 10/10 locally.
- **Sync:** `make supabase-sync PROFILE=demo` returned rc 0. As datamad-10 reported it, the remote now has:
  - `feature_value` 120,586 (+1,120);
  - `feature_registry` 77;
  - `metric_registry` 57;
  - `dataset_registry` 66;
  - 217 MB in total.

## 2. After the sync, 09:49–09:53 UTC
1. **Smoke:** 13/13 ([deploy-37/smoke-despues-del-sync.txt](deploy-37/smoke-despues-del-sync.txt)).
2. **API** ([deploy-37/search.txt](deploy-37/search.txt)):
   - **Unchanged:** the 11 searches, the 31 `/gaps` and the 6 value answers are identical without `meta`, and the same size in bytes.
     - The searches' `meta.data_version` moves from 2026-11-15 to 2026-11-19. It is the latest computed date of the features a search loads, and `hi-features compute` ran on 19 Nov.
     - Every value stays the same.
   - **What changes:** only the feature lists, with features added and none removed or changed:
     - municipio: 40 → 42 (`suelo_vacante_unidades`, `unidades_comerciales_1000hab`);
     - distrito: 4 → 8 (`comercio_proximidad_1000hab`, `edificabilidad_remanente_residencial_m2`, `locales_abiertos_1000hab`, `locales_cerrados_pct`);
     - barrio: 0 → 1 (`piloto_inversores_m40`).
3. **Golden:** 10/10, identical line by line ([deploy-37/golden-api.txt](deploy-37/golden-api.txt)).
4. **e2e:** 116/116 at 1440 px and 92/92 at 390 px, with 0 console errors ([report](deploy-37/e2e-report.json)).
5. **The investor routes** ([deploy-37/inversores-api.txt](deploy-37/inversores-api.txt)):
   - **`/investors/zones`:** 108 barrios. Not one field is null.
     - `remaining_m2` runs from 0 to 1,161,094 m² (0 in 58 barrios).
     - `remaining_shared_areas` runs from 0 to 2.
     - `commerce_per_1000` runs from 0,70 to 16,93.
   - **Pinar del Rey's sheet:** no warnings, and every one of A's features carries a value.
     - Plan General areas: 55.628 m², the 4 areas the web lists (26.322 + 2.802 + 25.975 + 529).
     - Vacant land: 13.813 units, «dato de toda la ciudad».
     - Shops: 3,22 local shops per 1,000 inhabitants; 21,61 open premises per 1,000; 40,1 % closed; 16,03 commercial units per 1,000.
     - The only null is the sheet's gap row of large homes (`viviendas_grandes_por_100_hogares_grandes`, `SOURCE_MISSING`). It was there before the sync too.
   - **Viability:** the same answers as before the sync. It reads no database.
   - **Errors:** 404 and 422 as before. The web pages give 200, and an unknown barrio gives 404.
6. **#94's `check-inversores.mjs` again:** 12/12 screens with 0 and 0, no overflow, axe 0 and 0 console errors ([deploy-37/check-inversores-produccion.json](deploy-37/check-inversores-produccion.json)).
7. **`check-ux-mobile.mjs` again:** 0 and 0 on the 24 screens, and axe 0. The report is identical to before the sync apart from its timestamp ([deploy-37/tamanos-produccion.json](deploy-37/tamanos-produccion.json)).
8. **Logs from 09:46:51 UTC,** right after the first window ([deploy-37/logs-despues-del-sync.txt](deploy-37/logs-despues-del-sync.txt)):
   - **Runtime:** 531 lines, all info. 0 `WARNING`, and 0 pool, authentication or traceback lines.
   - **CDN:** 1,641 records, the whole window. 0 5xx.
   - **4xx:** only this check's deliberate errors: 2 × 404 and 2 × 422.

## Screenshots
- **After the sync:**
  - [the pilot list, 390](deploy-37/390-01-lista.jpg);
  - [Pinar del Rey's sheet, 390](deploy-37/390-02-ficha.jpg);
  - [its land, with the Plan General areas and the vacant land, 390](deploy-37/390-04-suelo.jpg);
  - [the three scenarios with a land price, 360](deploy-37/360-05-escenarios-con-suelo.jpg);
  - [the calculator, 1440](deploy-37/1440-06-calculadora.jpg).
- **Before the sync:** [the land with «Sin dato», 390](deploy-37/390-03-suelo-antes-del-sync.jpg).

## For review, not blocking
1. **«Ver en el visor de la Comunidad» wraps into two lines at 390 px in the sheet's land cards** ([390](deploy-37/390-04-suelo.jpg)).
   - It is the same link as D-246's, which wrapped only at 360 px in the zone card (deploy-36). The sheet's card is narrower.
   - It is still a target over 44 px.
   - datamad-10 put it in Saturday's batch.
2. **Before a sync, the sheet's values that are not loaded yet come back with `mark: "dato"`, `value: null` and the source «Aún sin cargar».** The web shows «Sin dato», so nothing wrong reaches a person. A null with the «dato» mark is line A's or line B's call.

## Rollback
- **To `dpl_9KhiCQnJ8yVQdM8mQxUe4PGLBEZz` (747cb65):** code only.
- #95 has no migration. 747cb65's web and API never name the investor routes or A's new features (`git grep`).
- The synced rows would not be shown, and its feature lists would just carry 7 more entries. No rollback was tested.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
