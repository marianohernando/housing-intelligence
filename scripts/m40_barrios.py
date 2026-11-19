"""D-247: the pilot barrios of the investor version, Madrid inside the M-40.

Reads the M-40 once from OpenStreetMap (Overpass: the motorway ways tagged `ref=M-40`, ODbL),
closes it into a polygon and keeps the barrios of Madrid whose centroid is inside, with the
distance of each centroid to the ring and the share of the barrio inside it. Writes
data/catalog/manual/inversores_barrios_m40.yaml with the query, the OSM timestamp, the day it
was read and the ring with its checksum. The reviews written by hand for the barrios on the
edge (a centroid less than 500 m from the ring, or a barrio the ring crosses) are kept by code;
a new edge barrio gets none, so the contract (`PilotZonesTable`) fails until a person reviews
it. Needs the geography in DATABASE_URL (barrio polygons).

    DATABASE_URL=... uv run python scripts/m40_barrios.py
"""

import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import httpx
import shapely
import yaml
from pyproj import Transformer
from shapely.geometry import LineString, MultiPolygon, Polygon
from sqlalchemy import Engine, text

from hi_contracts.catalog.manual import PilotZonesTable, ring_checksum
from hi_db.session import make_engine
from hi_ingestion.http import make_client, polite_retry

MANUAL = Path(__file__).resolve().parents[1] / "data" / "catalog" / "manual"
TABLE = MANUAL / "inversores_barrios_m40.yaml"
OVERPASS = "https://overpass-api.de/api/interpreter"
QUERY = (
    '[out:json][timeout:120];area["ISO3166-2"="ES-MD"]->.a;'
    'way["highway"="motorway"]["ref"~"(^|;)M-40(;|$)"](area.a);out geom;'
)
MADRID = "28079"
CLOSE_M = 25  # the carriageways are joined by a 25 m buffer; the ring is its inner edge + 25 m
SIMPLIFY_M = 5
EDGE_M = 500
CROSSING_PCT = 5  # between 5 % and 95 % of the barrio inside: the ring crosses it
HEADER = """\
# D-247: barrios piloto de la versión para inversores, Madrid dentro de la M-40. Un barrio entra
# si su centroide cae dentro del anillo de la M-40 de OpenStreetMap (© OpenStreetMap
# contributors, ODbL 1.0), leído una vez el día `consulted` por scripts/m40_barrios.py. Los
# barrios del borde, dentro o fuera (centroide a menos de `edge_m` del anillo, o un barrio que la
# M-40 cruza), llevan la nota de su revisión a mano (`review`). No editar a mano salvo las notas:
# volver a lanzar el script, que las conserva.
"""

_BARRIOS = text(
    """
    WITH ring AS (SELECT ST_GeomFromText(:ring, 25830) AS g)
    SELECT b.code_official AS code, b.name, d.name AS distrito,
           ST_Distance(ST_Centroid(b.geom_25830), ST_Boundary(ring.g))
             * CASE WHEN ST_Contains(ring.g, ST_Centroid(b.geom_25830)) THEN 1 ELSE -1 END
             AS margin,
           100 * ST_Area(ST_Intersection(b.geom_25830, ring.g)) / ST_Area(b.geom_25830)
             AS inside_pct
      FROM geo_admin_unit b
      JOIN geo_admin_unit d ON d.admin_unit_id = b.parent_admin_unit_id, ring
     WHERE b.level = 'barrio' AND b.code_official LIKE :prefix
     ORDER BY b.code_official
    """
)


@polite_retry
def read_overpass(client: httpx.Client) -> dict[str, Any]:
    response = client.post(OVERPASS, data={"data": QUERY})
    response.raise_for_status()
    return response.json()


def ring_polygon(elements: list[dict[str, Any]]) -> Polygon:
    """The area the carriageways enclose: their union, joined by a small buffer, has one large
    hole (inside the ring); that hole, grown back by the same buffer, is the polygon."""
    to_25830 = Transformer.from_crs(4326, 25830, always_xy=True)
    lines = [
        LineString(to_25830.transform(lon, lat) for lon, lat in ((p["lon"], p["lat"]) for p in way))
        for way in (e["geometry"] for e in elements)
    ]
    joined = shapely.unary_union(lines).buffer(CLOSE_M)
    parts = list(joined.geoms) if isinstance(joined, MultiPolygon) else [joined]
    holes = [
        Polygon(ring) for part in parts if isinstance(part, Polygon) for ring in part.interiors
    ]
    if not holes:
        raise ValueError("the M-40 ways do not close a ring")
    inside = max(holes, key=lambda h: h.area).buffer(CLOSE_M).simplify(SIMPLIFY_M)
    if not isinstance(inside, Polygon):
        raise ValueError("the ring is not one polygon")
    return Polygon([(round(x), round(y)) for x, y in inside.exterior.coords])


