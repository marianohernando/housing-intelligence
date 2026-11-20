# OPS-001 (line C) · deploy of d29e8416: the plan's uses preloaded (#115, D-252c) · 2026-11-20 (Madrid)

**Status:** in production and verified in full.
- The four demo sheets come out complete, they are in the CDN, and each second visit was a «HIT».
- Mayor 61, Almería 1 and Luis Misson were checked on screen.
- `check-parcela` 21/21 and the e2e 145/145 and 121/121, live.

## What the deploy brings
- **#115, D-252c:**
  - **The plan's uses:** tables 4 and 5 of USOS_SUELO are no longer asked live. They come from a generated module, `hi_domain.plan_uses_data` (627 KB, a snapshot of 20 Nov 2026), through layer 3's `UBOV_ID`.
  - **The other sigma layers:** the plan in force and the Z are bounded by the time left, so each one degrades only its own part.
  - **The timing line:** the parcel line adds `stages=`, with the ms of catastro, planning, layer3, instrument and z, also on a complete sheet.
  - **New texts for an urban parcel without a figure:**
    - «El plan no fija uso pormenorizado ni cifra de edificabilidad para esta parcela urbanística» when its use is «SIN USO PORMENORIZADO»;
    - «El plan fija su uso principal (…), pero sin cifra de edificabilidad» otherwise.
- **#114:** deploy-42's evidence.
- **No data sync, no migration and no new variable.** The snapshot is code, in `packages/domain`, which both `.vercelignore` and the API's `Dockerfile.dockerignore` include.

## Deploy · `dpl_94jjgL9uoCocQcfFajZtbZMpsmL3` · 01:20
- **CI:** green on d29e8416, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-43/deploy-output.txt](deploy-43/deploy-output.txt).
- **Verification:** on round 1.
  - In round 0, 6 of the 13 smoke requests still came from c4eaab1's deployment.
  - In round 1, all 13 came from the new one.
- **Disk:** the build is remote. Free disk stayed at 6.9–8 GB.

## Verification, 00:14–00:25 UTC
1. **Smoke:** 13/13, `/search` included.
2. **API:** 54 of 54 answers identical to c4eaab1's without `meta`, and the same size in bytes ([deploy-43/search.txt](deploy-43/search.txt)). D-252c changes only the parcel sheets, which these 54 do not include.
3. **Golden:** 10/10 through the public API, identical line by line to before the deploy ([deploy-43/golden-api.txt](deploy-43/golden-api.txt)).
4. **The four demo sheets, warmed by reference, once each** ([deploy-43/parcelas-en-vivo.txt](deploy-43/parcelas-en-vivo.txt)):
   - **Méndez Álvaro (9.4 s), Almería 1 (1.3 s), Luis Misson (14.4 s) and Mayor 61 (9.5 s):**
     - all four with `degraded=-` and `parts=-`;
     - all four `public, max-age=3600`;
     - the second visit «HIT» in 0.10–0.12 s.
   - **D-252c's timing line:**

     ```
     2122202VK4722A ms=9296  upstream_ms=8994 stages=catastro:380,planning:8646,instrument:523,layer3:7397,z:8644
     3959601VK4735H ms=1236  upstream_ms=1119 stages=catastro:750,planning:369,instrument:141,z:270,layer3:369
     0390314VK4709A ms=14348 upstream_ms=9551 stages=catastro:618,planning:8933,instrument:108,layer3:443,z:8931
     9943003VK3794D ms=9440  upstream_ms=9301 stages=catastro:970,planning:8331,instrument:231,layer3:8253,z:8329
     ```

   - **What it shows:**
     - the Catastro takes 0.4–1.0 s;
     - the first lookup's time is sigma's other layers when cold: layer 3 7.4–8.3 s, the Z 8.3–8.9 s;
     - so the 7.6–10 s before the tables in deploy-42 were these layers, not the Catastro.
   - **The snapshot is in the API's image:** Méndez Álvaro's plan uses come with no table request, and their source says «del plan a fecha 20/11/2026». They are MANZANA B's 60,230.88 m² residential and 21,299.91 m² tertiary.
5. **Mayor 61 (`9943003VK3794D`) on screen, from the CDN, at 360, 390 and 1440 px** ([deploy-43/parcelas-produccion.json](deploy-43/parcelas-produccion.json)). The three widths give the same figures.
   - **«Edificabilidad de partida»:** 224 m² edificables, «Supuesto». It is 68 m² of parcel × Z 5 × C 0,66, norma zonal 1 grado 2º, art. 8.1.10. The API gives 224.4.
   - **«Construido hoy»:** 376 m².
   - **The planning:** norma zonal 1, grado 2º, Protección del Patrimonio Histórico; «Residencial vivienda colectiva»; urban parcel M08336.
   - **«Edificabilidad publicada, por uso»:** «El plan fija su uso principal (residencial vivienda colectiva), pero sin cifra de edificabilidad.» Neither VEDA nor the Portal del Suelo publishes a figure.
   - **The calculator:** PEM 968 «Supuesto», coefficient 1,3575. The most that can be paid for the land, for a 20 % margin:

     | scenario | land | per buildable m² | sales | construction | max. construction for the margin |
     |---|---|---|---|---|---|
     | Base | about 802,000 € | about 3,580 € | 1.52 million € | 294,349 € | 4,894 €/m² |
     | Optimista (+10 % precio, −5 % coste) | about 926,000 € | about 4,140 € | 1.67 million € | 279,632 € | 5,667 €/m² |
     | Pesimista (−10 % precio, +15 % coste) | about 648,000 € | about 2,890 € | 1.37 million € | 338,502 € | 3,830 €/m² |

     The gross rental yield is 5.3 % in all three.
   - No overflow at any width, and 0 console errors.
