"""Geometry normalisation shared by pipelines."""

import shapely
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry


def to_multipolygon(geom: BaseGeometry | None) -> MultiPolygon | None:
    """Repair and coerce to MultiPolygon; non-polygonal parts are dropped. None if empty."""
    if geom is None or geom.is_empty:
        return None
    fixed = geom if geom.is_valid else shapely.make_valid(geom)
    if isinstance(fixed, Polygon):
        return MultiPolygon([fixed])
    if isinstance(fixed, MultiPolygon):
        return fixed
    if isinstance(fixed, GeometryCollection):
        polygons: list[Polygon] = []
        for part in fixed.geoms:
            if isinstance(part, Polygon):
                polygons.append(part)
            elif isinstance(part, MultiPolygon):
                polygons.extend(part.geoms)
        return MultiPolygon(polygons) if polygons else None
    return None
