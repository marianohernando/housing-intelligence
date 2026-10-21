"""Transactional publication of admin units and H3 links into PostGIS."""

import uuid
from collections.abc import Iterator, Sequence
from datetime import UTC, datetime
from typing import Any

import geopandas as gpd
import pandas as pd
from geoalchemy2.shape import from_shape
from sqlalchemy import delete, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from hi_db.models import DatasetVersion, GeoAdminUnit, H3Cell, H3CellAdminUnit
from hi_ingestion.pipelines.admin_boundaries import config
from hi_ingestion.pipelines.admin_boundaries.h3map import H3Mapping
from hi_ingestion.pipelines.admin_boundaries.transform import to_wgs84
from hi_ingestion.pipelines.fetch import FetchedFile

LEVELS_CHILD_FIRST = ("seccion_censal", "barrio", "distrito", "municipio")


def _chunks(
    rows: Sequence[dict[str, Any]], size: int = config.INSERT_CHUNK
) -> Iterator[Sequence[dict[str, Any]]]:
    for start in range(0, len(rows), size):
        yield rows[start : start + size]


def find_version(session: Session, dataset_id: str, checksum: str) -> DatasetVersion | None:
    return session.scalar(
        select(DatasetVersion).where(
            DatasetVersion.dataset_id == dataset_id, DatasetVersion.checksum_sha256 == checksum
        )
    )


def register_version(
    session: Session,
    primary: FetchedFile,
    checksum: str,
    row_count: int,
    schema_hash: str,
    manifest: str,
) -> DatasetVersion:
    existing = find_version(session, primary.dataset_id, checksum)
    if existing is not None:  # same Bronze content, possibly new parser: reprocess in place
        existing.parser_version = config.PARSER_VERSION
        existing.quality_status = "PENDING"
        existing.schema_hash = schema_hash
        return existing
    version = DatasetVersion(
        dataset_id=primary.dataset_id,
        version_label=f"{datetime.now(UTC):%Y-%m-%d}-{checksum[:12]}",
        retrieved_at=datetime.fromisoformat(primary.retrieved_at),
        checksum_sha256=checksum,
        byte_size=primary.bytes,
        row_count=row_count,
        schema_hash=schema_hash,
        parser_version=config.PARSER_VERSION,
        quality_status="PENDING",
        bronze_manifest_path=manifest,
    )
    session.add(version)
    session.flush()
    return version


UNIT_FIELDS = (
    "admin_unit_id",
    "level",
    "code_official",
    "code_source",
    "name",
    "parent_admin_unit_id",
)


def _clean(value: Any) -> Any:
    return None if value is None or (isinstance(value, float) and pd.isna(value)) else value


def _unit_rows(
    units: gpd.GeoDataFrame, version_id: uuid.UUID, source_id: str
) -> list[dict[str, Any]]:
    units_4326 = to_wgs84(units)
    columns = [units[f].tolist() for f in UNIT_FIELDS]
    rows: list[dict[str, Any]] = []
    for i, (g25830, g4326) in enumerate(zip(units.geometry, units_4326.geometry, strict=True)):
        row = {field: _clean(columns[j][i]) for j, field in enumerate(UNIT_FIELDS)}
        row |= {
            "geom_25830": from_shape(g25830, srid=25830),
            "geom_4326": from_shape(g4326, srid=4326),
            "area_m2": float(g25830.area),
            "source_id": source_id,
            "dataset_version_id": version_id,
        }
        rows.append(row)
    return rows


def replace_geography(
    session: Session, units: gpd.GeoDataFrame, version_id: uuid.UUID, source_id: str
) -> int:
    for level in LEVELS_CHILD_FIRST:
        session.execute(
            delete(GeoAdminUnit).where(
                GeoAdminUnit.source_id == source_id, GeoAdminUnit.level == level
            )
        )
    rows = _unit_rows(units, version_id, source_id)
    for level in reversed(LEVELS_CHILD_FIRST):  # parents first for the self FK
        level_rows = [r for r in rows if r["level"] == level]
        for chunk in _chunks(level_rows):
            session.execute(insert(GeoAdminUnit), chunk)
    return len(rows)


def upsert_h3(session: Session, mapping: H3Mapping) -> dict[str, int]:
    cell_rows = [
        {
            "h3_index": h,
            "resolution": int(r),
            "geom_4326": from_shape(g, srid=4326),
            "centroid_4326": from_shape(c, srid=4326),
        }
        for h, r, g, c in zip(
            mapping.cells["h3_index"],
            mapping.cells["resolution"],
            mapping.cells.geometry,
            mapping.cells["centroid"],
            strict=True,
        )
    ]
    for chunk in _chunks(cell_rows):
        session.execute(
            pg_insert(H3Cell)
            .values(list(chunk))
            .on_conflict_do_nothing(index_elements=["h3_index"])
        )
    link_rows: list[dict[str, Any]] = mapping.links.to_dict("records")  # pyright: ignore[reportAssignmentType]
    for chunk in _chunks(link_rows):
        session.execute(insert(H3CellAdminUnit), chunk)
    return {"h3_cells": len(cell_rows), "h3_links": len(link_rows)}


def mark_last_valid(session: Session, version: DatasetVersion, quality_status: str) -> None:
    session.execute(
        update(DatasetVersion)
        .where(DatasetVersion.dataset_id == version.dataset_id, DatasetVersion.id != version.id)
        .values(is_last_valid=False)
    )
    version.is_last_valid = True
    version.quality_status = quality_status
