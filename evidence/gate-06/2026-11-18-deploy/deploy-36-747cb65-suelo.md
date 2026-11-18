# OPS-001 (line C) · deploy of 747cb65: F7 web debt (#88) and public land for housing (#89, D-246) · 2026-11-18 (Madrid)

## What the deploy brings
- **#88, F7 web debt (D-245 §13):**
  - «Tarda 1 min más…», never «unos 1 min»;
  - «Somos mayores» with «Solo/a» speaks to one person;
  - one barrio panel at a time;
  - a shared link relabels the home place.
- **#89, D-246:**
  - «Suelo público para vivienda» in «Vivienda nueva y lo que viene», inside «Más datos de la zona», with its parcels in a folded list and a link to the Comunidad's map viewer.
  - In the API, `ContextItem` gains four optional fields (`parcel`, `regime`, `manager`, `url`). They are left out when empty, so the other items keep their bytes.
  - The data is the new feature `suelo_publico_vivienda_m2`, loaded by datamad-10's sync. There are no migrations.
- **Order:**
  1. the code, verified with the old data;
  2. the sync;
  3. a second verification.
- **Next 16.4.2:** Vercel built it with no error, so Next was not touched.

## Deploy · `dpl_9KhiCQnJ8yVQdM8mQxUe4PGLBEZz` · 23:04
- **CI:** green on 747cb65, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-36/deploy-output.txt](deploy-36/deploy-output.txt).
- **Verification:** on round 0. All 13 smoke requests came from the new deployment.

## 1. With the old data, 22:05–22:14 UTC
1. **Smoke:** 13/13, `/search` included (the example gives 42 of 199, Puente de Vallecas 1st).
2. **API:** 51 answers identical to 55651c2's, without `meta`. Details in [deploy-36/search.txt](deploy-36/search.txt).
   - They are:
     - 11 search bodies;
     - `/gaps` of 21 districts and 10 municipios;
     - the feature list at 3 levels;
     - 6 value answers of context features.
   - `suelo_publico_vivienda_m2/values` answers 404 at municipio and distrito, before and after the deploy.
3. **Golden:** 10/10 through the public API, identical line by line to deploy-34's.
4. **e2e: 115/116 at 1440 px and 91/92 at 390 px** ([report](deploy-36/e2e-antes-del-sync.json)).
   - In both runs the only failure is «no browser console errors» in J6. Chromium logs as a console error the 404 of `/api/v1/features/suelo_publico_vivienda_m2/values`, which has no rows until the sync.
   - The web handles it: a `console.warn`, and the line is hidden.
   - Every other check passes, including `nearMissLine`, which now rejects «unos 1 min».
5. **`check-ux-mobile.mjs`:**
   - 0 texts under 16 px and 0 targets under 44 px on 24 screens (12 at 390 px, 12 at 360 px), apart from the map's 3 attribution controls;
   - axe 0;
   - the counts are deploy-35's.
6. **#88, at 1440, 390 and 360 px.** Both notes left in deploy-35 are closed.
   - The family example with «Tardar como mucho» 45 min shows «Casi valen»: «Tarda 1 min más de lo que pedís», then «Tarda unos 6 / 11 / 8 / 6 min más…».
   - For «Solo/a» with «Somos mayores»: «¿Cerca de dónde quieres vivir? (opcional)», with «Donde vivo ahora», «Cerca de mi familia» and «¿Dónde vives ahora?».
7. **#89 before the sync:** Vicálvaro, Majadahonda and Puente de Vallecas show «Vivienda nueva y lo que viene» without the land line, and the rest of the card as before. Details in [deploy-36/web-checks.txt](deploy-36/web-checks.txt), part 1.
8. **Logs** ([deploy-36/logs-antes-del-sync.txt](deploy-36/logs-antes-del-sync.txt)):
   - **Runtime:** 1,090 lines, all info, with 7 instances started. 0 `WARNING`, and 0 pool, authentication or traceback lines.
   - **CDN:** 0 5xx.
   - **4xx:** 24, all the 404 of `suelo_publico_vivienda_m2/values`, from these checks and from browsers.

## The sync (datamad-10)
`make supabase-sync PROFILE=demo` returned rc 0. As datamad-10 reported it, the remote now has:
- `feature_value` 119,466 (+331);
- `feature_registry` 69;
- `dataset_version` 74;
- `metric_registry` 49;
- 216 MB in total.

## 2. After the sync, 22:16–22:24 UTC
1. **Smoke:** 13/13 ([deploy-36/smoke-despues-del-sync.txt](deploy-36/smoke-despues-del-sync.txt)).
2. **API** ([deploy-36/search.txt](deploy-36/search.txt)):
   - **Unchanged:** the 11 searches, the 31 `/gaps` and the other feature answers. D-246 never scores.
   - **What changes:**
     - `features?level=municipio` lists 40 features instead of 39, with `suelo_publico_vivienda_m2` added and none removed;
     - its values answer 200.
   - **Vicálvaro:** 67,808.3 m², 16 parcels, all with the viewer link.
   - **Majadahonda:** 29,312 m², 101 parcels.
   - **Puente de Vallecas:** 0 m² and 0 parcels, a confirmed 0.
   - **The whole region:** 29 municipios with 291 parcels; at distrito level, 7 of Madrid's districts with 38 parcels.
