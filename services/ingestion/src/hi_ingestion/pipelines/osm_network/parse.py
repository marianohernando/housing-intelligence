"""OSM extract -> one row per segment of a walkable way, with both ends' id and lon/lat."""

from collections.abc import Mapping
from itertools import pairwise
from pathlib import Path

import pandas as pd
from osmium import FileProcessor
from osmium.filter import EntityFilter, KeyFilter
from osmium.osm import NODE, WAY, NodeRef, Way

from hi_contracts.catalog.pipeline import OsmWalkNetworkPipeline

SEGMENT_COLUMNS = ["u_id", "v_id", "u_lon", "u_lat", "v_lon", "v_lat", "highway"]
NOT_BUILT = ("proposed", "construction", "abandoned", "razed", "disused")


def is_walkable(tags: Mapping[str, str], spec: OsmWalkNetworkPipeline) -> bool:
    highway = tags.get("highway", "")
    foot = tags.get("foot", "")
    if not highway or highway in NOT_BUILT or foot == "no":
        return False
    if foot in spec.foot_allowed:
        return True
    if tags.get("access", "") in spec.access_denied:
        return False
    return highway in spec.walkable_highways


def _point(node: NodeRef) -> tuple[float, float]:
    """(lon, lat), or NaNs when the extract lacks the node (quarantined later)."""
    if not node.location.valid():
        return float("nan"), float("nan")
    return node.lon, node.lat


def parse_extract(path: Path, spec: OsmWalkNetworkPipeline) -> pd.DataFrame:
    u_id: list[int] = []
    v_id: list[int] = []
    u_lon: list[float] = []
    u_lat: list[float] = []
    v_lon: list[float] = []
    v_lat: list[float] = []
    highway: list[str] = []
    processor = (
        FileProcessor(str(path), NODE | WAY)
        .with_locations()
        .with_filter(EntityFilter(WAY))
        .with_filter(KeyFilter("highway"))
    )
    for way in processor:
        if not isinstance(way, Way):
            continue
        tags = {tag.k: tag.v for tag in way.tags}
        if not is_walkable(tags, spec):
            continue
        refs = list(way.nodes)
        for start, end in pairwise(refs):
            start_lon, start_lat = _point(start)
            end_lon, end_lat = _point(end)
            u_id.append(start.ref)
            v_id.append(end.ref)
            u_lon.append(start_lon)
            u_lat.append(start_lat)
            v_lon.append(end_lon)
            v_lat.append(end_lat)
            highway.append(tags["highway"])
    columns = (u_id, v_id, u_lon, u_lat, v_lon, v_lat, highway)
    return pd.DataFrame(dict(zip(SEGMENT_COLUMNS, columns, strict=True)))
