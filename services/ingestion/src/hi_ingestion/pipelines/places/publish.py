"""Replace a dataset's places atomically and attach them to the canonical geography."""

import uuid
from typing import Any

import geopandas as gpd
from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy import delete, insert, text
from sqlalchemy.orm import Session

from hi_db.models import PlaceMaster, PlaceSourceAlias
from hi_ingestion.pipelines.places.normalize import Places

INSERT_CHUNK = 2000
OFFICIAL_MATCH = ("official_id", 1.0)

_ASSIGN_SECTIONS = text(
    """
    UPDATE place_master p
       SET seccion_admin_unit_id = u.admin_unit_id,
           municipio_ine = COALESCE(p.municipio_ine, substr(u.code_official, 1, 5))
      FROM geo_admin_unit u
     WHERE p.official_dataset_id = :dataset_id
       AND u.level = 'seccion_censal'
       AND ST_Contains(u.geom_25830, p.geom_25830)
    """
)
_ASSIGNMENT_STATS = text(
    """
    SELECT count(*) AS total,
           count(*) FILTER (WHERE p.seccion_admin_unit_id IS NOT NULL) AS assigned,
           count(*) FILTER (
               WHERE u.code_official IS NOT NULL
                 AND substr(u.code_official, 1, 5) <> p.municipio_ine
           ) AS municipio_mismatch
      FROM place_master p
      LEFT JOIN geo_admin_unit u ON u.admin_unit_id = p.seccion_admin_unit_id
     WHERE p.official_dataset_id = :dataset_id
    """
)


def _rows(
    places: Places, dataset_id: str, source_id: str, version_id: uuid.UUID
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    frame = places.frame
    projected = gpd.GeoSeries.from_xy(frame["lon"], frame["lat"], crs=4326).to_crs(25830)
    records: list[dict[str, Any]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    masters: list[dict[str, Any]] = []
    aliases: list[dict[str, Any]] = []
    for record, p25830 in zip(records, projected, strict=True):
        point = Point(record["lon"], record["lat"])
        masters.append(
            {
                "canonical_place_id": record["canonical_place_id"],
                "canonical_name": record["canonical_name"],
                "category": record["category"],
                "subcategory": record["subcategory"],
                "status": record["status"],
                "geom_4326": from_shape(point, srid=4326),
                "geom_25830": from_shape(p25830, srid=25830),
                "municipio_ine": record["municipio_ine"],
                "h3_r9": record["h3_r9"],
                "official_source_id": source_id,
                "official_dataset_id": dataset_id,
                "official_entity_id": record["external_id"],
                "confidence": float(record["confidence"]),
                "attributes": record["attributes"],
                "dataset_version_id": version_id,
            }
        )
        aliases.append(
            {
                "dataset_id": dataset_id,
                "external_id": record["external_id"],
                "canonical_place_id": record["canonical_place_id"],
                "source_id": source_id,
                "source_name": record["canonical_name"],
                "source_geom": from_shape(point, srid=4326),
                "match_method": OFFICIAL_MATCH[0],
                "match_score": OFFICIAL_MATCH[1],
            }
        )
    return masters, aliases


def replace_places(
    session: Session, places: Places, dataset_id: str, source_id: str, version_id: uuid.UUID
) -> dict[str, Any]:
    session.execute(delete(PlaceMaster).where(PlaceMaster.official_dataset_id == dataset_id))
    masters, aliases = _rows(places, dataset_id, source_id, version_id)
    for start in range(0, len(masters), INSERT_CHUNK):
        session.execute(insert(PlaceMaster), masters[start : start + INSERT_CHUNK])
        session.execute(insert(PlaceSourceAlias), aliases[start : start + INSERT_CHUNK])
    session.execute(_ASSIGN_SECTIONS, {"dataset_id": dataset_id})
    stats = session.execute(_ASSIGNMENT_STATS, {"dataset_id": dataset_id}).mappings().one()
    return {
        "places": int(stats["total"]),
        "assigned_to_section": int(stats["assigned"]),
        "municipio_mismatch": int(stats["municipio_mismatch"]),
    }
