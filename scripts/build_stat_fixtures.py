"""Build small stat-table fixtures from Bronze (CC BY 4.0, Comunidad de Madrid).

Keeps the territories present in the admin_sample fixture (Madrid, La Acebeda, Ajalvir), the
regional total, one statistical zone and the latest period, preserving the source encoding.
A table that names its municipios by hand (D-235) gives two files: Madrid's rows of its last two
years in stat_sample, and every row the pipeline reads plus the rows with a misspelt name in
municipio_names_sample, for the test that no municipio is lost.
Usage: uv run python scripts/build_stat_fixtures.py [dataset_id ...]
"""

import sys
from pathlib import Path
from typing import cast

import pandas as pd

from hi_contracts.catalog.pipeline import (
    CmMunicipioConceptPipeline,
    CmPostcodeConceptPipeline,
    CmStatTablePipeline,
)
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import read_csv

REPO = Path(__file__).resolve().parents[1]
BRONZE = REPO / "data" / "bronze" / "datasets"
OUT = REPO / "data" / "fixtures" / "golden" / "stat_sample"
NAMES_OUT = REPO / "data" / "fixtures" / "golden" / "municipio_names_sample"
SAMPLE_MUNICIPIO = "Madrid"
CM_CODES = {"0014", "0029", "0796"}  # La Acebeda, Ajalvir, Madrid (municipio + check digit)
POSTCODES = (
    "28013",
    "28026",
    "28029",
    "28036",
    "28046",
)  # 28029 and 28036 hold sample health centres


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
            or kind in ("Comunidad de Madrid", "Otros")  # «Otros»: regional-only tables
            or (kind == "Zonas Estadísticas" and code == first_zone)
        )
        for period, kind, code in zip(periods, types, codes, strict=True)
    ]
    return frame.loc[keep]


def _write(sample: pd.DataFrame, path: Path, separator: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(path, sep=separator, index=False, encoding="latin-1")
    print(f"{path.relative_to(REPO)}: {len(sample)} rows")


def _sample_municipio_concept(
    frame: pd.DataFrame, spec: CmMunicipioConceptPipeline
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(Madrid's rows of the last two years, the rows read plus those with a misspelt name)."""
    years = sorted(set(frame[spec.period_column].tolist()))[-2:]
    madrid = frame.loc[
        (frame[spec.municipio_column] == SAMPLE_MUNICIPIO) & frame[spec.period_column].isin(years)
    ]
    concepts: list[str] = frame[spec.concept_column].tolist()
    names: list[str] = frame[spec.municipio_column].tolist()
    keep = [
        spec.concept_value(concept) is not None or not concept.endswith(f" en {name}")
        for concept, name in zip(concepts, names, strict=True)
    ]
    return cast(pd.DataFrame, madrid), cast(pd.DataFrame, frame.loc[keep])


def main() -> None:
    catalog = load_catalog()
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(sys.argv[1:])
    for dataset_id, spec in sorted(catalog.pipelines.items()):
        if not isinstance(
            spec, CmStatTablePipeline | CmPostcodeConceptPipeline | CmMunicipioConceptPipeline
        ):
            continue
        if only and dataset_id not in only:
            continue
        frame = read_csv(_latest_bronze(dataset_id), spec.csv)
        if isinstance(spec, CmMunicipioConceptPipeline):
            madrid, named = _sample_municipio_concept(frame, spec)
            _write(madrid, OUT / f"{dataset_id}.csv", spec.csv.separator)
            _write(named, NAMES_OUT / f"{dataset_id}.csv", spec.csv.separator)
            continue
        if isinstance(spec, CmStatTablePipeline):
            sample = _sample_stat(frame, spec)
        else:
            sample = frame[frame[spec.concept_column].str.contains("|".join(POSTCODES))]
        _write(cast(pd.DataFrame, sample), OUT / f"{dataset_id}.csv", spec.csv.separator)


if __name__ == "__main__":
    main()
