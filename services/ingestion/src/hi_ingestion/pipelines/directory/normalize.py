"""One XLSX sheet of an official directory -> the region's entries, typed (D-218)."""

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from hi_contracts.catalog.pipeline import FacilityDirectoryPipeline

DIRECTORY_FILE = "directory.csv"
DIRECTORY_COLUMNS = [
    "external_id",
    "name",
    "address",
    "postal_code",
    "kind",
    "dependency",
    "capacity",
]


@dataclass(frozen=True)
class Directory:
    frame: pd.DataFrame  # DIRECTORY_COLUMNS, one row per entry of the region
    quarantine: pd.DataFrame  # external_id, reason
    source_rows: int
    out_of_scope: int


def parse_sheet(path: Path, spec: FacilityDirectoryPipeline) -> pd.DataFrame:
    """Only the declared columns are read: contact columns never leave the file."""
    frame = pd.read_excel(
        path, sheet_name=spec.sheet, dtype=str, engine="openpyxl", usecols=spec.kept_columns()
    )
    return frame.fillna("")


def _text(raw: Any) -> str:
    return " ".join(str(raw).split())


def _postal_code(raw: Any) -> str:
    digits = _text(raw)
    return digits.zfill(5) if digits.isdigit() and len(digits) <= 5 else digits


def _capacity(raw: Any) -> float | None:
    """'1161' -> 1161.0; '' -> None (not published); anything else -> nan (quarantined)."""
    text = _text(raw).replace(",", ".")
    if not text:
        return None
    try:
        value = float(text)
    except ValueError:
        return math.nan
    return value if math.isfinite(value) and value >= 0 else math.nan


def _entry(row: dict[str, Any], spec: FacilityDirectoryPipeline) -> dict[str, Any]:
    capacity = _capacity(row[spec.capacity_column]) if spec.capacity_column else None
    return {
        "external_id": _text(row[spec.id_column]),
        "name": _text(row[spec.name_column]),
        "address": _text(row[spec.address_column]),
        "postal_code": _postal_code(row[spec.postal_code_column]),
        "kind": _text(row[spec.kind_column]),
        "dependency": _text(row[spec.dependency_column]) if spec.dependency_column else "",
        "capacity": capacity,
    }


def _problem(entry: dict[str, Any]) -> str | None:
    if not entry["external_id"]:
        return "no id"
    if not entry["name"]:
        return "no name"
    if not (entry["postal_code"].isdigit() and len(entry["postal_code"]) == 5):
        return f"postal code {entry['postal_code']!r} is not 5 digits"
    capacity = entry["capacity"]
    if capacity is not None and math.isnan(capacity):
        return "capacity is not a non-negative number"
    return None


def normalize_directory(frame: pd.DataFrame, spec: FacilityDirectoryPipeline) -> Directory:
    scope = frame[spec.scope_column].map(_text).isin(spec.scope_values)
    rows: list[dict[str, Any]] = frame.loc[scope].to_dict("records")  # pyright: ignore[reportAssignmentType]
    entries: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    for row in rows:
        entry = _entry(row, spec)
        problem = _problem(entry)
        if problem:
            bad.append({"external_id": entry["external_id"], "reason": problem})
        else:
            entries.append(entry)
    return Directory(
        pd.DataFrame(entries, columns=DIRECTORY_COLUMNS),
        pd.DataFrame(bad, columns=["external_id", "reason"]),
        source_rows=len(frame),
        out_of_scope=scope.tolist().count(False),
    )


def published_capacities(directory: Directory) -> list[float]:
    """Capacities the directory publishes (an empty cell is «not published», never 0)."""
    values: list[float] = [float(v) for v in directory.frame["capacity"].tolist()]
    return [v for v in values if not math.isnan(v)]


def write_directory_silver(directory: Directory, folder: Path) -> Path:
    path = folder / DIRECTORY_FILE
    directory.frame.to_csv(path, index=False)
    return path
