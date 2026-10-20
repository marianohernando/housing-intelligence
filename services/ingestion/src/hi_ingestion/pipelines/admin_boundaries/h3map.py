"""Section <-> H3 mapping: area-overlap shares (r8, r9) and centroid assignment for all levels."""

from dataclasses import dataclass
from typing import cast

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

from hi_domain.geo.h3_mapping import cell_centroid, cell_polygon, cells_for_polygon
from hi_ingestion.pipelines.admin_boundaries import config
from hi_ingestion.pipelines.admin_boundaries.transform import to_wgs84


@dataclass(frozen=True)
class H3Mapping:
    cells: gpd.GeoDataFrame  # h3_index, resolution, geometry (4326), centroid (4326)
    links: pd.DataFrame  # h3_index, admin_unit_id, method, overlap_share


def _pairs(sections_4326: gpd.GeoDataFrame, resolution: int) -> pd.DataFrame:
    rows = [
        (cell, unit_id)
        for unit_id, geom in zip(
            sections_4326["admin_unit_id"], sections_4326.geometry, strict=True
        )
        for cell in cells_for_polygon(geom, resolution, "overlap")
    ]
    return pd.DataFrame(rows, columns=["h3_index", "admin_unit_id"])


def _cells_frame(cells: list[str]) -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {
            "h3_index": cells,
            "resolution": [int(c[1], 16) for c in cells],
            "centroid": [shapely.Point(*cell_centroid(c)) for c in cells],
        },
        geometry=[cell_polygon(c) for c in cells],
        crs=config.WGS84,
    )


def _overlap_links(
    pairs: pd.DataFrame, cells: gpd.GeoDataFrame, sections: gpd.GeoDataFrame
) -> pd.DataFrame:
    cell_geom = cells.set_index("h3_index").to_crs(config.SOURCE_CRS).geometry
    sec_geom = sections.set_index("admin_unit_id").geometry
    a = cell_geom.reindex(pairs["h3_index"]).to_numpy()
    b = sec_geom.reindex(pairs["admin_unit_id"]).to_numpy()
    share = shapely.area(shapely.intersection(a, b)) / shapely.area(a)
    links = pairs.assign(method="overlap", overlap_share=np.clip(share, 0, 1))
    kept = links.loc[links["overlap_share"] >= config.MIN_OVERLAP_SHARE]
    return cast(pd.DataFrame, kept).reset_index(drop=True)


def _ancestors(units: gpd.GeoDataFrame) -> dict[str, list[str]]:
    parent = dict(zip(units["admin_unit_id"], units["parent_admin_unit_id"], strict=True))
    chains: dict[str, list[str]] = {}
    for unit_id in units.loc[units["level"] == "seccion_censal", "admin_unit_id"]:
        chain: list[str] = [unit_id]
        while isinstance(parent.get(chain[-1]), str):
            chain.append(parent[chain[-1]])
        chains[unit_id] = chain
    return chains


def _centroid_links(
    cells: gpd.GeoDataFrame, sections_4326: gpd.GeoDataFrame, units: gpd.GeoDataFrame
) -> pd.DataFrame:
    points = gpd.GeoDataFrame(
        {"h3_index": cells["h3_index"].to_numpy()},
        geometry=gpd.GeoSeries(cells["centroid"].to_numpy(), crs=config.WGS84),
        crs=config.WGS84,
    )
    polygons = cast(gpd.GeoDataFrame, sections_4326[["admin_unit_id", "geometry"]])
    joined = gpd.sjoin(points, polygons, predicate="within", how="inner")
    chains = _ancestors(units)
    rows = [
        (cell, ancestor)
        for cell, section in zip(joined["h3_index"], joined["admin_unit_id"], strict=True)
        for ancestor in chains[section]
    ]
    links = pd.DataFrame(rows, columns=["h3_index", "admin_unit_id"]).drop_duplicates()
    return links.assign(method="centroid", overlap_share=1.0)


def build_h3_mapping(units: gpd.GeoDataFrame) -> H3Mapping:
    sections = units[units["level"] == "seccion_censal"]
    sections_4326 = to_wgs84(sections)  # pyright: ignore[reportArgumentType]
    pairs = pd.concat([_pairs(sections_4326, r) for r in config.H3_RESOLUTIONS], ignore_index=True)
    cells = _cells_frame(sorted(pairs["h3_index"].unique()))
    overlap = _overlap_links(pairs, cells, sections)  # pyright: ignore[reportArgumentType]
    centroid = _centroid_links(cells, sections_4326, units)
    links = pd.concat([overlap, centroid], ignore_index=True)
    used = set(links["h3_index"])
    return H3Mapping(cells[cells["h3_index"].isin(used)].reset_index(drop=True), links)  # pyright: ignore[reportArgumentType]
