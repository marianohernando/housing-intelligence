# OPS-001 (line C) · deploy of 59187f8, batch 4, and its sync · 2026-11-15 (Madrid)

## What the batch brings
- **#67:** new housing, D-241.
- **#68:** Web Analytics.
- **#70:** polish (hospital pills, beds, m², «Cerca, pero no alcanza para todos»).
- **#71:** SERPAVI rent, D-242.
- **#65:** «Entorno», D-237.

## Order
1. Deploy the code.
2. Verify with the data Supabase had then.
3. datamad-10 recalculated `housing` (golden 10/10) and ran `make supabase-sync PROFILE=demo` from 59187f8. There were no migrations.
4. Verify again, now with the data.

## Deploy · `dpl_G26vduZvm6kATEGzMoyHjv1ftfM7` · 12:10
- **CI:** green on 59187f8, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-31/deploy-output.txt](deploy-31/deploy-output.txt).
- **Verification:** on round 1.
  - Round 0: 6 of the 13 smoke requests still came from `dpl_25dWq…`, the usual switch-over window.
  - Round 1: 13/13 from the new deployment.

## Before the sync
Search details are in [deploy-31/search.txt](deploy-31/search.txt), and the web checks in [deploy-31/web-checks.txt](deploy-31/web-checks.txt).
- **Smoke and e2e:**
  - smoke 13/13;
  - e2e 70/70 at 1440 px and 44/44 at 390 px, with the new check that the example sends `min_floor_area_m2: null` ([report](deploy-31/e2e-report-presync.json)).
- **Searches:** the example, buying 400.000 €, telework, renting 10.000 €/month and «Pueblos» are identical to 785bac0. The only addition is the new field `estimated_cost_range`, which is `null` in every zone.
  - The example gives 27 of 199, with Latina, Moratalaz, Ciudad Lineal and Puente de Vallecas at 98 %. «Casi» is Chamartín, Salamanca, Centro, Chamberí and Retiro.
- **Other endpoints:** all 200 ([deploy-31/endpoints-presync.txt](deploy-31/endpoints-presync.txt)).
  - They cover `/places`, `/gaps` (municipio, district and impact), `/features` (context, leisure, hospitals and safety), `/datasets` and the barrio outlines.
  - `/datasets` lists the same 38 datasets, 29 of them CM.
- **Hidden, as expected,** at both widths:
  - no «Entorno» and no «Vivienda nueva y lo que viene», in Moncloa-Aravaca or in Pozuelo;
  - no «Aparcamientos» button;
  - «Pueblos» keeps the D-238 text («Casi ninguno publica su alquiler…»).
- **Visible from #70,** at both widths:
  - **Hospital rows:** the pill comes first («Público» filled, «Privado» outlined, each with its icon), then the name. «Gestión privada» goes under the Fundación Jiménez Díaz.
  - **Beds:** an icon and the number. The visible number is `aria-hidden`, so the screen reader hears «651 camas instaladas» once.
  - **«¿Qué significa público y privado?»:** present and folded.
  - **m²:** «Para unos 77 m² (cámbialo)» opens 24 options: «Lo normal para tu hogar (77 m²)», then 40 to 150 m² in steps of 5. The Census help shows under it.
  - **Latina's card** after the example: «Centro de salud a unos 10 min andando, pero van justos para tanta gente: por eso sale JUSTO.»
  - Screenshots: [hospitals 1440](deploy-31/presync-1440-3-hospitales.jpg) · [hospitals 390](deploy-31/presync-390-3-hospitales.jpg) · [m² 390](deploy-31/presync-390-2-m2.jpg) · [Latina](deploy-31/presync-1440-1-latina-cerca-pocas.jpg).
- **Web Analytics** ([deploy-31/analytics.txt](deploy-31/analytics.txt)):
  - `/_vercel/insights/script.js` answers 200.
  - The page loads the same script, 2,076 B, from the project's own path `/c701312a495cf1d6/script.js`, with 200 at 1440 and at 390.
  - Headless Chromium sent no page-view beacon. Whether visits are counted is for the Vercel dashboard.
- **Console:**
  - The home page and `/que-falta` have 0 errors.
  - The zone views show only «Failed to load resource: 404» for the 9 features of D-237 and D-241 that had no data yet. That is what hid their blocks.
- **Logs:** 0 `fit bindings ignored` and 0 `WARNING`.

## After the sync
- **Supabase** ([deploy-31/supabase-postsync.txt](deploy-31/supabase-postsync.txt)):
  - the counts match datamad-10's: `source_registry` 16, `dataset_registry` 61, `dataset_version` 73, `metric_registry` 48, `feature_registry` 68, `place_master` 41,686, `feature_value` 119,135, and 216 MB;
  - `/datasets` goes from 38 to **52** datasets, of which **35** are CM (29 before).
- **Smoke and e2e:** smoke 13/13 ([deploy-31/smoke-postsync.txt](deploy-31/smoke-postsync.txt)); e2e 70/70 and 44/44 ([report](deploy-31/e2e-report-postsync.json)).
- **The example:** **42 of 199, with 0 «sin datos»**. Before the sync it was 27 and 15.
  - **The order does not change.** The top 10 and «casi» have the same order, %, costs and facts.
  - «+5 min a pie hasta colegio» now adds 49 (it added 17).
  - 110 municipios that fail the school condition rise 1 to 7 points; D-242 says 111. The other 74 zones that had a % keep it.
  - The 15 zones that had no data now fit, all of them villages, among them Villanueva del Pardillo, Velilla de San Antonio and Casarrubuelos.
