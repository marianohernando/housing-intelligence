"""Read Silver from PostGIS into frames for the pure feature methods."""

from collections.abc import Mapping

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
# Postcodes written in the address of places geocoded to a census section, by district or by
# the barrio the section belongs to (D-232: a barrio is the section's parent, not a prefix).
_PLACE_POSTCODES = {
    "distrito": text(
        """
        SELECT left(u.code_official, 7) AS territory_code, p.attributes
          FROM place_master p
          JOIN geo_admin_unit u ON u.admin_unit_id = p.seccion_admin_unit_id
         WHERE p.status = 'ACTIVE' AND p.municipio_ine = :municipio
           AND jsonb_exists_any(p.attributes, :keys)
        """
    ),
    "barrio": text(
        """
        SELECT b.code_official AS territory_code, p.attributes
          FROM place_master p
          JOIN geo_admin_unit u ON u.admin_unit_id = p.seccion_admin_unit_id
          JOIN geo_admin_unit b ON b.admin_unit_id = u.parent_admin_unit_id
         WHERE p.status = 'ACTIVE' AND p.municipio_ine = :municipio AND b.level = 'barrio'
           AND jsonb_exists_any(p.attributes, :keys)
        """
    ),
}
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


def postcode_from_address(attributes: Mapping[str, object], keys: list[str]) -> str | None:
    """The first postcode found among the declared address keys, as five digits."""
    for key in keys:
        raw = str(attributes.get(key) or "").strip()
        if raw.isdigit() and len(raw) <= 5:
            return raw.zfill(5)
    return None


def place_postcodes(
    engine: Engine, keys: list[str], municipio: str, level: str = "distrito"
) -> pd.DataFrame:
    """How many geocoded places of each zone carry each postcode (CORE-006 weights), within
    the municipio the postcode values are published for."""
    if level not in _PLACE_POSTCODES:
        msg = f"postcode weights are built by {sorted(_PLACE_POSTCODES)}, not {level!r}"
        raise ValueError(msg)
    with engine.connect() as conn:
        params = {"keys": keys, "municipio": municipio}
        rows = conn.execute(_PLACE_POSTCODES[level], params).mappings().all()
    counts: dict[tuple[str, str], int] = {}
    for row in rows:
        postcode = postcode_from_address(row["attributes"] or {}, keys)
        if postcode is not None:
            pair = (str(row["territory_code"]), postcode)
            counts[pair] = counts.get(pair, 0) + 1
    return pd.DataFrame(
        [(zone, cp, float(n)) for (zone, cp), n in sorted(counts.items())],
        columns=["territory_code", "postcode", "weight"],
    )
