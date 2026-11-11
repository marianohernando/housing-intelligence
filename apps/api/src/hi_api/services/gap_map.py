"""One row of the list for every zone of a level (GAP-001 F4): the map of what is missing.

Same feature, regional reference and cut-offs as each zone's list (services/gaps.py), so a
zone's colour on the map and its row in the list always agree. Parameterised SQL only.
"""

from typing import Any, NamedTuple

from sqlalchemy import Connection, text

from hi_api.services.gap_reference import Assessment, References, assess, load_references
from hi_api.services.gaps import (
    REGION_CODE,
    REGION_LEVEL,
    dataset_refs,
    missing_row_warnings,
    significant,
    split_bound,
)
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public import GapRowMap, GapStatus, GapStatusCounts, ZoneGapStatus
from hi_domain.gaps import (
    GAP_METHOD,
    REGION_TEXT,
    Direction,
    UnclassifiableError,
    classify,
    oriented_ratio,
)
from hi_domain.geo.names import display_name

_BOUND_ROW = text(
    """
    SELECT feature_id, human_name, unit, direction, spec->'gap_row' AS gap_row
      FROM feature_registry
     WHERE spec->'gap_row' IS NOT NULL AND spec->'gap_row' <> 'null'::jsonb
       AND spec->'gap_row'->>'row' = :row
    """
)
_LEVEL_VALUES = text(
    """
    SELECT v.territory_code, v.admin_unit_id, v.value, v.null_reason, v.confidence, v.inputs,
           v.computed_at, u.name
      FROM feature_value v
      LEFT JOIN geo_admin_unit u ON u.admin_unit_id = v.admin_unit_id
     WHERE v.feature_id = :feature_id AND v.territory_level = :level
     ORDER BY v.territory_code
    """
)
_REGION_VALUE = text(
    """
    SELECT value, inputs, computed_at FROM feature_value
     WHERE feature_id = :feature_id AND territory_level = :level AND territory_code = :code
    """
)


class RowNotBoundError(LookupError):
    """No feature of the Feature Dictionary is the primary indicator of this row."""


class RowContext(NamedTuple):
    feature_id: str
    direction: Direction
    region: dict[str, Any] | None
    references: References


def _zone(row: dict[str, Any], context: RowContext) -> ZoneGapStatus:
    value = None if row["value"] is None else significant(float(row["value"]))
    ref = context.references.for_zone(context.feature_id, row["territory_code"], context.region)
    ratio, judged = None, Assessment(None, True)
    if value is not None:
        if ref is None:
            msg = f"{row['territory_code']}: no regional reference"
            raise UnclassifiableError(msg)
        ratio = oriented_ratio(value, ref.value, context.direction)
        judged = assess(row, ref, context.direction)
    return ZoneGapStatus(
        admin_unit_id=row["admin_unit_id"] or row["territory_code"],
        code=row["territory_code"],
        name=display_name(row["name"]) if row["name"] else row["territory_code"],
        status=classify(ratio, significant=judged.significant),
        value=value,
        reference=None if ref is None else significant(ref.value),
        reference_label=REGION_TEXT.label if ref is None else ref.label,
        ratio_to_reference=None if ratio is None else significant(ratio),
        confidence=float(row["confidence"]),
        null_reason=row["null_reason"],
        reliable=judged.reliable,
    )


def _counts(zones: list[ZoneGapStatus]) -> GapStatusCounts:
    return GapStatusCounts(
        **{s.value.lower(): sum(z.status is s for z in zones) for s in GapStatus}
    )


def _versions(rows: list[dict[str, Any]]) -> dict[str, str]:
    versions: dict[str, str] = {}
    for row in rows:
        versions.update(row["inputs"].get("dataset_versions", {}))
    return versions


def _primary_feature(conn: Connection, row: GapRowKey) -> dict[str, Any]:
    bound = conn.execute(_BOUND_ROW, {"row": row.value}).mappings()
    primaries, _ = split_bound(dict(f) for f in bound)
    if not primaries:
        msg = f"row {row.value} has no primary indicator in the Feature Dictionary"
        raise RowNotBoundError(msg)
    return next(iter(primaries.values()))


def _zones(
    values: list[dict[str, Any]], context: RowContext
) -> tuple[list[ZoneGapStatus], list[str]]:
    zones: list[ZoneGapStatus] = []
    warnings: list[str] = []
    for value_row in values:
        try:
            zones.append(_zone(value_row, context))
        except UnclassifiableError as exc:
            warnings.append(str(exc))
    return zones, warnings


def gap_row_map(
    conn: Connection, level: TerritoryLevel, row: GapRowKey
) -> tuple[GapRowMap, list[str], str | None]:
    """The map, warnings (row not computed at this level, zones that could not be classified)
    and the data version (latest computation among the values shown)."""
    feature = _primary_feature(conn, row)
    params = {"feature_id": feature["feature_id"]}
    region_params = params | {"level": REGION_LEVEL, "code": REGION_CODE}
    region = conn.execute(_REGION_VALUE, region_params).mappings().first()
    reference = None if region is None or region["value"] is None else float(region["value"])
    level_params = params | {"level": level.value}
    values = [dict(r) for r in conn.execute(_LEVEL_VALUES, level_params).mappings()]
    references = load_references(conn, [feature["feature_id"]])
    region_row = None if region is None else dict(region)
    context = RowContext(feature["feature_id"], feature["direction"], region_row, references)
    zones, warnings = _zones(values, context)
    if not values:  # not computed at this level yet: no zones, not SIN_DATOS
        warnings += missing_row_warnings(set(GapRowKey) - {row}, level)
    used = [*([region_row] if region_row is not None else []), *values]
    binding = feature["gap_row"]
    gap_map = GapRowMap(
        row=row,
        label=binding["label"],
        level=level,
        indicator_label=feature["human_name"],
        unit=feature["unit"],
        direction=feature["direction"],
        reference=None if reference is None else significant(reference),
        reference_label=REGION_TEXT.label,
        proxy_note=binding.get("proxy_note"),
        method=GAP_METHOD,
        counts=_counts(zones),
        zones=zones,
        datasets=dataset_refs(conn, references.versions | _versions(used)),
    )
    data_version = max(v["computed_at"] for v in used).date().isoformat() if used else None
    return gap_map, warnings, data_version
