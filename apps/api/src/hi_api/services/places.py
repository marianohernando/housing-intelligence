"""Canonical places as GeoJSON points. Parameterised SQL only."""

import math
from dataclasses import dataclass
from typing import Any, NamedTuple

from sqlalchemy import Connection, text

from hi_contracts.catalog.enums import PlaceCategory
from hi_domain.facilities import privately_managed

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
           p.municipio_ine, p.seccion_admin_unit_id, p.attributes, p.confidence,
           p.official_dataset_id,
           ST_X(p.geom_4326) AS lon, ST_Y(p.geom_4326) AS lat, count(*) OVER () AS total
      FROM place_master p
      LEFT JOIN geo_admin_unit s ON s.admin_unit_id = p.seccion_admin_unit_id
     WHERE p.category = ANY(CAST(:categories AS text[])) AND p.status = 'ACTIVE'
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


# The rows of the list of what is missing count places with these filters (Feature Dictionary).
_GAP_ROW_FILTERS = text(
    """
    SELECT spec->'gap_row'->>'row' AS row, spec->'formula' AS formula
      FROM feature_registry
     WHERE spec->'gap_row'->>'role' = 'primary'
       AND spec->'formula'->>'category' IS NOT NULL
    """
)
# Register value -> public label (cm_centros_educativos, column TITULARIDAD).
_OWNERSHIP = {
    "PÚBLICO": "publica",
    "PÚBLICO-TITULARIDAD PRIVADA": "publica",
    "PRIVADO CONCERTADO": "concertada",
    "PRIVADO": "privada",
}
_DEPENDENCIES = ("publica", "privada")
# The register's hospital types all start so: general, especializado, media y larga estancia...
_HOSPITAL = "Hospital"
# Capacity a register publishes per place: attribute -> (unit). Never estimated.
_CAPACITY_ATTRIBUTES = {"plazas_autorizadas_numero": "plazas autorizadas", "camas": "camas"}


class RowFilter(NamedTuple):
    row: str
    category: str
    subcategories: frozenset[str]
    attributes: dict[str, frozenset[str]]

    def counts(self, category: str, subcategory: str, attributes: dict[str, Any]) -> bool:
        if category != self.category:
            return False
        if self.subcategories and subcategory not in self.subcategories:
            return False
        return all(str(attributes.get(k)) in allowed for k, allowed in self.attributes.items())


def row_filters(conn: Connection) -> list[RowFilter]:
    filters: list[RowFilter] = []
    for r in conn.execute(_GAP_ROW_FILTERS).mappings():
        formula: dict[str, Any] = r["formula"] or {}
        filters.append(
            RowFilter(
                str(r["row"]),
                str(formula["category"]),
                frozenset(formula.get("subcategories") or []),
                {k: frozenset(v) for k, v in (formula.get("attributes") or {}).items()},
            )
        )
    return sorted(filters, key=lambda f: f.row)


def _directory_capacity(attributes: dict[str, Any], subcategory: str) -> dict[str, Any] | None:
    """Capacity an official directory publishes for the place it was matched to (D-218)."""
    directory = attributes.get("directory")
    if not isinstance(directory, dict) or directory.get("capacity") is None:
        return None
    return {
        "value": float(directory["capacity"]),
        "unit": str(directory.get("capacity_unit") or "camas"),
        "dataset_id": str(directory["dataset_id"]),
        "dependency": _dependency(attributes),
        "kind": subcategory,
    }


def _capacity(
    attributes: dict[str, Any], dataset_id: str, subcategory: str
) -> dict[str, Any] | None:
    if (from_directory := _directory_capacity(attributes, subcategory)) is not None:
        return from_directory
    for key, unit in _CAPACITY_ATTRIBUTES.items():
        raw = attributes.get(key)
        try:
            value = float(str(raw).replace(",", ".")) if raw not in (None, "") else None
        except ValueError:
            value = None
        if value is not None and math.isfinite(value) and value >= 0:
            return {"value": value, "unit": unit, "dataset_id": dataset_id}
    return None


def _dependency(attributes: dict[str, Any]) -> str | None:
    """Public (the network of the Servicio Madrileño de Salud) or private, as the load wrote it
    from the register; a network hospital a private company runs is public (D-239). A value
    this contract does not know is left out, never passed on."""
    if privately_managed(attributes.get("directory")):
        return "publica"
    value = attributes.get("dependency")
    return value if value in _DEPENDENCIES else None


def _management(attributes: dict[str, Any], subcategory: str) -> str | None:
    """Hospitals only (D-239): private for a private hospital and for a network hospital a
    private company runs, public for the rest of the public ones; None without a dependency."""
    dependency = _dependency(attributes)
    if not subcategory.startswith(_HOSPITAL) or dependency is None:
        return None
    if dependency == "privada" or privately_managed(attributes.get("directory")):
        return "privada"
    return "publica"


def _feature(r: Any, filters: list[RowFilter]) -> dict[str, Any]:
    attributes: dict[str, Any] = r["attributes"] or {}
    origin = (attributes.get("coordinates") or {}).get("origin", "source")
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
            "ownership": _OWNERSHIP.get(str(attributes.get("titularidad") or "")),
            "dependency": _dependency(attributes),
            "management": _management(attributes, r["subcategory"]),
            "gap_rows": [
                f.row for f in filters if f.counts(r["category"], r["subcategory"], attributes)
            ],
            "capacity": _capacity(attributes, r["official_dataset_id"], r["subcategory"]),
            "coordinates": origin,
            "confidence": float(r["confidence"]),
        },
    }


def places_geojson(
    conn: Connection,
    category: PlaceCategory | list[PlaceCategory],
    admin_unit_id: str | None = None,
    subcategories: list[str] | None = None,
    page: int = 1,
) -> PlacesResult:
    categories = category if isinstance(category, list) else [category]
    params = {
        "categories": sorted({c.value for c in categories}),
        "subcategories": subcategories or None,
        **_zone_params(conn, admin_unit_id),
        "limit": PAGE_SIZE,
        "offset": (page - 1) * PAGE_SIZE,
    }
    rows = conn.execute(_PLACES, params).mappings().all()
    if not rows and page > 1:
        msg = f"Page {page} has no places: the last page is smaller (start again at page 1)"
        raise PageOutOfRangeError(msg)
    filters = row_filters(conn)
    return PlacesResult(
        collection={
            "type": "FeatureCollection",
            "features": [_feature(r, filters) for r in rows],
        },
        total=int(rows[0]["total"]) if rows else 0,
        page=page,
    )