- **The other cases:**
  - **Buying 400.000 €:** identical to before the sync (41 zones), apart from `datasets` and the range field.
  - **Telework:** 42 zones, with villages among the first.
  - **Renting 10.000 €/month:** 183 zones (57 before), with the same D-239 top 10.
- **«Pueblos», a couple renting up to 1.500 €:**
  - **122 of 138** fit, 16 without data, and **181** in «Toda la Comunidad».
  - The help is now D-242's: «Su alquiler es la referencia del Ministerio de Vivienda, un dato aproximado; …».
  - The list reads «16 de los 138 pueblos salen «Sin datos», sobre todo porque tienen tan pocas viviendas alquiladas…», and none of the D-238 wording is left.
  - Casarrubuelos's card shows «Alquiler ≈ 571 €/mes» with «Dato aproximado».
  - Under it, on its own line: «La mitad de los contratos, entre 500 y 790 €/mes», then «Elaboración propia a partir del Ministerio de Vivienda (SERPAVI), 2024».
  - Screenshots: [1440](deploy-31/postsync-1440-1-pueblo-alquiler.jpg) · [390](deploy-31/postsync-390-1-pueblo-alquiler.jpg).
- **Sol is filled.** With «Madrid capital» and a couple at 1.500 €: ≈ 1.490 €/month, confidence 0.7, range 1.080–1.820 €, «media de sus 7 secciones censales».
- **«Entorno»:**
  - **Usera:** «Calles con ruido alto: 14 % de las calles de día, 32 % de noche». The NO₂ line reads «21,2 µg/m³ en la estación de Méndez Álvaro, la más cercana de su zona de calidad del aire, a 2,7 km». It also has a public car park about 13 min away and 2 park-and-ride car parks.
  - **Getafe:** the noise line reads «sin dato publicado», and the air line «25,6 µg/m³ en la estación de tráfico de Getafe».
  - **Fuencarral-El Pardo:** «4 aparcamientos disuasorios en Fuencarral-El Pardo (de 1 no consta si es gratuito)».
  - **Torrejón de Velasco:** noise «sin dato publicado», and air from Valdemoro, the nearest in its air quality zone.
  - Screenshots: [Usera 1440](deploy-31/postsync-1440-2-entorno-usera.jpg) · [Usera 390](deploy-31/postsync-390-2-entorno-usera.jpg) · [Getafe](deploy-31/postsync-1440-2-entorno-getafe.jpg).
- **«Vivienda nueva y lo que viene»:**
  - **Madrid districts (Usera, Fuencarral-El Pardo):** the city's sales and appraisal figures, labelled «La fuente no lo da por distritos», and the Plan General areas.
  - **Getafe:** «Plan Vive, 864 viviendas … en entrega».
  - **Torrejón de Velasco:** «Plan Vive, 41 viviendas de alquiler asequible en obras (c/ Carmen Tagle)».
  - Screenshot: [Torrejón de Velasco](deploy-31/postsync-1440-3-vivienda-nueva-torrejon_velasco.jpg).
- **«Aparcamientos»** in «Todos los centros», Fuencarral-El Pardo:
  - the button now shows: «Aparcamientos 24»;
  - «Ninguno», then «Todos», leaves it off;
  - pressed, it turns on;
  - with Colegios turned off, «Todos» turns Colegios back on and leaves Aparcamientos on. With all 7 services on, «Todos» is disabled.
  - Screenshots: [1440](deploy-31/postsync-1440-4-aparcamientos.jpg) · [390](deploy-31/postsync-390-4-aparcamientos.jpg).
- **Counter and footer:**
  - the counter reads «Datos: 35 conjuntos de la Comunidad de Madrid (con los del CRTM) + Ayuntamiento de Madrid + Ministerio de Sanidad + Agencia Tributaria + Ministerio de Vivienda»;
  - the independence line reads «Vida Fácil no es un servicio de … ni del Ministerio de Vivienda».
- **Console:** 0 errors at both widths. The 9 404s are gone.

## Logs, 11:07–11:26 UTC, through the sync
Details in [deploy-31/logs-summary.txt](deploy-31/logs-summary.txt).
- **Runtime:** 825 lines, all info, with 7 instances started.
  - 0 `fit bindings ignored`, 0 `WARNING`, and 0 pool, prepared-statement, authentication, validation or traceback lines.
- **CDN 4xx/5xx,** asked for apart because the full listing stops at 2,000 records: **43**.
  - All 43 are this check's own requests before the sync (11:12–11:16), to the 9 features of D-237 and D-241.
  - **None after 11:17.** No 5xx.

## Also in this PR
`git apply` of datamad-10's patch to 4 Silver manifests:
- `ayto_aparcamientos_residentes`, `ayto_calidad_aire_estaciones` and `cm_calidad_aire_estaciones` go to `places-1.8.1`;
- `cm_valor_tasado_vivienda_antiguedad` goes to `stat_tables-1.1.0`;
- each one's `retrieved_at` is updated.

These are the parser versions of the recalculation. The unit tests of the directory and station pipelines and `tests/data` pass (128).

## For review, not blocking
1. **A village's name breaks mid-word in its card at 1440 px.** Casarrubuelos reads «Casarrubuelo / s» next to the «100 %» badge ([screenshot](deploy-31/postsync-1440-1-pueblo-alquiler.jpg)).
2. **`pitch/guion.md:104` still says «27 conjuntos»;** the screen now says 35.

## Rollback
**After this sync, D-241 §9 applies:** no rollback to `dpl_25dWq…` or earlier without first removing D-241's 5 `feature_registry` rows and its dataset versions. Otherwise `/datasets` and the counter cite CM datasets that the old web does not show.
- D-237 and D-242 alone would allow the rollback without touching data.
- The D-233 and D-236 rules still apply before ad4a8f2.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
