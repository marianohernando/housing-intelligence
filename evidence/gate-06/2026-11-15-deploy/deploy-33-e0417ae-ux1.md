# OPS-001 (line C) · deploy of e0417ae, UX mobile 1 (#79, D-244) · 2026-11-15 (Madrid)

## What the deploy brings
- **#79, web:** the first delivery of the mobile clarity audit (option 1). It brings:
  - text of at least 16 px and touch targets of at least 44 px;
  - quick amounts for the budget;
  - plain words: the bands, «Casi valen» and «unos … € al mes»;
  - help behind «¿Qué es esto?»;
  - «Más opciones» folded;
  - a phone portada that opens on the search, with two examples.
- **#79, D-244 «Somos mayores»:** in the API, `Household.seniors: bool = False` (additive). `highlight_rows` brings «Centros de mayores» forward, and the commute fact now says «el % se queda en la mitad».
- **Web and API went together.** 025a4a2 answers 422 to `household.seniors`.
- **No data sync.**

## Deploy · `dpl_ByScLXFa2ixyreAQMsbQWf6tf4ZG` · 19:28
- **CI:** green on e0417ae, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-33/deploy-output.txt](deploy-33/deploy-output.txt).
- **Verification:** on round 0. All 13 smoke requests came from the new deployment.

## Verification, at 1440, 390 and 360 px
Details:
- the searches: [deploy-33/search.txt](deploy-33/search.txt);
- the web: [deploy-33/web-checks.txt](deploy-33/web-checks.txt);
- the sizes: [deploy-33/tamanos-produccion.json](deploy-33/tamanos-produccion.json).

1. **Smoke and e2e:**
   - smoke 13/13, `fit-0.9`;
   - e2e **86/86** at 1440 px and **62/62** at 390 px ([report](deploy-33/e2e-report.json)). The new J5 passes 12/12 at both widths, with 0 console errors.
2. **Portada on the phone, at 390 and 360 px:** the sheet opens on the search.
   - The first screen holds:
     - «Te decimos en qué zonas de la Comunidad de Madrid puedes vivir con tu presupuesto y con lo que necesitas cerca.»;
     - the two examples;
     - «Tu búsqueda», at 663 px from the top;
     - «¿Dónde?», at 701 px from the top.
   - The map is behind «Ver el mapa».
   - At 1440 px nothing moved: the map fills the screen behind the left panel, and there is no «Ver el mapa».
3. **Measurement on the phone,** with `apps/web/scripts/check-ux-mobile.mjs`, at 390 and 360 px:
   - **0 texts under 16 px and 0 targets under 44 px** on all 8 screens: portada, form, open form, form with the example, list, card, district, and «Somos mayores» with a place picked.
   - The only exceptions are MapLibre's 3 attribution controls on the portada, which the licences require:
     - the (i), 24 × 24;
     - «© OpenStreetMap», 14 px high;
     - «Powered by CRTM», 14 px high.
   - Their 3 texts are also the only ones under 16 px.
   - **axe:** 0 incidents.
4. **Quick amounts:**
   - **Renting:** 600 · 900 · **1.200** (chosen) · 1.500 · «Otra cantidad».
     - «Otra cantidad» opens «Escribe la cantidad, en euros al mes». Typing 750 moves the slider to 750.
     - The e2e sends 900 € as `amount_eur: 900`.
   - **«Comprar»:** 150.000 · **250.000** (chosen) · 400.000 · 600.000 · «Otra cantidad».
     - The slider starts at 250.000.
     - The search sends `{"kind":"buy","amount_eur":250000}`.
5. **Plain texts:**
   - **Bands:** every visible row carries exactly one band, the one its `match_band` gives.
     - The retired example: 2 «Muy buena opción» and 8 «Buena opción».
     - A search with «Solo/a», 600 € and «Trabajo en» Vicálvaro: 1 «Buena opción», 1 «Opción regular» and 8 «Poco recomendable».
     - «Cómo lo calculamos» names all four, and none of the old ones.
   - **«Casi valen (5)»:** its rows read «Se pasa unos 90 / 20 / 190 / 230 / 30 € al mes de tu presupuesto».
   - **The card:** «unos 1.129 € al mes por 77 m²», with no «≈».
   - **The form:**
     - Three «¿Qué es esto?» are visible on the phone. The other two are inside «Más opciones».
     - «Trabajo en (opcional)».
     - «Más opciones» is folded, with «Servicios a un paseo, familia o amigos y tamaño del piso».
6. **«Somos mayores»,** marked after «En pareja»:
   - **What appears:**
     - «¿Cerca de dónde queréis vivir?», with «Donde vivimos ahora» (chosen) or «Cerca de nuestra familia»;
     - «Madrid capital»;
     - Centro de salud 1, Metro o tren sin escaleras 2 and Transporte 3, already marked;
     - «Trabajo en», folded in «Más opciones».
   - **With the Ciudad Lineal (metro) station picked:**
     - the field shows «Tardar como mucho 30 min»;
     - the search sends `seniors: true` and the `other` place «donde vivimos ahora» at 30 min and 3 days, in `madrid`;
     - it finds 22 of the 131 barrios.
   - **Unmarked:**
     - «¿Cerca de dónde queréis vivir?» and every «donde vivimos ahora» leave the form.
     - The next search sends no `seniors` and `anchors: []`.
     - It keeps `madrid` and the three priorities, all in view, and finds 84 of the 131 barrios.
     - Nothing filters unseen.
