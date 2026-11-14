"""Source rows -> metric observations for the zone context pipelines (D-241). Pure functions.

Three shapes: an Instituto de Estadística table whose only territory is the municipio's name
(sales of new and second-hand homes), the Ayuntamiento's register of planning areas (VEDA) and
a table typed by hand from an official page (Plan Vive). They all give the observation frame
of the stat tables, so publishing and the common quality checks are shared.
"""

import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.catalog.manual import ZoneItem, ZoneItemsTable
from hi_contracts.catalog.pipeline import (
    CmMunicipioNameTablePipeline,
    DevelopmentReading,
    MadridDevelopmentAreasPipeline,
)
from hi_domain.geo.codes import admin_unit_id
from hi_domain.geo.names import name_key, title_case
from hi_domain.urbanism import development_stage
from hi_ingestion.catalog_harvester.common import slugify
from hi_ingestion.pipelines.stat_tables.normalize import (
    OBS_COLUMNS,
    Observations,
    RowError,
    dims_key,
    parse_period,
    parse_value,
)

_QUARTER = re.compile(r"^T([1-4])$")
QUARTER_MONTHS = 3


def observation(**fields: Any) -> dict[str, Any]:
    return {column: fields.get(column) for column in OBS_COLUMNS}


def quarter_period(year: str, quarter: str) -> tuple[date, date]:
    """«2026», «T2» -> 1 Apr 2026 .. 30 Jun 2026."""
    start, _ = parse_period(year)
    match = _QUARTER.match(quarter)
    if not match:
        msg = f"unsupported quarter {quarter!r} (expected T1..T4)"
        raise RowError(msg)
    first = (int(match.group(1)) - 1) * QUARTER_MONTHS + 1
    begin = date(start.year, first, 1)
    following = date(start.year + 1, 1, 1) if first == 10 else date(start.year, first + 3, 1)
    return begin, date.fromordinal(following.toordinal() - 1)


@dataclass(frozen=True)
class MunicipioNames:
    """Municipio names of the geography by their key (`name_key`): name -> INE code."""

    codes: Mapping[str, str]

    def resolve(self, name: str) -> str:
        code = self.codes.get(name_key(name))
        if code is None:
            msg = f"municipio {name!r} is not a municipio of the geography"
            raise RowError(msg)
        return code


def municipio_names(rows: Mapping[str, str]) -> MunicipioNames:
    """INE code -> official name, as the geography keeps them. Two municipios with the same key
    would make a name ambiguous: that is a geography error, never resolved by picking one."""
    codes: dict[str, str] = {}
    for code, name in rows.items():
        key = name_key(name)
        if key in codes and codes[key] != code:
            msg = f"two municipios share the name key {key!r}"
            raise ValueError(msg)
        codes[key] = code
    return MunicipioNames(codes)


def _in_scope(row: Mapping[str, str], filters: Mapping[str, list[str]]) -> bool:
    return all(row.get(column, "") in allowed for column, allowed in filters.items())


def _named_row(
    row: dict[str, str], spec: CmMunicipioNameTablePipeline, names: MunicipioNames
) -> dict[str, Any]:
    name = " ".join(row[spec.territory_name_column].split())
    code = names.resolve(name)
    if spec.quarter_column:
        start, end = quarter_period(row[spec.period_column], row[spec.quarter_column])
    else:
        start, end = parse_period(row[spec.period_column])
    dims = {
        dim: slugify(row[column]) or "unknown" for column, dim in spec.dimension_columns.items()
    }
    status = (row.get(spec.status_column) or "").strip() if spec.status_column else ""
    if spec.status_dimension and status:
        dims[spec.status_dimension] = slugify(status)
    value, null_reason = parse_value(row[spec.value_column], spec.missing_markers, spec.csv.decimal)
    return observation(
        metric_id=spec.metric_id,
        territory_level=TerritoryLevel.MUNICIPIO.value,
        territory_code=code,
        territory_name=name,
        admin_unit_id=admin_unit_id("municipio", code),
        period_start=start,
        period_end=end,
        dims=dims,
        dims_key=dims_key(dims),
        value=value,
        null_reason=null_reason,
        unit=row[spec.unit_column] if spec.unit_column else None,
        raw_value=row[spec.value_column],
    )


def _recent(row: Mapping[str, str], spec: CmMunicipioNameTablePipeline) -> bool:
    period = row.get(spec.period_column, "")
    return spec.period_min is None or not period.isdigit() or int(period) >= spec.period_min


