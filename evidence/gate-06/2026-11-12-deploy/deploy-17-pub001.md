# OPS-001 (line C) · deploy of 28a0f2f (mobile LCP, icons, green areas) and offline package · 2026-11-12 15:30 (Madrid)

## Deploy
- **Code:** `28a0f2f`, the HEAD of `claude/sprint-1-public`, CI green on all five jobs. It carries:
  - B's PR #22: the map attribution collapsed on mobile, the icons, and M2/M3/M4;
  - A's `8330771`: green areas, where «sin parque a un paseo» is 0 with low confidence. Code only, with no sync.
- **Deployed from a detached checkout.** Migration 0007; the variables are unchanged.
- **`ALLOW_BRANCH=1 make deploy-demo`:** `dpl_7oZfh8rMzroPGUR1r4Yd2gGMmv9b`, verified on round 1. Output: [deploy-17/deploy-output.txt](deploy-17/deploy-output.txt).
  - **Round 0:** 8/8, but 4 of its requests came from `dpl_AtNd6…`.
  - **Round 1:** 8/8, all from the new deployment.
  - **Demo case:** 33 of 199 zones, 1st Fuencarral-El Pardo at 100 %.
- **Icons:** `favicon.ico`, `apple-touch-icon.png` and the linked `apple-icon.png` and `icon.svg` all return 200 ([deploy-17/icons.txt](deploy-17/icons.txt)).

## Watch, 14:22–14:27 UTC
- **Load:** 8 zone view loads of Fuencarral-El Pardo and Chamartín, with 48 API requests and 0 5xx, plus 5 `/search` with the demo case, all 200 in 0.35–0.70 s. Output: [deploy-17/watch.txt](deploy-17/watch.txt).
- **Logs, 14:19–14:27 UTC:** [deploy-17/logs-summary.txt](deploy-17/logs-summary.txt).

| Measure | Value |
|---|---|
| `EMAXCONNSESSION`, «prepared statement», authentication, connection, timeout | 0 |
| Tracebacks | 0 |
| API access lines | 162, all 200 |
| Instances started | 4 |
| CDN records | 811: 810 × 200 and 1 × 404 |

- **The 404 is `/manifest.webmanifest`,** which only the icon check asked for. The page does not link it.

## LCP, one pass on a phone with slow 4G (`perf_prod.mjs --runs 1`)
Report: [deploy-17/perf-report.json](deploy-17/perf-report.json). LCP elements: [deploy-17/lcp-elements.txt](deploy-17/lcp-elements.txt).

| Page | LCP now | Before (`deploy-15-6543.md`) | LCP element now |
|---|---|---|---|
| home | **1.18 s** | 4.46 s | the lead paragraph, at 1.12 s |
| zone Chamartín | **2.04 s** | 4.40 s | «Mira sus servicios…», at 2.00 s |
| «Qué falta» Madrid | 2.18 s | 1.97 s | the intro paragraph, after `/gaps` |

- **All three are under the 2.5 s good threshold.** The collapsed attribution is no longer the LCP.
- **B measured these locally:** 668 ms for the home page and 2,056 ms for the zone.

## Offline package regenerated with 28a0f2f and the local basemap
- **`make demo-offline-tiles`:** run with the reviewer's fixes (PR of this branch), using the pinned extract and md5. 4,750 tiles, 4,490 of them with content. Output: [offline-pub001/tiles-output.txt](offline-pub001/tiles-output.txt).
- **`make demo-offline-prepare`:** checkout `28a0f2f`, with `basemap local, madrid-261111.osm.pbf` ([manifest](offline-pub001/package-manifest.txt), [output](offline-pub001/prepare-output.txt)).
- **`make demo-offline`:** smoke 7/7 ([output](offline-pub001/start-output.txt)).
- **Pitch journeys with `--block-external`:** 66/66 and 40/40, with 0 blocked hosts and 0 console errors ([report](offline-pub001/e2e-nonet/e2e-report.json)).
- **Attribution on mobile:** it is collapsed. The «Fuentes y licencias del mapa» button opens it with «© OpenStreetMap contributors (ODbL) · © OpenMapTiles» ([screenshot](offline-pub001/sin-red-mobile-atribucion-abierta.jpg)).

**Data: the local database is ahead of Supabase** with A's work in progress, which is not in `28a0f2f`.

| Table | Package | Supabase |
|---|---|---|
| `dataset_registry` | 42 | 39 |
| `dataset_version` | 53 | 47 |
| `feature_registry` | 42 | 41 |
| `feature_value` | 82,334 | 77,491 |

- **What the extra is:** the CRTM topology datasets (metro, metro ligero and cercanías), and the feature `min_a_pie_estacion_sin_escaleras`, with 4,843 rows computed at 14:07 UTC.
- **Package against production:**
  - `/search` for the demo case gives the same ranking and figures. It only lists those 3 extra sources.
  - The gaps of Madrid, Chamartín and Fuencarral-El Pardo are identical.
  - `/datasets` gives 26 Comunidad datasets against 23, so the screen would say «26 conjuntos» instead of «23».
- **Regenerate the package once A merges and syncs that work.**

Package stopped afterwards with `make demo-offline-stop`.
