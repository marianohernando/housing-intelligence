# Offline package with a local basemap: streets with no network · 2026-11-12 15:05 (Madrid)

Mariano authorised tilemaker in line C's session (option A). Without network the map now has streets, parks and 3D buildings. The pitch journeys pass with no blocked host and no console errors.

## Tooling: tilemaker 3.2.0, official image pinned by digest
- **Why the image:** Homebrew has no tilemaker formula, and the v3.1.0 and v3.2.0 releases publish no binaries. The only one is the v3.0.0 zip from 2024, built for x86.
- **The image:** `ghcr.io/systemed/tilemaker@sha256:9cd8728a37a31c8a5205e091cedd3ff2c2c450c57e1ce3e5b58916185540ebba`.
  - It is published by github.com/systemed/tilemaker: label `Version 3.2.0`, commit `2789651`, built on 3 Nov, with an arm64 variant.
  - `tilemaker --help` reports `v3.2.0+g278965195157`.
- **Isolation:** it runs with `--network none` and reads the extract read-only. Nothing is installed on the laptop.

## `make demo-offline-tiles` (new, about 1 min)
Output: [offline-teselas/tiles-output.txt](offline-teselas/tiles-output.txt). Manifest: [offline-teselas/tiles-manifest.txt](offline-teselas/tiles-manifest.txt).
1. **Source:** `madrid-latest.osm.pbf` from Geofabrik (ODbL) redirects to `madrid-261111.osm.pbf`, OSM data of 11 Nov, 86 MB.
   - It is checked against its `.md5`: `1f5fc60a7a14235518265dd1bbfaf613`.
   - `PBF_FILE=` pins it on a rerun.
2. **tilemaker:** run with its own `config-openmaptiles.json` and `process-openmaptiles.lua`, the schema the web's style uses.
   - The shapefile layers (`ocean`, `urban_areas`, `ice_shelf`, `glacier`) are dropped: Madrid needs none.
   - Tiles are written uncompressed, so the web can serve them as static files.
3. **`infra/deploy/offline/tiles_meta.py`** writes `tiles.json` (TileJSON 3.0.0) with the attribution «© OpenStreetMap contributors (ODbL) · © OpenMapTiles».
   - **Bounds:** taken from the z14 tiles, because the bounds tilemaker writes are wrong (an east of `2.2e-308`).
   - **Holes:** filled with empty tiles inside those bounds. Otherwise MapLibre would ask for them and each 404 would be a console error.

| Result | Value |
|---|---|
| Tiles with content | 4,750, z0–14 |
| Empty tiles | 3,365 |
| Size | 89 MB |
| Bounds | −4.592, 39.876 to −2.900, 41.179 |
| Layers | `place`, `boundary`, `poi`, `housenumber`, `waterway`, `transportation`, `transportation_name`, `building`, `water`, `water_name`, `aeroway`, `aerodrome_label`, `park`, `landuse`, `landcover`, `mountain_peak` |

- **Where it goes:** `data/offline/tiles/` and `data/offline/tiles-src/`, inside `data/offline/`, which git already ignores. No tile or extract goes into the repo.

## `make demo-offline-prepare` with the basemap (4.5 min)
Output: [offline-teselas/prepare-output.txt](offline-teselas/prepare-output.txt). Manifest: [offline-teselas/package-manifest.txt](offline-teselas/package-manifest.txt).
- **Web build:** `NEXT_PUBLIC_MAP_TILES_URL=/tiles/tiles.json`. The web turns that into `http://localhost:3012/tiles/tiles.json`, and `prepare` copies the tiles into its `public/tiles`.
- **The package's manifest** says `basemap local, madrid-261111.osm.pbf`.
- **Checkout `f09eccc`,** the HEAD of the integration branch.
  - Its API already includes DATA-018 Fase 3b (`8330771`, «sin parque a un paseo» goes from UNKNOWN to 0 with low confidence), which production (`50d4b28`) does not have yet.
  - The package will be regenerated after that deploy.

## Checks without network
**`make demo-offline`:** smoke 7/7, «33 of 199 zones, 1st Fuencarral-El Pardo». Output: [offline-teselas/start-output.txt](offline-teselas/start-output.txt).

**Serving** ([offline-teselas/probe-sin-red.txt](offline-teselas/probe-sin-red.txt)):

| Request | Result |
|---|---|
| `tiles.json` | 200 |
| A z14 tile | 200, 7 KB |
| An empty tile | 200, 0 B |
| A tile outside the bounds | 404, but MapLibre never asks for it |

**Browser with every host other than localhost blocked:**

| Page | Tiles with content | Empty tiles | Failed tiles | Console errors |
|---|---|---|---|---|
| desktop `/map` | 6 | 2 | 0 | 0 |
| desktop Chamartín | 71 | 2 | 0 | 0 |
| mobile `/map` | 5 | 0 | 0 | 0 |
| mobile Chamartín | 21 | 0 | 0 | 0 |

- **Notices:** neither «Mapa sin fondo de calles.» nor «No se ha podido cargar el mapa» shows.
- **Attribution:** the map shows «© OpenStreetMap contributors (ODbL) · © OpenMapTiles», then the data sources.
- **Screenshots:**
  - Chamartín, with streets, parks and 3D buildings: [desktop](offline-teselas/sin-red-desktop-zona-distrito-2807905.jpg) · [mobile](offline-teselas/sin-red-mobile-zona-distrito-2807905.jpg).
  - The home page: [desktop](offline-teselas/sin-red-desktop-map.jpg) · [mobile](offline-teselas/sin-red-mobile-map.jpg).

**Pitch journeys, `e2e_prod.mjs --base http://localhost:3012 --block-external`:** 66/66 at 1440 px and 40/40 at 390 px, with **0 blocked hosts and 0 console errors**. Before, it was 65/66 and 39/40, with `tiles.openfreemap.org` blocked. Report: [offline-teselas/e2e-nonet/e2e-report.json](offline-teselas/e2e-nonet/e2e-report.json).

Package stopped afterwards with `make demo-offline-stop`.
