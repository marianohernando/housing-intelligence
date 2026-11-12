"""Source rows -> canonical places (one per official id), with quarantine for bad coordinates."""

import uuid
from dataclasses import dataclass, field
from typing import Any, cast

import geopandas as gpd
import h3
import pandas as pd

from hi_contracts.catalog.corrections import AddressFix, PlaceCorrection
from hi_contracts.catalog.enums import PlaceStatus
from hi_contracts.catalog.pipeline import PointsPipeline
from hi_domain.facilities import dependency
from hi_domain.geo.bounds import is_within_madrid
from hi_domain.geo.codes import MADRID_PROVINCE_CODE
from hi_ingestion.pipelines.places.coordinates import (
    GEOCODED,
    SOURCE,
    Declared,
    Geocode,
    Locate,
    Resolution,
    fold_name,
    house_number,
    resolve,
)
from hi_ingestion.pipelines.places.corrections import correction_attribute
from hi_ingestion.pipelines.places.directory import (
    LINK_COLUMNS,
    LoadedDirectory,
    RegisterPlace,
    attach_directories,
)

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
    "confidence",
]
MADRID_MUNICIPIO = "28079"
REPAIR_COLUMNS = ["external_id", "origin", "note"]


@dataclass(frozen=True)
class Repair:
    """What `normalize_places` needs to repair coordinates (D-216); None keeps the source."""

    locate: Locate
    geocode: Geocode
    municipio_by_name: dict[str, str]  # fold_name(official name) -> INE code


@dataclass(frozen=True)
class Places:
    frame: pd.DataFrame  # one row per place; lon/lat (4326) and x/y (source CRS)
    quarantine: pd.DataFrame
    source_rows: int
    filtered_out: dict[str, int]
    repairs: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=REPAIR_COLUMNS))
    # Official directories (D-218): aliases of the matched entries and what was left unmatched
    links: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=LINK_COLUMNS))
    directory_report: dict[str, dict[str, object]] = field(
        default_factory=dict[str, dict[str, object]]
    )


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


def _name(row: dict[str, Any], spec: PointsPipeline) -> str:
    if spec.name_template:
        values = {c: str(row.get(c) or "") for c in spec.name_template_columns()}
        return " ".join(spec.name_template.format_map(values).split())
    return str(row[spec.name_column]) if spec.name_column and row.get(spec.name_column) else ""


def _declared(row: dict[str, Any], spec: PointsPipeline, repair: Repair) -> Declared:
    municipio = _municipio(row, spec)
    if municipio is None and spec.municipio_name_column:
        name = str(row.get(spec.municipio_name_column) or "")
        municipio = repair.municipio_by_name.get(fold_name(name)) if name else None
    district = None
    code = (
        str(row.get(spec.district_code_column) or "").strip() if spec.district_code_column else ""
    )
    if municipio == MADRID_MUNICIPIO and code.isdigit():
        district = f"{MADRID_MUNICIPIO}{int(code):02d}"
    address = None
    if spec.address_template:
        values = {c: str(row.get(c) or "").strip() for c in spec.address_template_columns()}
        address = " ".join(spec.address_template.format_map(values).split()).strip(" ,") or None
    number = None
    if spec.address_number_column:
        number = house_number(str(row.get(spec.address_number_column) or ""))
    street = None
    if spec.address_street_column:
        street = str(row.get(spec.address_street_column) or "").strip() or None
    return Declared(municipio, district, address, number, street)


def _place(
    row: dict[str, Any], spec: PointsPipeline, lon: float, lat: float, x: float, y: float
) -> dict[str, Any]:
    external_id = str(row[spec.id_column])
    subcategory = spec.subcategory_value or str(row[spec.subcategory_column or ""])
    municipio = _municipio(row, spec)
    name = _name(row, spec)
    attributes = {
        c.lower(): row.get(c) for c in [*spec.attribute_columns, *spec.grouped_list_columns]
    }
    if spec.dependency_column:
        attributes["dependency"] = dependency(str(row.get(spec.dependency_column) or ""))
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
        "confidence": 1.0,
    }


def _source_lonlat(records: list[dict[str, Any]], spec: PointsPipeline) -> dict[int, Any]:
    """Row index -> (lon, lat, x, y) for rows with parseable source coordinates."""
    xs = [_to_float(r[spec.x_column], spec.csv.decimal) for r in records]
    ys = [_to_float(r[spec.y_column], spec.csv.decimal) for r in records]
    valid = [
        i for i, (x, y) in enumerate(zip(xs, ys, strict=True)) if x is not None and y is not None
    ]
    vx: list[float] = [float(xs[i] or 0) for i in valid]
    vy: list[float] = [float(ys[i] or 0) for i in valid]
    points = gpd.GeoSeries.from_xy(vx, vy, crs=spec.crs).to_crs(4326)
    return {
        i: (float(p.x), float(p.y), vx[k], vy[k])
        for k, (i, p) in enumerate(zip(valid, points, strict=True))
    }


