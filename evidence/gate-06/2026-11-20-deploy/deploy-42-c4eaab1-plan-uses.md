# OPS-001 (line C) · deploy of c4eaab1: plan uses within the budget, kept by parts, logged (#111, D-252b) · 2026-11-20 (Madrid)

**Status:** in production, with no errors. Almería 1 is now complete and in the CDN.

**Open:** Méndez Álvaro, Luis Misson and Mayor 61 still come out degraded in `plan_uses`. D-252b's new timing line found why: sigma's own server answers tables 4 and 5 in 6.5–10 s for a parcel it has not cached.

**Next:**
- datamad-10 decided: no second pass and no rollback. c4eaab1 stays.
- D-252c (line F) will read the two tables from a versioned snapshot.
- Mayor 61 on screen, `check-parcela` and the e2e wait for it.

## What the deploy brings
- **#111, D-252b:** API code only.
  - **The tables' time:** tables 4 and 5 of USOS_SUELO use the time left before the sheet's 15 s deadline, instead of a fixed 4 s, and retry once after a quick failure.
  - **A cache by parts:** the planning is kept even when a secondary part fails, and the next visit asks only for what failed.
  - **The logs:** the `hi_api` loggers write at INFO to stdout, through the address filter. Each sheet logs `parcel … ms= upstream_ms= parts=`.
  - **The errors:** a 422 of `/parcels` or `/parcels/candidates`, and the errors of `?address=` and `?q=`, go out `private, no-store`, and the 422s carry no `input`.
- **#112:** deploy-41's evidence.
- **No data sync, no migration and no new variable.**

## Deploy · `dpl_9DWhMMGTHhzAoBiATNMPvd98tJbV` · 00:27 (20 Nov)
- **CI:** green on c4eaab1, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-42/deploy-output.txt](deploy-42/deploy-output.txt).
- **Verification:** on round 0. All 13 smoke requests came from the new deployment.
- **Disk:** the build is remote. Free disk stayed at about 9 GB.

## Verification, 23:24–23:32 UTC (19 Nov)
1. **Smoke:** 13/13, `/search` included.
2. **API:** 54 of 54 answers identical to f806850's without `meta`, and the same size in bytes ([deploy-42/search.txt](deploy-42/search.txt)).
3. **Golden:** 10/10 through the public API, identical line by line to before the deploy ([deploy-42/golden-api.txt](deploy-42/golden-api.txt)).
4. **The four demo sheets, warmed by reference, once each: 4 live lookups of the 20 allowed** ([deploy-42/parcelas-en-vivo.txt](deploy-42/parcelas-en-vivo.txt)).
   - **Almería 1:**
     - complete in 13.4 s (`degraded=- … parts=-`);
     - `public, max-age=3600`, so it is in the CDN;
     - then 3 of 3 browser reads were «HIT».
   - **Méndez Álvaro, Luis Misson and Mayor 61:**
     - degraded in `plan_uses`, `no-store`, 14.6–14.7 s, the whole budget;
     - the timing lines say `parts=plan_uses:TimeoutError:6557`, `:4648` and `:7017`.
   - datamad-10 had asked to stop if any sheet stayed degraded, so there was no second pass.
5. **D-252b's timing line:** the four lines are in [deploy-42/logs.txt](deploy-42/logs.txt).
   - **What it confirms:**
     - the tables failed by time (TimeoutError), not by a quick error, so the one retry never applied;
     - they had 4.6–7.0 s this time, not 4 s, and still did not answer, so the fixed 4 s was not the cause;
     - before the tables, the Catastro and layer 3 took 7.6–10.0 s.
   - **What it cannot show:** the line gives the time only of the parts that fail. A complete sheet says `parts=-`, with no time per step.
   - **The cause:** datamad-10 then measured sigma from Madrid.
     - A query of tables 4 and 5 for a `CODIGO` the server has not cached takes 6.5–10 s on the server (time to first byte 8.4, 10.4 and 7.0 s).
     - The same query takes about 0.2 s once cached.
     - This also explains deploy-41's local diagnosis, where the tables answered in under 0.3 s right after the production queries had asked for them.