6. **The new texts of the plan's uses**, at 360, 390 and 1440 px:
   - **Almería 1:** «El plan no fija uso pormenorizado ni cifra de edificabilidad para esta parcela urbanística.» Its use in table 4 is «SIN USO PORMENORIZADO». The rest of its sheet is as in deploy-42: «Sin dato», with the 32,697 m² as a reference and the pending-ambit notice.
   - **Luis Misson:** «El plan fija su uso principal (residencial vivienda colectiva), pero sin cifra de edificabilidad.»
   - Both say «del plan a fecha 20/11/2026».
7. **`check-parcela` against production: 21/21** ([deploy-43/check-parcela-produccion.json](deploy-43/check-parcela-produccion.json)).
   - It covers the search, its states, the 4 sheets and the print view, at 360, 390 and 1440 px.
   - On every screen: 0 texts under 16 px, 0 targets under 44 px, no horizontal overflow and axe 0.
8. **e2e:** **145/145** at 1440 px and **121/121** at 390 px, with 0 console errors ([report](deploy-43/e2e-report.json)). J9, «Busca tu parcela», passes at both widths.
9. **Live lookups: 7 of the 16 left, so 11 of the 20 since D-252b.**
   - **What they were:**
     - the 4 sheets by reference;
     - check-parcela's 3 address boxes («calle de prueba 1»).
   - **Everything else came from the CDN:** 29 sheets in all, from the second visit, the probe, check-parcela and the e2e.
10. **Logs from 00:17 UTC** ([deploy-43/logs.txt](deploy-43/logs.txt)):
    - **Runtime:** 450 lines, all info, with 7 instances started. 0 `WARNING`, and 0 pool, authentication or traceback lines.
      - The 4 `parcel input=` lines and the 3 `parcel candidates=` lines appear.
      - No line has `lat=` or `lon=`. The 3 address boxes say `q=[redactado]`, and the typed text never appears.
    - **CDN:** 1,766 records, every one from the new deployment.
      - **0 4xx and 0 5xx:** 200 × 1,671 and 304 × 95.
      - **WAF:** all `allow`.
    - **No visitor:** no browser other than this run's, and no Web Analytics page view.
    - **Another session's requests:** at 00:23:25–34 UTC, a curl that is not this run's read 2 sheets from the CDN and made 3 `POST /viability`: «D, lectura de cifras para el pitch (#113)», reading Mayor 61's and Méndez Álvaro's figures in the API.

## Screenshots in production
- [1440 px: Mayor 61's «Edificabilidad», «Supuesto» 224 m², and the plan's principal use without a figure](deploy-43/1440-mayor-edificabilidad.jpg)
- [1440 px: Mayor 61's three scenarios, 802,000 / 926,000 / 648,000 €](deploy-43/1440-mayor-escenarios.jpg)
- [1440 px: Almería 1's «Edificabilidad», with «El plan no fija uso pormenorizado…»](deploy-43/1440-almeria-edificabilidad.jpg), reduced to 1,800 px high
- [390 px: Luis Misson's «Edificabilidad», with «El plan fija su uso principal…»](deploy-43/390-luis-misson-edificabilidad.jpg), reduced to 1,800 px high

## For review
1. **A first lookup still takes 9–14 s, because of sigma's layer 3 and Z when cold** (7.4–8.9 s each).
   - Luis Misson used 14.3 s of the 15 s budget.
   - Once warmed, every sheet is served by the CDN for a day.
   - **Before the demo:** open the 4 demo sheets after any deploy. They are warm now.
2. **Luis Misson spent 4.8 s outside the sources** (`ms` 14,348 against `upstream_ms` 9,551). It may be the barrio's context from the database or a cold instance. The timing line does not say which. That is line A's call.
3. **Not re-tested from deploy-39's findings:** the coordinates of a map click in uvicorn's access line. There were no point lookups this time and no line with `lat=`.

## Rollback
- **To `dpl_9DWhMMGTHhzAoBiATNMPvd98tJbV` (c4eaab1):** code only, with no data and no variable to undo.
- A rollback would bring back the live tables 4 and 5, so three of the four demo sheets would be degraded again.
- No rollback was tested.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
