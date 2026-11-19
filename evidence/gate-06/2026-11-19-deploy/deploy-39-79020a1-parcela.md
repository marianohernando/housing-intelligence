# OPS-001 (line C) · deploy of 79020a1: «Busca tu parcela» (#101, D-250) · 2026-11-19 (Madrid)

## What the deploy brings
- **#101, D-250:**
  - `/inversores` opens with «Busca tu parcela»: by cadastral reference, by address (the person picks the portal) or with a click on the map. The barrio list follows as «Explorar barrios».
  - `/inversores/parcela/{rc}` is one parcel of Madrid capital, with a shareable URL and a print view.
  - The API gains `GET /api/v1/investors/parcels?rc=|lat=&lon=|address=` and `GET /api/v1/investors/parcels/candidates?q=`.
    - They call the Catastro, the Ayuntamiento (sigma) and CartoCiudad live, with a cache in each instance and a per-IP guard.
    - When a source fails, the API serves the 4 demo sheets saved in `parcel_demo.json`.
  - `/desarrolladores` documents 2 more routes, 15 in all.
  - The API image gains `httpx`.
- **No data sync, no load into `housing` and no new variable.** `PARCEL_UPSTREAMS` is left unset in production, so it keeps its default, `true`.

## Deploy · `dpl_7ySG3suaT3tXBGJHRZ6Ar3eu9YEN` · 16:30
- **CI:** green on 79020a1, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-39/deploy-output.txt](deploy-39/deploy-output.txt).
- **Verification:** on round 0. All 13 smoke requests came from the new deployment.
- **Disk:** the build is remote. Free disk stayed at 2.5 GB through the deploy and every check, above the 2 GB floor.

## Verification, 15:30–15:40 UTC
1. **Smoke:** 13/13, `/search` included.
2. **API:** 54 answers identical to 20b46d9's without `meta`, and the same size in bytes ([deploy-39/search.txt](deploy-39/search.txt)).
   - They are deploy-38's 54.
   - Only `request_id` and `generated_at` change.
3. **Golden:** 10/10 through the public API, identical line by line to before the deploy and to deploy-38's ([deploy-39/golden-api.txt](deploy-39/golden-api.txt)).
4. **e2e:** **145/145** at 1440 px and **121/121** at 390 px, with 0 console errors ([report](deploy-39/e2e-report.json)).
   - The new journey J9 passes its 22 checks at both widths:
     - the three ways in;
     - the four demo chips;
     - «Explorar barrios»;
     - Méndez Álvaro from its chip;
     - Mayor 61 typed by hand as «9943003 vk3794d»;
     - every figure as the API sent it;
     - the Catastro's citation;
     - the printed legal notice.
   - J8 now counts 15 routes.
5. **The four demo parcels by reference, live** ([deploy-39/parcelas-en-vivo.txt](deploy-39/parcelas-en-vivo.txt)):

   | Parcel | Barrio (pilot) | First lookup | Buildability | Planning and its link |
   |---|---|---|---|---|
   | Méndez Álvaro 47, `2122202VK4722A` | Atocha, Arganzuela (yes) | 11.0 s | official, 13,121 m² (VEDA) | APR.02.06, «Ficha del expediente MPR.02.391» |
   | Almería 1, `3959601VK4735H` | Fuente del Berro, Salamanca (yes) | 11.5 s | official, 32,697 m² (Portal del Suelo) | APR.04.09, the Geoportal viewer (no sheet, as in the saved sheet) |
   | Luis Misson 2, `0390314VK4709A` | Berruguete, Tetuán (yes) | 10.8 s | «Sin dato» (NZ 4 has no coefficient) | Norma zonal 4, article 8.4.9 |
   | Mayor 61, `9943003VK3794D` | Palacio, Centro (yes) | 1.6 s | «Supuesto», 224 m² (68 × 5 × 0,66) | Norma zonal 1 grado 2º, article 8.1.10 |

   - **All four:**
     - `fallback` none, `degraded` none and no warnings, so all four are live and complete;
     - the Catastro's citation «consultados el 19/11/2026»;
     - the Ayuntamiento's «Consultado el 19/11/2026», with «Información urbanística sin valor jurídico».
   - **Against the saved sheets:** their parcel, planning and buildability blocks are field for field the demo sheets in `parcel_demo.json`.
   - **Méndez Álvaro** gives Atocha, a pilot barrio, and a complete sheet.
