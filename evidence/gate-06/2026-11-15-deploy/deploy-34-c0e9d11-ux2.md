# OPS-001 (line C) · deploy of c0e9d11, UX mobile 2 (#81, D-245) · 2026-11-15 (Madrid)

## What the deploy brings
- **#81, web:** the second delivery of the mobile clarity audit (option 2):
  - the essential list row: name, band in words, «Unos … € al mes» and «›»;
  - the essential zone card, with the rest behind «Ver más sobre…»;
  - the zone in the address (`?zona=`), with the back button and «Volver a la lista»;
  - the zone screen with «Más datos de la zona» folded;
  - the debt of delivery 1, including the old search's options after unmarking «Somos mayores».
- **#81, API, two texts (D-245 §7 and §9):**
  - «No comparable» says its real reason;
  - the trip to a family place or to «donde vivimos ahora» no longer says «a las 9:00».
  - Neither the contract nor the formula changes.
- **Web and API went together.** The web shows the API's «No comparable» sentence as it is.
- **No data sync.**

## Deploy · `dpl_7paGtjUZ1syEwCvfgxqUqY6KCBWm` · 21:31
- **CI:** green on c0e9d11, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-34/deploy-output.txt](deploy-34/deploy-output.txt).
- **Verification:** on round 1.
  - Round 0 passed 13/13, but 7 of its requests still came from the previous deployment, the usual domain switch.
  - In round 1, all 13 came from the new one.

## Verification, at 1440, 390 and 360 px
Details:
- the API: [deploy-34/search.txt](deploy-34/search.txt);
- the web: [deploy-34/web-checks.txt](deploy-34/web-checks.txt);
- the sizes: [deploy-34/tamanos-produccion.json](deploy-34/tamanos-produccion.json).

1. **Smoke and e2e:**
   - smoke 13/13, `fit-0.9`;
   - e2e **114/114** at 1440 px and **90/90** at 390 px, J5, J6 and J7 included, with 0 console errors and 0 px of horizontal overflow ([report](deploy-34/e2e-report.json)).
   - J5 now checks deploy-33's item 2: after unmarking «Somos mayores», the previous search's options are no longer offered, and none marks it again after searching.
   - A first e2e run, at the same time as the probe, gave 106/107 at 1440 px. J2 waited 30 s for `/gaps/municipio/28079` and the probe's Chromium crashed at 390 px; the logs have no 4xx or 5xx in that window. Run alone, it gave 114/114 and 90/90.
2. **The list:**
   - **At 390 and 360 px**, all 10 rows of both examples read only:
     - the name;
     - the band in words;
     - «Unos … € al mes», from the API;
     - «›».
   - No row has a %, a tie, m², «Dato aproximado» or «Distrito de», and there is no «Empatan» heading.
   - **At 1440 px**, the % comes small after the band: «Muy buena opción · 94 %».
   - **Above the list:**
     - «Hemos encontrado 42 zonas para vosotros.» and «Hemos encontrado 22 barrios para vosotros.»;
     - with «Solo/a», «Hemos encontrado 165 zonas para ti.» under «Zonas que te convienen».
3. **The card,** for Puente de Vallecas in the family example, identical at 1440, 390 and 360 px.
   - **The essentials:**
     - «‹ Volver a la lista»;
     - «Puente de Vallecas»;
     - «Distrito de Madrid · Muy buena opción»;
     - «Unos 1.129 € al mes · Precio orientativo»;
     - what was asked, with its minutes: colegio 4 min, bus 2 and metro 10, centro de salud 8 min, and «41 min … hasta Paseo de la Castellana (Azca), llegando a las 9:00»;
     - «No le falta nada de lo que buscáis.», with the green tick.
   - No % appears in the essentials.
   - **«Ver más sobre Puente de Vallecas» unfolds:**
     - the band with 94 % and «¿Qué es el %?»;
     - «La 1.ª que más os conviene»;
     - «Igual de buena que Latina (94 %).»;
     - the 5 facts of the API, each with its reliability;
     - the 2024 notice;
     - «Lo que le falta a esta zona»;
     - «Ver la zona».
