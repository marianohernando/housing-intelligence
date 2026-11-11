# OPS-001 (line C) · search turned on in production (NEXT_PUBLIC_FEATURE_SEARCH=true) · 2026-11-11 22:26 UTC

## What was deployed
`b930765` = origin/claude/sprint-1-public `22b464e` + the line C evidence commit. It includes:
- PR #9 (`9722944`): the map by row, the small-zone state, local fonts, and `/map` redirecting to the home page;
- PR #10 (`22b464e`): search, ranking and «¿Y si cambias algo?».

Vercel, Production: `NEXT_PUBLIC_FEATURE_SEARCH` was added with value `true` as a Config variable (not Secret), via `vercel env add … --environment production --no-sensitive`. It is baked in when the web is built.

Gate: `make lint typecheck test-unit` green, with 367 Python tests and 226 web tests.

## make deploy-demo (ALLOW_BRANCH=1) · 90 s · exit 0 · verified on the first round
```
-> deploying b930765 (claude/s1-deploy) to production
-> deployment dpl_21KYC4aXC9r5EmVWDFGc5m9kUwZJ is ready
smoke: https://vidafacil-madrid.vercel.app (2026-11-11T22:27:31Z) tag dpl_21KYC4aXC9r5EmVWDFGc5m9kUwZJ-0
smoke: 7/7 OK
-> which deployment served the smoke (vercel logs requests, tag dpl_21KYC4aXC9r5EmVWDFGc5m9kUwZJ-0)
   7 from dpl_21KYC4aXC9r5EmVWDFGc5m9kUwZJ (this deploy)
-> verified: https://vidafacil-madrid.vercel.app serves dpl_21KYC4aXC9r5EmVWDFGc5m9kUwZJ, and the smoke passed against it
```

## Checks
- **Fonts:** the build log of `dpl_21KY…` (169 lines) never mentions `fonts.googleapis`, `fonts.gstatic` or `next/font/google`. The build compiled in 4.1 s and completed in 50 s. In the browser there were 0 requests to Google Fonts, on desktop and on mobile.
- **`/map`:** HTTP 307 to `https://vidafacil-madrid.vercel.app/`, which answers 200.
- **Browser checks:** B's `apps/web/scripts/check-search.mjs`, copied and pointed at production, plus the row selector and Google font requests. Full results: [prod-buscador-check.json](prod-buscador-check.json).

| Check | Desktop 1440 px | Mobile 390 px |
|---|---|---|
| «¿Qué quieres ver?» → «Colegios» | `GET /api/v1/gaps?level=distrito&row=colegio` and `…level=municipio&row=colegio` return 200. Legend: FALTA 1 zone · JUSTO 30 · CUBIERTO 28 · small zone for comparing 140 · SIN DATOS 0 | — |
| «Ver un ejemplo» (couple with 2 children, the Castellana) | «Con tu búsqueda tal cual salen 32 zonas.» API: 32 of 199, 15 unknown, 1st **Ciudad Lineal 99 %**, Chamartín 8th (95 %) | 32 zones, the result in view |
| Legend count = API count | yes | — |
| «¿Y si cambias algo?» | Shown: «+5 min a pie hasta colegio con primaria: saldrían 49 zonas, 17 más». Applied with the keyboard: 49 zones, minutes 10 → 15. Undone: 32 zones, minutes 15 → 10, focus on «Zonas que encajan» | shown and unfolded |
| `/search` requests and `max_minutes` | 6 requests, every anchor with `max_minutes: null` | 1 request, `null` |
| Console errors | 0 | 0 |
| Horizontal overflow | 0 px | 0 px |
| axe WCAG 2.2 AA | 0 violations (home, results, zone card, buying) | 0 (results, zone card) |

The check also covered «Trabajo en» with the keyboard and buying: «Sin datos», «no sale ninguna zona», with 48 zones unknown.

## Screenshots of production
- Search with the demo case: [desktop](prod-buscador-c1_busqueda_desktop.png) · [mobile](prod-buscador-c1_busqueda_mobile.png)
- Ciudad Lineal zone card: [desktop](prod-buscador-c2_tarjeta_zona_desktop.png) · [mobile](prod-buscador-c2_tarjeta_zona_mobile.png)
- «¿Y si cambias algo?» unfolded: [desktop](prod-buscador-c3_y_si_cambias_desktop.png) · [mobile](prod-buscador-c3_y_si_cambias_mobile.png)
- Relaxation applied, 49 zones: [desktop](prod-buscador-f9_aplicada_desktop.png)
- Map by row «Colegios»: [desktop](prod-buscador-mapa-por-fila-desktop.png)

## If something fails
Roll back with `npx vercel@65.12.1 rollback`, which returns to `dpl_G88JsCXfGKMCciDDopZKbTkW8bjr` (search off in the web, API with `/search`). Or remove the variable and deploy again. Neither was needed.
