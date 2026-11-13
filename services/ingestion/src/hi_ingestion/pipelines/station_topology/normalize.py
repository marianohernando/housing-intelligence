"""CRTM topology layer (ArcGIS JSON) -> one row per station with its step-free reading."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from hi_contracts.catalog.pipeline import StationTopologyPipeline

TOPOLOGY_FILE = "stations.csv"
COLUMNS = ["station_id", "operator_code", "name", "grade", "step_free"]
QUARANTINE_COLUMNS = ["station_id", "name", "grade", "reason"]


@dataclass(frozen=True)
class Topology:
    frame: pd.DataFrame  # COLUMNS
    quarantine: pd.DataFrame  # QUARANTINE_COLUMNS


def parse_layer(path: Path) -> pd.DataFrame:
    """The attributes of every feature of an ArcGIS query answer. A cut answer (the server's
    transfer limit) or an error object fails: a partial network would read as missing stations."""
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if "error" in data:
        msg = f"{path.name}: ArcGIS answered with an error: {data['error']}"
        raise ValueError(msg)
    if data.get("exceededTransferLimit"):
        msg = f"{path.name}: the query hit the server's transfer limit; the layer is incomplete"
        raise ValueError(msg)
    features = data.get("features")
    if not isinstance(features, list):
        msg = f"{path.name}: no features list in the answer"
        raise ValueError(msg)
    rows: list[dict[str, Any]] = [dict(f.get("attributes") or {}) for f in features]  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
    return pd.DataFrame(rows, dtype=object)


def _text(value: object) -> str:
    missing = value is None or (isinstance(value, float) and pd.isna(value))
    return "" if missing else str(value).strip()


def normalize_topology(frame: pd.DataFrame, spec: StationTopologyPipeline) -> Topology:
    """Each grade becomes its declared reading; a station without one, or with a grade the
    spec does not declare, is quarantined (never read as accessible or not)."""
    rows: list[dict[str, str]] = []
    quarantine: list[dict[str, str]] = []
    for record in frame.to_dict("records"):
        station = _text(record.get(spec.id_field))
        grade = _text(record.get(spec.grade_field))
        name = _text(record.get(spec.name_field))
        seen = {"station_id": station, "name": name, "grade": grade}
        if not station:
            quarantine.append(seen | {"reason": "no_id"})
        elif grade not in spec.step_free:
            quarantine.append(seen | {"reason": "grade_not_published"})
        else:
            rows.append(
                {
                    "station_id": station,
                    "operator_code": _text(record.get(spec.operator_code_field)),
                    "name": name,
                    "grade": grade,
                    "step_free": spec.step_free[grade],
                }
            )
    return Topology(
        pd.DataFrame(rows, columns=COLUMNS, dtype=object),
        pd.DataFrame(quarantine, columns=QUARANTINE_COLUMNS, dtype=object),
    )


def write_topology_silver(topology: Topology, folder: Path) -> Path:
    path = folder / TOPOLOGY_FILE
    topology.frame.to_csv(path, index=False)
    return path


def read_topology(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False)