def normalize_municipio_names(
    frame: pd.DataFrame, spec: CmMunicipioNameTablePipeline, names: MunicipioNames
) -> Observations:
    """Rows outside `row_filters` or before `period_min` are counted, never quarantined; a row
    whose name or period cannot be read is quarantined. `source_rows` counts the rows read."""
    records: list[dict[str, str]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    in_scope = [r for r in records if _in_scope(r, spec.row_filters)]
    recent = [(i, r) for i, r in enumerate(in_scope) if _recent(r, spec)]
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    for index, row in recent:
        try:
            rows.append(_named_row(row, spec, names))
        except (RowError, KeyError) as exc:
            bad.append({"source_row": index, "reason": str(exc), "raw": str(row)[:300]})
    return Observations(
        pd.DataFrame(rows, columns=OBS_COLUMNS),
        pd.DataFrame(bad, columns=["source_row", "reason", "raw"]),
        len(recent),
        len(in_scope) - len(recent),
    )


@dataclass(frozen=True)
class AreaObservations:
    """The kept areas, plus what the whole register says (its size and districts)."""

    obs: Observations
    areas: int
    districts: frozenset[str]
    out_of_scope: int


def _area_state(raw: Any, spec: MadridDevelopmentAreasPipeline) -> DevelopmentReading:
    state = " ".join(str(raw or "").split())
    if state not in spec.states:
        msg = f"unknown development state {state!r}"
        raise RowError(msg)
    return spec.states[state]


def _area_date(raw: Any) -> date:
    text = str(raw or "").strip()[:10]
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        msg = f"unreadable date {raw!r}"
        raise RowError(msg) from exc


def district_code(municipio_ine: str, raw: Any) -> str:
    text = str(raw or "").strip()
    if not text.isdigit() or int(text) == 0 or len(text) > len("21"):
        msg = f"invalid district code {raw!r}"
        raise RowError(msg)
    return f"{municipio_ine}{int(text):02d}"


def _without_prefix(name: str, spec: MadridDevelopmentAreasPipeline) -> str:
    """«DESARROLLO DEL ESTE - LOS AHIJONES» -> «LOS AHIJONES»: the part that tells it apart."""
    prefix = next((p for p in spec.drop_name_prefixes if name.startswith(p)), "")
    return name[len(prefix) :].strip() or name


def _area_row(row: dict[str, Any], spec: MadridDevelopmentAreasPipeline) -> dict[str, Any] | None:
    """The area's observation, or None when it is out of scope (another use, or finished)."""
    use = " ".join(str(row.get(spec.use_column) or "").split())
    if use not in spec.uses:
        return None
    stage = development_stage([_area_state(row.get(c), spec) for c in spec.phase_columns])
    if stage is None:
        return None
    code = district_code(spec.municipio_ine, row.get(spec.district_column))
    area_code = str(row.get(spec.code_column) or "").strip()
    raw_name = _without_prefix(" ".join(str(row.get(spec.name_column) or "").split()), spec)
    if not area_code or not raw_name:
        msg = "an area without code or name"
        raise RowError(msg)
    raw_area = str(row.get(spec.area_column) or "").strip()
    value, null_reason = parse_value(raw_area, ["", "-"], ".")
    observed = _area_date(row.get(spec.date_column))
    dims = {
        "item": area_code,
        "name": title_case(raw_name, frozenset(spec.keep_upper)),
        "stage": stage.value,
    }
    return observation(
        metric_id=spec.metric_id,
        territory_level=TerritoryLevel.DISTRITO.value,
        territory_code=code,
        territory_name=str(row.get(spec.district_name_column) or "").strip() or None,
        admin_unit_id=admin_unit_id("distrito", code),
        period_start=observed,
        period_end=observed,
        dims=dims,
        dims_key=dims_key(dims),
        value=value,
        null_reason=null_reason,
        unit="m2",
        raw_value=raw_area,
    )


def normalize_development_areas(
    frame: pd.DataFrame, spec: MadridDevelopmentAreasPipeline
) -> AreaObservations:
    records: list[dict[str, Any]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    districts: set[str] = set()
    for index, row in enumerate(records):
        try:
            districts.add(district_code(spec.municipio_ine, row.get(spec.district_column)))
            kept = _area_row(row, spec)
        except (RowError, KeyError) as exc:
            bad.append({"source_row": index, "reason": str(exc), "raw": str(row)[:300]})
            continue
        if kept is not None:
            rows.append(kept)
    obs = Observations(
        pd.DataFrame(rows, columns=OBS_COLUMNS),
        pd.DataFrame(bad, columns=["source_row", "reason", "raw"]),
        len(records),
    )
    return AreaObservations(obs, len(records), frozenset(districts), len(records) - len(rows))


def _item_rows(item: ZoneItem, metric_id: str, observed: date) -> list[dict[str, Any]]:
    """The entry in its municipio and in each Madrid district it names."""
    dims = {"item": item.item, "name": item.name, "stage": item.stage}
    if item.note:
        dims["note"] = item.note
    places = [("municipio", item.municipio_ine, item.municipio)] + [
        ("distrito", d.code, None) for d in item.districts
    ]
    return [
        observation(
            metric_id=metric_id,
            territory_level=level,
            territory_code=code,
            territory_name=name,
            admin_unit_id=admin_unit_id(level, code),
            period_start=observed,
            period_end=observed,
            dims=dims,
            dims_key=dims_key(dims),
            value=float(item.value),
            null_reason=None,
            unit=None,
            raw_value=str(item.value),
        )
        for level, code, name in places
    ]


def normalize_zone_items(table: ZoneItemsTable, metric_id: str) -> Observations:
    """Every entry was checked against its quote by the contract: nothing to quarantine."""
    rows = [row for item in table.items for row in _item_rows(item, metric_id, table.consulted)]
    frame = pd.DataFrame(rows, columns=OBS_COLUMNS)
    frame["unit"] = table.unit
    return Observations(
        frame, pd.DataFrame(columns=["source_row", "reason", "raw"]), len(table.items)
    )


def zone_items_frame(table: ZoneItemsTable) -> pd.DataFrame:
    """The table as the PARSE stage's frame (one row per entry), for its row count and hash."""
    return pd.DataFrame(
        [item.model_dump(exclude={"districts", "district_source"}) for item in table.items]
    )
