"""TileJSON for the offline basemap extract (OpenMapTiles schema, made by tilemaker).

    uv run --frozen python -I infra/deploy/offline/tiles_meta.py TILES_DIR TILES_BASE_URL

- Bounds come from the z14 tiles. The bounds tilemaker writes in metadata.json can be wrong
  (an east of 2.2e-308 for the Madrid extract).
- MapLibre asks for every tile inside the bounds. tilemaker only writes tiles with content, so each
  missing tile inside them would be a 404 and a console error. They are filled with empty tiles: a
  zero-length protobuf is a valid vector tile with no layers. Outside the Comunidad (the corners of
  the bounds) the map therefore shows only its land colour, with no streets.
- Before filling, it checks that tilemaker wrote enough tiles with content at every zoom, so a run
  that failed half-way is not hidden behind empty tiles.
- Writes TILES_DIR/tiles.json and prints a summary. Standard library only.
"""

import json
import math
import sys
from pathlib import Path

MAXZOOM = 14
EPSILON = 1e-6  # keeps each bound strictly inside its edge tile
# The Madrid extract of 11 Nov 2026 gives 4,490 tiles with content; well under that means tilemaker
# failed or the extract is not the Comunidad.
MIN_TILES_WITH_CONTENT = 4000
# Zooms that must have content: from the style's first street layer (roads-major, minzoom 7). At
# z0–2 the Comunidad is too small for any feature, so those tiles are legitimately empty.
CONTENT_ZOOMS = range(7, MAXZOOM + 1)
ATTRIBUTION = (
    '<a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap</a> '
    "contributors (ODbL) · "
    '<a href="https://openmaptiles.org/" target="_blank">© OpenMapTiles</a>'
)


def tile_lon(x: int, z: int) -> float:
    return x / 2**z * 360 - 180


def tile_lat(y: int, z: int) -> float:
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / 2**z))))


def tile_x(lon: float, z: int) -> int:
    return math.floor((lon + 180) / 360 * 2**z)


def tile_y(lat: float, z: int) -> int:
    rad = math.radians(lat)
    return math.floor((1 - math.asinh(math.tan(rad)) / math.pi) / 2 * 2**z)


def bounds_from_tiles(tiles_dir: Path) -> list[float]:
    coords = [(int(p.parent.name), int(p.stem)) for p in (tiles_dir / str(MAXZOOM)).glob("*/*.pbf")]
    if not coords:
        raise SystemExit(f"no z{MAXZOOM} tiles in {tiles_dir}")
    xs, ys = [x for x, _ in coords], [y for _, y in coords]
    return [
        tile_lon(min(xs), MAXZOOM) + EPSILON,
        tile_lat(max(ys) + 1, MAXZOOM) + EPSILON,
        tile_lon(max(xs) + 1, MAXZOOM) - EPSILON,
        tile_lat(min(ys), MAXZOOM) - EPSILON,
    ]


def tile_files(tiles_dir: Path) -> list[Path]:
    """The z/x/y.pbf tiles, leaving out what sits beside them (fonts/<fontstack>/<range>.pbf)."""
    return [p for p in tiles_dir.glob("*/*/*.pbf") if p.parent.parent.name.isdigit()]


def check_written(tiles_dir: Path) -> int:
    """Tiles with content tilemaker wrote; fails if too few overall or none at a street zoom."""
    with_content = dict.fromkeys(range(MAXZOOM + 1), 0)
    for path in tile_files(tiles_dir):
        z = int(path.parent.parent.name)
        if z in with_content and path.stat().st_size > 0:
            with_content[z] += 1
    total = sum(with_content.values())
    empty_zooms = [z for z in CONTENT_ZOOMS if with_content[z] == 0]
    if total < MIN_TILES_WITH_CONTENT or empty_zooms:
        missing = f", none at zoom {empty_zooms}" if empty_zooms else ""
        minimum = MIN_TILES_WITH_CONTENT
        raise SystemExit(
            f"tilemaker wrote {total} tiles with content (minimum {minimum}){missing}: it may have"
            " failed half-way. Not filling holes; check it and rerun."
        )
    return total


def fill_missing(tiles_dir: Path, bounds: list[float]) -> int:
    west, south, east, north = bounds
    filled = 0
    for z in range(MAXZOOM + 1):
        for x in range(tile_x(west, z), tile_x(east, z) + 1):
            for y in range(tile_y(north, z), tile_y(south, z) + 1):
                path = tiles_dir / str(z) / str(x) / f"{y}.pbf"
                if not path.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b"")
                    filled += 1
    return filled


def main(tiles_dir: Path, base_url: str) -> None:
    written = len(tile_files(tiles_dir))
    with_content = check_written(tiles_dir)
    bounds = bounds_from_tiles(tiles_dir)
    filled = fill_missing(tiles_dir, bounds)
    metadata = json.loads((tiles_dir / "metadata.json").read_text(encoding="utf-8"))
    tilejson = {
        "tilejson": "3.0.0",
        "name": "Comunidad de Madrid (OpenMapTiles schema)",
        "tiles": [f"{base_url}/{{z}}/{{x}}/{{y}}.pbf"],
        "minzoom": 0,
        "maxzoom": MAXZOOM,
        "bounds": [round(b, 6) for b in bounds],
        "attribution": ATTRIBUTION,
        "vector_layers": metadata["vector_layers"],
    }
    tilejson_text = json.dumps(tilejson, ensure_ascii=False, indent=1)
    (tiles_dir / "tiles.json").write_text(tilejson_text, encoding="utf-8")
    print(f"tiles_written {written}")
    print(f"tiles_with_content {with_content}")
    print(f"tiles_filled_empty {filled}")
    print(f"bounds {' '.join(f'{b:.6f}' for b in bounds)}")
    print(f"layers {' '.join(layer['id'] for layer in metadata['vector_layers'])}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: tiles_meta.py TILES_DIR TILES_BASE_URL")
    main(Path(sys.argv[1]), sys.argv[2].rstrip("/"))
