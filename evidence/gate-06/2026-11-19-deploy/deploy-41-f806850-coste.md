# OPS-001 (line C) · deploy of f806850: what misled, buildability by use and the construction cost (#109, D-252) · 2026-11-19 (Madrid)

**Status:** in production and verified, except two demo sheets.
- Almería 1 and Mayor 61 come out degraded in `plan_uses`, so the CDN cannot keep them.
- Their check on screen, `check-parcela` and the e2e wait for the D-252b fix ([Pending](#pending-after-d-252b)).

## What the deploy brings
- **#109, D-252:**
  - **The construction cost:**
    - the calculator starts from a PEM of 968 €/m², marked «supuesto». It is the midpoint of the open block in Madrid, from the Comunidad's Costes de Referencia General of 2022.
    - The permits' PEM, 644 €/m² from 2025, stays as the low reference. The API reads it from the Feature Store into a new field, `defaults.pem_permits_m2`, marked «dato».
    - «De dónde sale el coste y cuánto varía» lists the three references.
  - **The coefficient and the scenarios:**
    - the coefficient is 1.3575, with the ICIO at 3.75 %;
    - the pessimistic scenario is −10 % price and +15 % cost;
    - «Ajustar» starts at 15 %;
    - the ECO/805 citation, 18 %;
    - the break-even and the residual headline with three figures (`viability-0.2`).
  - **The parcel's sheet:**
    - buildability by use: each source's figure with its use, and the plan's tables 4 and 5 of USOS_SUELO;
    - the ambit's state;
    - the guard-rails;
    - «¿Está sin edificar?».
  - **The demo sheets** were rebuilt. Almería 1 now gives «sin dato», with its 32,697 m² as a reference.
- **#108:** coordination only. **#107:** deploy-40's evidence.
- **No data sync, no migration and no new variable.**
  - The two new YAML tables, `costes_referencia_construccion.yaml` and `pgoum_ambitos_estado.yaml`, only generate code modules.
  - `pem_visado_vivienda_bloque_m2` was already in Supabase: before the deploy, Pinar del Rey's sheet served 644 from `cm_visados_presupuesto_obra`.
  - No other feature is read.

## Deploy · `dpl_8v14MKyk8tejVqL1YR7LouEhv2s1` · 23:43
- **CI:** green on f806850, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-41/deploy-output.txt](deploy-41/deploy-output.txt).
- **Verification:** on round 1.
  - In round 0, 5 of the 13 smoke requests still came from e3e85b6's deployment.
  - In round 1, all 13 came from the new one.
- **Disk:** the build is remote. Free disk stayed between 8.4 and 10 GB.

## Verification, 22:39–22:56 UTC
1. **Smoke:** 13/13, `/search` included.
2. **API:** 52 of the 54 answers are identical to e3e85b6's without `meta`, and the same size in bytes ([deploy-41/search.txt](deploy-41/search.txt)).
   - The other 2 change exactly as D-252 says, field by field in [deploy-41/inversores-api.txt](deploy-41/inversores-api.txt).
   - **Pinar del Rey's sheet:**
     - `defaults.pem_m2` goes from 644 «dato» to 968 «supuesto», with the source of the Costes de Referencia General 2022;
     - the new `defaults.pem_permits_m2` is 644 «dato», with `cm_visados_presupuesto_obra` and dataset 1006022;
     - the coefficient goes from 1.36 to 1.3575;
     - `adjust_floor_pct` goes from 10 to 15.
   - **The viability:**
     - `viability-0.2`;
     - the pessimistic scenario is «Pesimista (−10 % precio, +15 % coste)»;
     - each scenario has `break_even` and `break_even_free_land`.
3. **Golden:** 10/10 through the public API, identical line by line to before the deploy ([deploy-41/golden-api.txt](deploy-41/golden-api.txt)).
4. **The header, `check-cabecera` against production:** 15/15 ([deploy-41/check-cabecera-produccion.json](deploy-41/check-cabecera-produccion.json)).
   - On every screen:
     - the 4 tabs in one row;
     - the active tab right on all five pages;
     - 0 texts under 16 px and 0 targets under 44 px;
     - axe 0.
   - Contrast: 5.48:1 over the map at 360 and 390 px, 5.51:1 at 1440 px, and 5.62–5.67:1 elsewhere.
5. **`/como-lo-calculamos#inversores` at 360, 390 and 1440 px** ([deploy-41/d252-produccion.json](deploy-41/d252-produccion.json), `method`). It shows, and links:
   - **the three cost references:**
     - the permits' PEM, 644 €/m² (2025), with dataset 1006022;
     - the Costes de Referencia General 2022: open block 871–1,064 €/m², and «La calculadora parte del punto medio del bloque abierto: 968 €/m² (supuesto)»;
     - the Sociedad de Tasación, 1,360 €/m², December 2025;
   - «Ajustar» between 15 % and the target;
   - «un margen mínimo del 18 % en vivienda de primera residencia… (Orden ECO/805/2003, disposición adicional sexta)».
   - No horizontal overflow and 0 console errors.
6. **The calculator on Méndez Álvaro's sheet** (`2122202VK4722A`, from the CDN), at 360, 390 and 1440 px:
   - **PEM:** 968, marked «Supuesto», with «Referencia de la Comunidad de Madrid de 2022; los costes han subido desde entonces… 644 €/m², es la referencia baja».
   - **«De dónde sale el coste y cuánto varía»:** three lines.
     - The first is marked «Dato»: «PEM medio de los visados… (2025): 644 €/m²… Fuente: Comunidad de Madrid · 2025…», with its link to dataset 1006022.
     - Then the Costes de Referencia General 2022 and the Sociedad de Tasación.
   - **Coefficient:** 1,3575, «Supuesto», «el PEM más un 35,75 %».
   - **The scenarios:** the residual land value, as datamad-10 expected.
     - Base: about 61.2 million € (about 4,670 € per buildable m²).
     - «Optimista (+10 % precio, −5 % coste)»: about 69.9 million €.
     - «Pesimista (−10 % precio, +15 % coste)»: about 50.8 million €.
     - Each one «antes de financiación, impuestos de compra del suelo, urbanización y derribo», with its maximum construction cost for the target margin.
   - **The thresholds:** «Ajustar» between 15 % and the target; ECO/805 and its 18 %.
   - **At 360 px:** no element of the calculator past the screen, no page overflow, and 0 console errors. Without a land price there is no verdict, as before.
7. **The parcel's sheet, D-252** (the same probe):
   - **Méndez Álvaro:**
     - «¿Está sin edificar? (según su uso en el Catastro)»: Sí. «¿Es un solar?» is gone.
     - **«Estado del ámbito»:** APR.02.06, its four phases «finalizado», «según el Ayuntamiento a 1 de julio de 2026». VEDA «en fase de edificación… no quiere decir que se pueda construir ya».
     - **«Edificabilidad publicada, por uso»:**
       - the plan's urban parcel MANZANA B, with 60,231 m² residential (main use) and 21,300 m² tertiary, and its caveats;
       - VEDA's 13,121 m² residential, «Dato», which the calculator starts from.
   - **Luis Misson** (`0390314VK4709A`, from the CDN): «Sin dato», «Pon tú los m² edificables», «El plan no publica la edificabilidad por uso de esta parcela» and «¿Está sin edificar?»: Sí.
   - **The «El Ayuntamiento no publica su estado» notice:** neither of these two parcels needs it. APR.02.06 is tracked, and Luis Misson has no ambit.
   - **Almería 1 and Mayor 61:** checked only in the API answers of point 9.
8. **The other scripts against production:**
   - `check-inversores` (a barrio's sheet and its calculator, at 360, 390 and 1440 px): 12/12 ([report](deploy-41/check-inversores-produccion.json)). It uses the new text «Lo máximo que se puede pagar por el suelo, antes de…».
   - `check-desarrolladores`: 6/6 ([report](deploy-41/check-desarrolladores-produccion.json)).
   - `check-ux-mobile`: identical to deploy-40's apart from its timestamp ([deploy-41/tamanos-produccion.json](deploy-41/tamanos-produccion.json)).
   - On every screen: 0 texts under 16 px, 0 targets under 44 px, no overflow and axe 0.
9. **The four demo parcels: 8 live lookups, under the ~10 allowed** ([deploy-41/parcelas-en-vivo.txt](deploy-41/parcelas-en-vivo.txt)).
   - **What was asked:**
     - 4 by reference right after the deploy, to warm the CDN;
     - the same 4 again, because none of the first had stayed in the CDN.
     - Every other sheet came from the CDN (16 «HIT»).
   - **1st pass, 8.6–11.7 s:** all four degraded.
     - Méndez, Almería and Luis Misson in `plan_uses`.
     - Mayor 61 in the whole `planning`, so it gave «sin dato» instead of «supuesto».
   - **2nd pass:**
     - Méndez Álvaro (0.9 s) and Luis Misson (0.5 s) came back complete and are now in the CDN (`public, max-age=3600`).
     - Almería 1 (11.4 s) and Mayor 61 (8.5 s) were degraded again in `plan_uses`.
   - A degraded sheet goes out with `no-store` (D-250), so these two are not cached, and every visit is a ~9–12 s live lookup.
   - **What their answers already show at the API level:**
     - Almería: «sin dato», the Portal del Suelo's 32,697 m² residential as a reference in `by_use`, and the `ambito_pendiente` caution of APR.04.09;
     - Mayor 61: «supuesto» 224.4 m².
   - **Diagnosis, outside our API:** the API's own functions, run from Madrid against the Ayuntamiento's service only (16 requests, no Catastro).
     - Layer 3 answered in 0.14–0.20 s, and tables 4 and 5 in 0.08–0.27 s, with 1 row in table 4 for each parcel.
     - The whole planning comes out complete for both.
     - The runtime log has no timing or cause line (deploy-39, finding 1), so the step that failed from Dublin is not known.
     - datamad-10's reading: the times fit the tables' fixed 4 s (`PLAN_USES_TIMEOUT_S`) after a cold Catastro and layer 3, with the sheet's 15 s budget not used up.
     - Line F is preparing D-252b (point 1 of [For review](#for-review)).
10. **Logs from 22:41 UTC** ([deploy-41/logs.txt](deploy-41/logs.txt)):
    - **Runtime:** 465 lines, all info, with 10 instances started. 0 `WARNING`, and 0 pool, authentication or traceback lines.
    - **CDN:** 1,753 records, the whole window, every one from the new deployment.
      - **0 4xx and 0 5xx:** 200 × 1,697 and 304 × 56.
      - **WAF:** all `allow`.
    - **No typed address:** no address, point or candidates request in the window.
    - **No visitor:** no Web Analytics page view; only this run's requests.

## Pending, after D-252b
datamad-10 asked for no more lookups of Almería 1 and Mayor 61 until line F's fix, D-252b.
- **What D-252b brings:**
  - the tables use the time left before the deadline and retry once;
  - a cache by parts;
  - the timing and cause line in the logs;
  - `private, no-store` on `?address=` errors.
- **The limit then goes up to 20 live lookups.**
- **What the verification will cover:**
  - warm the 4 demo sheets;
  - `check-parcela` and the e2e in full, live;
  - Almería 1 («sin dato», 32,697 m² as a reference) and Mayor 61 (about 802k, 926k and 648k €) on screen;
  - the ms of each step, from the new timing line.

## Screenshots in production
- [390 px: Méndez Álvaro's «De dónde sale el coste y cuánto varía», the permits' line with «Dato»](deploy-41/390-ficha-mendez-coste.jpg)
- [360 px: the same, inside the screen](deploy-41/360-ficha-mendez-coste.jpg)
- [1440 px: Méndez Álvaro's calculator with its three scenarios](deploy-41/1440-ficha-mendez-calculadora.jpg), reduced to 1,400 px high

## For review
1. **From Dublin, the plan's tables 4 and 5 often miss their 4 s (point 9).**
   - When they do, the sheet is degraded in `plan_uses` and goes out with `no-store`, so it never reaches the CDN.
   - In this run that happened to Almería 1 and Mayor 61 on both passes: they cannot be warmed before the demo.
   - It is honest (no error, «No hemos podido leer ahora la edificabilidad por uso del plan»), but slow: ~9–12 s on every visit.
   - D-252b, line F.
2. **Mayor 61's first lookup lost the whole planning,** so «sin dato» instead of «supuesto» 224 m².
   - deploy-39 and deploy-40 never saw this.
   - Locally, its planning took 9 s because of another sigma layer, not the tables.
   - Worth checking against D-252b's timing line.
3. **Deploy-39's finding 1, no timing line, again blocked the diagnosis.** D-252b brings the line.

## Rollback
- **To `dpl_FCcfhjEZYiTgNic444FexZDU34Ds` (e3e85b6):** code only, with no data and no variable to undo.
- **What a rollback would change:** the calculator goes back to:
  - the permits' 644 €/m² as its PEM;
  - a coefficient of 1.36;
  - a pessimistic scenario of +5 % cost;
  - «Ajustar» from 10 %;
  - Almería 1 «oficial».
- datamad-10 decided not to roll back: there are no errors and the notice is honest.
- No rollback was tested.

## Not done
- `check-parcela` and the e2e: after D-252b, with the new limit.
- The offline package was not rebuilt. It is still at 39644a9.
