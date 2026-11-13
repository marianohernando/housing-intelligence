# Offline package with search on · 2026-11-12 01:05 (Madrid)

Line C, test phase T4 (`prompts/FASE_PRUEBAS.md` §C, asked by D).

## Change
`infra/deploy/offline/demo_offline.sh` → `build_web` now compiles the private copy of the web with `NEXT_PUBLIC_FEATURE_SEARCH=true`, next to `NEXT_PUBLIC_API_URL=http://localhost:8012`. The other `NEXT_PUBLIC_*` variables of the shell are still removed.

## Regeneration (`make demo-offline-prepare`, 40 s)
- Checkout: `2d9e83a`, which is origin/claude/sprint-1-public `1913393` (DATA-AUDIT T1, D-216, migration 0006) plus line C.
- Source and checkout are both at migration 0006, with no override. The first attempt stopped as it should: the checkout was at 0005 and the source at 0006, so I rebased.
- Dump: 43 MB.
- Row counts in [offline/manifest.txt](offline/manifest.txt):

| Table | Rows |
|---|---|
| `place_master` | 23,370 |
| `feature_value` | 61,956 |
| `geo_admin_unit` | 4,973 |

Output: [offline/prepare-output.txt](offline/prepare-output.txt).

## Start (`make demo-offline`, 8 s) and smoke 6/6
[offline/start-output.txt](offline/start-output.txt).
- With the typed `/places` of D-216, page 1 of transport weighs 1.84 MB and education 1.55 MB. Production, still without D-216, gives 1.41 MB and 1.16 MB.
- Those 1.84 MB are 41 % of Vercel's 4.5 MB limit. They reach production when A publishes D-216.

## Pitch journeys against the package (`e2e_prod.mjs --base http://localhost:3012`)
| Run | Desktop 1440 | Mobile 390 | Report |
|---|---|---|---|
| With network | 36/36 | 30/30 | [e2e-offline-report.json](offline/e2e-offline-report.json) |
| Without network (`--block-external`) | 35/36 | 29/30 | [e2e-offline-sin-red-report.json](offline/e2e-offline-sin-red-report.json) |

**Search works offline.**
- The demo case gives 33 zones, and the first is Ciudad Lineal at 99 %. «+5 min a pie hasta colegio con primaria» gives 50 zones, and undoing it gives 33 again. Every `/search` sends `max_minutes: null`.
- These figures come from the local database, which already has D-216. Production (Supabase without D-216) gives 32 and 49.
- They will match once A syncs and the package is regenerated after that, on 23 Nov.

**Without network:**
- The only blocked host is `tiles.openfreemap.org`, the basemap.
- Every data check passes: search, card, «¿Y si cambias algo?», «Qué falta» in Madrid, map by row and the list.
- What fails is «no console errors», with `Failed to load resource: net::ERR_INTERNET_DISCONNECTED` from those tiles.
- On screen: the coloured zones on a background without a map, and the notice «No se ha podido cargar el mapa. Puedes seguir con la lista de zonas.»

Screenshots:
- [desktop with network](offline/con-red-chromium-desktop-1440-j1-card.jpg) · [desktop without network](offline/sin-red-chromium-desktop-1440-j1-card.jpg)
- [mobile with network](offline/con-red-chromium-mobile-390-j1-results.jpg) · [mobile without network](offline/sin-red-chromium-mobile-390-j1-results.jpg)

## Proposals (not done)
- **B:**
  - do not show the «No se ha podido cargar el mapa» notice when only the basemap fails and the zones have loaded;
  - or make the TileJSON configurable (today it is fixed in `apps/web/src/lib/map/style.ts`).
- **C, if B makes it configurable:** serve a local extract of Madrid's tiles in the package.
- **D:** in the offline block of the script, mention that the map has no background, or rehearse it as it is.

Package stopped afterwards with `make demo-offline-stop`. Nothing is left listening on 3012, 8012 or 5441.