3. **Golden:** 10/10, identical line by line ([deploy-36/golden-api.txt](deploy-36/golden-api.txt)).
4. **e2e: 116/116 at 1440 px and 92/92 at 390 px**, with 0 console errors ([report](deploy-36/e2e-report.json)).
5. **#89's `capture-portal-suelo.mjs` against production: 82/84** ([capturas-suelo-produccion.json](deploy-36/capturas-suelo-produccion.json)). The run adds 360 px to the script's 1440 and 390 px.
   - **Vicálvaro:**
     - «Suelo público para vivienda: 16 parcelas, 67.808 m² edificables.»;
     - «Portal del Suelo 4.0 de la Comunidad de Madrid, en su portal de datos abiertos, a 18 de noviembre de 2026.»;
     - «Ver las 16 parcelas», folded;
     - open, 16 «Ver en el visor de la Comunidad» links, each in a new tab, and a régimen only when the Comunidad explains its code.
   - **Majadahonda:** «101 parcelas, 29.312 m² edificables», and 101 links.
   - **Puente de Vallecas:** no line, and never «0 parcelas».
   - **Every zone at every width:**
     - no text under 16 px or target under 44 px in the card;
     - no alarm red;
     - axe 0 with the list open;
     - nothing in the essential card.
   - **The 2 failures are at 360 px only,** a width the script never had (Vicálvaro and Majadahonda).
     - «Ver en el visor de la Comunidad» wraps into two lines, 268 × 77 px; the check expects one line, 44 to 60 px high.
     - At 390 px it is one line, 289 × 50 px.
     - It is still a target over 44 px, readable, with its icon after the text and the same accessible name.
6. **Morata de Tajuña,** the only zone with a parcel whose buildable m² is not published:
   - «Suelo público para vivienda: 1 parcela.»;
   - «De alguna parcela no se publica la superficie edificable.»;
   - «Ver la parcela», then «Superficie edificable sin publicar · En venta · Ayuntamiento de Morata de Tajuña»;
   - 0 console errors.
7. **`check-ux-mobile.mjs` again:** 0 and 0 on the 24 screens, and axe 0. Every screen's sizes and the counts are identical to before the sync ([deploy-36/tamanos-produccion.json](deploy-36/tamanos-produccion.json)).
8. **Logs from 22:16 UTC** ([deploy-36/logs-despues-del-sync.txt](deploy-36/logs-despues-del-sync.txt)):
   - **Runtime:** 798 lines, all info. 0 `WARNING`, and 0 pool, authentication or traceback lines.
   - **CDN:** 0 4xx and 0 5xx. The listing stops at 2,000 records, so a separate `httpStatus >= 400` query covered the window. It returned nothing.

## Screenshots
- **After the sync:**
  - Vicálvaro: [the line, 390](deploy-36/390-01-vicalvaro-linea.jpg) · [the open list, 390](deploy-36/390-02-vicalvaro-lista.jpg) · [the card, 1440](deploy-36/1440-02-vicalvaro.jpg);
  - Majadahonda: [390](deploy-36/390-03-majadahonda.jpg) · [the open list, 1440](deploy-36/1440-03-majadahonda-lista.jpg);
  - [Puente de Vallecas without the line, 390](deploy-36/390-04-puente-de-vallecas-sin-linea.jpg);
  - [the viewer link in two lines, 360](deploy-36/360-05-visor-en-dos-lineas.jpg);
  - [Morata without the m², 390](deploy-36/390-06-morata-sin-superficie.jpg).
- **#88:** [«Tarda 1 min más», 390](deploy-36/390-07-casi-valen-1-min.jpg) · [«¿Cerca de dónde quieres vivir?» for one older person, 360](deploy-36/360-08-mayor-sola-cerca-de.jpg).

## For review, not blocking
1. **«Ver en el visor de la Comunidad» wraps into two lines at 360 px.**
   - It is not a size problem: it is still over 44 px.
   - Line B could keep it on one line (a shorter text, or the icon with no break), or accept the two lines and relax the check.
2. **Morata de Tajuña says «De alguna parcela no se publica la superficie edificable.» with a single parcel.** «De esta parcela…» would fit one parcel better. That is line B's call.
3. **Before a sync, a new context feature fails the e2e's console check.**
   - The web hides the line, but Chromium logs the 404. It happened the same way on 14 Nov.
   - It is expected in the window between the deploy and the sync, which follows the rule of code first, then data.

## Rollback
- **To `dpl_F5vfeRz1…` (55651c2):** code only.
- 55651c2's web and API never name `suelo_publico_vivienda_m2` (`git grep`). The synced rows would not be shown, and its feature list would just carry one more entry. No rollback was tested.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
