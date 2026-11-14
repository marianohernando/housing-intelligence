"""OSM extract -> one row per node or area with one of the declared tags: id, name, access, the
tag and a point (the node itself, or a point inside the area)."""

from collections.abc import Iterable
from pathlib import Path

import pandas as pd
import shapely
from osmium import FileProcessor
from osmium.filter import TagFilter
from osmium.geom import WKBFactory
from osmium.osm import Area, Node

from hi_contracts.catalog.pipeline import OsmPoisPipeline

POI_COLUMNS = ["external_id", "name", "access", "key", "value", "lon", "lat"]


def _tag(entity: Node | Area, spec: OsmPoisPipeline) -> tuple[str, str] | None:
    """The first declared tag the entity carries (the order of the pipeline's classes)."""
    for cls in spec.classes:
        if entity.tags.get(cls.key) == cls.value:
            return cls.key, cls.value
    return None


def _point(entity: Node | Area, factory: WKBFactory) -> tuple[float, float] | None:
    if isinstance(entity, Node):
        return (entity.location.lon, entity.location.lat) if entity.location.valid() else None
    try:
        inside = shapely.point_on_surface(shapely.from_wkb(factory.create_multipolygon(entity)))
    except (RuntimeError, shapely.errors.GEOSException):
        return None
    return None if inside.is_empty else (inside.x, inside.y)


def _external_id(entity: Node | Area) -> str:
    if isinstance(entity, Node):
        return f"node/{entity.id}"
    return f"{'way' if entity.from_way() else 'relation'}/{entity.orig_id()}"


def _rows(path: Path, spec: OsmPoisPipeline) -> Iterable[dict[str, object]]:
    wanted = TagFilter(*[(c.key, c.value) for c in spec.classes])
    factory = WKBFactory()
    for entity in FileProcessor(str(path)).with_areas(wanted).with_filter(wanted):
        if not isinstance(entity, Node | Area):
            continue  # a closed way comes again as its area; an open one is not a place
        tag = _tag(entity, spec)
        if tag is None:
            continue
        point = _point(entity, factory)
        yield {
            "external_id": _external_id(entity),
            "name": entity.tags.get("name", ""),
            "access": entity.tags.get("access", ""),
            "key": tag[0],
            "value": tag[1],
            "lon": None if point is None else point[0],
            "lat": None if point is None else point[1],
        }


def parse_pois(path: Path, spec: OsmPoisPipeline) -> pd.DataFrame:
    """Nodes, closed ways and multipolygon relations with a declared tag (osmium assembles the
    areas). An area osmium cannot build keeps an empty point (quarantined later)."""
    frame = pd.DataFrame(list(_rows(path, spec)), columns=POI_COLUMNS)
    return frame.drop_duplicates("external_id").reset_index(drop=True)