7. **The «Pareja jubilada» example:**
   - **What it sends:**
     - `seniors: true` and `madrid`;
     - the family place «Ciudad Lineal (metro)», at 30 min and 3 days;
     - salud, sin_escaleras and transporte.
   - **What the list shows:**
     - «Hemos encontrado 22 barrios para ti.»;
     - Casco Histórico de Barajas 92 and Alameda de Osuna 92, tied;
     - then Quintana, San Pascual, Pueblo Nuevo and Ventas at 89;
     - then La Concepción 88, Arcos 87, Rosas 87 and Amposta 79;
     - no «¿Trabajas fuera de casa?».
   - **The card of its 1st barrio, «Lo que le falta a Barajas»:**
     - Centros de salud: 20 min on foot, «No comparable»;
     - Farmacias: 9 min, «CUBIERTO»;
     - Centros de mayores: 18 min, «No comparable»;
     - no colegio or escuela infantil anywhere in the card.
   - **Through the API,** the search gives the same zones, %, order and Reality Check with and without `seniors`.
8. **The pitch example does not change:**
   - 42 of 199 zones, 0 without data;
   - Puente de Vallecas 94 and Latina 94, tied; Usera 93; …; Leganés 90 tenth;
   - «Hemos encontrado 42 zonas para ti.».
9. **Console:** 0 errors in every run (e2e, the three probes and the measurement) at 1440, 390 and 360 px. The logs are below.
- **Screenshots:**
  - portada: [1440](deploy-33/1440-01-portada.jpg) · [390](deploy-33/390-01-portada.jpg) · [360](deploy-33/360-01-portada.jpg);
  - buying: [390](deploy-33/390-02-importes-compra.jpg);
  - «Somos mayores»: [with a place, 360](deploy-33/360-03-somos-mayores-lugar.jpg) · [unmarked, 390](deploy-33/390-04-somos-mayores-desmarcado.jpg);
  - «Pareja jubilada»: [1440](deploy-33/1440-05-pareja-jubilada.jpg) · [390](deploy-33/390-05-pareja-jubilada.jpg) · [Barajas card, 390](deploy-33/390-06-tarjeta-barajas.jpg);
  - the family example: [list, 360](deploy-33/360-07-lista-ejemplo.jpg) · [card, 390](deploy-33/390-08-tarjeta-ejemplo.jpg);
  - [bands, 390](deploy-33/390-09-bandas.jpg).

## The API, before and after
- **025a4a2 and e0417ae give the same answers to the same 10 bodies,** after undoing the two expected changes. The 11th body, the retired example with `seniors`, got a 422 from 025a4a2. The two changes:
  - the echoed scenario carries `household.seniors: false`;
  - «el encaje se queda en la mitad» now reads «el % se queda en la mitad».
- Zones, %, `match_band`, order, facts, «casi», `all_zones`, Reality Check and datasets are byte for byte the same.
- **The golden through the public API** ([deploy-33/golden-api.txt](deploy-33/golden-api.txt)) is deploy-32's, line by line, except that one sentence of the golden student.

## Logs, 18:26–18:39 UTC
Details in [deploy-33/logs-summary.txt](deploy-33/logs-summary.txt).
- **Runtime:** 639 lines, all info, with 8 instances started.
  - 0 `WARNING`;
  - 0 pool, prepared-statement, authentication, validation or traceback lines.
- **CDN:** 0 4xx and 0 5xx.
  - The listing stops at 2,000 records, so a separate `httpStatus >= 400` query covered the whole window. It returned nothing.
- **The previous deployment:**
  - its only 4xx is the deliberate 422 of the baseline (18:23, `vida-facil-smoke/base`);
  - it got no request after 18:27:30.

## For review, not blocking
1. **The order of the ties.**
   - #79's evidence text names Alameda de Osuna first and «Ventas, Pueblo Nuevo, Quintana…», and so does the instruction.
   - Production gives Casco Histórico de Barajas first, then Quintana, San Pascual, Pueblo Nuevo and Ventas, with the same %.
   - #79's own screenshot (`04-ejemplo-pareja-jubilada-1440.png`) shows production's order. Only the wording differs.
2. **The previous search's option after unmarking «Somos mayores».**
   - Until the next search, «¿Quieres ver más zonas?» still offers the previous search's «Sin límite de tiempo hasta donde vivimos ahora».
   - Tapping it reapplies that search. «Somos mayores» is marked again, and the place shows as «Donde vivimos ahora» with «Quitar» and «Sin límite».
   - The place is visible and removable, so nothing is hidden. Only the station's name is missing ([390](deploy-33/390-10-opcion-anterior.jpg)).
   - For line B: keep the name in the place, or drop the old options when the form changes.
3. **The list row still reads «≈ 1.129 €/mes».** The card and «Casi valen» say «unos», as #79 planned. Delivery 2 redoes the row.

## Rollback
- **To `dpl_8tDBNAFx…` (025a4a2):** code only, and no data changed.
- A browser that still has the new web loaded and «Somos mayores» marked would get a 422 until it reloads.
- D-241 §9 still applies before `dpl_G26vdu…`.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
