# OPS-001 (line C) · deploy of 20b46d9: «Para desarrolladores» (#97, D-249) and pitch text (#98) · 2026-11-19 (Madrid)

## What the deploy brings
- **#97, D-249:**
  - the public page `/desarrolladores`, documenting the API and the MCP, with a copyable example per route;
  - links to it from the footer and from `/inversores`;
  - two MCP tools, which do not affect the deployed API.
- **#98:** pitch text only.
- **No API, contract or data change, and no sync.**
- **Not run before merging:** line E did not run the local build, the e2e or the screenshots, because of disk; CI built the web. This deploy's verification covers them.

## Deploy · `dpl_CXZbyzGYdHXqxszrzcTmE71i1K6U` · 11:38
- **CI:** green on 20b46d9, all five jobs.
- **Deploy:** `ALLOW_BRANCH=1 make deploy-demo` from a detached checkout. Output: [deploy-38/deploy-output.txt](deploy-38/deploy-output.txt).
- **Verification:** on round 0. All 13 smoke requests came from the new deployment.
- **Disk:** the build is remote. Free disk was 2.3–2.4 GB through the deploy and every check.

## Verification, 10:38–10:46 UTC
1. **Smoke:** 13/13, `/search` included.
2. **API:** 54 answers identical to 396d8f6's without `meta`, and the same size in bytes ([deploy-38/search.txt](deploy-38/search.txt)).
   - They are deploy-37's 51 and 3 investor answers: the zone list, Pinar del Rey's sheet and one viability.
   - Only `request_id` and `generated_at` change.
3. **Golden:** 10/10 through the public API, identical line by line ([deploy-38/golden-api.txt](deploy-38/golden-api.txt)).
4. **e2e:** **123/123** at 1440 px and **99/99** at 390 px, with 0 console errors ([report](deploy-38/e2e-report.json)). The new journey J8 passes its 7 checks at both widths:
   - «Para inversores» links to `/desarrolladores`;
   - 13 routes, each with its curl against the public API;
   - every example has its «Copiar»;
   - the MCP's 7 tools;
   - the 4 planned items say «Aún no disponible»;
   - the footer links to the page;
   - no horizontal overflow.
5. **#97's `check-desarrolladores.mjs` against production:** 6/6 screens clean ([deploy-38/check-desarrolladores-produccion.json](deploy-38/check-desarrolladores-produccion.json)).
   - The screens are the page and the page after «Copiar», each at 360, 390 and 1440 px.
   - On every screen: 0 texts under 16 px, 0 targets under 44 px, no horizontal overflow, axe 0 and 0 console errors.
   - The clipboard text equals the example shown.
   - The footer's licence citations are shared by every page, so the script counts them apart: 1 at 360 px, 2 at 390 px and 4 at 1440 px.
   - On a phone, the long curl lines scroll inside their own code box, and the page never overflows.
6. **The printed examples:** four of the page's curls, copied from the live page and run verbatim ([deploy-38/curls.txt](deploy-38/curls.txt)). Every result matches [desarrolladores.md](../2026-11-19-desarrolladores/desarrolladores.md).
   - **`POST /search`:** 140 KB, 10 results, Puente de Vallecas 1st.
   - **`GET /gaps/municipio/28106`:** Parla, with Farmacias and Vivienda para familias at FALTA and the rest at JUSTO.
   - **`GET /investors/zones/ES.28.BAR.28079164`:** Pinar del Rey, with no warnings.
   - **`POST /investors/viability`:** 15,1 % «Ajustar», 22,8 % «Sale» and 5,6 % «No sale».
7. **`check-inversores.mjs`:** 12/12 screens clean, with 0 console errors ([deploy-38/check-inversores-produccion.json](deploy-38/check-inversores-produccion.json)). The run adds 360 px.
8. **`check-ux-mobile.mjs`:**
   - 0 texts under 16 px and 0 targets under 44 px on the 24 screens, and axe 0;
   - its output is identical to deploy-37's ([deploy-38/tamanos-produccion.json](deploy-38/tamanos-produccion.json)).
9. **Logs from 10:35 UTC** ([deploy-38/logs.txt](deploy-38/logs.txt)):
   - **Runtime:** 600 lines, all info, with 7 instances started. 0 `WARNING`, and 0 pool, authentication or traceback lines.
   - **CDN:** 1,944 records, the whole window. 0 4xx and 0 5xx.
10. **Firewall:** the log-only rule, live since ~11:00 as datamad-10 reported it, counts more than 300 requests to `/api/v1/` in 60 s per IP. It had no hits during this run.
    - All 1,944 CDN records have `wafAction: allow`, and none has `log`.
    - `vercel firewall overview`, which is read-only, lists 1 active rule and «No rule traffic for this period», for 18 Nov 10:00 to 19 Nov 11:00 UTC.
    - The busiest 60 s on `/api/v1/`, all clients together, had 118 requests.

## Screenshots of `/desarrolladores`
In [2026-11-19-desarrolladores](../2026-11-19-desarrolladores/):
- at 390 px:
  - [the first screen](../2026-11-19-desarrolladores/390-01-portada.jpg);
  - [the search example](../2026-11-19-desarrolladores/390-02-ejemplo-search.jpg);
  - [«Copiado»](../2026-11-19-desarrolladores/390-03-copiado.jpg);
  - [the MCP](../2026-11-19-desarrolladores/390-04-mcp.jpg);
  - [«Planteado»](../2026-11-19-desarrolladores/390-05-planteado.jpg);
- at 1440 px: [the whole page](../2026-11-19-desarrolladores/1440-01-pagina-entera.jpg).

## Rollback
To `dpl_GAcSQGpjuj7AKa178gFS2Yq1kNRU` (396d8f6): code only, and no data or API changed.

## Not done
The offline package was not rebuilt. It is still at 39644a9.
