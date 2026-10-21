"""Source rows -> canonical places (one per official id), with quarantine for bad coordinates."""

import uuid
from dataclasses import dataclass
from typing import Any, cast

import geopandas as gpd
import h3
import pandas as pd

from hi_contracts.catalog.enums import PlaceStatus
from hi_contracts.catalog.pipeline import PointsPipeline
from hi_domain.geo.bounds import is_within_madrid
from hi_domain.geo.codes import MADRID_PROVINCE_CODE

PLACE_NAMESPACE = uuid.UUID("6f1c2f3e-6a43-4f0b-9a53-2b2f7a1d5c10")
H3_RESOLUTION = 9
PLACE_COLUMNS = [
    "canonical_place_id",
    "external_id",
    "canonical_name",
    "category",
    "subcategory",
    "status",
    "lon",
    "lat",
    "x",
    "y",
    "municipio_ine",
    "h3_r9",
    "attributes",
]


@dataclass(frozen=True)
class Places:
    frame: pd.DataFrame  # one row per place; lon/lat (4326) and x/y (source CRS)
    quarantine: pd.DataFrame
    source_rows: int
    filtered_out: dict[str, int]


def canonical_place_id(dataset_id: str, external_id: str) -> uuid.UUID:
    """Stable across reloads: same official entity -> same canonical id."""
    return uuid.uuid5(PLACE_NAMESPACE, f"{dataset_id}:{external_id}")


def _keep(frame: pd.DataFrame, column: str, allowed: list[str]) -> tuple[pd.DataFrame, int]:
    values: list[str] = frame[column].tolist()
    mask = [v in allowed for v in values]
    return cast(pd.DataFrame, frame.loc[mask]), mask.count(False)


def apply_filters(frame: pd.DataFrame, spec: PointsPipeline) -> tuple[pd.DataFrame, dict[str, int]]:
    removed: dict[str, int] = {}
    if spec.status_column:
        frame, dropped = _keep(frame, spec.status_column, spec.active_values)
        removed[f"{spec.status_column}_not_active"] = dropped
    for column, allowed in spec.row_filters.items():
        frame, dropped = _keep(frame, column, allowed)
        removed[f"{column}_not_allowed"] = dropped
    return frame, removed


def _group(frame: pd.DataFrame, spec: PointsPipeline) -> pd.DataFrame:
    if not spec.group_by_id:
        return frame.drop_duplicates(spec.id_column)
    first = frame.drop_duplicates(spec.id_column).set_index(spec.id_column)
    for column in spec.grouped_list_columns:
        lists = frame.groupby(spec.id_column)[column].agg(lambda s: sorted({v for v in s if v}))
        first[column] = lists
    return first.reset_index()


def _to_float(raw: Any, decimal: str) -> float | None:
    try:
        return float(str(raw).replace(decimal, ".")) if str(raw).strip() else None
    except ValueError:
        return None


def _municipio(row: dict[str, Any], spec: PointsPipeline) -> str | None:
    if not spec.municipio_code_column:
        return None
    code = str(row.get(spec.municipio_code_column) or "").strip()
    return MADRID_PROVINCE_CODE + code[:3] if code[:3].isdigit() and len(code) >= 3 else None


def _place(
    row: dict[str, Any], spec: PointsPipeline, lon: float, lat: float, x: float, y: float
) -> dict[str, Any]:
    external_id = str(row[spec.id_column])
    subcategory = str(row[spec.subcategory_column])
    municipio = _municipio(row, spec)
    name = str(row[spec.name_column]) if spec.name_column and row.get(spec.name_column) else ""
    attributes = {
        c.lower(): row.get(c) for c in [*spec.attribute_columns, *spec.grouped_list_columns]
    }
    return {
        "canonical_place_id": canonical_place_id(spec.dataset_id, external_id),
        "external_id": external_id,
        "canonical_name": name
        or f"{subcategory} ({municipio or row.get('municipio_nombre', '')})".strip(),
        "category": spec.category.value,
        "subcategory": subcategory,
        "status": PlaceStatus.ACTIVE.value,
        "lon": lon,
        "lat": lat,
        "x": x,
        "y": y,
        "municipio_ine": municipio,
        "h3_r9": h3.latlng_to_cell(lat, lon, H3_RESOLUTION),
        "attributes": {k: v for k, v in attributes.items() if v not in (None, "", [])},
    }


def normalize_places(frame: pd.DataFrame, spec: PointsPipeline) -> Places:
    source_rows = len(frame)
    filtered, removed = apply_filters(frame, spec)
    grouped = _group(filtered, spec)
    records: list[dict[str, Any]] = grouped.to_dict("records")  # pyright: ignore[reportAssignmentType]
    xs = [_to_float(r[spec.x_column], spec.csv.decimal) for r in records]
    ys = [_to_float(r[spec.y_column], spec.csv.decimal) for r in records]
    valid = [
        i for i, (x, y) in enumerate(zip(xs, ys, strict=True)) if x is not None and y is not None
    ]
    vx: list[float] = [float(xs[i] or 0) for i in valid]
    vy: list[float] = [float(ys[i] or 0) for i in valid]
    points = gpd.GeoSeries.from_xy(vx, vy, crs=spec.crs).to_crs(4326)
    lonlat = {i: (float(p.x), float(p.y)) for i, p in zip(valid, points, strict=True)}
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    for i, record in enumerate(records):
        if i not in lonlat:
            bad.append(
                {
                    "external_id": record[spec.id_column],
                    "reason": "missing or unparseable coordinates",
                }
            )
            continue
        lon, lat = lonlat[i]
        if not is_within_madrid(lon, lat):
            bad.append(
                {
                    "external_id": record[spec.id_column],
                    "reason": f"outside Madrid bounds ({lon:.4f}, {lat:.4f})",
                }
            )
            continue
        rows.append(_place(record, spec, lon, lat, float(xs[i] or 0), float(ys[i] or 0)))
    quarantine = pd.DataFrame(bad, columns=["external_id", "reason"])
    return Places(pd.DataFrame(rows, columns=PLACE_COLUMNS), quarantine, source_rows, removed)
