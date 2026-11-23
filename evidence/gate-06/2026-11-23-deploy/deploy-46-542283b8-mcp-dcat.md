# OPS-001 (line C) · deploy of 542283b8: the remote MCP (#123), the DCAT-AP and SDM files (#124), the final texts (#126) · 2026-11-23 (Madrid)

**Status:** in production and verified.
- Smoke 15/15, with the 2 new MCP checks. The golden 10/10 and the 62 API answers are identical to before the deploy.
- The four demo sheets come out complete and in the CDN.
- The scripts: `check-parcela` 21/21, `check-inversores` 12/12 and `check-desarrolladores` 6/6.
- The e2e from the repo gives **139/139** and **119/119**, complete.
- **The remote MCP works** at `https://vidafacil-madrid.vercel.app/api/v1/mcp`:
  - `initialize`, `tools/list` (7) and three `tools/call`;
  - `claude mcp add --transport http` and the tool list from Claude Code.
- The three `/datos/` files answer 200 and parse as JSON.
- deploy-46's own checks on screen: 34/34.

**One finding about the MCP** (not critical): Claude Code keeps one request open until Vercel's 300 s limit (see «The remote MCP», point 5).

**No migration, no sync and no new variable.** `MCP_ALLOWED_HOSTS` was not needed: the container receives the public Host.

## What was deployed
- **542283b8** is the head of `claude/sprint-1-public`: the merge of #126 on top of #123, #124 and #125.
  - CI on 542283b8: green in all five jobs.
  - #123's own push run was cancelled when #125 merged on top. 542283b8 carries it, with CI 5/5.
- **#123, D-255:** the API container runs `hi_mcp.http:app`, which is the API unchanged plus `POST /api/v1/mcp`.
  - It speaks Streamable HTTP, stateless, with JSON answers and no key.
  - If the MCP fails, the API still runs.
  - The smoke gets `mcp-init` and `mcp-tools`.
- **#124:**
  - three static files: `/datos/catalogo.dcat.jsonld`, `/datos/sdm/datasets.json` and `/datos/sdm/farmacias.json`;
  - their links in `/desarrolladores`.
- **#125:** deploy-45's evidence.
- **#126:**
  - `/desarrolladores` announces the remote MCP («Funciona hoy») and keeps 3 planned items;
  - the investors' «plan empresarial e informes personalizados»;
  - no «no es casualidad»;
  - the e2e updated for J8 and J9.

## Deploy · `dpl_GyEfen16H6Kxbcng13cABR124UY6` · 12:17 Madrid (11:17 UTC)
- **Command:** `ALLOW_BRANCH=1 make deploy-demo`, from a detached and clean checkout. Output: [deploy-46/deploy-output.txt](deploy-46/deploy-output.txt).
- **Verification:** on round 1.
  - In round 0, 5 of the 15 smoke requests still came from 861f94f0's deployment.
  - In round 1, all 15 came from the new one.
- **Time:** 2 min 34 s. Free disk stayed at about 7 GB.

## Verification, 11:13–11:27 UTC
1. **Smoke:** 15/15.
   - The first 13 checks have the same bytes as in deploy-45.
   - `mcp-init`: «vida-facil 0.0.1, protocol 2025-06-18», 1.739 B, in 0.14–0.27 s.
   - `mcp-tools`: «7 tools», 95.074 B, in 0.17–0.18 s.
2. **The API before and after the deploy:** **62 of 62 identical** without `meta`, with deploy-45's 62 requests ([deploy-46/search.txt](deploy-46/search.txt)).
   - `/api/v1/openapi.json` is identical too: the MCP is not in it, and no API route changed.
3. **Golden:** 10/10 through the public API ([deploy-46/golden-api.txt](deploy-46/golden-api.txt)), identical to before the deploy and to deploy-45's.
4. **The four demo sheets, warmed by reference once each** ([deploy-46/parcelas-en-vivo.txt](deploy-46/parcelas-en-vivo.txt)):
   - all four `degraded=-`, no warnings, `public, max-age=3600`, and the second visit «HIT» in 0.10–0.13 s;
   - each one identical, without `meta`, to deploy-45's: `sale_price_m2.mark` «estimacion», and no «vigente en 2025»;
   - the first lookup took 7.7–10.7 s, and Mayor 61 1.5 s. The slow part is still sigma's Z when cold.
