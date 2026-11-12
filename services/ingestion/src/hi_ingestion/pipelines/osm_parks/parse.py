"""OSM extract -> one row per area tagged as a park: id, name, access and its geometry (WKB)."""

from pathlib import Path

import pandas as pd
from osmium import FileProcessor
from osmium.filter import TagFilter
from osmium.geom import WKBFactory
from osmium.osm import Area

from hi_contracts.catalog.pipeline import OsmParksPipeline

PARK_COLUMNS = ["external_id", "name", "access", "leisure", "wkb"]


def parse_parks(path: Path, spec: OsmParksPipeline) -> pd.DataFrame:
    """Closed ways and multipolygon relations whose `leisure` is listed; osmium assembles the
    areas. A geometry osmium cannot build is kept with an empty WKB (quarantined later)."""
    wanted = [("leisure", value) for value in spec.leisure]
    factory = WKBFactory()
    rows: list[dict[str, object]] = []
    processor = (
        FileProcessor(str(path)).with_areas(TagFilter(*wanted)).with_filter(TagFilter(*wanted))
    )
    for area in processor:
        if not isinstance(area, Area) or area.tags.get("leisure") not in spec.leisure:
            continue
        try:
            wkb = factory.create_multipolygon(area)
        except RuntimeError:
            wkb = ""
        kind = "way" if area.from_way() else "relation"
        rows.append(
            {
                "external_id": f"{kind}/{area.orig_id()}",
                "name": area.tags.get("name", ""),
                "access": area.tags.get("access", ""),
                "leisure": area.tags.get("leisure", ""),
                "wkb": wkb,
            }
        )
    return pd.DataFrame(rows, columns=PARK_COLUMNS)