def barrio_rows(engine: Engine, ring: Polygon) -> list[dict[str, Any]]:
    with engine.connect() as conn:
        rows = conn.execute(_BARRIOS, {"ring": ring.wkt, "prefix": f"{MADRID}%"}).mappings()
        return [
            {
                "code": r["code"],
                "name": r["name"],
                "distrito": r["distrito"],
                "margin_m": round(r["margin"]),
                "area_inside_pct": round(r["inside_pct"]),
            }
            for r in rows
        ]


def previous_reviews() -> dict[str, str]:
    if not TABLE.exists():
        return {}
    old = yaml.safe_load(TABLE.read_text(encoding="utf-8"))
    entries = [*old.get("barrios", []), *old.get("reviewed_outside", [])]
    return {e["code"]: e["review"] for e in entries if e.get("review")}


def on_edge(row: dict[str, Any]) -> bool:
    crossed = CROSSING_PCT < row["area_inside_pct"] < 100 - CROSSING_PCT
    return abs(row["margin_m"]) < EDGE_M or crossed


def with_review(row: dict[str, Any], reviews: dict[str, str]) -> dict[str, Any]:
    return row | {"review": reviews.get(row["code"])} if on_edge(row) else row


def pilot_table(overpass: dict[str, Any], rows: list[dict[str, Any]], ring: Polygon) -> Any:
    reviews = previous_reviews()
    coordinates = [(int(x), int(y)) for x, y in ring.exterior.coords]
    inside = [with_review(r, reviews) for r in rows if r["margin_m"] > 0]
    near = [with_review(r, reviews) for r in rows if r["margin_m"] <= 0 and on_edge(r)]
    return {
        "title": "Barrios piloto de la versión para inversores: Madrid dentro de la M-40",
        "publisher": "OpenStreetMap contributors (Overpass API)",
        "license": "ODbL 1.0 (© OpenStreetMap contributors)",
        "url": f"{OVERPASS}?{urlencode({'data': QUERY})}",
        "query": QUERY,
        "osm_timestamp": overpass["osm3s"]["timestamp_osm_base"],
        "consulted": datetime.now(UTC).date().isoformat(),
        "crs": "EPSG:25830",
        "method": (
            f"Vías highway=motorway con ref=M-40 ({len(overpass['elements'])}), unidas con un "
            f"búfer de {CLOSE_M} m; el hueco interior mayor, devuelto al eje con otros {CLOSE_M} "
            f"m y simplificado a {SIMPLIFY_M} m, es el anillo. Un barrio entra si su centroide "
            f"(ST_Centroid de su polígono en geo_admin_unit) cae dentro. margin_m: distancia del "
            f"centroide al anillo (positiva dentro); area_inside_pct: % de su superficie dentro."
        ),
        "municipio_ine": MADRID,
        "edge_m": EDGE_M,
        "crossing_pct": CROSSING_PCT,
        "ring": {
            "ways": len(overpass["elements"]),
            "area_km2": round(ring.area / 1e6, 2),
            "sha256": ring_checksum(coordinates),
            "coordinates": [list(c) for c in coordinates],
        },
        "barrios": inside,
        "reviewed_outside": near,
        "outside": len(rows) - len(inside) - len(near),
    }


class FlowPairs(yaml.SafeDumper):
    """One vertex per line, `[x, y]`, so a diff of the ring reads vertex by vertex."""


def _pair(dumper: yaml.SafeDumper, data: list[Any]) -> yaml.Node:
    vertex = len(data) == len(("x", "y")) and all(isinstance(v, int) for v in data)
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=vertex)


FlowPairs.add_representer(list, _pair)


def main() -> None:
    engine = make_engine(os.environ.get("DATABASE_URL"))
    with make_client(timeout=180) as client:
        overpass = read_overpass(client)
    ring = ring_polygon(overpass["elements"])
    body = pilot_table(overpass, barrio_rows(engine, ring), ring)
    TABLE.write_text(
        HEADER + yaml.dump(body, Dumper=FlowPairs, allow_unicode=True, sort_keys=False, width=100),
        encoding="utf-8",
    )
    edge = len(body["reviewed_outside"])
    print(f"{len(body['barrios'])} barrios inside, {edge} on the edge outside")
    PilotZonesTable.model_validate(body)  # fails while an edge barrio has no review


if __name__ == "__main__":
    main()
