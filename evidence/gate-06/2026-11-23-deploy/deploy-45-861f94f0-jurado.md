# OPS-001 (line C) · deploy of 861f94f0: the jury's fixes, web (#120) and API (#121), plus the pitch (#122) · 2026-11-23 (Madrid)

**Status:** in production and verified.
- Smoke 13/13, the golden 10/10 identical to before the deploy, `check-parcela` 21/21, `check-inversores` 12/12.
- The four demo sheets come out complete, not degraded, and in the CDN.
- The e2e gives 137/138 and 117/118 as it is in the repo. The one failure is an expectation that #120 made stale on purpose: Mayor 61's calculator now starts empty. With that expectation adjusted, it gives 139/139 and 119/119 (see «e2e»).
- deploy-45's own checks: the API as #121 says, and 48/48 on screen for #120.

**No migration, no sync and no new variable.** Nothing wrote to the database.

## What was deployed
- **861f94f0** is the head of `claude/sprint-1-public`: the merge of #122 on top of #121 (7969d6a8) and #120 (d1949464).
  - CI on 861f94f0: green in all five jobs.
- **#120, web:**
  - the tagline «La zona que te conviene, y lo que le falta» in the H1 and the `<title>`;
  - the licence sentence with the urbanization only when planning, management and VEDA are finished; otherwise «Antes de pedir licencia, el ámbito necesita su planeamiento y su gestión.»;
  - a catalogued building's calculator starts at «Sin dato», with the rehabilitation notice;
  - the residual per m² buildable and as a share of the sales;
  - «Llévate esta ficha» once;
  - the method's real version;
  - vacant land «de toda la ciudad»;
  - the price of the 2024 leases;
  - the pharmacy off the card unless it is marked.
- **#121, API:**
  - `gap-0.4` (D-254): the housing row is CONTEXTO and leaves `/gaps/impact`;
  - the OpenAPI `info`;
  - `ValueMark` «estimacion» on the sale price;
  - the ICIO without «vigente en 2025».
- **#122:** pitch, docs and README only.

## Deploy · `dpl_5EoD1qfUSF3Ltud8ZEifSf7fPko6` · 11:26 Madrid (10:26 UTC)
- **Command:** `ALLOW_BRANCH=1 make deploy-demo`, from a detached and clean checkout. Output: [deploy-45/deploy-output.txt](deploy-45/deploy-output.txt).
- **Verification:** on round 1.
  - In round 0, 6 of the 13 smoke requests still came from a6690573's deployment.
  - In round 1, all 13 came from the new one.
- **Time:** 2 min 32 s. The build is remote; free disk stayed above 7 GB.

## Verification, 10:24–10:39 UTC
1. **Smoke:** 13/13, `/search` included.
   - The bytes are the same as in deploy-44, except the web (45,975 → 46,087 B) and `zone` (35,701 → 35,920 B, the housing row).
2. **The API before and after the deploy:** 62 requests ([deploy-45/search.txt](deploy-45/search.txt)): deploy-44's 55 and 7 new ones for #121. 18 come out identical and 44 change, all of them for #121:
   - **The 31 `/gaps` lists and Valdilecha and Madrid:**
     - the method goes to `gap-0.4`;
     - the housing row gets its new label;
     - in the 12 municipios, that row goes to CONTEXTO, without a ratio and with the context sentence. Before, 5 were FALTA, 6 JUSTO and 1 CUBIERTO.
     - The other 5 rows are identical in all 33.
   - **5 searches** (buy400, couple1500, couple1500-pueblos, rent10k, student: households without children):
     - only the third highlight, «Vivienda para familias», leaves, with its 2 datasets;
     - no zone, %, order or fact changes.
     - The 6 searches with children or older people (the example, telework, pueblos, couple1500-madrid, retired, retired-noflag) are identical.
   - **`/gaps/impact` and the maps:** see point 4.
   - **Pinar del Rey's sheet:**
     - «estimacion» on the 3 sale prices;
     - the ICIO without «vigente en 2025»;
     - the housing row's label.
   - **The OpenAPI:** its `info`.
   - **Identical:** `/datasets` (59), the feature lists and values, the zone list and the viability.
3. **Golden:** 10/10 through the public API ([deploy-45/golden-api.txt](deploy-45/golden-api.txt)), identical line by line to before the deploy and to deploy-44's.
   - The script was lost with the scratchpad and was rebuilt from `scripts/golden_search.py`. Before the deploy it reproduced deploy-44's file byte for byte.
