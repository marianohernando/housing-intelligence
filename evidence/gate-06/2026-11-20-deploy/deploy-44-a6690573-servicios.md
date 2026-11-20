# OPS-001 (line C) · deploy of a6690573 (the code of 1677f515): services and supplies, catalogue, first filter (#110, D-253) · 2026-11-20 (Madrid)

**Status:** in production and verified.
- The four demo sheets come out complete and are in the CDN.
- The services, catalogue and first-filter sections show what D-253 says.
- `check-parcela` 21/21, `check-inversores` 12/12, and the e2e 145/145 and 121/121.

**Pending:** the registry sync, for `/api/v1/datasets` only. datamad-10 moved it to Saturday's batch.

## What was deployed, and why a6690573
- **1677f515 is the merge of #110 (D-253).**
  - Its CI was cancelled in `integration`, because the merge of #116 (a6690573) landed right after it. The other four jobs had passed.
- **a6690573 is 1677f515 plus deploy-43's evidence (#116) and its board row.** The code is the same.
  - Its CI is green in all five jobs, so a6690573 is what was deployed.
- **#110, D-253:**
  - **«4. Servicios y suministros»:**
    - «solar» as a legal condition;
    - a power estimate from the buildable m² (ITC-BT-10), with the transformer notice above 100 kW (RD 1048/2013, art. 26.1) or art. 25.1 below it;
    - only a link to the CNMC's capacity map;
    - Canal de Isabel II;
    - a glossary.
  - **The catalogue of protected buildings:** EDIFICIOS_PROTEGIDOS layer 5, read live, bounded by the sheet's deadline; a failure degrades only `catalog`.
  - **The existing building notice.**
  - **The first filter:** «Lo que añade un estudio completo» and «Llévate esta ficha (PDF) a tu consultora».
  - **The ICIO citation** without the ordinance number.
  - **New catalogue entries:** the datasets `ayto_edificios_protegidos` and `cm_costes_referencia_edificacion`, and the source `cnmc_capacidad_redes`.
- **No migration and no new variable.**

## The registry sync: pending
- **What depends on it:** `/api/v1/datasets` reads `dataset_registry` and `source_registry` from the database. It still lists 59 datasets, without D-253's two new datasets and its new source.
- **What does not:** the parcel sheet cites `ayto_edificios_protegidos` (300158) from code.
- **Why not tonight** (datamad-10's decision): `scripts/supabase_sync.sh` truncates 11 production tables, `feature_value` among them, and then copies in a separate command, so a failed copy would leave production empty.
- **Saturday's plan, prepared by datamad-10:**
  1. load the catalogue into the local registry;
  2. compare the 11 tables' counts, local against production;
  3. if possible, a profile that syncs only the registry, in one transaction;
  4. the sync, then the full smoke.

## Deploy · `dpl_5udnLokddKKNCueMzPiwnPsrvQXX` · 01:46
- **CI:** green on a6690573, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-44/deploy-output.txt](deploy-44/deploy-output.txt).
- **Verification:** on round 1.
  - In round 0, 2 of the 13 smoke requests still came from d29e8416's deployment.
  - In round 1, all 13 came from the new one.
- **Disk:** the build is remote. Free disk stayed at about 6.3 GB.

## Verification, 00:38–00:53 UTC
1. **Smoke:** 13/13, `/search` included.
2. **API:** 54 of 55 answers identical to d29e8416's without `meta`: deploy-43's 54 and `/api/v1/datasets` ([deploy-44/search.txt](deploy-44/search.txt)). The one that changes is Pinar del Rey's sheet, only in the ICIO citation:
   - before: «Ordenanza fiscal 7/2023, art. 25»;
   - after: «ordenanza fiscal del ICIO, art. 25, en el Libro de Ordenanzas Fiscales 2024, p. 154».
3. **Golden:** 10/10 through the public API, identical line by line to before the deploy ([deploy-44/golden-api.txt](deploy-44/golden-api.txt)).
4. **The four demo sheets, warmed by reference once each** ([deploy-44/parcelas-en-vivo.txt](deploy-44/parcelas-en-vivo.txt)):
   - all four `degraded=-`, `public, max-age=3600`, and the second visit «HIT» in 0.10–0.22 s;
   - **the timing lines:**

     ```
     2122202VK4722A ms=9689  stages=catastro:381,planning:9103,catalog:442,instrument:444,z:6215,layer3:9102
     3959601VK4735H ms=9111  stages=catastro:757,planning:8217,instrument:176,catalog:295,layer3:5791,z:8215
     0390314VK4709A ms=10159 stages=catastro:751,planning:9285,instrument:125,catalog:219,z:285,layer3:9285
     9943003VK3794D ms=7707  stages=catastro:986,planning:6601,catalog:235,instrument:237,z:254,layer3:6601
     ```

   - **The catalogue layer** takes 219–442 ms and never degraded. The slow part is still sigma's layer 3 and Z when cold, 5.8–9.3 s.
