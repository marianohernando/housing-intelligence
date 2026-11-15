"""SERPAVI workbook -> canonical observations (D-242).

The workbook has one sheet per level and one row per territory; every year is a block of
columns with the suffix `_YY` (`ALQM2_LV_M_VC_24`: median rent per m² of flats in 2024). The
parser reads the declared sheets as they are, keeping the columns of the years from
`period_min`; `normalize` keeps the province's rows and turns each cell into one observation.
"""

import math
import re
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
from openpyxl import load_workbook

from hi_contracts.catalog.enums import NullReason
from hi_contracts.catalog.pipeline import SerpaviRentPipeline, SerpaviSheet
from hi_domain.geo.codes import admin_unit_id
from hi_ingestion.pipelines.stat_tables.normalize import (
    OBS_COLUMNS,
    Observations,
    RowError,
    dims_key,
)

CODE_DIGITS = {"municipio": 5, "distrito": 7, "seccion_censal": 10}
LEAD_COLUMNS = ["level", "province", "code", "name"]
RENT_UNIT, COUNT_UNIT = "EUR/m2/mes", "contratos"
_YEAR_SUFFIX = re.compile(r"_(\d{2})$")


def years_in_header(header: Iterable[str], spec: SerpaviRentPipeline) -> list[int]:
    """The years whose count column is in the header, from `period_min` on."""
    first = next(iter(spec.typologies))
    prefix = spec.count_column.format(typology=first, yy="")
    years = {
        2000 + int(found.group(1))
        for column in header
        if column.startswith(prefix) and (found := _YEAR_SUFFIX.search(column))
    }
    return sorted(y for y in years if y >= spec.period_min)


def value_columns(spec: SerpaviRentPipeline, year: int) -> list[str]:
    yy = f"{year % 100:02d}"
    counts = [spec.count_column.format(typology=t, yy=yy) for t in spec.typologies]
    rents = [
        spec.rent_column.format(statistic=s, typology=t, yy=yy)
        for t in spec.typologies
        for s in spec.statistics
    ]
    return counts + rents


def _sheet_frame(
    rows: Iterable[tuple[Any, ...]], level: str, sheet: SerpaviSheet, spec: SerpaviRentPipeline
) -> pd.DataFrame:
    """One sheet as raw cells (kept as objects: an empty cell stays None, never NaN): the lead
    columns plus every value column of the years read."""
    iterator = iter(rows)
    header = [str(c).strip() if c is not None else "" for c in next(iterator)]
    years = years_in_header(header, spec)
    if not years:
        msg = f"{sheet.sheet}: no year from {spec.period_min} in the header"
        raise ValueError(msg)
    wanted = [c for y in years for c in value_columns(spec, y)]
    names = [sheet.name_column] if sheet.name_column else []
    lead = [spec.province_column, sheet.code_column, *names]
    missing = sorted(set(lead + wanted) - set(header))
    if missing:
        msg = f"{sheet.sheet}: missing columns {missing[:6]}"
        raise ValueError(msg)
    index = {name: header.index(name) for name in lead + wanted}
    records = []
    for row in iterator:
        if all(cell is None for cell in row):
            continue
        record: dict[str, Any] = {
            "level": level,
            "province": row[index[spec.province_column]],
            "code": row[index[sheet.code_column]],
            "name": row[index[sheet.name_column]] if sheet.name_column else None,
        }
        record |= {column: row[index[column]] for column in wanted}
        records.append(record)
    return pd.DataFrame(records, columns=LEAD_COLUMNS + wanted, dtype=object)


def parse_workbook(path: Path, spec: SerpaviRentPipeline) -> pd.DataFrame:
    """Every declared sheet, one raw row per territory (all provinces), stacked by level."""
    book = load_workbook(path, read_only=True, data_only=True)
    try:
        frames = []
        for level, sheet in spec.sheets.items():
            if sheet.sheet not in book.sheetnames:
                msg = f"{path.name}: no sheet {sheet.sheet!r} (has {book.sheetnames})"
                raise ValueError(msg)
            rows = book[sheet.sheet].iter_rows(values_only=True)
            frames.append(_sheet_frame(rows, level, sheet, spec))
    finally:
        book.close()
    return pd.concat(frames, ignore_index=True)


