"""D-247: points of the planning areas of «PGOUM 97. Edificabilidad remanente en ámbitos».

The register (XLS, Ayuntamiento de Madrid) gives each area its district, not its place. The
layer of the areas in force of the Ayuntamiento's own viewer (VEDA Madrid, ArcGIS service,
EPSG:25830) has their polygons. This script reads the register and the layer once and writes,
for each area of the register, a point inside its polygon and inside the district the register
names (an area across two districts stays in the register's), with the share of the area in the
barrio of that point, to data/catalog/manual/, with the layer's URL and the day it was read.
The pipeline places each area in its barrio from that file, without network. Run it again when
the pipeline quarantines an area without a point (one the register added later). Needs the
geography in DATABASE_URL (district and barrio polygons).

    DATABASE_URL=... uv run python scripts/veda_remanente_points.py
"""

import os
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import yaml
from shapely import wkb
from shapely.geometry import Point, shape
from shapely.geometry.base import BaseGeometry
from sqlalchemy import Engine, text

from hi_contracts.catalog.manual import AreaPointsTable
from hi_contracts.catalog.pipeline import MadridBuildableAreasPipeline
from hi_db.session import make_engine
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.http import make_client, polite_retry
from hi_ingestion.pipelines.fetch import download
from hi_ingestion.pipelines.zone_context.normalize import district_code
from hi_ingestion.pipelines.zone_context.run import MANUAL_DIR, read_areas

DATASET_ID = "ayto_edificabilidad_remanente_ambitos"
LABEL = "AMB_TX_ETI"
LAYER = "ANALISIS_URBANO/Visor_Edificabilidad_julio_2026_actual: Ambitos_Vigentes_julio26"
HEADER = """\
# D-247: un punto dentro de cada ámbito de «PGOUM 97. Edificabilidad remanente en ámbitos»
# (Ayuntamiento de Madrid, CC BY 4.0), y dentro del distrito que le da el fichero. El fichero no
# trae coordenadas; estas salen de la capa de ámbitos vigentes del propio visor VEDA Madrid
# (servicio del Departamento de Análisis Urbano), leída una vez el día `consulted` por
# scripts/veda_remanente_points.py, para que la carga sitúe cada ámbito en su barrio sin red.
# share_pct: % de la superficie del ámbito en el barrio del punto. No editar a mano.
"""
_ZONES = text(
    """
    SELECT level, code_official, ST_AsBinary(geom_25830) AS geom
      FROM geo_admin_unit
     WHERE level IN ('distrito', 'barrio') AND code_official LIKE :prefix
    """
)


@polite_retry
def read_layer(client: httpx.Client, url: str) -> dict[str, Any]:
    response = client.get(url)
    response.raise_for_status()
    layer = response.json()
    if layer.get("exceededTransferLimit") or layer.get("properties", {}).get(
        "exceededTransferLimit"
    ):
        raise ValueError("the layer was cut by the service: page the request")
    return layer


def zones(engine: Engine, prefix: str) -> dict[str, dict[str, BaseGeometry]]:
    out: dict[str, dict[str, BaseGeometry]] = {"distrito": {}, "barrio": {}}
    with engine.connect() as conn:
        for row in conn.execute(_ZONES, {"prefix": f"{prefix}%"}).mappings():
            out[row["level"]][row["code_official"]] = wkb.loads(bytes(row["geom"]))
    return out


def area_point(
    polygon: BaseGeometry, district: BaseGeometry, barrios: dict[str, BaseGeometry]
) -> dict[str, int]:
    """A point inside the part of the area in its district, to the metre, and the share of the
    area in the barrio of that point."""
    part = polygon.intersection(district)
    if part.is_empty:
        raise ValueError("the area is not in the district the register gives it")
    point = part.representative_point()
    x, y = round(point.x), round(point.y)
    if not part.contains(Point(x, y)):
        x, y = int(point.x), int(point.y)
        if not part.contains(Point(x, y)):
            raise ValueError(f"the rounded point ({x}, {y}) is not inside the area")
    barrio = next((b for b in barrios.values() if b.contains(Point(x, y))), None)
    share = 0 if barrio is None else round(100 * polygon.intersection(barrio).area / polygon.area)
    return {"x": x, "y": y, "share_pct": share}


def register_areas(url: str, spec: MadridBuildableAreasPipeline) -> dict[str, str]:
    """COD_AMBITO -> its district code, from the register itself."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "register.xls"
        with make_client(timeout=120) as client:
            download(client, url, path)
        frame = read_areas(path)
    return {
        str(row[spec.code_column]).strip(): district_code(
            spec.municipio_ine, row[spec.district_column]
        )
        for row in frame.to_dict("records")
    }


def main() -> None:
    catalog = load_catalog()
    spec = catalog.pipelines[DATASET_ID]
    assert isinstance(spec, MadridBuildableAreasPipeline)  # noqa: S101 - the catalog declares it
    dataset = catalog.datasets[DATASET_ID]
    register = next(str(r.url) for r in dataset.resources if r.role == spec.resource_role)
    url = next(str(r.url) for r in dataset.resources if r.role == "points")
    areas = register_areas(register, spec)
    with make_client(timeout=180) as client:
        layer = read_layer(client, url)
    polygons = {f["properties"][LABEL]: shape(f["geometry"]) for f in layer["features"]}
    geo = zones(make_engine(os.environ.get("DATABASE_URL")), spec.municipio_ine)
    points = []
    for code, district in sorted(areas.items()):
        if code not in polygons:
            msg = f"area {code} is not in the layer"
            raise ValueError(msg)
        barrios = {b: g for b, g in geo["barrio"].items() if b.startswith(district)}
        points.append(
            {"ref": code} | area_point(polygons[code], geo["distrito"][district], barrios)
        )
    table = AreaPointsTable.model_validate(
        {
            "title": "Ámbitos de la edificabilidad remanente: un punto dentro de cada ámbito",
            "publisher": "Ayuntamiento de Madrid (VEDA Madrid, Departamento de Análisis Urbano)",
            "url": url,
            "layer": LAYER,
            "crs": "EPSG:25830",
            "consulted": datetime.now(UTC).date(),
            "method": "Punto interior (shapely representative_point) de la parte del polígono del "
            "ámbito dentro del distrito que le da el fichero, redondeado al metro y comprobado "
            "dentro; share_pct es el % de la superficie del ámbito en el barrio de ese punto.",
            "municipio_ine": spec.municipio_ine,
            "points": points,
        }
    )
    path = MANUAL_DIR / spec.points
    body = yaml.safe_dump(
        table.model_dump(mode="json"), allow_unicode=True, sort_keys=False, width=100
    )
    path.write_text(HEADER + body, encoding="utf-8")
    crossing = [p.ref for p in table.points if p.share_pct < spec.whole_area_pct]
    print(f"{len(table.points)} areas -> data/catalog/manual/{spec.points}")
    print(f"across barrios (under {spec.whole_area_pct} % in the barrio of the point): {crossing}")


if __name__ == "__main__":
    main()
