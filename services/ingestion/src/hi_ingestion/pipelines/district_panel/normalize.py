"""Panel rows -> one observation per declared indicator, district and reference date.

Rows of other indicators are outside the scope: they are counted (`out_of_window`), not
quarantined. So are barrio rows, unless the indicator is in `barrio_indicators` (D-232): then
the row is the barrio (28079 + its three-digit code), named as the Ayuntamiento names it.
The city row is the one with neither district code nor district name; a row with a name but
no code lost its code and goes to quarantine. The
city row of a `city_indicators` indicator is kept as the municipio (D-226). A reference date
carried by several panel editions is kept once, from the latest edition (a revision); a repeat
inside one edition is left for the `unique_keys` check to fail. An edition that is not a year
goes to quarantine.
`source_rows` counts the rows in scope, so the quarantine ratio measures what the pipeline
actually reads; `source_row` in the quarantine is the position in the source file.
"""

from datetime import date, datetime
from typing import Any

import pandas as pd

from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.catalog.pipeline import MadridDistrictPanelPipeline
from hi_domain.geo.codes import admin_unit_id
from hi_ingestion.pipelines.padron.normalize import district_code
from hi_ingestion.pipelines.stat_tables.normalize import (
    OBS_COLUMNS,
    Observations,
    RowError,
    parse_value,
)
from hi_ingestion.pipelines.stat_tables.quality import KEY


def _period(raw: str) -> date:
    try:
        return datetime.strptime(raw, "%d/%m/%Y").date()
    except ValueError as exc:
        msg = f"unsupported date {raw!r} (expected DD/MM/YYYY)"
        raise RowError(msg) from exc


def _is_city(row: dict[str, str], spec: MadridDistrictPanelPipeline) -> bool:
    return not row.get(spec.district_column) and not (
        spec.district_name_column and row.get(spec.district_name_column)
    )


def _in_scope(row: dict[str, str], spec: MadridDistrictPanelPipeline) -> bool:
    indicator = row.get(spec.indicator_column)
    if indicator not in spec.indicators:
        return False
    if row.get(spec.barrio_column):
        return indicator in spec.barrio_indicators
    return not _is_city(row, spec) or indicator in spec.city_indicators


BARRIO_DIGITS = 3  # district (2) + barrio (1): '11' is Palacio (01 1), '201' is Simancas
FIRST_BARRIO = 11


def barrio_code(raw: str, municipio_ine: str) -> str:
    """Ayuntamiento barrio number ('11', '201') -> 8-digit code, e.g. '201' -> '28079201'."""
    if not raw.isdigit() or len(raw) > BARRIO_DIGITS or int(raw) < FIRST_BARRIO:
        msg = f"invalid barrio {raw!r}"
        raise RowError(msg)
    return f"{municipio_ine}{int(raw):03d}"


def _territory(row: dict[str, str], spec: MadridDistrictPanelPipeline) -> tuple[str, str]:
    if row.get(spec.barrio_column):
        return TerritoryLevel.BARRIO.value, barrio_code(row[spec.barrio_column], spec.municipio_ine)
    if _is_city(row, spec):
        return TerritoryLevel.MUNICIPIO.value, spec.municipio_ine
    return TerritoryLevel.DISTRITO.value, district_code(
        row[spec.district_column], spec.municipio_ine
    )


def _name(row: dict[str, str], spec: MadridDistrictPanelPipeline, level: str) -> str | None:
    if level == TerritoryLevel.BARRIO.value:
        return row.get(spec.barrio_name_column) or None
    return (row[spec.district_name_column] or None) if spec.district_name_column else None


def _observation(row: dict[str, str], spec: MadridDistrictPanelPipeline) -> dict[str, Any]:
    level, code = _territory(row, spec)
    day = _period(row[spec.period_column])
    raw = row[spec.value_column]
    value, null_reason = parse_value(raw, spec.missing_markers, spec.csv.decimal)
    return {
        "metric_id": spec.indicators[row[spec.indicator_column]],
        "territory_level": level,
        "territory_code": code,
        "territory_name": _name(row, spec, level),
        "admin_unit_id": admin_unit_id(level, code),
        "period_start": day,
        "period_end": day,
        "dims": {},
        "dims_key": "",
        "value": value,
        "null_reason": null_reason,
        "unit": row[spec.unit_column] if spec.unit_column else None,
        "raw_value": raw,
    }


def _edition(row: dict[str, str], spec: MadridDistrictPanelPipeline) -> int:
    raw = str(row.get(spec.edition_column) or "").strip()
    if not raw.isdigit():
        msg = f"panel edition {raw!r} is not a year"
        raise RowError(msg)
    return int(raw)


def latest_edition(rows: list[tuple[int, dict[str, Any]]]) -> list[dict[str, Any]]:
    """Per key, the observations of the latest panel edition that carries it, in file order.
    Older editions are revisions and drop out; two rows of the same edition both stay."""
    latest: dict[tuple[Any, ...], int] = {}
    for edition, observation in rows:
        key = tuple(observation[k] for k in KEY)
        latest[key] = max(edition, latest.get(key, edition))
    return [obs for edition, obs in rows if latest[tuple(obs[k] for k in KEY)] == edition]


def normalize(frame: pd.DataFrame, spec: MadridDistrictPanelPipeline) -> Observations:
    records: list[dict[str, str]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    in_scope = [(index, row) for index, row in enumerate(records) if _in_scope(row, spec)]
    rows: list[tuple[int, dict[str, Any]]] = []
    bad: list[dict[str, Any]] = []
    for index, row in in_scope:
        try:
            rows.append((_edition(row, spec), _observation(row, spec)))
        except (RowError, KeyError) as exc:
            bad.append({"source_row": index, "reason": str(exc), "raw": str(row)[:300]})
    return Observations(
        pd.DataFrame(latest_edition(rows), columns=OBS_COLUMNS),
        pd.DataFrame(bad, columns=["source_row", "reason", "raw"]),
        len(in_scope),
        len(records) - len(in_scope),
    )