def territory_code(raw: Any, level: str) -> str:
    """INE code as text: an integer cell gets its leading zeros back."""
    if isinstance(raw, bool) or raw is None:
        msg = f"no {level} code"
        raise RowError(msg)
    text = str(int(raw)) if isinstance(raw, int | float) else str(raw).strip()
    code = text.zfill(CODE_DIGITS[level])
    if not code.isdigit() or len(code) != CODE_DIGITS[level]:
        msg = f"invalid {level} code {raw!r}"
        raise RowError(msg)
    return code


def in_province(raw: Any, province: str) -> bool:
    if is_empty(raw):
        return False
    text = str(int(raw)) if isinstance(raw, int | float) else str(raw).strip()
    return text.zfill(2) == province


def is_empty(raw: Any) -> bool:
    return (
        raw is None
        or (isinstance(raw, str) and not raw.strip())
        or bool(isinstance(raw, float) and math.isnan(raw))
    )


def cell_value(raw: Any) -> tuple[float | None, str | None]:
    """An empty cell is SOURCE_MISSING (the source does not publish fewer than 10 homes),
    never 0; a number is kept; anything else cannot be read and goes to quarantine."""
    if is_empty(raw):
        return None, NullReason.SOURCE_MISSING.value
    if isinstance(raw, bool):
        msg = f"not a number: {raw!r}"
        raise RowError(msg)
    if isinstance(raw, int | float):
        return float(raw), None
    try:
        return float(str(raw).strip().replace(",", ".")), None
    except ValueError as exc:
        msg = f"not a number: {raw!r}"
        raise RowError(msg) from exc


def _observation(
    metric_id: str,
    place: tuple[str, str, str | None, str | None],
    year: int,
    dims: dict[str, str],
    raw: Any,
    unit: str,
) -> dict[str, Any]:
    level, code, name, unit_id = place
    value, null_reason = cell_value(raw)
    return {
        "metric_id": metric_id,
        "territory_level": level,
        "territory_code": code,
        "territory_name": name,
        "admin_unit_id": unit_id,
        "period_start": date(year, 1, 1),
        "period_end": date(year, 12, 31),
        "dims": dims,
        "dims_key": dims_key(dims),
        "value": value,
        "null_reason": null_reason,
        "unit": unit,
        "raw_value": None if is_empty(raw) else str(raw),
    }


def _row_observations(
    row: dict[str, Any], spec: SerpaviRentPipeline, years: list[int], known_units: set[str]
) -> list[dict[str, Any]]:
    level = str(row["level"])
    code = territory_code(row["code"], level)
    unit_id = admin_unit_id(level, code)
    name = None if is_empty(row["name"]) else str(row["name"]).strip()
    place = (level, code, name, unit_id if unit_id in known_units else None)
    out: list[dict[str, Any]] = []
    for year in years:
        yy = f"{year % 100:02d}"
        for typology_code, typology in spec.typologies.items():
            count = spec.count_column.format(typology=typology_code, yy=yy)
            dims = {spec.typology_dim: typology}
            out.append(
                _observation(spec.count_metric_id, place, year, dims, row[count], COUNT_UNIT)
            )
            for statistic_code, statistic in spec.statistics.items():
                column = spec.rent_column.format(
                    statistic=statistic_code, typology=typology_code, yy=yy
                )
                rent_dims = dims | {spec.statistic_dim: statistic}
                out.append(
                    _observation(
                        spec.rent_metric_id, place, year, rent_dims, row[column], RENT_UNIT
                    )
                )
    return out


def normalize(
    frame: pd.DataFrame, spec: SerpaviRentPipeline, known_units: set[str]
) -> Observations:
    """The province's rows -> one observation per cell; rows of other provinces are counted
    (`out_of_window`), never quarantined; a row that does not parse is. `known_units`: the
    admin units of the geography, so a section of another census edition keeps its code
    without a broken link."""
    years = years_in_header(frame.columns, spec)
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    in_scope = 0
    records: list[dict[str, Any]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    for index, row in enumerate(records):
        if not in_province(row["province"], spec.province_code):
            continue
        in_scope += 1
        try:
            rows.extend(_row_observations(row, spec, years, known_units))
        except RowError as exc:
            bad.append({"source_row": index, "reason": str(exc), "raw": str(row)[:300]})
    return Observations(
        pd.DataFrame(rows, columns=OBS_COLUMNS),
        pd.DataFrame(bad, columns=["source_row", "reason", "raw"]),
        in_scope,
        len(frame) - in_scope,
    )