4. **Honesty:**
   - **«Pareja jubilada», Casco Histórico de Barajas:**
     - «En Barajas, de lo que podemos comparar, no falta nada.», with an (i) and no green tick;
     - under it, «No sabemos si en Barajas faltan centros de salud o centros de mayores.», with a (?);
     - Barajas has centros de salud and centros de mayores CUBIERTO but `reliable: false`, and farmacias CUBIERTO;
     - no colegios and no escuelas infantiles.
   - **«Familia»:** «No le falta nada de lo que buscáis.», with the green tick.
     - The household's rows are colegio, centro de salud and farmacia, plus what is marked, and all three are CUBIERTO.
     - The children are 4 and 8, so the escuela infantil, FALTA in Puente de Vallecas, is not the household's: the age limit is 2.
   - **A couple without children who marks «Colegios»** («Alrededores de Madrid», 900 €):
     - Parla's card (1st, colegios JUSTO) says «Colegios: las aulas van justas para tantos niños.», with farmacias and centros de salud;
     - with «Colegios» unmarked, the same card (Parla 8th) says nothing of colegios.
     - No zone has FALTA of colegios today (0 of 179 municipios and 0 of 21 districts), so JUSTO is the only short status there is to check.
5. **Navigation, at 1440, 390 and 360 px:**
   - opening a row puts `/?zona=distrito/2807913` in the address;
   - the back button returns to `/` and gives the focus back to the row (`data-zone`);
   - forward opens the card again with `?zona=`;
   - «Volver a la lista» returns to `/` and closes the card;
   - `?zona=distrito/2800000`, `?zona=seccion_censal/2807901001` and `?zona=nada` go back to `/`, with no card and no error;
   - `?zona=distrito/2807921` opens Barajas;
   - **barrio to district:** the retired couple's Casco Histórico de Barajas (`?zona=barrio/28079213`) becomes `?zona=distrito/2807921`, and the card becomes «Barajas», after searching with «Toda la Comunidad».
6. **The zone screen,** `/zona/distrito/2807913`:
   - the essential card on top, with no %;
   - then «Los barrios que más os convienen»;
   - «Más datos de la zona» folded, holding «Otros datos de la zona», «Vivienda nueva y lo que viene» and «Entorno»;
   - «Volver a la lista» goes back to `/` with the list in view.
7. **A district's barrios:**
   - **The row:** «Palomeras Bajas · Muy buena opción · Unos 1.110 € al mes», with no % on the phone and with it at 1440 px.
   - **Tapped, it adds:**
     - «Muy buena opción · 94 %»;
     - «Igual de bueno que San Diego, Numancia y Entrevías (94 %).»;
     - «Alquiler: unos 1.110 € al mes por 77 m² · Dato aproximado»;
     - its facts.
8. **«No comparable»:**
   - **The API, with D-245 §7's sentence:**
     - Barajas, centros de salud: «No comparable: para la gente que vive aquí le corresponden menos de 4 centros de salud y, con números tan pequeños, no se puede saber si faltan.», then the same figures;
     - the same for centros de mayores in Barajas, centros de salud in Moratalaz, Villarejo de Salvanés's two rows, and La Acebeda's four service rows, colegios included.
   - **Housing:** La Acebeda keeps «aquí viven muy pocos hogares de 4 o más personas (1)».
   - «Qué falta» shows both sentences as the API sends them.
9. **The trip:**
   - **To family or home:** «27 min en transporte público hasta Ciudad Lineal (metro)», in the API (30 lines in each retired body) and in the card, with no «9:00» anywhere in it.
   - **To work:** still «41 min … hasta Paseo de la Castellana (Azca), llegando a las 9:00».
   - **Through the golden:** 10 lines lose «, llegando a las 9:00», those of the family place of `golden_senior` and the `other` place of `golden_reduced_mobility`. The 40 lines of work and study keep it.
10. **Measurement, with `apps/web/scripts/check-ux-mobile.mjs`:**
    - **0 texts under 16 px and 0 targets under 44 px** on all 12 screens, at 390 and 360 px: portada, the three forms, list, card, card with «Ver más», district, zone screen closed and open, «No comparable» and «Somos mayores» with a place.
    - The only exceptions are MapLibre's 3 attribution controls, on the portada and on the zone screen.
    - **axe: 0 incidents** in 9 states at 390 and 360 px, and at 1440 px in the list, the card with «Ver más» and the open zone screen.
    - **Things per row:** 4 at 390 and 360 px, 5 at 1440 px.
    - **Card things,** as first screen / whole / with «Ver más», the same as #81's evidence:

      | | 390 px | 360 px | 1440 px |
      |---|---|---|---|
      | Family | 12 / 12 / 48 | 12 / 12 / 48 | 12 / 12 / 48 |
      | Retired couple | 12 / 13 / 54 | 11 / 13 / 54 | 13 / 13 / 54 |

    - **Console:** 0 errors in every run: e2e, probes, measurement and shots.
    - **The pitch example does not change:** the same JSON byte for byte, with 42 of 199 zones, Puente de Vallecas 94 and Latina 94 tied, Usera 93, …, Leganés 90 tenth.