5. **«4. Servicios y suministros», on screen at 360, 390 and 1440 px, from the CDN** ([deploy-44/d253-produccion.json](deploy-44/d253-produccion.json)). The three widths say the same.
   - **Méndez Álvaro:**
     - «Obras de urbanización del APR.02.06: finalizado, según el Ayuntamiento.»
     - **The estimate, marked «Supuesto»:** «Con unas 164 viviendas (…), la previsión de potencia es de al menos 499,1 kW: 5,75 kW por vivienda (electrificación básica) por el coeficiente de simultaneidad de la ITC-BT-10 (…) (86,8 para 164 viviendas). Sin servicios comunes ni garaje, que se suman aparte.»
     - **The transformer notice:** «Por encima de 100 kW, el edificio tiene que reservar un local para un centro de transformación de la distribuidora (RD 1048/2013, art. 26.1). Y la extensión de red la paga quien pide el suministro (art. 25.2): solo hasta 100 kW en baja tensión, en suelo urbanizado, la hace la distribuidora y cobra los derechos de extensión (art. 25.1).»
     - **The rest of the section:**
       - the substation and CUPS sentence (i-DE or UFD);
       - «Ver el mapa de capacidad de demanda de la CNMC», only the link, with no figure;
       - Canal de Isabel II's «10 días laborables, «siempre que exista una red adecuada»»;
       - the glossary «Palabras y plazos de los suministros»: CUPS, Acometida, Derechos de acometida, Quién paga la red, Centro de transformación, Plazos de la norma.
   - **Mayor 61:**
     - «Norma zonal: suelo urbano común o consolidado (…) (Normas Urbanísticas, arts. 3.1.4 y 3.2.2).»
     - **The estimate, marked «Supuesto»:** «Con unas 3 viviendas (…), al menos 17,3 kW (…) (3,0 para 3 viviendas).»
     - **No transformer notice.** Instead: «Hasta 100 kW en baja tensión, en suelo urbanizado, la extensión de red la hace la distribuidora y cobra los derechos de extensión (RD 1048/2013, art. 25.1).»
     - The same CNMC link, Canal sentence and glossary as Méndez Álvaro.
   - **Almería 1 and Luis Misson:** no power estimate, since they have no buildable m² to start from. Same CNMC link, Canal sentence and glossary.
