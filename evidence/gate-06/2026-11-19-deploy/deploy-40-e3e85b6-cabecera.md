# OPS-001 (line C) · deploy of e3e85b6: «Inversores» in the header and the investor method (#104, D-251), pitch (#103, #106) · 2026-11-19 (Madrid)

## What the deploy brings
- **#104, D-251:**
  - an «Inversores» tab in the site header on every page, the map included. Below 760 px, the header over the map gets an almost opaque gradient (98 %);
  - a new section, «Cómo calculamos la ficha para inversores», at `/como-lo-calculamos#inversores`. Its figures come from `apps/web/src/lib/investorMethod.ts`, which `scripts/export_investor_data.py` generates;
  - a «Cómo lo calculamos» link to that section in a parcel's sheet and under a barrio's calculator, hidden in print;
  - `/desarrolladores` links `main` (`REPO_BRANCH`), and its `git clone` has no `--branch`;
  - the API only moves its 15 s budget to `hi_domain.parcels.LOOKUP_BUDGET_S`. It answers the same.
- **#103 and #106:** pitch files only.
- **No data sync and no new variable.**

## Deploy · `dpl_FCcfhjEZYiTgNic444FexZDU34Ds` · 18:24
- **CI:** green on e3e85b6, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-40/deploy-output.txt](deploy-40/deploy-output.txt).
- **Verification:** on round 1.
  - In round 0, 2 of the 13 smoke requests still came from 79020a1's deployment: the usual domain switch.
  - In round 1, all 13 came from the new one.
- **Disk:**
  - The build is remote, and the deploy left no local artefact.
  - Free disk fell from 3.9 to 2.9 GB during the deploy, because another session's Docker disk grew.
  - It was back at 3.9 GB by the end, and never went under the 2 GB floor.

## Verification, 17:24–17:50 UTC
1. **Smoke:** 13/13, `/search` included.
2. **API:** 54 answers identical to 79020a1's without `meta`, and the same size in bytes. They are deploy-39's 54 ([deploy-40/search.txt](deploy-40/search.txt)).
3. **Golden:** 10/10 through the public API, identical line by line to before the deploy and to deploy-39's ([deploy-40/golden-api.txt](deploy-40/golden-api.txt)).
4. **The header: #104's `check-cabecera.mjs` against production, 15/15** ([deploy-40/check-cabecera-produccion.json](deploy-40/check-cabecera-produccion.json)).
   - It covers 5 pages at 360, 390 and 1440 px: the map, «Qué falta», «Cómo lo calculamos», `/inversores` and a demo parcel's sheet (`/inversores/parcela/2122202VK4722A`).
   - **On every screen:**
     - the 4 tabs in one row, inside the screen;
     - 0 texts under 16 px and 0 targets under 44 px in the header;
     - no horizontal overflow;
     - axe 0;
     - the active tab marked with `aria-current`, a tint and a ring.
   - **The active tab is the right one on every page:** «Mapa», «Qué falta», «Cómo lo calculamos», «Inversores», and «Inversores» again on the parcel's sheet.
     - The script only requires that some tab is active.
     - The expected tab for each page was checked against its report.
   - **Contrast of each tab's letters over the pixels behind them, the worst pixel counting:**
     - over the map: 5.48:1 at 360 and 390 px, and 5.51:1 at 1440 px;
     - on the other pages: 5.62–5.67:1.
     - #104 measured 5.48:1 over the map locally.
   - The production copy of the script adds only a smoke User-Agent and writes `base: "production"`.
5. **`/como-lo-calculamos#inversores`** ([deploy-40/metodo-y-enlaces-produccion.json](deploy-40/metodo-y-enlaces-produccion.json)):
   - **Where it opens:** at 390 and 1440 px, the heading «Cómo calculamos la ficha para inversores» lands at the top of the screen, both from the address and from the parcel sheet's link.
     - The header does not stick, so nothing covers the heading.
   - **The figures, as `investorMethod.ts` gives them:**
     - «uno de los 108 del piloto»;
     - «(1.109 parcelas, de vivienda y de otros usos)» for VEDA;
     - «(50 parcelas de Madrid capital)» for the Portal del Suelo;
     - «644 €/m², 2025» for the PEM, with its link to the Comunidad's dataset 1006022.
6. **One «Cómo lo calculamos» link to `#inversores`:**
   - **The parcel sheet `2122202VK4722A`, at 390 and 1440 px:**
     - exactly one link to `/como-lo-calculamos#inversores`, at the end of «3. Edificabilidad»;
     - its text is «Cómo lo calculamos», and its accessible name «Cómo lo calculamos: la ficha para inversores»;
     - it is visible on screen and hidden in print;
     - the calculator in the sheet adds none.
     - The page's two other links to `/como-lo-calculamos` carry no anchor: one is the header tab, the other belongs to the site's own navigation.
   - **A barrio's sheet, `/inversores/28079164`:** one link, the calculator's, hidden in print.
7. **e2e:** **145/145** at 1440 px and **121/121** at 390 px, with 0 console errors ([report](deploy-40/e2e-report.json)). J9, «Busca tu parcela», passes at both widths.
8. **The other scripts against production:**
   - `check-parcela.mjs`: **21/21** ([deploy-40/check-parcela-produccion.json](deploy-40/check-parcela-produccion.json));
   - `check-inversores.mjs`: **12/12** ([deploy-40/check-inversores-produccion.json](deploy-40/check-inversores-produccion.json));
   - `check-desarrolladores.mjs`: **6/6** ([deploy-40/check-desarrolladores-produccion.json](deploy-40/check-desarrolladores-produccion.json)).
   - On every screen: 0 texts under 16 px, 0 targets under 44 px, no horizontal overflow, axe 0 and 0 console errors.
   - `check-ux-mobile.mjs` is identical to deploy-39's apart from its timestamp ([deploy-40/tamanos-produccion.json](deploy-40/tamanos-produccion.json)).
