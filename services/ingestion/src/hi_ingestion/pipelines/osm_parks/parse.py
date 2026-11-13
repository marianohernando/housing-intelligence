"""OSM extract -> one row per area tagged as a park: id, name, access and its geometry (WKB)."""

from collections.abc import Iterable, Sequence
from pathlib import Path

import pandas as pd
from osmium import FileProcessor
from osmium.filter import EntityFilter, IdFilter, TagFilter
from osmium.geom import WKBFactory
from osmium.osm import AREA, Area

from hi_contracts.catalog.pipeline import OsmParksPipeline

PARK_COLUMNS = ["external_id", "name", "access", "leisure", "wkb"]


def _area_id(osm_id: str) -> int:
    """osmium numbers an area from a way as 2 x id and one from a relation as 2 x id + 1."""
    kind, number = osm_id.split("/")
    return 2 * int(number) + (kind == "relation")


def _row(area: Area, factory: WKBFactory) -> dict[str, object]:
    try:
        wkb = factory.create_multipolygon(area)
    except RuntimeError:
        wkb = ""
    kind = "way" if area.from_way() else "relation"
    return {
        "external_id": f"{kind}/{area.orig_id()}",
        "name": area.tags.get("name", ""),
        "access": area.tags.get("access", ""),
        "leisure": area.tags.get("leisure", ""),
        "wkb": wkb,
    }


def _areas(path: Path, spec: OsmParksPipeline, included: Sequence[str]) -> Iterable[Area]:
    wanted = [("leisure", value) for value in spec.leisure]
    tagged = FileProcessor(str(path)).with_areas(TagFilter(*wanted)).with_filter(TagFilter(*wanted))
    for area in tagged:
        if isinstance(area, Area) and area.tags.get("leisure") in spec.leisure:
            yield area
    if included:  # areas an official source lists as parks, whatever OSM tags them (D-222 §5)
        listed = (
            FileProcessor(str(path))
            .with_areas()
            .with_filter(EntityFilter(AREA))
            .with_filter(IdFilter([_area_id(i) for i in included]))
        )
        yield from (area for area in listed if isinstance(area, Area))


def parse_parks(path: Path, spec: OsmParksPipeline, included: Sequence[str] = ()) -> pd.DataFrame:
    """Closed ways and multipolygon relations whose `leisure` is listed, plus the `included`
    OSM areas; osmium assembles the areas. A geometry osmium cannot build is kept with an
    empty WKB (quarantined later). An area read twice is kept once."""
    factory = WKBFactory()
    frame = pd.DataFrame(
        [_row(a, factory) for a in _areas(path, spec, included)], columns=PARK_COLUMNS
    )
    return frame.drop_duplicates("external_id").reset_index(drop=True)
