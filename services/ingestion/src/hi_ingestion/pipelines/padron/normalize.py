"""Padrón rows (census section x single year of age) -> people by district and CM age band.

The padrón is an exhaustive register: an age with no row in a district means nobody of that
age lives there, so every band is published (0 included). A row that cannot be read goes to
quarantine and is never counted as 0.
"""

import re
from collections import Counter
from datetime import date
from typing import Any

import pandas as pd

from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.catalog.pipeline import MadridPadronPipeline
from hi_domain.geo.codes import admin_unit_id
from hi_domain.population import TOTAL_AGE, five_year_age_band, five_year_age_bands
from hi_ingestion.pipelines.stat_tables.normalize import (
    OBS_COLUMNS,
    Observations,
    RowError,
    dims_key,
)

UNIT = "personas"
_LEADING_INTEGER = re.compile(r"^(\d+)")  # "100 o +" is the open band


def parse_age(raw: str) -> int:
    match = _LEADING_INTEGER.match(raw.strip())
    if not match:
        msg = f"unreadable age {raw!r}"
        raise RowError(msg)
    return int(match.group(1))


def _count(raw: str) -> int:
    if not raw.isdigit():
        msg = f"count is not a non-negative integer: {raw!r}"
        raise RowError(msg)
    return int(raw)


def district_code(raw: str, municipio_ine: str) -> str:
    """Ayuntamiento district number (1-21) -> 7-digit code, e.g. '6' -> '2807906'."""
    if not raw.isdigit() or not 1 <= int(raw) <= 99:
        msg = f"invalid district {raw!r}"
        raise RowError(msg)
    return f"{municipio_ine}{int(raw):02d}"


def _period(raw: str) -> date:
    try:
        return date.fromisoformat(raw)
    except ValueError as exc:
        msg = f"unsupported period {raw!r} (expected YYYY-MM-DD)"
        raise RowError(msg) from exc


def _observation(
    spec: MadridPadronPipeline, code: str, name: str | None, period: date, band: str, value: int
) -> dict[str, Any]:
    dims = {"edad": band}
    return {
        "metric_id": spec.metric_id,
        "territory_level": TerritoryLevel.DISTRITO.value,
        "territory_code": code,
        "territory_name": name,
        "admin_unit_id": admin_unit_id(TerritoryLevel.DISTRITO.value, code),
        "period_start": period,
        "period_end": period,
        "dims": dims,
        "dims_key": dims_key(dims),
        "value": float(value),
        "null_reason": None,
        "unit": UNIT,
        "raw_value": None,
    }


def normalize(frame: pd.DataFrame, spec: MadridPadronPipeline) -> Observations:
    people: Counter[tuple[str, date, str]] = Counter()
    names: dict[str, str] = {}
    bad: list[dict[str, Any]] = []
    records: list[dict[str, str]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    for index, row in enumerate(records):
        try:
            code = district_code(row[spec.district_column], spec.municipio_ine)
            period = _period(row[spec.period_column])
            band = five_year_age_band(parse_age(row[spec.age_column]))
            count = sum(_count(row[column]) for column in spec.count_columns)
        except (RowError, KeyError) as exc:
            bad.append({"source_row": index, "reason": str(exc), "raw": str(row)[:300]})
            continue
        people[(code, period, band)] += count
        people[(code, period, TOTAL_AGE)] += count
        if spec.district_name_column:
            names.setdefault(code, row[spec.district_name_column])
    districts = sorted({(code, period) for code, period, _ in people})
    rows = [
        _observation(spec, code, names.get(code), period, band, people[(code, period, band)])
        for code, period in districts
        for band in [*five_year_age_bands(), TOTAL_AGE]
    ]
    return Observations(
        pd.DataFrame(rows, columns=OBS_COLUMNS),
        pd.DataFrame(bad, columns=["source_row", "reason", "raw"]),
        len(frame),
    )
