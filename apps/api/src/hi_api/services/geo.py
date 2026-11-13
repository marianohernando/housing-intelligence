"""Canonical geography queries. Parameterised SQL only; no user-provided SQL."""

import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, text

from hi_contracts.catalog.enums import AdminLevel
from hi_domain.geo.names import display_name

MAX_SIMPLIFY_METERS = 500
GEOJSON_DECIMALS = 6

_UNITS_SQL = text(
    """
    SELECT u.admin_unit_id, u.level, u.code_official, u.name, u.parent_admin_unit_id,
           round((u.area_m2 / 1e6)::numeric, 4) AS area_km2,
           ST_AsGeoJSON(
               ST_Transform(ST_SimplifyPreserveTopology(u.geom_25830, :tolerance), 4326), :decimals
           ) AS geometry
    FROM geo_admin_unit u
    WHERE u.level = :level
      AND (CAST(:parent AS text) IS NULL OR u.parent_admin_unit_id = :parent)
    ORDER BY u.admin_unit_id
    """
)
_LINEAGE_SQL = text(
    """
    SELECT v.version_label, v.parser_version, s.attribution_text, s.license_name
    FROM geo_admin_unit u
    JOIN dataset_version v ON v.id = u.dataset_version_id
    JOIN source_registry s ON s.source_id = u.source_id
    WHERE u.level = :level
    LIMIT 1
    """
)


@dataclass(frozen=True)
class AdminUnitsResult:
    feature_collection: dict[str, Any]
    data_version: str | None
    lineage: dict[str, Any]


def admin_units_geojson(
    conn: Connection, level: AdminLevel, simplify_m: float, parent: str | None = None
) -> AdminUnitsResult:
    """Units of a level, optionally only the direct children of `parent` (an admin_unit_id)."""
    tolerance = min(max(simplify_m, 0.0), MAX_SIMPLIFY_METERS)
    params = {
        "level": level.value,
        "parent": parent,
        "tolerance": tolerance,
        "decimals": GEOJSON_DECIMALS,
    }
    rows = conn.execute(_UNITS_SQL, params).mappings().all()
    features = [
        {
            "type": "Feature",
            "id": row["admin_unit_id"],
            "geometry": json.loads(row["geometry"]),
            "properties": {
                "admin_unit_id": row["admin_unit_id"],
                "level": row["level"],
                "code": row["code_official"],
                "name": display_name(row["name"]) if row["name"] else None,
                "parent": row["parent_admin_unit_id"],
                "area_km2": float(row["area_km2"]),
            },
        }
        for row in rows
    ]
    lineage_row = conn.execute(_LINEAGE_SQL, {"level": level.value}).mappings().first()
    lineage = dict(lineage_row) if lineage_row else {}
    return AdminUnitsResult(
        feature_collection={"type": "FeatureCollection", "features": features},
        data_version=lineage.get("version_label"),
        lineage=lineage | {"simplify_m": tolerance},
    )