5. **The remote MCP:** see the next section and [deploy-46/mcp.txt](deploy-46/mcp.txt).
6. **DCAT-AP and SDM** ([deploy-46/datos.txt](deploy-46/datos.txt)). Before the deploy, all three were 404.

   | Path | HTTP | `Content-Type` | Bytes | Content |
   |---|---|---|---|---|
   | `/datos/catalogo.dcat.jsonld` | 200 | `application/ld+json` | 236.366 | 1 `dcat:Catalog`, 1 `dcat:DataService`, 62 `dcat:Dataset` |
   | `/datos/sdm/datasets.json` | 200 | `application/json; charset=utf-8` | 66.784 | 39 `Dataset` (dataModel.DCAT-AP 3.0.0), with MELODA |
   | `/datos/sdm/farmacias.json` | 200 | `application/json; charset=utf-8` | 1.719.965 | 2.957 `PointOfInterest` (dataModel.PointOfInterest 0.3.1) |

   - All three parse as JSON and have the same bytes as `apps/web/public/datos/` in the repo.
   - The 3 links of `/desarrolladores` reach them, at 1440 and 390 px.
7. **#123, #124 and #126 on screen, at 1440 and 390 px:** 34/34 ([deploy-46/probe-d46.json](deploy-46/probe-d46.json), script [deploy-46/probe_d46.mjs](deploy-46/probe_d46.mjs)).
   - **`/desarrolladores`:**
     - «El MCP, para agentes de IA» is marked «Funciona hoy»;
     - it shows the URL `https://vidafacil-madrid.vercel.app/api/v1/mcp`, the `claude mcp add --transport http vida-facil …` command, the `npx -y mcp-remote …` bridge and «Sus 7 herramientas»;
     - «planteado» has 3 items, none of them the remote MCP;
     - the 3 `/datos/` links are there;
     - no horizontal overflow.
   - **`/inversores`:** «Para inversores y promotores habrá un plan empresarial e informes personalizados», and no «plan de pago».
   - **`/como-lo-calculamos`:**
     - no «no es casualidad»;
     - «demasiado grande para explicarla por el tamaño de la zona» appears twice: in the steps and in the example.
     - The home doesn't have «no es casualidad» either.
   - 0 console errors.
8. **The scripts against production:**
   - `check-parcela`: **21/21** ([report](deploy-46/check-parcela-produccion.json)).
   - `check-inversores`: **12/12** ([report](deploy-46/check-inversores-produccion.json)).
   - `check-desarrolladores`: **6/6** at 360, 390 and 1440 px, with the copy buttons used ([report](deploy-46/check-desarrolladores-produccion.json); the repo's URL is written as `<REPO_URL>`).
   - On every screen: 0 texts under 16 px, 0 targets under 44 px, no horizontal overflow and axe 0.
9. **e2e from the repo:** **139/139** at 1440 px and **119/119** at 390 px, with 0 console errors ([report](deploy-46/e2e-report.json)).
   - The same checks as deploy-45's adjusted run. The one difference is J8: «the MCP: 7 tools, remote at /api/v1/mcp and local (D-255)».
   - J9 now expects Mayor 61's calculator at «Sin dato» (bc84d3b0).
10. **Live lookups: 7.**
    - What they were: the 4 sheets by reference and check-parcela's 3 address boxes (2 of those from the API's own cache).
    - The MCP calls no upstream source.
11. **Logs, 11:17–11:26 UTC** ([deploy-46/logs.txt](deploy-46/logs.txt)):
    - **Runtime:** 0 warning, error, pool, authentication, «Invalid Host», «not built» or «did not start» lines. So the MCP was built and started on all 7 new instances.
      - The `hi_mcp` lines give the tool and its time, never the arguments.
      - No coordinates and no typed text.
    - **CDN:** 2.084 records. All but 5 came from the new deployment; the 5 were smoke round 0.
      - Status: 200 × 1.979, 304 × 99, 403 × 1 and 405 × 5. **0 5xx.** WAF: all `allow`.
    - **«Visitantes sin identificar (Chrome/Windows)»:** 3 `GET /api/v1/mcp` at 11:20, 11:21 and 11:25 UTC, each with another Chrome version and from a US connection. Each was answered 405. Who they were is not known.

## The remote MCP ([deploy-46/mcp.txt](deploy-46/mcp.txt))
1. **`initialize`:** 200, `application/json`, no `Mcp-Session-Id`.
   - `serverInfo.name` «vida-facil», version 0.0.1, protocol 2025-06-18.
   - It carries the server's instructions (1.432 characters).
