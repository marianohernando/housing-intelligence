"""Inputs of the walking-access features (CORE-005): the last valid OSM walking network, the
origin streets placed in their census section, and the distance from every node to the nearest
destination. Each is loaded once per process: 12 features x 3 levels share one network.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from functools import cache
from pathlib import Path

import numpy as np
import pandas as pd
import shapely
from numpy.typing import NDArray
from sqlalchemy import Engine, text

from hi_domain.access.graph import FloatArray, IntArray
from hi_domain.access.walk import RoutableNetwork, origin_weights
from hi_features.methods import destination_points, place_filter
from hi_ingestion.bronze import REPO_ROOT
from hi_ingestion.pipelines.osm_network.network import NETWORK_FILE, load_network

NETWORK_DATASET = "osm_red_peatonal"
# A census section code is municipio (5) + district (2) + section (3): 28079 01 001.
CODE_LENGTH = {"municipio": 5, "distrito": 7, "seccion_censal": 10}
# A Madrid barrio is not a prefix of the code (section 2807905013 lies in barrio 28079051): each
# section names it as its parent in the geography (D-232).
PARENT_LEVELS = ("barrio",)

_VERSION = text(
    """
    SELECT bronze_manifest_path, coalesce(source_modified_at, retrieved_at)::date AS observed
      FROM dataset_version
     WHERE dataset_id = :dataset_id AND is_last_valid
    """
)
_SECTIONS = text(
    """
    SELECT code_official, ST_AsBinary(geom_25830) AS wkb
      FROM geo_admin_unit
     WHERE level = 'seccion_censal'
    """
)
_DESTINATIONS = text(
    """
    SELECT subcategory, attributes, ST_X(geom_25830) AS x, ST_Y(geom_25830) AS y
      FROM place_master
     WHERE category = :category AND status = 'ACTIVE'
    """
)
_ZONES = text("SELECT code_official FROM geo_admin_unit WHERE level = :level ORDER BY 1")
_SECTION_PARENTS = text(
    """
    SELECT s.code_official AS section, p.code_official AS zone
      FROM geo_admin_unit s
      JOIN geo_admin_unit p ON p.admin_unit_id = s.parent_admin_unit_id
     WHERE s.level = 'seccion_censal' AND p.level = :level
    """
)


@dataclass(frozen=True)
class NetworkVersion:
    path: Path
    observed: date


@dataclass(frozen=True)
class Origins:
    """Nodes of the streets where people live, the street metres each stands for and the
    census section it lies in ('' outside every section)."""

    node: IntArray
    weight: FloatArray
    section: NDArray[np.str_]


def network_version(engine: Engine) -> NetworkVersion:
    with engine.connect() as conn:
        row = conn.execute(_VERSION, {"dataset_id": NETWORK_DATASET}).mappings().first()
    if row is None:
        msg = f"{NETWORK_DATASET} has no valid version: make ingest DATASET={NETWORK_DATASET}"
        raise LookupError(msg)
    manifest = Path(row["bronze_manifest_path"])
    directory = (manifest if manifest.is_absolute() else REPO_ROOT / manifest).parent
    return NetworkVersion(directory / NETWORK_FILE, row["observed"])


@cache
def routable(path: Path) -> RoutableNetwork:
    return RoutableNetwork.build(load_network(path))


def _sections_of(engine: Engine, x: FloatArray, y: FloatArray) -> NDArray[np.str_]:
    with engine.connect() as conn:
        rows = conn.execute(_SECTIONS).all()
    codes = np.array([str(r[0]) for r in rows])
    tree = shapely.STRtree(shapely.from_wkb([bytes(r[1]) for r in rows]))
    point, polygon = tree.query(shapely.points(x, y), predicate="intersects")
    section = np.full(len(x), "", dtype=codes.dtype if len(codes) else "<U10")
    section[point[::-1]] = codes[polygon[::-1]]  # a point on a shared edge keeps its first match
    return section


@cache
def origins(engine: Engine, path: Path, origin_highways: tuple[str, ...]) -> Origins:
    network = routable(path).network
    weights = origin_weights(network, list(origin_highways))
    node = np.flatnonzero(weights > 0)
    section = _sections_of(engine, network.node_x[node], network.node_y[node])
    return Origins(node.astype(np.int64), weights[node], section)


@cache
def distances(
    engine: Engine,
    path: Path,
    category: str,
    subcategories: tuple[str, ...],
    attributes: tuple[tuple[str, tuple[str, ...]], ...],
) -> FloatArray:
    """Metres from every network node to the nearest selected destination."""
    with engine.connect() as conn:
        frame = pd.DataFrame(conn.execute(_DESTINATIONS, {"category": category}).mappings().all())
    kept = (
        place_filter(frame, subcategories or None, dict(attributes) or None) if len(frame) else []
    )
    x, y = destination_points(kept)
    return routable(path).distance_to_nearest(x, y)


def frozen_attributes(
    attributes: Mapping[str, Sequence[str]] | None,
) -> tuple[tuple[str, tuple[str, ...]], ...]:
    return tuple(sorted((k, tuple(v)) for k, v in (attributes or {}).items()))


def zone_of_node(
    section: NDArray[np.str_], level: str, parent_of: Mapping[str, str] | None = None
) -> NDArray[np.str_]:
    """Each origin node's zone at `level`: a prefix of the code of the section it lies in or,
    for a barrio, the section's parent (`parent_of`, section -> barrio; '' outside Madrid)."""
    if level in PARENT_LEVELS:
        if parent_of is None:
            msg = f"zones by {level!r} need each section's parent {level}"
            raise ValueError(msg)
        return np.array([parent_of.get(s, "") for s in section.tolist()], dtype=section.dtype)
    if level not in CODE_LENGTH:
        known = sorted([*CODE_LENGTH, *PARENT_LEVELS])
        msg = f"walking access is computed by {known}, not by {level!r}"
        raise ValueError(msg)
    return np.array([s[: CODE_LENGTH[level]] for s in section.tolist()], dtype=section.dtype)


def section_parents(engine: Engine, level: str) -> dict[str, str] | None:
    """Section code -> code of its parent zone at `level`, for the levels that are not a
    prefix of the section code (None for the others)."""
    if level not in PARENT_LEVELS:
        return None
    with engine.connect() as conn:
        rows = conn.execute(_SECTION_PARENTS, {"level": level}).all()
    return {str(section): str(zone) for section, zone in rows}


def zone_codes(engine: Engine, level: str) -> list[str]:
    with engine.connect() as conn:
        return [str(c) for c in conn.execute(_ZONES, {"level": level}).scalars()]
