"""Pure helpers to map polygons to H3 cells (H3 is computed in Python, never in SQL)."""

from typing import Literal

import h3
from shapely.geometry import MultiPolygon, Polygon, mapping

ContainMode = Literal["center", "overlap", "full"]
GeoPolygon = Polygon | MultiPolygon


def cells_for_polygon(
    geom_4326: GeoPolygon, resolution: int, mode: ContainMode = "overlap"
) -> set[str]:
    """Cells at `resolution` related to the polygon (lon/lat, EPSG:4326)."""
    shape = h3.geo_to_h3shape(mapping(geom_4326))
    return set(h3.h3shape_to_cells_experimental(shape, resolution, contain=mode))


def cell_polygon(cell: str) -> Polygon:
    """H3 cell boundary as a shapely polygon in (lon, lat)."""
    return Polygon([(lng, lat) for lat, lng in h3.cell_to_boundary(cell)])


def cell_centroid(cell: str) -> tuple[float, float]:
    lat, lng = h3.cell_to_latlng(cell)
    return lng, lat