def _projected(lon: float, lat: float, crs: str) -> tuple[float, float]:
    point = gpd.GeoSeries.from_xy([lon], [lat], crs=4326).to_crs(crs).iloc[0]
    return float(point.x), float(point.y)


def _resolve(
    record: dict[str, Any], spec: PointsPipeline, source: Any, repair: Repair | None
) -> Resolution:
    """The coordinates to publish; a quarantine reason that keeps the source's own problem."""
    lonlat = (source[0], source[1]) if source is not None else None
    problem = None if source is not None else "missing or unparseable coordinates"
    if lonlat is not None and not is_within_madrid(*lonlat):
        problem, lonlat = f"outside Madrid bounds ({lonlat[0]:.4f}, {lonlat[1]:.4f})", None
    if repair is None:
        if lonlat is None:
            return Resolution(None, None, SOURCE, problem)
        return Resolution(lonlat[0], lonlat[1], SOURCE)
    declared = _declared(record, spec, repair)
    resolution = resolve(lonlat, declared, repair.locate, repair.geocode)
    if not resolution.accepted and problem:
        reason = f"{problem}; {resolution.quarantine_reason}"
        return Resolution(None, None, SOURCE, reason)
    return resolution


def _register_place(
    record: dict[str, Any], spec: PointsPipeline, subcategory: str
) -> RegisterPlace:
    def column(name: str | None) -> str:
        return str(record.get(name) or "").strip() if name else ""

    postal_code = column(spec.postal_code_column)
    return RegisterPlace(
        external_id=str(record[spec.id_column]),
        subcategory=subcategory,
        postal_code=postal_code.zfill(5) if postal_code.isdigit() else None,
        street=column(spec.address_street_column) or None,
        number=house_number(column(spec.address_number_column)),
        dependency=dependency(column(spec.dependency_column)) if spec.dependency_column else None,
        municipality=column(spec.municipio_name_column) or None,
    )


def _with_address(record: dict[str, Any], spec: PointsPipeline, fix: AddressFix) -> dict[str, Any]:
    """The record with the corrected street and number, for the geocoder and the matching."""
    if spec.address_street_column is None or spec.address_number_column is None:
        msg = f"{spec.dataset_id}: an address correction needs street and number columns"
        raise ValueError(msg)
    return record | {spec.address_street_column: fix.street, spec.address_number_column: fix.number}


def normalize_places(
    frame: pd.DataFrame,
    spec: PointsPipeline,
    repair: Repair | None = None,
    directories: list[LoadedDirectory] | None = None,
    corrections: list[PlaceCorrection] | None = None,
) -> Places:
    source_rows = len(frame)
    filtered, removed = apply_filters(frame, spec)
    grouped = _group(filtered, spec)
    records: list[dict[str, Any]] = grouped.to_dict("records")  # pyright: ignore[reportAssignmentType]
    source = _source_lonlat(records, spec)
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    repairs: list[dict[str, Any]] = []
    register: dict[str, RegisterPlace] = {}
    fixes = {c.entity_id: c for c in corrections or []}
    for i, record in enumerate(records):
        external_id = record[spec.id_column]
        fix = fixes.get(str(external_id))
        if fix is not None and fix.address is not None:
            record = _with_address(record, spec, fix.address)
        resolution = _resolve(record, spec, source.get(i), repair)
        if resolution.lon is None or resolution.lat is None:
            bad.append({"external_id": external_id, "reason": resolution.quarantine_reason})
            continue
        lon, lat = resolution.lon, resolution.lat
        if not is_within_madrid(lon, lat):
            bad.append(
                {
                    "external_id": external_id,
                    "reason": f"outside Madrid bounds ({lon:.4f}, {lat:.4f})",
                }
            )
            continue
        if resolution.origin == GEOCODED:
            x, y = _projected(lon, lat, spec.crs)
        else:
            x, y = source[i][2], source[i][3]
        place = _place(record, spec, lon, lat, x, y)
        if resolution.origin == GEOCODED:
            place["confidence"] = resolution.confidence
            place["attributes"]["coordinates"] = {"origin": GEOCODED, "note": resolution.note}
        if resolution.note:
            repairs.append(
                {"external_id": external_id, "origin": resolution.origin, "note": resolution.note}
            )
        if fix is not None:
            place["attributes"]["correction"] = correction_attribute(fix)
        rows.append(place)
        register[place["external_id"]] = _register_place(record, spec, place["subcategory"])
    forced = {
        c.entity_id: (c.directory.dataset_id, c.directory.entry_id)
        for c in fixes.values()
        if c.directory is not None
    }
    attached = attach_directories(rows, register, directories or [], forced)
    return Places(
        pd.DataFrame(rows, columns=PLACE_COLUMNS),
        pd.DataFrame(bad, columns=["external_id", "reason"]),
        source_rows,
        removed,
        pd.DataFrame(repairs, columns=REPAIR_COLUMNS),
        attached.links,
        attached.report,
    )
