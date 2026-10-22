"""Canonical places as GeoJSON points. Parameterised SQL only."""

from typing import Any

from sqlalchemy import Connection, text

from hi_contracts.catalog.enums import PlaceCategory

MAX_PLACES = 10000
_PLACES = text(
    """
    SELECT canonical_place_id::text AS id, canonical_name, category, subcategory, municipio_ine,
           seccion_admin_unit_id, ST_X(geom_4326) AS lon, ST_Y(geom_4326) AS lat
      FROM place_master
     WHERE category = :category AND status = 'ACTIVE'
     ORDER BY canonical_place_id
     LIMIT :limit
    """
)


def places_geojson(conn: Connection, category: PlaceCategory) -> dict[str, Any]:
    rows = conn.execute(_PLACES, {"category": category.value, "limit": MAX_PLACES}).mappings().all()
    features = [
        {
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
        for r in rows
    ]
    return {"type": "FeatureCollection", "features": features}
