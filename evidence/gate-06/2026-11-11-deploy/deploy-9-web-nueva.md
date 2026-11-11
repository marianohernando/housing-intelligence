# OPS-001 (line C) · new Vida Fácil web (PR #2, bd5b006) and GAP-001 F5 (gap-0.2) in production · 2026-11-11 20:13 UTC

## What was deployed
`41aa7d1` = origin/claude/sprint-1-public `f1b487a` + line C's 3 commits of PR #8 (smoke, guide, `deploy.sh`). The app code is the integration branch's. It includes:
- the new web of line B (MAP-004, PUB-001, merge `bd5b006`);
- GAP-001 F4 (`/gaps?level=&row=`) and F5 (method `gap-0.2`, D-213).

Gate after the rebase: `make lint typecheck test-unit` green, with 327 Python tests and 172 web tests. The first typecheck failed only locally, for two reasons:
- the new web dependencies (`lucide-react` and others) were not installed in this worktree; `make web-install` fixed it;
- a stale `apps/web/.next/types` still pointed to the old `src/app/page`; removing the ignored cache fixed it.

## Attempt 1: the web build failed on Vercel (production unchanged)
`dpl_4c6v2BDDUNkXWffnMHREF7uzAxQ8`, after 30 s:
```
Error: Turbopack build failed with 8 errors:
[next]/internal/font/google/plus_jakarta_sans_9700e99a.module.css:7:8
Error: Module not found: Can't resolve '@vercel/turbopack-next/internal/font/google/font'
>  7 |   src: url(@vercel/turbopack-next/internal/font/google/font?{%22url%22:%22https://fonts.gs...
next/font/google queries have exactly one entry
```
- The same commit built locally (`next build`, Next.js 16.4.2, Turbopack).
- The font CSS was downloaded. What failed was resolving the font file from the URL Google returned to the build machine (cle1). The log truncates that URL, so the exact cause is not confirmed.
- A failed build is never promoted, so the previous deployment kept serving.

## Attempt 2: same commit · 134 s · verified on the first round
```
-> deploying 41aa7d1 (claude/s1-deploy) to production
-> deployment dpl_CSPfjJ9JDvw6uDfszQ3HEfE4ro6J is ready
-> smoke test against https://vidafacil-madrid.vercel.app
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T20:17:02Z) tag dpl_CSPfjJ9JDvw6uDfszQ3HEfE4ro6J-0
OK   web         0.53s     25618 B  /
OK   health      4.15s       225 B  /api/v1/health  process up
OK   ready       0.50s       225 B  /api/v1/health/ready  database and geography visible
OK   zone        1.72s     23986 B  /api/v1/gaps/municipio/28079  Madrid: 6 rows
OK   geography   1.04s    331914 B  /api/v1/geo/admin-units?level=municipio&simplify_m=50  179 municipios
OK   layer       0.58s   1156882 B  /api/v1/places?category=education  3851 places
OK   largest     1.76s   1407222 B  /api/v1/places?category=transport  14982 stops, page 1/3
smoke: 7/7 OK
-> which deployment served the smoke (vercel logs requests, tag dpl_CSPfjJ9JDvw6uDfszQ3HEfE4ro6J-0)
   7 from dpl_CSPfjJ9JDvw6uDfszQ3HEfE4ro6J (this deploy)
-> verified: https://vidafacil-madrid.vercel.app serves dpl_CSPfjJ9JDvw6uDfszQ3HEfE4ro6J, and the smoke passed against it
```
The page `/` grew from 5,596 B (old web) to 25,618 B (new web).

## Browser checks against production (Playwright 1.63, Chromium; desktop 1440×900, mobile 390×844)
Full results: [web-prod-check.json](web-prod-check.json).

| Check | Desktop | Mobile |
|---|---|---|
| Home title | «Vida Fácil · Encuentra tu sitio en Madrid» | same |
| «Housing Intelligence» on the home page | no | no |
| Map canvas on the home page | yes | yes |
| Search button | «Ver zonas que encajan · Muy pronto», disabled | same |
| Chamartín (`/zona/distrito/2807905`), card «Qué falta aquí» | 3 rows and «Ver todo lo que falta» | same |
| «Qué falta en Chamartín» (`/que-falta?zona=distrito/2807905`) | 6 rows | 6 rows |
| Horizontal overflow | 0 px | 0 px |
| Console errors, page errors, failed requests, HTTP ≥ 400 | none | none |
| Requests to `/search` | none | none |
| Origin of the API calls | `https://vidafacil-madrid.vercel.app` only | same |
| Calls to localhost | none | none |

The 6 rows are «Centros de salud», «Centros de mayores», «Escuelas infantiles», «Colegios», «Farmacias» and «Vivienda para familias».

Notes:
- `NEXT_PUBLIC_API_URL` is set in Vercel (Production), and every API call goes to the public domain. No configuration change was needed.
- The bundle still holds the literal `http://localhost:8010`. It is the exported fallback `DEFAULT_API_URL` from `src/lib/geo.ts`, and it is never called.
- `NEXT_PUBLIC_FEATURE_SEARCH` is not defined in Vercel, so search stays off.
- The footer reads «Vida Fácil · Plataforma Housing Intelligence · Proyecto para DATAMAD 2026», on purpose, from line B. The legacy route `/map` still has the title «Mapa — Housing Intelligence».

Screenshots:
- Home: [desktop](web-prod-inicio-desktop.png) · [mobile](web-prod-inicio-mobile.png)
- Chamartín: [desktop](web-prod-chamartin-desktop.png) · [mobile](web-prod-chamartin-mobile.png)
- «Qué falta» in Chamartín: [desktop](web-prod-que-falta-chamartin-desktop.png) · [mobile](web-prod-que-falta-chamartin-mobile.png)

## GAP-001 F5 is served (the Supabase sync with counts is done)
- `GET /api/v1/gaps/distrito/2807905`: `meta.methodology_version` is `gap-0.2`, and the reference is «Otros municipios urbanos de la Comunidad de Madrid».
- Chamartín rows:
  - escuela_infantil: CUBIERTO, 1.024
  - colegio: CUBIERTO, 1.046
  - centro_salud: **JUSTO**, 0.8446 (FALTA under gap-0.1)
  - mayores: JUSTO, 0.6681
  - farmacia: CUBIERTO, 2.501
  - vivienda: SIN_DATOS
- Supabase (read-only MCP): 61,935 rows in `feature_value`, 1,744 of them with `inputs.counts`, last computed 2026-11-11 17:48 UTC.