4. **#121 in the API** ([deploy-45/api-especificos.txt](deploy-45/api-especificos.txt)):
   - **Valdilecha** (`/gaps/municipio/28165`):
     - the housing row is CONTEXTO, ratio `null`, labelled «Viviendas grandes por cada 100 hogares grandes (contexto)»;
     - it keeps its value 262,1, its reference 438,2 and the Comunidad's 177,6;
     - **no p:** the row has no p field. Valdilecha is no longer in `/gaps/impact`, where before it had `p_value` 3.59E-59 in the housing row.
   - **`/gaps/impact`:**
     - no housing row. Before, it had 25 zones and 99.483 households.
     - Escuela infantil is still at **25.551** children in 3 zones.
     - The 5 judged rows are identical.
   - **The housing map by municipio:** from CUBIERTO 134 · FALTA 25 · JUSTO 20 to CONTEXTO 179. The districts stay SIN_DATOS.
   - **`/openapi.json`:**
     - `info.title` «Vida Fácil API», with a description;
     - `license` Apache-2.0 (`identifier` Apache-2.0);
     - `contact` with the repo's URL;
     - `servers` with the public URL.
   - **The four sheets:** `sale_price_m2.mark` is «estimacion» in `defaults` and in `context.sheet.defaults`, and their ICIO text has no «vigente en 2025».
5. **The four demo sheets, warmed by reference once each** ([deploy-45/parcelas-en-vivo.txt](deploy-45/parcelas-en-vivo.txt)):
   - all four `degraded=-`, no warnings, `public, max-age=3600`, and the second visit «HIT» in 0.10–0.14 s;
   - **the timing lines:**

     ```
     2122202VK4722A ms=916   stages=catastro:380,planning:375,z:240,layer3:327,catalog:373,instrument:374
     3959601VK4735H ms=10786 stages=catastro:646,planning:10007,instrument:131,layer3:225,catalog:291,z:10005
     0390314VK4709A ms=11012 stages=catastro:772,planning:10113,layer3:275,catalog:274,instrument:435,z:10112
     9943003VK3794D ms=9884  stages=catastro:1031,planning:8729,catalog:222,layer3:268,instrument:275,z:8727
     ```

   - The slow part is now sigma's Z when cold, at 8.7–10.1 s. Méndez Álvaro found sigma warm and took 0.9 s.
6. **#120 on screen, at 1440 and 390 px, from the CDN:** 48/48 ([deploy-45/probe-d45.json](deploy-45/probe-d45.json), script [deploy-45/probe_d45.mjs](deploy-45/probe_d45.mjs)).
   - **Home:** the H1 is «La zona que te conviene, y lo que le falta». The `<title>` is «Vida Fácil · La zona que te conviene, y lo que le falta».
   - **Mayor 61:**
     - the calculator's m² is empty, marked «Sin dato», with «Ponla tú si quieres: en un edificio catalogado no partimos de ninguna cifra»;
     - above the fields, «Edificio catalogado: una cuenta de obra nueva no sirve; hace falta un estudio de rehabilitación.»;
     - «3. Edificabilidad» still says «Supuesto», 224 m².
   - **Almería 1:**
     - «4. Servicios y suministros» says «Antes de pedir licencia, el ámbito necesita su planeamiento y su gestión.»;
     - and not the sentence about a licence with the urbanization at once.
   - **Méndez Álvaro:**
     - the residual row of each of the three scenarios says «€ por m² edificable» and the %: «unos 61,2 millones de € (unos 4.670 € por m² edificable; el 56 % de los ingresos por ventas)». The optimistic scenario says 69,9 M, 5.330 € and 58 %; the pessimistic, 50,8 M, 3.870 € and 52 %.
     - Below the scenarios: «La cuenta no incluye sótanos, urbanización, financiación ni IVA.» and «Método de la cuenta: viability-0.2.»
     - The heading sentence of each scenario comes from the API's verdict. It still gives only the € per m², without the %, because #120 did not change it.
   - **«Llévate esta ficha»** appears once on each of the four sheets. In deploy-44 it appeared twice.
   - **Pinar del Rey's barrio sheet:**
     - the sale price is marked «Estimación»;
     - the land reads «Suelo vacante de toda la ciudad (Catastro)», 13.813;
     - the sources say «Método: viability-0.2.», no longer «viabilidad v0 (D-248)».
   - **`/como-lo-calculamos`:** the ICIO without «vigente en 2025», and «Vivienda (solo contexto)».
   - **On every page:** 0 console errors, and every sheet request was «HIT».
   - The price of the 2024 leases on the card, and the pharmacy off it, are covered by the e2e's J1.
7. **The scripts against production:**
   - `check-parcela`: **21/21** ([report](deploy-45/check-parcela-produccion.json)). It covers the search, its states, the 4 sheets and the print view, at 360, 390 and 1440 px.
   - `check-inversores`: **12/12** ([report](deploy-45/check-inversores-produccion.json)).
   - On every screen: 0 texts under 16 px, 0 targets under 44 px, no horizontal overflow and axe 0.
