"""Agencia Tributaria HTML rent table -> canonical observations (D-228). Pure functions.

The table «Comparativa de rentabilidad y precios de alquiler como vivienda habitual con los
nuevos contratos» has one row per territory: a heading cell («Alcalá de Henares-28005»,
«28001-Salamanca- Goya», «Madrid, Comunidad de») and numeric cells in Spanish format. Only
the first four are read: mean monthly rent (all leases, new leases) and mean m² (all, new).
"""

import re
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import pandas as pd

from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_contracts.catalog.pipeline import DEFAULT_MISSING_MARKERS, AeatRentComparisonPipeline
from hi_domain.geo.codes import MADRID_PROVINCE_CODE, admin_unit_id
from hi_ingestion.pipelines.stat_tables.normalize import (
    OBS_COLUMNS,
    Observations,
    RowError,
    dims_key,
)

# The header the four columns must carry, in this order (any change stops the pipeline).
EXPECTED_HEADER = (
    "Alquiler medio mensual",
    "Alquiler medio mensual (nuevos contratos)",
    "m2 medios",
    "m2 medios (nuevos contratos)",
)
HEADER_LABEL = "Localización de la vivienda"
FRAME_COLUMNS = ["label", "rent_all", "rent_new", "m2_all", "m2_new", "period"]
CONTRACTS = {"todos": ("rent_all", "m2_all"), "nuevos": ("rent_new", "m2_new")}
_PERIOD = re.compile(r"Ejercicio\s+(\d{4})")
_MUNICIPIO = re.compile(r"^(?P<name>.+)-(?P<code>\d{5})$")
_POSTCODE = re.compile(r"^(?P<code>\d{5})-(?P<name>.+)$")


class _Rows(HTMLParser):
    """Text of every cell (th or td) of every table row, in document order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self._cells: list[str] | None = None
        self._text: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._cells = []
        elif tag in {"th", "td"} and self._cells is not None:
            self._text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"th", "td"} and self._cells is not None and self._text is not None:
            self._cells.append(" ".join("".join(self._text).split()))
            self._text = None
        elif tag == "tr" and self._cells is not None:
            self.rows.append(self._cells)
            self._cells = None

    def handle_data(self, data: str) -> None:
        if self._text is not None:
            self._text.append(data)


def table_rows(html: str) -> list[list[str]]:
    parser = _Rows()
    parser.feed(html)
    return parser.rows


def parse_html(path: Path) -> pd.DataFrame:
    """The table as raw strings, one row per territory, after checking its header and year."""
    html = path.read_text(encoding="utf-8", errors="replace")
    period = _PERIOD.search(html)
    if period is None:
        msg = f"{path.name}: no «Ejercicio YYYY» in the page"
        raise ValueError(msg)
    rows = table_rows(html)
    header = next((r for r in rows if r and r[0] == HEADER_LABEL), None)
    if header is None or tuple(header[1:5]) != EXPECTED_HEADER:
        msg = f"{path.name}: unexpected header {header[:5] if header else None}"
        raise ValueError(msg)
    body = [r for r in rows if len(r) >= 5 and r[0] and r[0] != HEADER_LABEL]
    return pd.DataFrame([[r[0], *r[1:5], period.group(1)] for r in body], columns=FRAME_COLUMNS)


def parse_number(raw: str) -> float:
    """Spanish format: «1.167» is 1167 and «6,7» is 6.7."""
    text = raw.strip().replace(".", "").replace(",", ".")
    try:
        return float(text)
    except ValueError as exc:
        msg = f"not a number: {raw!r}"
        raise RowError(msg) from exc


def parse_cell(raw: str) -> tuple[float | None, str | None]:
    """A missing marker («-», empty) is SOURCE_MISSING, never 0; anything else must parse."""
    if raw.strip() in DEFAULT_MISSING_MARKERS:
        return None, NullReason.SOURCE_MISSING.value
    return parse_number(raw), None


def territory(
    label: str, spec: AeatRentComparisonPipeline
) -> tuple[TerritoryLevel, str, str] | None:
    """(level, code, name) of a row in scope; None for rows of other provinces or totals."""
    if spec.region_label is not None and label == spec.region_label:
        return TerritoryLevel.CCAA, MADRID_PROVINCE_CODE, label
    pattern = _MUNICIPIO if spec.level == "municipio" else _POSTCODE
    match = pattern.match(label)
    if match is None or not match.group("code").startswith(spec.province_prefix):
        return None
    return TerritoryLevel(spec.level), match.group("code"), match.group("name").strip()


def _observations(
    row: dict[str, str], place: tuple[TerritoryLevel, str, str], spec: AeatRentComparisonPipeline
) -> list[dict[str, Any]]:
    level, code, name = place
    year = int(row["period"])
    unit_id = admin_unit_id(level.value, code) if level is TerritoryLevel.MUNICIPIO else None
    out: list[dict[str, Any]] = []
    for contract, (rent_column, area_column) in CONTRACTS.items():
        dims = {spec.contract_dim: contract}
        for metric_id, column, unit in (
            (spec.rent_metric_id, rent_column, "EUR/mes"),
            (spec.area_metric_id, area_column, "m2"),
        ):
            value, null_reason = parse_cell(row[column])
            out.append(
                {
                    "metric_id": metric_id,
                    "territory_level": level.value,
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
                    "raw_value": row[column],
                }
            )
    return out


def normalize(frame: pd.DataFrame, spec: AeatRentComparisonPipeline) -> Observations:
    """Rows of the province (and the region) -> four observations per contract kind; rows out
    of scope are counted, never quarantined; a row in scope that does not parse is."""
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    out_of_scope = 0
    records: list[dict[str, str]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    for index, row in enumerate(records):
        place = territory(row["label"], spec)
        if place is None:
            out_of_scope += 1
            continue
        try:
            rows.extend(_observations(row, place, spec))
        except RowError as exc:
            bad.append({"source_row": index, "reason": str(exc), "raw": str(row)[:300]})
    return Observations(
        pd.DataFrame(rows, columns=OBS_COLUMNS),
        pd.DataFrame(bad, columns=["source_row", "reason", "raw"]),
        len(frame) - out_of_scope,
        out_of_scope,
    )
