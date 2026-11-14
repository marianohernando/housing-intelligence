"""Points of interest -> places: the category and subcategory of its tag, its name and its
point. Nothing else of OSM is kept (no address, phone or opening hours)."""

import math
from collections import defaultdict
from typing import Any

import h3
import pandas as pd
from pyproj import Transformer

from hi_contracts.catalog.enums import PlaceStatus
from hi_contracts.catalog.pipeline import OsmPoiClass, OsmPoisPipeline
from hi_domain.geo.bounds import is_within_madrid
from hi_ingestion.pipelines.places.normalize import (
    H3_RESOLUTION,
    PLACE_COLUMNS,
    Places,
    canonical_place_id,
)

_TO_25830 = Transformer.from_crs(4326, 25830, always_xy=True)


def unnamed(subcategory: str) -> str:
    """«Bar sin nombre»: OSM has no name for it."""
    return f"{subcategory} sin nombre"


def _place(row: dict[str, Any], cls: OsmPoiClass, spec: OsmPoisPipeline) -> dict[str, Any]:
    lon, lat = float(row["lon"]), float(row["lat"])
    x, y = _TO_25830.transform(lon, lat)
    external_id = str(row["external_id"])
    return {
        "canonical_place_id": canonical_place_id(spec.dataset_id, external_id),
        "external_id": external_id,
        "canonical_name": str(row["name"] or "").strip() or unnamed(cls.subcategory),
        "category": cls.category.value,
        "subcategory": cls.subcategory,
        "status": PlaceStatus.ACTIVE.value,
        "lon": lon,
        "lat": lat,
        "x": x,
        "y": y,
        "municipio_ine": None,  # from the census section it lies in, when published
        "h3_r9": h3.latlng_to_cell(lat, lon, H3_RESOLUTION),
        "attributes": {"osm_tag": f"{cls.key}={cls.value}"},
        "confidence": 1.0,
    }


SAME_PLACE_M = 50.0  # a node this close to the area of the same tag and name is that place


def drop_nodes_of_areas(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """A place drawn twice, as its building (area) and as a node inside it, counts once: the
    area is kept. Only named places: two «Bar sin nombre» side by side are two bars."""

    def same(row: dict[str, Any]) -> tuple[str, str]:
        return str(row["attributes"]["osm_tag"]), str(row["canonical_name"])

    areas: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        if row["named"] and not str(row["external_id"]).startswith("node/"):
            areas[same(row)].append((row["x"], row["y"]))
    kept: list[dict[str, Any]] = []
    for row in rows:
        near = areas.get(same(row), []) if str(row["external_id"]).startswith("node/") else []
        if row["named"] and any(
            math.hypot(row["x"] - x, row["y"] - y) <= SAME_PLACE_M for x, y in near
        ):
            continue
        kept.append(row)
    return kept, len(rows) - len(kept)


def normalize_pois(frame: pd.DataFrame, spec: OsmPoisPipeline) -> Places:
    """Places open to the public, inside the region; one without a point is quarantined."""
    classes = {(c.key, c.value): c for c in spec.classes}
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, str]] = []
    removed = {"access_denied": 0, "node_of_area": 0}
    for row in frame.to_dict("records"):
        external_id = str(row["external_id"])
        if str(row["access"]) in spec.access_denied:
            removed["access_denied"] += 1
            continue
        if pd.isna(row["lon"]) or pd.isna(row["lat"]):
            bad.append({"external_id": external_id, "reason": "no usable point"})
            continue
        if not is_within_madrid(float(row["lon"]), float(row["lat"])):
            bad.append({"external_id": external_id, "reason": "outside Madrid bounds"})
            continue
        place = _place(row, classes[(str(row["key"]), str(row["value"]))], spec)
        rows.append(place | {"named": bool(str(row["name"] or "").strip())})
    rows, removed["node_of_area"] = drop_nodes_of_areas(rows)
    return Places(
        pd.DataFrame(rows, columns=PLACE_COLUMNS),
        pd.DataFrame(bad, columns=["external_id", "reason"]),
        len(frame),
        removed,
    )