6. **Almería 1 on screen, from the CDN, at 360, 390 and 1440 px** ([deploy-42/almeria-produccion.json](deploy-42/almeria-produccion.json)):
   - **«Edificabilidad de partida»: «Sin dato».** The text says «Portal del Suelo 4.0 (Comunidad de Madrid): superficie edificable publicada de la parcela: 32.697 m² edificables de vivienda, pero el ámbito APR.04.09 no está terminado. El ámbito no está terminado: la cifra es una referencia, no los m² de partida.»
   - **«Construido hoy»:** 6.573 m². «¿Está sin edificar?»: No.
   - **The planning:**
     - APR.04.09 «Cocheras Metro Pte. de Ventas», «Sin uso pormenorizado», urban parcel 231123;
     - «Estado del ámbito»: the four phases «sin iniciar», and VEDA «pendiente de planeamiento de desarrollo», as of 1 July 2026.
   - **The pending-ambit notice** (`ambito_pendiente`): «El ámbito APR.04.09 no está terminado según el Ayuntamiento: planeamiento sin iniciar; … en VEDA, pendiente de planeamiento de desarrollo. Faltan planeamiento, gestión o urbanización.»
   - **«Edificabilidad publicada, por uso»:**
     - the plan's line: «El plan no publica la edificabilidad por uso de esta parcela»;
     - each source's line: «Residencial: 32.697 m² edificables», Portal del Suelo 4.0.
   - **Public land:** «Parcela del Portal del Suelo de la Comunidad de Madrid: En venta, la ofrece Metro de Madrid, sin urbanizar.»
   - **The calculator:** PEM 968 «Supuesto» and coefficient 1,3575. There are no scenarios until the m² are given, as a «sin dato» sheet should.
   - No overflow at any width, and 0 console errors.
7. **Mayor 61, at the API level only:** «supuesto», 224.4 m², with `plan_uses` degraded. Its calculator and its buildability by use on screen need a complete sheet: pending.
8. **A 422 of `?address=`** ([deploy-42/privacidad-422.txt](deploy-42/privacidad-422.txt)):
   - **The request:** `address=calle de prueba 1` and `rc` together, rejected by validation, with no source called.
   - **The answer:** `Cache-Control: private, no-store`. The body has only `loc`, `msg` and `type`: no `input`, no `url` and no typed text.
9. **Logs from 23:26 UTC** ([deploy-42/logs.txt](deploy-42/logs.txt)):
   - **Runtime:** 151 lines, all info, with 7 instances started. 0 `WARNING`, and 0 pool, authentication or traceback lines.
     - The 4 `parcel …` lines appear, and they are the only `hi_api` lines.
     - No line has `lat=` or `lon=`. The only `address=` is this check's 422, as `address=[redactado]`.
     - The typed text never appears.
   - **CDN:** 277 records, every one from the new deployment.
     - 200 × 273, 304 × 3, and this check's 422 × 1. 0 5xx.
     - **WAF:** all `allow`.
   - **No visitor.**

## Pending, after D-252c
- **The plan:** line F's D-252c reads the two tables (40,021 + 1,328 rows) from a versioned snapshot, so the sheet no longer asks for them live.
- **Its verification:** with 16 live lookups left of the 20:
  - warm the 4 sheets;
  - check Mayor 61 on screen: «supuesto» 224.4 m², the calculator's figures and its buildability by use;
  - run `check-parcela` and the e2e in full, live.

## Screenshots in production
- [1440 px: Almería 1's «Edificabilidad»](deploy-42/1440-almeria-edificabilidad.jpg)
- [360 px: the same](deploy-42/360-almeria-edificabilidad.jpg), reduced to 1,600 px high

## For review
1. **A degraded sheet now takes the whole budget, 14.6–14.7 s,** against 8.5–11.7 s with f806850. That is the price of giving the tables all the time left. D-252c removes the live tables.
2. **The timing line logs only the parts that fail.** A per-step time for every part would let a complete sheet show where its 13 s go, the Catastro and the planning layers. That is line A's call.
3. **The rows of table 4.** Locally, deploy-41 found 1 row of table 4 for Almería's urban parcel 231123, but the sheet says «el plan no publica». It probably has no figure (`EDIFICABIL`). Worth a look when D-252c builds the snapshot.

## Rollback
- **To `dpl_8v14MKyk8tejVqL1YR7LouEhv2s1` (f806850):** code only, with no data and no variable to undo.
- **What a rollback would change:**
  - the timing line goes;
  - the tables go back to a fixed 4 s;
  - the 422s go back to `public` with their `input`.
- datamad-10 decided not to roll back.
- No rollback was tested.

## Not done
- **Not run:** Mayor 61 on screen, `check-parcela` and the e2e. They wait for D-252c.
- **The offline package** was not rebuilt. It is still at 39644a9.
