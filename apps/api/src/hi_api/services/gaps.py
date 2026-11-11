"""Per-zone list of what is missing (GAP-001): feature values against the regional reference.

Rows come from the features bound to a gap row in the Feature Dictionary (`gap_row`), so no
feature id is hardcoded here. Parameterised SQL only.
"""

from collections.abc import Iterable
from typing import Any

from sqlalchemy import Connection, text

from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public import (
    DatasetRef,
    GapRow,
    IndicatorValue,
    ZoneGapList,
    ZoneRef,
)
from hi_domain.gaps import (
    GAP_METHOD,
    UnclassifiableError,
    classify,
    explanation,
    oriented_ratio,
)
from hi_domain.geo.names import display_name

REGION_LEVEL, REGION_CODE = "ccaa", "28"
SIGNIFICANT_DIGITS = 4


def _significant(value: float) -> float:
    """Round for display without erasing small ratios (0.00287 stays 0.002871)."""
    return float(f"{value:.{SIGNIFICANT_DIGITS}g}")


ROW_ORDER = list(GapRowKey)

_ZONE = text(
    """
    SELECT u.admin_unit_id, u.code_official, u.name, m.code_official AS municipio_ine,
           m.name AS municipio_name, ST_X(c) AS lon, ST_Y(c) AS lat
      FROM (SELECT *, ST_PointOnSurface(geom_4326) AS c FROM geo_admin_unit
             WHERE level = :level AND code_official = :code) u
      LEFT JOIN geo_admin_unit m
        ON m.level = 'municipio' AND m.code_official = left(u.code_official, 5)
    """
)
_BOUND_FEATURES = text(
    """
    SELECT feature_id, human_name, unit, direction, spec->'gap_row' AS gap_row
      FROM feature_registry
     WHERE spec->'gap_row' IS NOT NULL AND spec->'gap_row' <> 'null'::jsonb
    """
)
_VALUES = text(
    """
    SELECT feature_id, territory_level, value, null_reason, confidence, inputs, computed_at
      FROM feature_value
     WHERE feature_id = ANY(:features)
       AND ((territory_level = :level AND territory_code = :code)
            OR (territory_level = :region_level AND territory_code = :region_code))
    """
)
_DATASETS = text(
    """
    SELECT d.dataset_id, d.name, d.owner, coalesce(d.portal_url, d.landing_url) AS url,
           d.is_cm_open_data, s.license_name
      FROM dataset_registry d JOIN source_registry s ON s.source_id = d.source_id
     WHERE d.dataset_id = ANY(:ids)
     ORDER BY d.dataset_id
    """
)


class ZoneNotFoundError(LookupError):
    pass


def zone_ref(conn: Connection, level: TerritoryLevel, code: str) -> ZoneRef:
    row = conn.execute(_ZONE, {"level": level.value, "code": code}).mappings().first()
    if row is None:
        msg = f"No {level.value} with code {code}"
        raise ZoneNotFoundError(msg)
    municipio_name = display_name(row["municipio_name"]) if row["municipio_name"] else None
    if level is TerritoryLevel.SECCION_CENSAL:  # sections have no official name
        name = f"Sección {code[5:7]}-{code[7:]}" + (
            f" · {municipio_name}" if municipio_name else ""
        )
    else:
        name = display_name(row["name"]) if row["name"] else code
    return ZoneRef(
        level=level,
        code=code,
        admin_unit_id=row["admin_unit_id"],
        name=name,
        municipio_ine=row["municipio_ine"],
        municipio_name=municipio_name,
        center_lon=round(row["lon"], 5),
        center_lat=round(row["lat"], 5),
    )


