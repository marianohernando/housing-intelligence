"""Read Silver from PostGIS into frames for the pure feature methods."""

import pandas as pd
from sqlalchemy import Engine, text

_OBS = text(
    """
    SELECT territory_code, period_start, dims, value, null_reason
      FROM metric_observation
     WHERE metric_id = :metric_id AND territory_level = :level
    """
)
# Each place's zone at a level: its municipio, or the district of the census section it lies in
# (a section code is municipio + district + section: 28079 01 001).
_PLACES = {
    "municipio": text(
        """
        SELECT municipio_ine AS territory_code, subcategory, attributes
          FROM place_master
         WHERE category = :category AND status = 'ACTIVE'
        """
    ),
    "distrito": text(
        """
        SELECT left(u.code_official, 7) AS territory_code, p.subcategory, p.attributes
          FROM place_master p
          JOIN geo_admin_unit u ON u.admin_unit_id = p.seccion_admin_unit_id
         WHERE p.category = :category AND p.status = 'ACTIVE'
        """
    ),
}
# Share of a municipio's places (of one category) that lie in a census section.
_SECTION_SHARE = text(
    """
    SELECT municipio_ine, avg((seccion_admin_unit_id IS NOT NULL)::int)::float AS share
      FROM place_master
     WHERE category = :category AND status = 'ACTIVE' AND municipio_ine IS NOT NULL
     GROUP BY municipio_ine
    """
)
_VERSIONS = text(
    """
    SELECT dataset_id, version_label FROM dataset_version
     WHERE is_last_valid AND dataset_id = ANY(:dataset_ids)
    """
)


def observations(engine: Engine, metric_id: str, level: str = "municipio") -> pd.DataFrame:
    with engine.connect() as conn:
        rows = conn.execute(_OBS, {"metric_id": metric_id, "level": level}).mappings().all()
    return pd.DataFrame(
        [dict(r) for r in rows],
        columns=["territory_code", "period_start", "dims", "value", "null_reason"],
    )


def places(engine: Engine, category: str, level: str = "municipio") -> pd.DataFrame:
    if level not in _PLACES:
        msg = f"places cannot be counted by {level!r} (known: {sorted(_PLACES)})"
        raise ValueError(msg)
    with engine.connect() as conn:
        rows = conn.execute(_PLACES[level], {"category": category}).mappings().all()
    return pd.DataFrame(
        [dict(r) for r in rows], columns=["territory_code", "subcategory", "attributes"]
    )


def section_share(engine: Engine, category: str) -> dict[str, float]:
    with engine.connect() as conn:
        rows = conn.execute(_SECTION_SHARE, {"category": category}).all()
    return {str(code): float(share) for code, share in rows}


def last_valid_versions(engine: Engine, dataset_ids: list[str]) -> dict[str, str]:
    with engine.connect() as conn:
        rows = conn.execute(_VERSIONS, {"dataset_ids": dataset_ids}).all()
    return {str(d): str(v) for d, v in rows}
