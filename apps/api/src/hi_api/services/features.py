"""Feature catalogue and values. Parameterised SQL only."""

from typing import Any

from sqlalchemy import Connection, text

from hi_domain.geo.names import display_name

_LIST = text(
    """
    SELECT feature_id, version, human_name, domain, unit, direction, geo_level,
           spec->'public_use' AS public_use, spec->'limitations' AS limitations,
           spec->'sources' AS sources
      FROM feature_registry
     WHERE geo_level = :level
     ORDER BY domain, feature_id
    """
)
_VALUES = text(
    """
    SELECT v.territory_code, v.admin_unit_id, v.period_start, v.value, v.null_reason,
           v.confidence, u.name
      FROM feature_value v
      LEFT JOIN geo_admin_unit u ON u.admin_unit_id = v.admin_unit_id
     WHERE v.feature_id = :feature_id AND v.territory_level = :level
     ORDER BY v.territory_code
    """
)
# Lineage of the requested level: each level cites its own datasets (e.g. district rent).
_LINEAGE = text(
    """
    SELECT inputs FROM feature_value
     WHERE feature_id = :feature_id AND territory_level = :level
     LIMIT 1
    """
)


def list_features(conn: Connection, level: str) -> list[dict[str, Any]]:
    return [dict(r) for r in conn.execute(_LIST, {"level": level}).mappings().all()]


def feature_values(
    conn: Connection, feature_id: str, level: str
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [
        dict(r) | {"name": display_name(r["name"]) if r["name"] else None}
        for r in conn.execute(_VALUES, {"feature_id": feature_id, "level": level}).mappings().all()
    ]
    params = {"feature_id": feature_id, "level": level}
    lineage = conn.execute(_LINEAGE, params).scalar() or {}
    return rows, lineage
