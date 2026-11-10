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
_PLACES = text(
    """
    SELECT municipio_ine, subcategory, attributes
      FROM place_master
     WHERE category = :category AND status = 'ACTIVE'
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


def places(engine: Engine, category: str) -> pd.DataFrame:
    with engine.connect() as conn:
        rows = conn.execute(_PLACES, {"category": category}).mappings().all()
    return pd.DataFrame(
        [dict(r) for r in rows], columns=["municipio_ine", "subcategory", "attributes"]
    )


def last_valid_versions(engine: Engine, dataset_ids: list[str]) -> dict[str, str]:
    with engine.connect() as conn:
        rows = conn.execute(_VERSIONS, {"dataset_ids": dataset_ids}).all()
    return {str(d): str(v) for d, v in rows}
