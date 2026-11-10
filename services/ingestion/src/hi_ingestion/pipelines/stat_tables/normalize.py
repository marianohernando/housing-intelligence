"""Source rows -> canonical observations. Pure functions over pandas frames."""

import re
from dataclasses import dataclass
from datetime import date
from typing import Any, cast

import pandas as pd

from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_contracts.catalog.pipeline import CmPostcodeConceptPipeline, CmStatTablePipeline
from hi_domain.geo.codes import MADRID_PROVINCE_CODE, admin_unit_id, ine_municipality_from_cm
from hi_ingestion.catalog_harvester.common import slugify

OBS_COLUMNS = [
    "metric_id",
    "territory_level",
    "territory_code",
    "territory_name",
    "admin_unit_id",
    "period_start",
    "period_end",
    "dims",
    "dims_key",
    "value",
    "null_reason",
    "unit",
    "raw_value",
]
_YEAR = re.compile(r"^(\d{4})$")


class RowError(ValueError):
    """A source row that cannot be normalised (goes to quarantine)."""


@dataclass(frozen=True)
class Observations:
    frame: pd.DataFrame
    quarantine: pd.DataFrame
    source_rows: int
    out_of_window: int = 0


def parse_period(raw: str) -> tuple[date, date]:
    match = _YEAR.match(raw)
    if not match:
        msg = f"unsupported period {raw!r} (expected YYYY)"
        raise RowError(msg)
    year = int(match.group(1))
    return date(year, 1, 1), date(year, 12, 31)


def parse_value(raw: str, missing: list[str], decimal: str) -> tuple[float | None, str | None]:
    """Missing markers -> SOURCE_MISSING; unparseable -> PARSE_ERROR. Never 0 by default."""
    if raw in missing:
        return None, NullReason.SOURCE_MISSING.value
    text = raw.replace(decimal, ".") if decimal != "." else raw
    try:
        return float(text), None
    except ValueError:
        return None, NullReason.PARSE_ERROR.value


def resolve_territory(level: TerritoryLevel, raw_code: str, name: str) -> tuple[str, str | None]:
    if level is TerritoryLevel.CCAA:
        return MADRID_PROVINCE_CODE, None
    if level is TerritoryLevel.MUNICIPIO:
        try:
            code = ine_municipality_from_cm(raw_code)
        except ValueError as exc:
            raise RowError(str(exc)) from exc
        return code, admin_unit_id("municipio", code)
    if level is TerritoryLevel.CODIGO_POSTAL:
        if not re.match(r"^28\d{3}$", raw_code):
            msg = f"invalid Madrid postcode {raw_code!r}"
            raise RowError(msg)
        return raw_code, None
    code = raw_code or slugify(name)
    if not code:
        msg = "territory without code or name"
        raise RowError(msg)
    return code, None


def dims_key(dims: dict[str, str]) -> str:
    return "|".join(f"{k}={v}" for k, v in sorted(dims.items()))


def _observation(**fields: Any) -> dict[str, Any]:
    return {column: fields.get(column) for column in OBS_COLUMNS}


def _stat_row(row: dict[str, str], spec: CmStatTablePipeline) -> dict[str, Any]:
    raw_type = row[spec.territory_type_column]
    if raw_type not in spec.territory_types:
        msg = f"unknown territory type {raw_type!r}"
        raise RowError(msg)
    level = spec.territory_types[raw_type]
    if spec.metric_split:
        split_value = row[spec.metric_split.column]
        if split_value not in spec.metric_split.metrics:
            msg = f"unknown {spec.metric_split.column} value {split_value!r}"
            raise RowError(msg)
        metric_id = spec.metric_split.metrics[split_value]
    else:
        metric_id = str(spec.metric_id)
    name = row[spec.territory_name_column]
    code, unit_id = resolve_territory(level, row[spec.territory_code_column], name)
    start, end = parse_period(row[spec.period_column])
    dims = {
        dim: slugify(row[column]) or "unknown" for column, dim in spec.dimension_columns.items()
    }
    value, null_reason = parse_value(row[spec.value_column], spec.missing_markers, spec.csv.decimal)
    return _observation(
        metric_id=metric_id,
        territory_level=level.value,
        territory_code=code,
        territory_name=name,
        admin_unit_id=unit_id,
        period_start=start,
        period_end=end,
        dims=dims,
        dims_key=dims_key(dims),
        value=value,
        null_reason=null_reason,
        unit=row[spec.unit_column] if spec.unit_column else None,
        raw_value=row[spec.value_column],
    )


def _postcode_row(row: dict[str, str], spec: CmPostcodeConceptPipeline) -> dict[str, Any]:
    match = re.search(spec.postcode_pattern, row[spec.concept_column], flags=re.IGNORECASE)
    if not match:
        msg = f"no postcode in concept {row[spec.concept_column][:60]!r}"
        raise RowError(msg)
    code, _ = resolve_territory(TerritoryLevel.CODIGO_POSTAL, match.group(1), "")
    label = row[spec.concept_column][match.end() :].lstrip(" -")
    start, end = parse_period(row[spec.period_column])
    value, null_reason = parse_value(row[spec.value_column], spec.missing_markers, spec.csv.decimal)
    return _observation(
        metric_id=spec.metric_id,
        territory_level=TerritoryLevel.CODIGO_POSTAL.value,
        territory_code=code,
        territory_name=label or None,
        admin_unit_id=None,
        period_start=start,
        period_end=end,
        dims={},
        dims_key="",
        value=value,
        null_reason=null_reason,
        unit=row.get("Unidad"),
        raw_value=row[spec.value_column],
    )


def within_period_window(frame: pd.DataFrame, spec: CmStatTablePipeline) -> pd.DataFrame:
    """Rows from period_min on; non-year periods stay so they still reach quarantine."""
    if spec.period_min is None:
        return frame
    periods: list[str] = frame[spec.period_column].astype(str).str.strip().tolist()
    keep = [not _YEAR.match(p) or int(p) >= spec.period_min for p in periods]
    return cast(pd.DataFrame, frame.loc[keep])


def normalize(
    frame: pd.DataFrame, spec: CmStatTablePipeline | CmPostcodeConceptPipeline
) -> Observations:
    source_rows = len(frame)
    if isinstance(spec, CmStatTablePipeline):
        frame = within_period_window(frame, spec)
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    records: list[dict[str, str]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    for index, row in enumerate(records):
        try:
            if isinstance(spec, CmStatTablePipeline):
                rows.append(_stat_row(row, spec))
            else:
                rows.append(_postcode_row(row, spec))
        except (RowError, KeyError) as exc:
            bad.append({"source_row": index, "reason": str(exc), "raw": str(row)[:300]})
    return Observations(
        pd.DataFrame(rows, columns=OBS_COLUMNS),
        pd.DataFrame(bad, columns=["source_row", "reason", "raw"]),
        len(frame),
        source_rows - len(frame),
    )