6. **By address and by point:**
   - **`/parcels/candidates?q=Calle Mayor 61`:** 2 portals, none picked: Mayor 61 (28013) and Mayo 61 (28022). `Cache-Control: private, max-age=600`.
   - **`?address=mendez alvaro 47`:** 200, the sheet of `2122202VK4722A`, with `Cache-Control: private, no-store`.
   - **`?address=Calle Mayor 61`:** 422 `AMBIGUOUS_INPUT` with the same 2 portals, so it never picks for the person. Its `Cache-Control` is not `private, no-store` (finding 2).
   - **`?lat=40.41667&lon=-3.70361`, Puerta del Sol:** 404 «it falls on the street», with the nearest parcel, Puerta del Sol 7, at 9.9 m.
   - **`?lat=40.415579&lon=-3.709864`, Mayor 61's portal:** 200, the same sheet as by reference, with input `point`.
7. **The shareable URL:**
   - `/inversores/parcela/9943003VK3794D` answers 200 as a page, and `/inversores/parcela/abc` answers 404 without asking the API.
   - `check-parcela` opens every sheet by its URL in a new page.
   - The print view keeps its sources and notices, and «Guardar como PDF» of Mayor 61 gives 24 pages, as on the branch ([PDF](deploy-39/ficha-parcela-mayor.pdf)).
8. **#101's `check-parcela.mjs` against production:** **21/21** screens clean ([deploy-39/check-parcela-produccion.json](deploy-39/check-parcela-produccion.json)).
   - The screens are the search, its states, the 4 sheets and the print view, at 360, 390 and 1440 px.
     - In the states, the address box answers for «calle de prueba 1» (3 × 200 in the CDN records) and a reference typed wrong is rejected without asking the API.
   - On every screen: 0 texts under 16 px, 0 targets under 44 px, no horizontal overflow, axe 0 and 0 console errors.
   - The marks are «Dato», «Dato», «Sin dato» and «Supuesto».
   - A read of the 4 sheets in the page shows:
     - the planning links;
     - the Catastro's citation with its date;
     - the Ayuntamiento's «Consultado el 19/11/2026», in «Planeamiento» and in «Fuentes»;
     - no «datos guardados» notice.
9. **`/desarrolladores`:**
   - The 2 new examples, copied from the live page and run verbatim, work ([deploy-39/curls.txt](deploy-39/curls.txt)):
     - **`?rc=2122202VK4722A`:** the complete sheet in Atocha;
     - **`/candidates?q=mendez%20alvaro%2047`:** one portal, the one with that reference.
   - The other 13 examples are deploy-38's, unchanged.
   - `check-desarrolladores`: 6/6 screens clean ([deploy-39/check-desarrolladores-produccion.json](deploy-39/check-desarrolladores-produccion.json)).
10. **`check-inversores.mjs`:** 12/12 screens clean, with «Explorar barrios» ([deploy-39/check-inversores-produccion.json](deploy-39/check-inversores-produccion.json)).
11. **`check-ux-mobile.mjs`:** identical to deploy-38's apart from its timestamp ([deploy-39/tamanos-produccion.json](deploy-39/tamanos-produccion.json)).
12. **Logs from 15:28 UTC** ([deploy-39/logs.txt](deploy-39/logs.txt)):
    - **Runtime:** 640 lines, all info, with 7 instances started. 0 `WARNING`, and 0 pool, authentication or traceback lines.
    - **CDN:** 2,531 records, the whole window. 0 5xx.
    - **4xx:** only this check's deliberate 404 (Puerta del Sol) and 422 (Calle Mayor 61).
    - **499:** 1, a static chunk that a probe cancelled when it navigated.
    - **No typed address in our logs:**
      - The 7 access lines with an address say `address=[redactado]` or `q=[redactado]`.
      - The CDN and runtime records keep the path without its query.
      - No other line names a typed street.
      - The reference and the coordinates do stay in the access lines (finding 4).
    - **Firewall:**
      - all 2,531 CDN records have `wafAction: allow`;
      - `vercel firewall overview`, which is read-only, says «No rule traffic for this period».
