"""Build small stat-table fixtures from Bronze (CC BY 4.0, Comunidad de Madrid).

Keeps the territories present in the admin_sample fixture (Madrid, La Acebeda, Ajalvir), the
regional total, one statistical zone and the latest period, preserving the source encoding.
Usage: uv run python scripts/build_stat_fixtures.py
"""

from pathlib import Path

import pandas as pd

from hi_contracts.catalog.pipeline import CmStatTablePipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import read_csv

REPO = Path(__file__).resolve().parents[1]
BRONZE = REPO / "data" / "bronze" / "datasets"
OUT = REPO / "data" / "fixtures" / "golden" / "stat_sample"
CM_CODES = {"0014", "0029", "0796"}  # La Acebeda, Ajalvir, Madrid (municipio + check digit)
POSTCODES = ("28013", "28026", "28046")


def _latest_bronze(dataset_id: str) -> Path:
    files = sorted((BRONZE / dataset_id).glob("*/*.csv"), key=lambda p: p.stat().st_mtime)
    return files[-1]


def _sample_stat(frame: pd.DataFrame, spec: CmStatTablePipeline) -> pd.DataFrame:
    periods: list[str] = frame[spec.period_column].tolist()
    latest = max(periods)
    types: list[str] = frame[spec.territory_type_column].tolist()
    codes: list[str] = frame[spec.territory_code_column].tolist()
    zones = [c for t, c in zip(types, codes, strict=True) if t == "Zonas Estadísticas"]
    first_zone = zones[0] if zones else None
    keep = [
        period == latest
        and (
            (kind == "Municipios" and code in CM_CODES)
            or kind == "Comunidad de Madrid"
            or (kind == "Zonas Estadísticas" and code == first_zone)
        )
        for period, kind, code in zip(periods, types, codes, strict=True)
    ]
    return frame.loc[keep]


def main() -> None:
    catalog = load_catalog()
    OUT.mkdir(parents=True, exist_ok=True)
    for dataset_id, spec in sorted(catalog.pipelines.items()):
        if spec.kind == "points_csv":
            continue
        frame = read_csv(_latest_bronze(dataset_id), spec.csv)
        if isinstance(spec, CmStatTablePipeline):
            sample = _sample_stat(frame, spec)
        else:
            sample = frame[frame[spec.concept_column].str.contains("|".join(POSTCODES))]
        sample.to_csv(
            OUT / f"{dataset_id}.csv", sep=spec.csv.separator, index=False, encoding="latin-1"
        )
        print(f"{dataset_id}: {len(sample)} rows")


if __name__ == "__main__":
    main()