6. **The catalogue:**
   - **Mayor 61:**
     - in «Planeamiento»: «Catálogo de edificios protegidos: Protección parcial, nº 02933 (nivel 3 de 3)»;
     - the notices, on screen at 360 and 1440 px ([deploy-44/mayor-avisos-produccion.json](deploy-44/mayor-avisos-produccion.json)):
       - «Edificio catalogado por el Plan General, protección parcial (nº 02933): se protegen elementos concretos. En ruina, se puede rehabilitar o derribar, pero la licencia puede obligar a mantener esos elementos en el edificio nuevo (Normas Urbanísticas, arts. 4.3.4 y 4.3.7). La cuenta de obra nueva sobre suelo libre no vale tal cual.»
       - «Hay un edificio de 376 m² construidos (de 1890), con 6 inmuebles en división horizontal. La calculadora es de obra nueva sobre suelo libre: no cuenta el derribo, el desalojo ni la compra a los propietarios de sus inmuebles.»
     - «Fuentes y avisos» links dataset 300158.
   - **Méndez Álvaro, Luis Misson and Almería 1:** «No aparece en el catálogo en el punto de referencia de la parcela». Their sources also cite 300158, which is cited whenever the layer is read (review of #110, R-06).
7. **The first filter, on all four sheets:**
   - the sentence at the top, «Esto es un primer filtro de minutos, gratis y con fuentes. No sustituye al estudio de viabilidad…»;
   - the section «Lo que añade un estudio completo», with contaminated soils (Real Decreto 9/2005);
   - «Llévate esta ficha (PDF) a tu consultora»: **it appears twice** on every sheet. It is known, and will be fixed on Saturday.
8. **Print:**
   - after `beforeprint`, as Chrome's print does, 6 of 6 `<details>` of the sheet are open on all four sheets;
   - Mayor 61's PDF (A4, from Chromium) has 32 pages.
   - **Why the PDF is not in this evidence:** it carries the link in the site's footer to the code repository, whose URL has a surname. The page count and the open breakdowns are in [deploy-44/d253-produccion.json](deploy-44/d253-produccion.json).
9. **`/como-lo-calculamos#inversores`:** the ICIO without «7/2023».
10. **The scripts against production:**
    - `check-parcela`: **21/21** ([report](deploy-44/check-parcela-produccion.json)). It covers the search, its states, the 4 sheets and the print view, at 360, 390 and 1440 px.
    - `check-inversores`, now with 360 px: **12/12** ([report](deploy-44/check-inversores-produccion.json)).
    - On every screen: 0 texts under 16 px, 0 targets under 44 px, no horizontal overflow and axe 0.
11. **e2e:** **145/145** at 1440 px and **121/121** at 390 px, with 0 console errors ([report](deploy-44/e2e-report.json)).
12. **Live lookups: 7 of the 12 allowed.**
    - What they were: the 4 sheets by reference and check-parcela's 3 address boxes.
    - 36 sheet reads of this run came from the CDN, and so did the unidentified visitor's one.
13. **Logs from 00:44 UTC** ([deploy-44/logs.txt](deploy-44/logs.txt)):
    - **Runtime:** 515 lines, all info, with 9 instances started. 0 `WARNING`, and 0 pool, authentication or traceback lines.
    - **The timing lines:** the 4 `parcel input=` lines and the 3 `parcel candidates=` lines.
    - **No coordinates and no typed text:** no line has `lat=` or `lon=`. The 3 address boxes say `q=[redactado]`, and the typed text never appears.
    - **CDN:** 2,273 records, the whole window (2 pages of the listing), every one from the new deployment.
      - **0 5xx:** 200 × 2,167, 304 × 105, and one 499 (a static chunk the probe cancelled when it navigated).
      - **WAF:** all `allow`.
    - **«Visitante sin identificar (Chrome/Mac)»:** at 00:51:21–00:53:05 UTC, a Chrome browser on a Mac. Who it was is not known.
      - It visited the map, «Qué falta», «Cómo lo calculamos», «Inversores» and 3 parcel sheets.
      - It sent 3 Web Analytics page views.
      - Its one parcel-sheet API request was a CDN «HIT», and it typed no address.
      - A client on Windows also asked for 2 sheet pages without running their JavaScript, probably a link preview.
      - Their references are not shown.

## Screenshots in production
- [1440 px: Méndez Álvaro's «4. Servicios y suministros», 164 homes, 499,1 kW and the transformer notice](deploy-44/1440-mendez-alvaro-servicios.jpg)
- [360 px: the same](deploy-44/360-mendez-alvaro-servicios.jpg), reduced to 2,000 px high
- [1440 px: Mayor 61's services, 3 homes and 17,3 kW, art. 25.1](deploy-44/1440-mayor-servicios.jpg)
- [1440 px: Mayor 61's «Planeamiento» with «Protección parcial, nº 02933 (nivel 3 de 3)»](deploy-44/1440-mayor-catalogo.jpg)

## For review
1. **The registry sync is pending:** `/datasets` has 59 entries, without D-253's two datasets and one source. It goes to Saturday's batch, with datamad-10's plan.
2. **«Llévate esta ficha (PDF) a tu consultora» appears twice** on every sheet. It is fixed on Saturday.
3. **A first lookup still takes 7.7–10.2 s,** because of sigma's layer 3 and Z when cold.
   - **Before the demo:** open the 4 demo sheets after any deploy. They are warm now, for a day.
4. **The CI of 1677f515** has a cancelled job, because the next merge superseded it. a6690573, which carries the same code, is green in all five.

## Rollback
- **To `dpl_94jjgL9uoCocQcfFajZtbZMpsmL3` (d29e8416):** code only, with no data and no variable to undo.
- A rollback removes the services, catalogue and first-filter sections, and brings back the ICIO's «7/2023».
- No rollback was tested.

## Not done
- **The registry sync:** pending, as above.
- **The offline package** was not rebuilt. It is still at 39644a9.