13. **Live lookups and latency:**
    - **How many:** 13 requests reached the API's parcel code; the CDN served the rest. They were:
      - 4 sheets by reference;
      - 2 points;
      - 2 addresses;
      - 5 address boxes: 1 of mine, the page's example and 3 from `check-parcela`.
    - **Calls to the sources:** at most 13, fewer where an instance had the answer in its cache.
    - **Latency:**
      - First lookups by reference: 11.0, 11.5, 10.8 and 1.6 s. None reached the 15 s budget or degraded.
      - After that, the CDN answers in 0.26–0.28 s (`x-vercel-cache: HIT`). A complete sheet reaches the browser as `public, max-age=3600`, and Vercel keeps the `s-maxage` for itself.
      - Address boxes: 0.48–0.78 s. Points: 0.6 s.

## Screenshots in production
- **At 390 px:**
  - [the search](deploy-39/390-buscar.jpg);
  - [its states](deploy-39/390-buscar-estados.jpg);
  - [Méndez Álvaro](deploy-39/390-ficha-mendez-alvaro.jpg);
  - [Mayor 61](deploy-39/390-ficha-mayor.jpg).
- **At 1440 px:**
  - [the small map](deploy-39/1440-buscar-mapa.jpg);
  - [Almería's whole sheet](deploy-39/1440-ficha-almeria.jpg), reduced to 900 px.

## For review, not blocking
1. **The API's own timing line never reaches the logs.**
   - `parcel input=… rc14=… fallback=… ms=… upstream_ms=…` and `parcel candidates=… ms=…` are `log.info` in `hi_api.services.parcel_sheet`. Production printed 0 of them.
   - Nothing configures Python's logging. uvicorn sets up only its own loggers, so the root logger stays at WARNING and drops INFO.
   - The latencies above are measured from outside.
   - A `logging.basicConfig(level=logging.INFO)` at start-up, or a uvicorn log config, would bring them back. That is line A's call.
2. **Error answers to `?address=` lose `private, no-store`.**
   - The header is set only on a successful answer. A 422 (ambiguous), 404, 429 or 503 goes out with Vercel's default, `public, max-age=0, must-revalidate`.
   - Nothing leaks today:
     - `max-age=0` means the CDN does not keep the answer (MISS);
     - the CDN and runtime records carry no query.
   - Still, `public` goes against D-250's rule that no shared cache keeps a typed address.
   - Passing the header in the `HTTPException` of an address query would close it. That is line A's call.
3. **«Calle Mayor 61» typed exactly is ambiguous with «Calle Mayo 61» (28022).**
   - `?address=` answers 422, and the box lists both.
   - It never picks for the person, as D-250 asks. An exact match of street and number could still come first. That is line A's or line B's call.
4. **A map click's coordinates stay in the access log with 6 decimals** (`?lat=40.415579&lon=-3.709864`).
   - The filter redacts only `address` and `q`.
   - A click is not typed, but it can point at a home as precisely as an address.
   - Redacting or rounding `lat` and `lon` is Mariano's or line A's call.
5. **Three of the four first lookups took about 11 s** (10.8–11.5 s), close to the 15 s budget. Mayor 61 took 1.6 s.
   - Without the line of finding 1, the logs cannot tell whether the Catastro, the Ayuntamiento or the database took the time.
   - Repeated lookups come from the CDN or the instance's cache.

## Rollback
- **To `dpl_CXZbyzGYdHXqxszrzcTmE71i1K6U` (20b46d9):** code only, with no data and no variable to undo.
- 20b46d9 has no parcel route: before this deploy, `/api/v1/investors/parcels` answered 404. A shared `/inversores/parcela/…` link would give 404 there.
- No rollback was tested.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