def dataset_refs(conn: Connection, versions: dict[str, str]) -> list[DatasetRef]:
    rows = conn.execute(_DATASETS, {"ids": sorted(versions)}).mappings().all()
    return [
        DatasetRef.model_validate(
            {
                "dataset_id": r["dataset_id"],
                "name": r["name"],
                "publisher": r["owner"],
                "is_cm_open_data": r["is_cm_open_data"],
                "url": r["url"],
                "version": versions.get(r["dataset_id"]),
                "license": r["license_name"],
            }
        )
        for r in rows
    ]


def _indicator(
    feature: dict[str, Any], row: dict[str, Any], level: TerritoryLevel
) -> IndicatorValue:
    return IndicatorValue(
        feature_id=feature["feature_id"],
        label=feature["human_name"],
        value=None if row["value"] is None else _significant(float(row["value"])),
        unit=feature["unit"],
        confidence=float(row["confidence"]),
        null_reason=row["null_reason"],
        level=level,
        datasets=sorted(row["inputs"].get("dataset_versions", {})),
    )


def _gap_row(
    conn: Connection,
    feature: dict[str, Any],
    row: dict[str, Any],
    reference_row: dict[str, Any] | None,
    level: TerritoryLevel,
) -> GapRow:
    binding = feature["gap_row"]
    indicator = _indicator(feature, row, level)
    reference = None if reference_row is None else reference_row["value"]
    if indicator.value is None:
        ratio, text_ = None, "Sin datos para esta zona"
    elif reference is None:
        msg = f"{feature['feature_id']}: no regional reference"
        raise UnclassifiableError(msg)
    else:
        ratio = oriented_ratio(indicator.value, float(reference), feature["direction"])
        text_ = explanation(indicator.value, float(reference), binding["phrase"])
    return GapRow(
        row=binding["row"],
        label=binding["label"],
        status=classify(ratio),
        indicator=indicator,
        reference=None if reference is None else _significant(float(reference)),
        reference_label="Comunidad de Madrid",
        direction=feature["direction"],
        ratio_to_reference=None if ratio is None else _significant(ratio),
        explanation=text_,
        proxy_note=binding.get("proxy_note"),
        datasets=dataset_refs(conn, row["inputs"].get("dataset_versions", {})),
    )


def _union(refs: Iterable[DatasetRef]) -> list[DatasetRef]:
    unique = {r.dataset_id: r for r in refs}
    return [unique[k] for k in sorted(unique)]


def zone_gap_list(
    conn: Connection, level: TerritoryLevel, code: str
) -> tuple[ZoneGapList, list[str], str | None]:
    """The list, warnings for rows that could not be classified, and the data version."""
    zone = zone_ref(conn, level, code)
    features = [dict(f) for f in conn.execute(_BOUND_FEATURES).mappings().all()]
    primaries = {f["feature_id"]: f for f in features if f["gap_row"]["role"] == "primary"}
    params = {
        "features": sorted(primaries),
        "level": level.value,
        "code": code,
        "region_level": REGION_LEVEL,
        "region_code": REGION_CODE,
    }
    values: dict[tuple[str, str], dict[str, Any]] = {
        (r["feature_id"], r["territory_level"]): dict(r)
        for r in conn.execute(_VALUES, params).mappings().all()
    }
    rows: list[GapRow] = []
    warnings: list[str] = []
    for feature_id, feature in primaries.items():
        row = values.get((feature_id, level.value))
        if row is None:
            continue  # not computed at this level yet: the row is absent, not SIN_DATOS
        try:
            rows.append(_gap_row(conn, feature, row, values.get((feature_id, REGION_LEVEL)), level))
        except UnclassifiableError as exc:
            warnings.append(str(exc))
    rows.sort(key=lambda r: ROW_ORDER.index(r.row))
    computed = [v["computed_at"] for v in values.values()]
    data_version = max(computed).date().isoformat() if computed else None
    gap_list = ZoneGapList(
        zone=zone,
        method=GAP_METHOD,
        rows=rows,
        datasets=_union(d for r in rows for d in r.datasets),
    )
    return gap_list, warnings, data_version