2. **`tools/list`:** 200, 95.074 B, **7 tools**: `buscar_zonas`, `que_falta`, `explicar_zona`, `encontrar_zona`, `fuentes_de_datos`, `ficha_inversor` and `viabilidad`. All are `readOnlyHint: true` and `openWorldHint: false`.
3. **`tools/call`:**
   - `fuentes_de_datos {cm_only: true}`: 39 datasets, 39 from the Comunidad, in 0.04 s.
   - `encontrar_zona {name: Chamartín}`: distrito 2807905, in 0.02 s.
   - `que_falta {level: distrito, code: 2807905}`: `gap-0.4`, with escuela infantil JUSTO and vivienda SIN_DATOS, in 0.09 s. Its `structuredContent` is identical, without `meta`, to `GET /api/v1/gaps/distrito/2807905`.
4. **Hosts, origins and methods:**
   - `vidafacil-madrid` and `vida-facil-eight`: 200. `Origin: https://claude.ai`: 200. `Origin: https://evil.example`: 403.
   - GET and OPTIONS: 405, with `Allow: POST`. A notification: 202, empty.
   - **The 421 cannot be reached in production.** Vercel's edge routes by Host, so `Host: evil.example` gets Vercel's own 404 (`DEPLOYMENT_NOT_FOUND`) and never reaches the container.
   - **The 421 on the same commit, run locally:** with `uvicorn hi_mcp.http:app`, `Host: evil.example` and `vidafacil-madrid.vercel.app.evil.example` give 421 «Invalid Host header», and the two public hosts give 200. `tests/unit/mcp/test_http.py` passes 18 of 18.
   - Production receives the public Host, so `MCP_ALLOWED_HOSTS` was not set.
5. **Claude Code 2.1.326 as a client:**
   - `claude mcp add --scope project --transport http vida-facil https://vidafacil-madrid.vercel.app/api/v1/mcp`, in a temporary folder, writes `.mcp.json`. `claude mcp list` shows the server «Pending approval», because a project server needs an interactive approval.
   - The same server passed with `--mcp-config`, through `claude -p`, lists **the 7 tools** as `mcp__vida-facil__*`.
   - Nothing was written to the user's configuration, and the folder was deleted.
   - **Finding: one request stays open until Vercel's 300 s limit.**
     - Claude Code speaks protocol 2026-07-28. Of its 5 POSTs, `subscriptions/listen` gets an SSE stream from the server (mcp 2.3.0) that stays open, waiting for list-changed notifications.
     - In production it lasted from 11:21:41.594 to 11:26:41.646, **exactly 300 s**, although `claude -p` had exited within seconds.
     - While it is open, Vercel also attributes every log line of that instance to it, so those lines appear twice in `vercel logs`.
     - Reproduced locally with a wrapper that logs the requests: that POST's body goes out with `more_body=True` and only ends when the client disconnects.
     - **Impact:** the MCP works. Each Claude Code session holds one container request for up to 5 min, and the instance keeps serving other requests meanwhile.

## Screenshots in production (1440 px)
- [`/desarrolladores`: «El MCP, para agentes de IA», «Funciona hoy», the remote URL, Claude Code, `mcp-remote` and the 7 tools](deploy-46/1440-desarrolladores-mcp-remoto.jpg). The image is cut before «También en tu ordenador», because the `git clone` line there carries the repo's URL.

## For review
1. **Claude Code's `subscriptions/listen` stream stays open for 300 s on Vercel** (above).
   - Options for #123's owner:
     - answer `subscriptions/listen` without a lasting stream;
     - or don't announce `listChanged`;
     - or accept it, and know that `vercel logs` counts repeat lines while one is open.
2. **The 421 cannot be checked in production:** Vercel answers an unknown Host before the container does. It is covered locally and by the unit tests.
3. **Claude Code's command, `claude mcp add --transport http vida-facil https://…/api/v1/mcp`, does not fit its code block at 1440 px.** It scrolls inside the block (the page does not overflow), and «Copiar» copies it whole.
4. **A first lookup still takes 7.7–10.7 s,** because of sigma's Z when cold. The 4 demo sheets are warm now.
5. The registry sync is still pending (`/datasets` 59). The offline package was not rebuilt (39644a9).

## Rollback
- **To `dpl_5EoD1qfUSF3Ltud8ZEifSf7fPko6` (861f94f0):** code only, with no data and no variable to undo: `npx vercel@65.12.1 rollback`.
- A rollback takes away the remote MCP (`/api/v1/mcp` gives 404 again), the `/datos/` files and #126's texts.
- No rollback was needed or tested.
