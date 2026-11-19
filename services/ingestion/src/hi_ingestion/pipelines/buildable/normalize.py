"""VEDA register of buildable area left -> one observation per residential planning area, in its
district and its barrio (D-247). Pure functions.

A blank cell is not a 0: an area with every residential cell blank but area left for another
use is not residential; one with every use blank keeps an unknown value. m² are never homes.
"""

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_contracts.catalog.pipeline import MadridBuildableAreasPipeline
from hi_domain.geo.codes import admin_unit_id
from hi_domain.geo.names import title_case
from hi_ingestion.catalog_harvester.common import slugify
from hi_ingestion.pipelines.stat_tables.normalize import (
    OBS_COLUMNS,
    Observations,
    RowError,
    dims_key,
)
from hi_ingestion.pipelines.zone_context.normalize import district_code, observation
from hi_ingestion.pipelines.zone_context.parcels import Placement


def clean(raw: Any) -> str:
    """One line of text; an empty Excel cell (None or NaN) is ''."""
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return ""
    return " ".join(str(raw).split())


PARTIAL_BLANK = "partial_blank"


@dataclass(frozen=True)
class PlacedArea:
    """Where an area's point is (its barrio, in the district of the point) and the share of the
    area in that barrio."""

    where: Placement
    share_pct: int


@dataclass(frozen=True)
class AreaRegister:
    obs: Observations
    rows: int
    kept: int
    out_of_scope: Mapping[str, int]
    dates: frozenset[date]
    districts: frozenset[str]
    partial_blank: int = 0  # kept areas with one residential cell blank


def area_size(raw: Any) -> float | None:
    """«16316.7» -> 16316.7; a blank cell -> None (never 0). A negative or unreadable figure is
    an error."""
    text = clean(raw)
    if not text:
        return None
    try:
        value = float(text)
    except ValueError as exc:
        msg = f"unreadable surface {text!r}"
        raise RowError(msg) from exc
    if value < 0:
        msg = f"negative surface {text!r}"
        raise RowError(msg)
    return round(value, 2)  # the register carries up to 14 decimals of a m²


def register_date(raw: Any) -> date:
    try:
        return date.fromisoformat(clean(raw)[:10])
    except ValueError as exc:
        msg = f"unreadable date {raw!r}"
        raise RowError(msg) from exc


def residential(
    row: Mapping[str, Any], spec: MadridBuildableAreasPipeline
) -> tuple[float | None, str, str | None]:
    """(m² left for homes, the building types with some, why it is out of scope or None)."""
    sizes = {slug: area_size(row.get(col)) for col, slug in spec.residential_columns.items()}
    others = [area_size(row.get(col)) for col in spec.other_use_columns]
    if all(v is None for v in sizes.values()):
        if any(v is not None for v in others):
            return None, "", "not_residential"
        return None, "", None  # every use blank: kept, unknown
    total = round(sum(v for v in sizes.values() if v is not None), 2)
    if total == 0:
        return 0.0, "", "nothing_left"
    uses = "_y_".join(slug for slug, v in sizes.items() if v)
    # Kept, and counted: one type of home has a figure and the other a blank cell (read as
    # «this type is not in the area»), so a change in how the register fills cells shows
    return total, uses, PARTIAL_BLANK if any(v is None for v in sizes.values()) else None


def _item(row: Mapping[str, Any], spec: MadridBuildableAreasPipeline) -> tuple[str, str]:
    code = clean(row.get(spec.code_column))
    name = clean(row.get(spec.name_column))
    if not code or not name:
        raise RowError("an area without code or name")
    stage = clean(row.get(spec.stage_column))
    label = title_case(name, frozenset(spec.keep_upper))
    if stage:
        return f"{code}|{slugify(stage)}", f"{label} ({stage.lower()})"
    return code, label


def _place(code: str, district: str, placed: Mapping[str, PlacedArea]) -> tuple[str, PlacedArea]:
    where = placed.get(code)
    if where is None:
        msg = f"area {code} has no point: read the points again"
        raise RowError(msg)
    if where.where.barrio is None or where.where.distrito != district:
        msg = f"the point of area {code} is in no barrio of district {district}"
        raise RowError(msg)
    return where.where.barrio, where


def _area_rows(
    row: Mapping[str, Any],
    spec: MadridBuildableAreasPipeline,
    placed: Mapping[str, PlacedArea],
) -> tuple[list[dict[str, Any]], str | None]:
    state = clean(row.get(spec.state_column))
    if state not in spec.states:
        msg = f"situation {state!r} is not declared (read what it means before showing it)"
        raise RowError(msg)
    district = district_code(spec.municipio_ine, row.get(spec.district_column))
    observed = register_date(row.get(spec.date_column))
    value, uses, out = residential(row, spec)
    if out is not None and out != PARTIAL_BLANK:
        return [], out
    code = clean(row.get(spec.code_column))
    item, name = _item(row, spec)
    barrio, where = _place(code, district, placed)
    dims = {"item": item, "name": name, "stage": spec.states[state], "use": uses}
    if where.share_pct < spec.whole_area_pct:
        dims["note"] = (
            f"El ámbito ocupa también otros barrios: aquí está el {where.share_pct} % de su "
            "superficie."
        )
    dims = {k: v for k, v in dims.items() if v}
    in_district = {k: v for k, v in dims.items() if k != "note"}  # the note is the barrio's
    rows = [
        observation(
            metric_id=spec.metric_id,
            territory_level=level.value,
            territory_code=zone,
            territory_name=None,
            admin_unit_id=admin_unit_id(level.value, zone),
            period_start=observed,
            period_end=observed,
            dims=zone_dims,
            dims_key=dims_key(zone_dims),
            value=value,
            null_reason=None if value is not None else NullReason.UNKNOWN.value,
            unit="m2",
            raw_value=None,
        )
        for level, zone, zone_dims in (
            (TerritoryLevel.DISTRITO, district, in_district),
            (TerritoryLevel.BARRIO, barrio, dims),
        )
    ]
    return rows, out


def normalize_buildable_areas(
    frame: pd.DataFrame, spec: MadridBuildableAreasPipeline, placed: Mapping[str, PlacedArea]
) -> AreaRegister:
    records: list[dict[str, Any]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    out: Counter[str] = Counter()
    dates: set[date] = set()
    districts: set[str] = set()
    for index, row in enumerate(records):
        try:
            dates.add(register_date(row.get(spec.date_column)))
            districts.add(district_code(spec.municipio_ine, row.get(spec.district_column)))
            kept, reason = _area_rows(row, spec, placed)
        except (RowError, KeyError) as exc:
            raw = {k: row.get(k) for k in (spec.code_column, spec.state_column)}
            bad.append({"source_row": index, "reason": str(exc), "raw": str(raw)[:300]})
            continue
        if reason:
            out[reason] += 1
        rows.extend(kept)
    partial = out.pop(PARTIAL_BLANK, 0)
    obs = Observations(
        pd.DataFrame(rows, columns=OBS_COLUMNS),
        pd.DataFrame(bad, columns=["source_row", "reason", "raw"]),
        len(records),
    )
    kept_areas = len(rows) // 2
    return AreaRegister(
        obs, len(records), kept_areas, dict(out), frozenset(dates), frozenset(districts), partial
    )
