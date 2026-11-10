"""Build facility fixtures from Bronze (CC BY 4.0, Comunidad de Madrid).

Keeps real rows whose coordinates fall inside the admin_sample sections, plus edge cases the
pipeline must handle: a closed school, missing coordinates and a protected social subtype.
Usage: uv run python scripts/build_places_fixtures.py
"""

from pathlib import Path
from typing import cast

import geopandas as gpd
import pandas as pd
from shapely.geometry.base import BaseGeometry

from hi_contracts.catalog.pipeline import PointsPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import read_csv
from hi_ingestion.pipelines.places.normalize import apply_filters

REPO = Path(__file__).resolve().parents[1]
BRONZE = REPO / "data" / "bronze" / "datasets"
SECTIONS = REPO / "data" / "fixtures" / "golden" / "admin_sample" / "sections.gpkg"
OUT = REPO / "data" / "fixtures" / "golden" / "places_sample"
MAX_INSIDE = 12
OUTSIDE = 10  # valid rows outside the fixture area: must stay unassigned, never mis-assigned


def _latest_bronze(dataset_id: str) -> Path:
    return sorted((BRONZE / dataset_id).glob("*/*.csv"), key=lambda p: p.stat().st_mtime)[-1]


def _inside_mask(frame: pd.DataFrame, spec: PointsPipeline, area: BaseGeometry) -> list[bool]:
    def num(values: list[str]) -> list[float]:
        out: list[float] = []
        for v in values:
            try:
                out.append(float(v.replace(",", ".")))
            except ValueError:
                out.append(0.0)
        return out

    xs = num(frame[spec.x_column].tolist())
    ys = num(frame[spec.y_column].tolist())
    points = gpd.GeoSeries.from_xy(xs, ys, crs=spec.crs)
    return [bool(area.contains(p)) for p in points]


def _edge_cases(frame: pd.DataFrame, allowed: pd.DataFrame, spec: PointsPipeline) -> pd.DataFrame:
    """A row that passes filters but lacks coordinates, plus rows the filters must drop."""
    picks: list[pd.DataFrame] = [
        cast(pd.DataFrame, allowed[allowed[spec.x_column] == ""].head(1)),
        cast(pd.DataFrame, allowed[allowed[spec.x_column] != ""].head(OUTSIDE)),
    ]
    if spec.status_column:
        picks.append(
            cast(pd.DataFrame, frame[~frame[spec.status_column].isin(spec.active_values)].head(1))
        )
    if spec.dataset_id == "cm_centros_atencion_social":
        picks.append(cast(pd.DataFrame, frame[frame["subtipo"] == "PISOS TUTELADOS"].head(1)))
    return pd.concat(picks)


def main() -> None:
    catalog = load_catalog()
    area = gpd.read_file(SECTIONS).union_all()
    OUT.mkdir(parents=True, exist_ok=True)
    for dataset_id, spec in sorted(catalog.pipelines.items()):
        if not isinstance(spec, PointsPipeline):
            continue
        frame = read_csv(_latest_bronze(dataset_id), spec.csv)
        allowed, _ = apply_filters(frame, spec)
        inside = allowed.loc[_inside_mask(allowed, spec, area)]
        ids: list[str] = inside[spec.id_column].drop_duplicates().head(MAX_INSIDE).tolist()
        sample = pd.concat(
            [frame[frame[spec.id_column].isin(ids)], _edge_cases(frame, allowed, spec)]
        )
        sample.to_csv(
            OUT / f"{dataset_id}.csv", sep=spec.csv.separator, index=False, encoding="utf-8-sig"
        )
        print(f"{dataset_id}: {len(sample)} rows ({len(ids)} ids inside fixture sections)")


if __name__ == "__main__":
    main()
