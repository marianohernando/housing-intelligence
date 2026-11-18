"""D-246: points of the Portal del Suelo parcels of Madrid, read from the CM's own map layer.

The portal's CSV has no coordinates. The IDEM layer of the same parcels (WFS
`UsoDelSuelo:IDEM_V_SUELO_PARCELA`, EPSG:25830) has their polygons. This script reads it once
and writes one point inside each polygon of the municipio the pipeline splits (Madrid) to
data/catalog/manual, with the request's URL and the day it was read. The pipeline places each
parcel in its district and barrio from that versioned file, without network. Run it again when
the pipeline quarantines a Madrid parcel without a point (a parcel the portal added later).

    uv run python scripts/portal_suelo_points.py
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import yaml
from shapely.geometry import Point, shape

from hi_contracts.catalog.manual import ParcelPointsTable
from hi_contracts.catalog.pipeline import PublicLandParcelsPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.http import make_client, polite_retry
from hi_ingestion.pipelines.zone_context.run import MANUAL_DIR

DATASET_ID = "cm_parcelas_portal_suelo"
POINTS_ROLE = "points"
HEADER = """\
# D-246: a point inside each parcel of Madrid in «Parcelas publicadas en el Portal del Suelo
# 4.0» (Comunidad de Madrid, CC BY 4.0). The CSV has no coordinates; these come from the CM's
# own map layer of the same parcels (IDEM, WFS), read once on `consulted` by
# scripts/portal_suelo_points.py, so the pipeline places each parcel in its district and barrio
# without network. Do not edit by hand: run the script again.
"""


@polite_retry
def read_layer(client: httpx.Client, url: str) -> dict[str, Any]:
    response = client.get(url)
    response.raise_for_status()
    return response.json()


def inside_point(geometry: dict[str, Any]) -> tuple[int, int]:
    """A point inside the polygon (never its centroid, which can fall outside), to the metre."""
    polygon = shape(geometry)
    point = polygon.representative_point()
    x, y = round(point.x), round(point.y)
    if not polygon.contains(Point(x, y)):
        msg = f"the rounded point ({x}, {y}) is not inside its parcel"
        raise ValueError(msg)
    return x, y


def points_table(
    layer: dict[str, Any], spec: PublicLandParcelsPipeline, url: str
) -> ParcelPointsTable:
    code = spec.split_municipio_ine[len(spec.province_ine) :]
    points: list[dict[str, Any]] = []
    for feature in layer["features"]:
        props = feature["properties"]
        if props.get("CD_MUNICIPIO") != code or not feature.get("geometry"):
            continue
        x, y = inside_point(feature["geometry"])
        points.append({"ref": props["CD_REFERENCIA"], "x": x, "y": y})
    return ParcelPointsTable.model_validate(
        {
            "title": "Parcelas del Portal del Suelo 4.0: un punto dentro de cada parcela",
            "publisher": "Comunidad de Madrid (IDEM, Dirección General de Suelo)",
            "url": url,
            "layer": "UsoDelSuelo:IDEM_V_SUELO_PARCELA",
            "crs": "EPSG:25830",
            "consulted": datetime.now(UTC).date(),
            "method": "Punto interior del polígono de la parcela (shapely representative_point), "
            "redondeado al metro y comprobado dentro del polígono.",
            "municipio_ine": spec.split_municipio_ine,
            "points": sorted(points, key=lambda p: p["ref"]),
        }
    )


def main() -> None:
    catalog = load_catalog()
    spec = catalog.pipelines[DATASET_ID]
    assert isinstance(spec, PublicLandParcelsPipeline)  # noqa: S101 - the catalog declares it
    resource = next(r for r in catalog.datasets[DATASET_ID].resources if r.role == POINTS_ROLE)
    url = str(resource.url)
    with make_client(timeout=120) as client:
        layer = read_layer(client, url)
    table = points_table(layer, spec, url)
    path: Path = MANUAL_DIR / spec.points
    body = yaml.safe_dump(
        table.model_dump(mode="json"), allow_unicode=True, sort_keys=False, width=100
    )
    path.write_text(HEADER + body, encoding="utf-8")
    where = f"data/catalog/manual/{spec.points}"
    print(f"{len(table.points)} points of {spec.split_municipio_ine} -> {where}")


if __name__ == "__main__":
    main()
