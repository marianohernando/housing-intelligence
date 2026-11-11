"""Canonical places as GeoJSON points. Parameterised SQL only."""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import Connection, text

from hi_contracts.catalog.enums import PlaceCategory

# Vercel answers 4.5 MB at most; 5,000 places are ~1.4 MB. Larger layers (transport: 14,982
# stops) come in pages, and the response says how to ask for the next one.
PAGE_SIZE = 5000
ZONE_LEVELS = ("municipio", "distrito", "seccion_censal")

_UNIT = text("SELECT level, code_official FROM geo_admin_unit WHERE admin_unit_id = :id")
# A place's zone is the one features count it in (hi_features.loaders): its municipio, or the
# district or census section of the section it lies in (28079 01 001).
_PLACES = text(
    """
    SELECT p.canonical_place_id::text AS id, p.canonical_name, p.category, p.subcategory,
           p.municipio_ine, p.seccion_admin_unit_id,
           ST_X(p.geom_4326) AS lon, ST_Y(p.geom_4326) AS lat, count(*) OVER () AS total
      FROM place_master p
      LEFT JOIN geo_admin_unit s ON s.admin_unit_id = p.seccion_admin_unit_id
     WHERE p.category = :category AND p.status = 'ACTIVE'
       AND (CAST(:subcategories AS text[]) IS NULL
            OR p.subcategory = ANY(CAST(:subcategories AS text[])))
       AND (CAST(:municipio AS text) IS NULL OR p.municipio_ine = :municipio)
       AND (CAST(:distrito AS text) IS NULL OR left(s.code_official, 7) = :distrito)
       AND (CAST(:seccion_censal AS text) IS NULL OR s.code_official = :seccion_censal)
     ORDER BY p.canonical_place_id
     LIMIT :limit OFFSET :offset
    """
)


class ZoneNotFoundError(LookupError):
    pass


class UnsupportedZoneLevelError(ValueError):
    pass


class PageOutOfRangeError(ValueError):
    pass


@dataclass(frozen=True)
class PlacesResult:
    collection: dict[str, Any]
    total: int
    page: int

    @property
    def pages(self) -> int:
        return max(1, -(-self.total // PAGE_SIZE))


def _zone_params(conn: Connection, admin_unit_id: str | None) -> dict[str, str | None]:
    params: dict[str, str | None] = dict.fromkeys(ZONE_LEVELS)
    if admin_unit_id is None:
        return params
    unit = conn.execute(_UNIT, {"id": admin_unit_id}).mappings().first()
    if unit is None:
        msg = f"No admin unit {admin_unit_id}"
        raise ZoneNotFoundError(msg)
    if unit["level"] not in ZONE_LEVELS:
        msg = f"Places can be filtered by {', '.join(ZONE_LEVELS)}, not by {unit['level']}"
        raise UnsupportedZoneLevelError(msg)
    params[unit["level"]] = unit["code_official"]
    return params


def _feature(r: Any) -> dict[str, Any]:
    return {
        "type": "Feature",
        "id": r["id"],
        "geometry": {"type": "Point", "coordinates": [round(r["lon"], 6), round(r["lat"], 6)]},
        "properties": {
            "name": r["canonical_name"],
            "category": r["category"],
            "subcategory": r["subcategory"],
            "municipio": r["municipio_ine"],
            "seccion": r["seccion_admin_unit_id"],
        },
    }


def places_geojson(
    conn: Connection,
    category: PlaceCategory,
    admin_unit_id: str | None = None,
    subcategories: list[str] | None = None,
    page: int = 1,
) -> PlacesResult:
    params = {
        "category": category.value,
        "subcategories": subcategories or None,
        **_zone_params(conn, admin_unit_id),
        "limit": PAGE_SIZE,
        "offset": (page - 1) * PAGE_SIZE,
    }
    rows = conn.execute(_PLACES, params).mappings().all()
    if not rows and page > 1:
        msg = f"Page {page} has no places: the last page is smaller (start again at page 1)"
        raise PageOutOfRangeError(msg)
    return PlacesResult(
        collection={"type": "FeatureCollection", "features": [_feature(r) for r in rows]},
        total=int(rows[0]["total"]) if rows else 0,
        page=page,
    )
