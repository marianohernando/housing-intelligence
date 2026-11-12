# Offline package regenerated with fit-0.2 and the CORE-009 tables · 2026-11-12 13:35 (Madrid)

Asked by D once A closed CORE-009 F3. The package now has `transit_hub` and `commute_time`, and the code that scores work by public-transport minutes (fit-0.2).

## Regeneration (`make demo-offline-prepare`, 75 s)
- **Checkout:** `91aeea1`, the HEAD of `claude/sprint-1-public` at the time, CI green.
  - Its API and web are the same as production's `a04467d` and as the later HEAD `70b112c`.
  - Between them only ingestion, feature computation, catalog and docs changed (DATA-018 parks, D-222), not `apps/` or `packages/domain`.
- **Migration:** 0007 in the source and in the checkout, with no override.
- **Dump:** 44 MB. Manifest: [offline-fit02/manifest.txt](offline-fit02/manifest.txt). Output: [offline-fit02/prepare-output.txt](offline-fit02/prepare-output.txt).
- **Search:** on, as in production.
- **Basemap:** still `tiles.openfreemap.org`. The local extract is waiting for permission to use tilemaker.

## Data: the package against Supabase (after D's sync of `e7102b0`)
- **Row counts:** the same in 10 of the 11 tables. The two new ones match: `transit_hub` 579 and `commute_time` 115,800.
- **The difference is in `feature_value`:** 77,491 rows in the package against 67,805 in Supabase.
  - The extra 9,686 rows are the two park features of DATA-018, `min_a_pie_parque` and `pct_calle_parque_5min`, 4,843 each.
  - A computed them in the local database at 12:33 UTC, after the sync, so they are not in Supabase yet.
  - Their registry entries are in both databases.
  - No API or web code at `91aeea1` or `70b112c` reads them.
- **API answers, package against production** (`meta` left out):

| Request | Result |
|---|---|
| `POST /search`, demo case | identical |
| `/gaps/distrito/2807905` (Chamartín) | identical |
| `/gaps/distrito/2807908` (Fuencarral-El Pardo) | identical |
| `/datasets` | identical |
| `/gaps/municipio/28079` (Madrid) | identical except the last digit of `confidence` in 6 rows (`0.997049748713441` against `0.9970497487134414`): floating-point rounding. Identical when rounded to 1e-9 |

- **If A syncs the park features to Supabase,** regenerate the package afterwards so both match again.

## Start (`make demo-offline`): smoke 7/7
- **Search:** «33 of 199 zones, 1st Fuencarral-El Pardo», the same as production.
- **Output:** [offline-fit02/start-output.txt](offline-fit02/start-output.txt).

## Pitch journeys against the package (`e2e_prod.mjs --base http://localhost:3012`)

| Run | 1440 px | 390 px | Report |
|---|---|---|---|
| With network | 66/66 | 40/40 | [e2e-net](offline-fit02/e2e-net/e2e-report.json) |
| Without network (`--block-external`) | 65/66 | 39/40 | [e2e-nonet](offline-fit02/e2e-nonet/e2e-report.json) |

- **What J1 saw on screen** (desktop):
  - the summary «Con tu búsqueda tal cual salen 33 zonas», de 199;
  - first card «Fuencarral-El Pardo», 100 %, with its 5 facts equal to the API's;
  - first option «+5 min a pie hasta colegio con primaria», which gives 50 zones once applied.
- **Without network:**
  - The only blocked host is `tiles.openfreemap.org`, the basemap.
  - The only failing check is «no console errors», from those tiles, the same as in the earlier rehearsal ([offline-buscador.md](offline-buscador.md)). Every data check passes.
- **The web without the basemap:**
  - It shows «Mapa sin fondo de calles.» with the zones drawn: [desktop](offline-fit02/sin-red-mapa-desktop.jpg) · [mobile](offline-fit02/sin-red-mapa-mobile.jpg).
  - Checked by blocking every host other than localhost.
  - The guide said «No se ha podido cargar el mapa…», which is now only for a failure of the whole map, and has been corrected.

Package stopped afterwards with `make demo-offline-stop`.
