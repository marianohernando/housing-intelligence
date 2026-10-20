"""Build the small admin-boundaries fixture from the real Bronze snapshot (CC BY 4.0, CM).

Usage: uv run python scripts/build_admin_fixture.py
Selects the sections containing the Madrid golden zones plus their neighbours, and every
section of two small municipalities, so integration tests exercise all admin levels.
"""

import json
from pathlib import Path
from typing import cast

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

REPO = Path(__file__).resolve().parents[1]
BRONZE = REPO / "data" / "bronze" / "datasets"
OUT = REPO / "data" / "fixtures" / "golden" / "admin_sample"
SMALL_MUNICIPIOS = ("001", "002")  # La Acebeda, Ajalvir
MADRID_ZONES = ("sol", "chamartin_plaza_castilla")


def _bronze(dataset_id: str, filename: str) -> Path:
    return next((BRONZE / dataset_id).glob(f"*/{filename}"))


def main() -> None:
    sections = gpd.read_file(f"zip://{_bronze('cm_secciones_censales', '558.zip')}")
    zones = json.loads((REPO / "data/fixtures/golden/madrid_zones.json").read_text())["zones"]
    points = gpd.GeoSeries(
        [Point(z["lon"], z["lat"]) for z in zones if z["zone_id"] in MADRID_ZONES], crs="EPSG:4326"
    ).to_crs("EPSG:25830")  # CRS of the source seccionado
    hits = sections[sections.geometry.apply(lambda g: any(g.contains(p) for p in points))]
    neighbours = sections[sections.geometry.intersects(hits.union_all())]
    small = sections[sections["CDMUNI"].isin(SMALL_MUNICIPIOS)]
    sample = cast(gpd.GeoDataFrame, pd.concat([neighbours, small]))
    sample = cast(gpd.GeoDataFrame, sample[~sample["CDGSECCION"].duplicated()])
    OUT.mkdir(parents=True, exist_ok=True)
    sample.to_file(OUT / "sections.gpkg", driver="GPKG")
    codes: list[str] = sample["CDGSECCION"].tolist()
    keys = {g.replace("-", "") for g in codes}
    names = pd.read_csv(
        _bronze("cm_secciones_censales", "secciones_censales.csv"),
        sep=";",
        dtype=str,
        encoding="latin-1",
    )
    names[names["seccion_codigo"].isin(sorted(keys))].to_csv(
        OUT / "names.csv", sep=";", index=False, encoding="latin-1"
    )
    barrios = pd.read_csv(
        _bronze("cm_barrios_madrid", "barrios_municipio_madrid.csv"),
        sep=";",
        dtype=str,
        encoding="latin-1",
    )
    shp_barrios: list[object] = sample["CDTBARRIO"].tolist()
    barrio_keys = {b[:3] + "6" + b[3:] for b in shp_barrios if isinstance(b, str) and len(b) == 6}
    barrios[barrios["barrio_codigo"].isin(sorted(barrio_keys))].to_csv(
        OUT / "barrios.csv", sep=";", index=False, encoding="latin-1"
    )
    n_munis = len(set(sample["CDMUNI"].tolist()))
    print(f"{len(sample)} sections, {n_munis} municipios -> {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
