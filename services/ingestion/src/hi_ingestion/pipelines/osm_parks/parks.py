"""Parks -> places: a point inside each park, its size and the points of its edge (D-222).

A walk reaches a park at its edge, not at its centre: El Retiro is 1.4 km across. The edge
points, every `edge_step_m` metres along the outer rings in EPSG:25830, are what the walking
features use as destinations (hi_features.walk); the place's own point is for the map.
"""

from collections.abc import Mapping
from typing import Any

import h3
import numpy as np
import pandas as pd
import shapely
from numpy.typing import NDArray
from pyproj import Transformer

from hi_contracts.catalog.corrections import ParkInclusion
from hi_contracts.catalog.enums import PlaceCategory, PlaceStatus
from hi_contracts.catalog.pipeline import OsmParksPipeline
from hi_domain.geo.bounds import is_within_madrid
from hi_ingestion.pipelines.osm_parks.inclusions import inclusion_attribute
from hi_ingestion.pipelines.places.normalize import (
    H3_RESOLUTION,
    PLACE_COLUMNS,
    Places,
    canonical_place_id,
)

EDGE_POINTS = "edge_points_25830"
UNNAMED = "Parque sin nombre"
_TO_25830 = Transformer.from_crs(4326, 25830, always_xy=True)
_TO_4326 = Transformer.from_crs(25830, 4326, always_xy=True)


def _to_25830(coords: NDArray[np.float64]) -> NDArray[np.float64]:
    x, y = _TO_25830.transform(coords[:, 0], coords[:, 1])
    return np.column_stack([x, y])


def edge_points(park: shapely.Geometry, step_m: float) -> list[list[float]]:
    """Points along the outer rings, no farther apart than `step_m`, rounded to 0.1 m."""
    polygons = shapely.get_parts(park)
    rings = [shapely.segmentize(p.exterior, step_m) for p in polygons]  # pyright: ignore[reportAttributeAccessIssue]
    coords = np.concatenate([shapely.get_coordinates(r)[:-1] for r in rings])
    unique = np.unique(np.round(coords, 1), axis=0)
    return unique.tolist()


def _place(row: dict[str, Any], park: shapely.Geometry, spec: OsmParksPipeline) -> dict[str, Any]:
    inside = shapely.point_on_surface(park)
    lon, lat = _TO_4326.transform(inside.x, inside.y)
    external_id = str(row["external_id"])
    return {
        "canonical_place_id": canonical_place_id(spec.dataset_id, external_id),
        "external_id": external_id,
        "canonical_name": str(row["name"] or "").strip() or UNNAMED,
        "category": PlaceCategory.GREEN.value,
        "subcategory": spec.subcategory,
        "status": PlaceStatus.ACTIVE.value,
        "lon": lon,
        "lat": lat,
        "x": inside.x,
        "y": inside.y,
        "municipio_ine": None,  # from the census section it lies in, when published
        "h3_r9": h3.latlng_to_cell(lat, lon, H3_RESOLUTION),
        "attributes": {
            "area_ha": round(float(shapely.area(park)) / 10_000, 2),
            "access": row["access"] or None,
            EDGE_POINTS: edge_points(park, spec.edge_step_m),
        },
        "confidence": 1.0,
    }


def _geometry(wkb: str) -> shapely.Geometry | None:
    if not wkb:
        return None
    park = shapely.transform(shapely.from_wkb(wkb), _to_25830)
    return park if park.is_valid and not park.is_empty else shapely.make_valid(park)


def normalize_parks(
    frame: pd.DataFrame,
    spec: OsmParksPipeline,
    inclusions: Mapping[str, ParkInclusion] | None = None,
) -> Places:
    """Parks open to the public and of the minimum size; an included area (D-222 §5) says so."""
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, str]] = []
    removed = {"access_denied": 0, "smaller_than_min_area": 0}
    for row in frame.to_dict("records"):
        if str(row["access"]) in spec.access_denied:
            removed["access_denied"] += 1
            continue
        park = _geometry(str(row["wkb"]))
        area_m2 = 0.0 if park is None else float(shapely.area(park))
        if park is None or area_m2 <= 0:
            bad.append({"external_id": str(row["external_id"]), "reason": "no usable polygon"})
            continue
        if area_m2 < spec.min_area_ha * 10_000:
            removed["smaller_than_min_area"] += 1
            continue
        place = _place(row, park, spec)
        inclusion = (inclusions or {}).get(place["external_id"])
        if inclusion is not None:
            place["attributes"]["inclusion"] = inclusion_attribute(inclusion)
        if not is_within_madrid(place["lon"], place["lat"]):
            bad.append({"external_id": place["external_id"], "reason": "outside Madrid bounds"})
            continue
        rows.append(place)
    return Places(
        pd.DataFrame(rows, columns=PLACE_COLUMNS),
        pd.DataFrame(bad, columns=["external_id", "reason"]),
        len(frame),
        removed,
    )