- **Screenshots:**
  - list: [title, 390](deploy-34/390-01-lista-titulo.jpg) · [rows, 360](deploy-34/360-01-lista-filas.jpg) · [1440](deploy-34/1440-01-lista.jpg);
  - card: [family, 390](deploy-34/390-02-tarjeta-familia.jpg) · [«Ver más», 390](deploy-34/390-03-tarjeta-ver-mas.jpg) · [retired couple, 360](deploy-34/360-04-tarjeta-jubilada.jpg) · [retired couple, 1440](deploy-34/1440-04-tarjeta-jubilada.jpg);
  - honesty: [Barajas, 390](deploy-34/390-05-honestidad-barajas.jpg) · [colegios in Parla, 390](deploy-34/390-06-colegios-parla.jpg);
  - zone screen: [folded, 390](deploy-34/390-07-pantalla-zona-plegada.jpg) · [1440](deploy-34/1440-07-pantalla-zona.jpg) · [a barrio tapped, 360](deploy-34/360-08-barrio-abierto.jpg);
  - «No comparable»: [Barajas, 390](deploy-34/390-09-no-comparable-barajas.jpg) · [La Acebeda's housing, 360](deploy-34/360-10-no-comparable-acebeda-vivienda.jpg).

## The API, before and after
Taken from e0417ae just before the deploy, then from c0e9d11, with the same requests: 11 search bodies, plus `/gaps` of the 21 districts and 10 municipios. The comparison leaves out `meta`.
- **9 bodies and 27 zones are identical.**
- **Every other difference is one of the two expected texts.** 0 are unexpected.
  - **«a las 9:00»:** 30 per retired body (with and without `seniors`).
  - **«No comparable»:**
    - Barajas 2, Moratalaz 1, La Acebeda 4 and Villarejo de Salvanés 2.
    - The rest of each sentence (figures, references) is the same.
  - Zones, %, `match_band`, order, «casi», Reality Check, statuses and `reliable` do not change.
- **The golden through the public API** ([deploy-34/golden-api.txt](deploy-34/golden-api.txt)) is deploy-33's except for those 10 trip lines.

## Logs, 20:29–20:52 UTC
Details in [deploy-34/logs-summary.txt](deploy-34/logs-summary.txt).
- **Runtime:** 1,485 lines, all info, with 9 instances started.
  - 0 `WARNING`;
  - 0 pool, prepared-statement, authentication, validation or traceback lines.
- **CDN:** 0 4xx and 0 5xx.
  - The listing stops at 2,000 records, so a separate `httpStatus >= 400` query covered the whole window. It returned nothing.
- **The previous deployment:**
  - its only 4xx are the five deliberate 422 of the baseline (20:26, `/gaps/barrio/…`, a level `/gaps` does not serve, `vida-facil-smoke/base`);
  - it got no request after 20:30:58.

## For review, not blocking
1. **Wording.** Production says «En Barajas, de lo que podemos comparar, no falta nada.» and «No sabemos si en Barajas faltan…», as D-245 §3–4 and `essentials.ts` write them. The instruction said «no le falta nada» and «le faltan».
2. **#81's evidence says the golden's places are all of work.** Two are not: the family place of `golden_senior` and the `other` place of `golden_reduced_mobility`. Their trip lines lose «a las 9:00», which is the new rule. Only the evidence's sentence is off.
3. **A tapped barrio repeats the row.** Its panel says the band and the price again («Muy buena opción · 94 %», «Alquiler: unos 1.110 € al mes por 77 m²») right under the row that already says them. For line B, if it is worth trimming.
4. **The «No comparable» tag's screen-reader help** is still the shared sentence («…muy pocos centros (menos de 4), o en la vivienda viven muy pocos hogares…») on every row. The visible text is the row's own. For line B.

## Rollback
- **To `dpl_ByScLXFa…` (e0417ae):** code only, and no data changed.
- The API's two texts go back with it.
- A `?zona=` link opens the portada without the zone.
- D-241 §9 still applies before `dpl_G26vdu…`.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
