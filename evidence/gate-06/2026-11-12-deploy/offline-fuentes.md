# Offline package: map fonts (glyphs) ready for the labels · 2026-11-12 23:30 (Madrid)

D's split of Mariano's feedback: the map labels go to B, in a PR after #32. With labels, MapLibre asks for glyph PBFs, which without network have to come from the package. This prepares them; the web does not ask for them yet.

## Source: OpenFreeMap's font bundle
- **The bundle:** `https://assets.openfreemap.com/fonts/ofm.tar.gz`, 61 MB, Last-Modified 10 Jan 2024. It is listed in the asset index of OpenFreeMap's README.
- **What it holds:** `Noto Sans Regular`, `Noto Sans Bold` and `Noto Sans Italic`, the three fonts of OpenFreeMap's «liberty» style. Each has 256 ranges and a `LICENSE.md`, the **SIL Open Font License 1.1**.
- **Why this one and not OpenMapTiles' `noto-sans.zip` (v2.0, 2017):** these are the very PBFs that `tiles.openfreemap.org/fonts` serves online, and online the web already uses OpenFreeMap. The range 0-255 of «Noto Sans Regular» has the same md5 in the bundle and online.
- **Pinned by sha256** in `demo_offline.sh` (`FONTS_URL`, `FONTS_SHA256`). Nothing goes into git.

## `make demo-offline-tiles` with the fonts
Output: [offline-fuentes/tiles-output.txt](offline-fuentes/tiles-output.txt). Manifest: [offline-fuentes/tiles-manifest.txt](offline-fuentes/tiles-manifest.txt).
- **Before:** the extract (pinned md5) and tilemaker as before, with the same result: 4,750 tiles, 4,490 with content, 3,365 filled.
- **Then `fetch_fonts`:** it downloads the bundle into `data/offline/tiles-src/ofm-fonts.tar.gz`, or reuses it if the sha256 matches, checks it, and unpacks it into `data/offline/tiles/fonts/<fontstack>/<range>.pbf`.
- **Requirement:** `sha256sum` or `shasum`, checked with a clear message.
- **Total size:** 191 MB, with 89 MB of tiles and 105 MB of fonts, all in `data/offline/`, which git ignores.
- **`tiles_meta.py`** now only counts the numeric zoom folders (`tile_files`), so the fonts beside the tiles cannot be mistaken for tiles. With the fonts present it still counts 8,115 tiles, 4,490 with content.

## Serving check
[offline-fuentes/serving-check.txt](offline-fuentes/serving-check.txt). The current package, with the fonts copied by hand into its `public/tiles/fonts`, removed afterwards.

| Request | Result |
|---|---|
| `/tiles/fonts/Noto%20Sans%20Regular/0-255.pbf` | 200, 76,580 B, the same md5 as online |
| `/tiles/fonts/Noto%20Sans%20Bold/8192-8447.pbf` | 200 |
| `/tiles/fonts/Noto%20Sans%20Italic/65280-65535.pbf` | 200 |
| `LICENSE.md` | 200 |
| A fontstack that is not in the bundle (`Noto Sans Medium`) | **404** |

## What is left (when B's labels PR says the route)
- **The glyphs setting:** `prepare` builds the web with it pointing at `/tiles/fonts/{fontstack}/{range}.pbf`. It is one line in `build_web`, with the variable name B chooses.
- **For B:** the style can only use `Noto Sans Regular`, `Bold` and `Italic`. Any other fontstack would be a 404 and, without network, a console error.
- **Then:** regenerate the package, and check with `--block-external` that there are 0 blocked hosts and 0 console errors, now with labels.