8. **e2e:** see the next section.
9. **Live lookups: 7.**
   - What they were: the 4 sheets by reference and check-parcela's 3 address boxes (2 of those from the API's own cache).
   - 40 sheet reads came from the CDN.
10. **Logs, 10:26–10:39 UTC** ([deploy-45/logs.txt](deploy-45/logs.txt)):
    - **Runtime:** 731 lines, all info, with 10 instances started. 0 warning, error, pool, authentication or traceback lines. No coordinates and no typed text.
    - **CDN:** 3.353 records, the whole window (2 pages of the listing).
      - All but 6 came from the new deployment. The 6 were smoke round 0.
      - Status: 200 × 3.165, 304 × 187 and one 404. **0 5xx.** WAF: all `allow`.
    - **«Visitante sin identificar (Chrome/Android)»:** at 10:35:48 UTC, one request to `/api/v1/mcp`, which answered 404. This deployment has no such route, because the remote MCP is not deployed. It made no other request. Who it was is not known.

## e2e: one stale expectation, from #120
- **As it is in the repo:** **137/138** at 1440 px and **117/118** at 390 px ([report](deploy-45/e2e-report.json)), with 0 console errors.
- **The only failure:** J9 «9943003VK3794D: the calculator starts from the parcel's m²», at both widths.
  - The e2e expects the field to hold the buildability, 224. #120 now starts a catalogued building's calculator empty, at «Sin dato» (F14, jury A1/A2), so this change is on purpose.
  - `check-parcela` passes because it only looks at «3. Edificabilidad», which still says «Supuesto». #120 did not update this e2e check.
- **Adjusted:** a copy of the e2e with that one expectation changed ([diff](deploy-45/e2e-j9-catalogado.diff)).
  - For a catalogued building, the field must be empty and the rehabilitation notice must show. For any other parcel, the check is as before.
  - Result: **139/139** and **119/119**, with 0 console errors ([report](deploy-45/e2e-report-ajustado.json)).
  - **The diff is not applied to the repo.** It is for whoever owns the e2e. Until it is applied, `make e2e-prod` gives 137/138 and 117/118.
- **Why there are fewer checks than in deploy-44** (145/121), all on purpose:
  - **J3:** «¿Qué quieres ver?» lists 5 rows, not 6. The housing row is context, so it is off the map (gap-0.4). That removes its caption and 5 legend counts at 1440 px, and its caption and one skipped count at 390 px.
  - **J1:** the essentials now carry the 2024 rent notice instead of «Precio orientativo» (#120). The check «Ver más: why the rent is orientative» is gone, in the repo's e2e.
  - **J2:** «Vivienda para familias» JUSTO is now «Viviendas grandes por cada 100 hogares grandes (contexto)» CONTEXTO.

## Screenshots in production (1440 px)
- [Home: the new H1](deploy-45/1440-portada-h1.jpg)
- [Mayor 61: the calculator at «Sin dato» with the catalogued-building notice](deploy-45/1440-mayor-calculadora.jpg)
- [Almería 1: «Antes de pedir licencia, el ámbito necesita su planeamiento y su gestión.»](deploy-45/1440-almeria-servicios.jpg)
- [Méndez Álvaro: the three scenarios with the residual per m² buildable and the % of the sales](deploy-45/1440-mendez-alvaro-residual.jpg)

## For review
1. **The e2e's J9 expectation for a catalogued building** ([diff](deploy-45/e2e-j9-catalogado.diff)). Without it, `make e2e-prod` fails on Mayor 61.
2. **The heading sentence of each scenario** comes from the API's verdict. It still gives only the € per m² of the residual, without the %. The row underneath has both.
3. **The registry sync is still pending:** `/datasets` stays at 59, as in deploy-44.
4. **A first lookup still takes 9.9–11.0 s,** because of sigma's Z when cold. The 4 demo sheets are warm now, and the CDN keeps them a day.
5. **`/api/v1/mcp` was asked for once** by an unidentified visitor, and answered 404.

## Rollback
- **To `dpl_5udnLokddKKNCueMzPiwnPsrvQXX` (a6690573):** code only, with no data and no variable to undo: `npx vercel@65.12.1 rollback`.
- A rollback brings back:
  - the housing row as a verdict (FALTA, JUSTO or CUBIERTO), and in `/gaps/impact`;
  - «Housing Intelligence API»;
  - «dato» on the sale price;
  - the old tagline;
  - «Llévate esta ficha» twice.
- No rollback was needed or tested.

## Not done
- **The offline package** was not rebuilt. It is still at 39644a9.
- **The registry sync:** pending, as above.