9. **`/desarrolladores` and the repo** ([deploy-40/enlaces-repo.txt](deploy-40/enlaces-repo.txt)). `<REPO_URL>` is `REPO_URL` in `apps/web/src/lib/developers.ts`.
   - **The clone line:** `git clone <REPO_URL>.git`, with no `--branch`.
   - **The links:**
     - 6 point to `blob/main/…` or `tree/main/…`;
     - the other 2 are the repo and its issues;
     - none names `claude/sprint-1-public`.
   - **Today:** all 6 paths exist in `main`, and GitHub answers 200.
   - **But `main` is still d60c180 (14 Nov), 337 commits behind e3e85b6.** Until #105 is merged, the clone and four of the links give older content than production serves:
     - `31_public_api_routes.md` and `32_mcp_server.md`;
     - 27 files of `data/catalog/datasets`;
     - 12 of `data/schemas/api`.
10. **The four demo parcels** ([deploy-40/parcelas-en-vivo.txt](deploy-40/parcelas-en-vivo.txt)):
    - **Live lookups of this run:** **7** reached the API's parcel code, under the ~10 allowed. They were:
      - each demo sheet the first time the new deployment was asked for it: 2 from the e2e and 2 from `check-parcela`;
      - `check-parcela`'s 3 address boxes («calle de prueba 1»).
      - Every other sheet came from the CDN (`x-vercel-cache: HIT`).
      - No address, point or candidates lookup of my own.
    - **First lookups, from the CDN's request record to uvicorn's access line:**
      - Méndez Álvaro 0.9 s;
      - Mayor 61 10.0 s;
      - Almería 11.4 s;
      - Luis Misson 10.2 s.
      - None reached the 15 s budget.
    - **Address boxes:** 0.42 s for the first, then 0.05 and 0.03 s.
    - **The 4 sheets read again from the CDN** take 0.11–0.43 s. Each has:
      - `fallback` none, `degraded` empty and no warnings;
      - the same blocks as deploy-39's live answers, dates aside.
11. **Logs from 17:22 UTC** ([deploy-40/logs.txt](deploy-40/logs.txt)):
    - **Runtime:** 795 lines, all info, with 10 instances started. 0 `WARNING`, and 0 pool, authentication or traceback lines.
    - **CDN:** 3,244 records, the whole window (2 pages), every one from the new deployment.
      - **0 4xx and 0 5xx:** 200 × 3,091, 206 × 3 and 304 × 150.
      - **WAF:** all `allow`. `vercel firewall overview`, which is read-only, says «No rule traffic for this period» and 0 attacks mitigated.
    - **No typed address in our logs:**
      - the CDN and runtime records keep the path without its query;
      - the 10 access lines of address boxes say `q=[redactado]`;
      - the only lines with «calle» are the feature `pct_calle_ruido_*`.
    - **A visitor:** at 17:32–17:33 UTC, someone on a phone used the parcel search (7 address boxes and 1 sheet).
      - It was not one of this run's scripts: it was Safari on an iPhone, and it sent the Web Analytics page view, which headless browsers do not send.
      - Their lines are counted in `logs.txt`.
      - Their reference is not shown, and their address boxes are redacted.

## Screenshots in production
- **At 390 px:**
  - [the map's first screen with the four tabs](deploy-40/390-mapa-primera-pantalla.jpg);
  - [the parcel sheet's «Cómo lo calculamos»](deploy-40/390-ficha-enlace-metodo.jpg);
  - [the method section: the data and the buildable area](deploy-40/390-metodo-inversores-1-2.jpg);
  - [the method section: the construction cost, 644 €/m²](deploy-40/390-metodo-inversores-3-coste.jpg).
- **At 360 px:**
  - [the map's first screen](deploy-40/360-mapa-primera-pantalla.jpg);
  - [the header on a parcel's sheet, «Inversores» active](deploy-40/360-cabecera-parcela.jpg).
- **At 1440 px:**
  - [the header over the map](deploy-40/1440-cabecera-mapa.jpg);
  - [`/inversores`' first screen](deploy-40/1440-inversores-primera-pantalla.jpg).

## For review, not blocking
1. **Until #105 is merged into `main`, `/desarrolladores` sends people to `main` at 14 Nov** (point 9). datamad-10 merges it right after this verification. The links' format is already right.
2. **The CDN cache starts empty with each deployment.**
   - After a deploy, the first lookup of each demo parcel goes live again: this time 10–11 s for 3 of the 4.
   - Before showing the demo, or after any deploy close to it, open the 4 demo sheets once. The CDN keeps a complete sheet for a day (`s-maxage=86400`), and then serves it in 0.1–0.4 s.
3. **Deploy-39's findings are still open.**
   - The API's own timing line is still not logged (finding 1), so the latencies above are estimated from the logs.
   - The slow first lookup moved: Méndez Álvaro was 11 s yesterday and 0.9 s today; Mayor 61 was 1.6 s and is now 10 s. So the ~10 s does not belong to a parcel.
   - Findings 2–4 were not re-tested: no address or point lookups this time, to stay within the lookup limit. The code they touch did not change.

## Rollback
- **To `dpl_7ySG3suaT3tXBGJHRZ6Ar3eu9YEN` (79020a1):** code only, with no data and no variable to undo.
- **What a rollback would change:**
  - the header loses «Inversores»;
  - `/como-lo-calculamos#inversores` opens the page without that section;
  - `/desarrolladores` goes back to the branch links.
- No rollback was tested.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
