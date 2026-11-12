"""Build directory fixtures from Bronze (Ministerio de Sanidad, reuse with attribution).

Keeps every row of the region (so the pipeline's row-count gate runs on real numbers) and only
the columns the pipeline reads: phones and emails never reach the repository (D-186, D-218).
Usage: uv run python scripts/build_directory_fixtures.py [dataset_id ...]
"""

import sys
from pathlib import Path

import pandas as pd

from hi_contracts.catalog.pipeline import FacilityDirectoryPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.directory.normalize import parse_sheet

REPO = Path(__file__).resolve().parents[1]
BRONZE = REPO / "data" / "bronze" / "datasets"
OUT = REPO / "data" / "fixtures" / "golden" / "directory_sample"


def _latest_bronze(dataset_id: str) -> Path:
    return sorted((BRONZE / dataset_id).glob("*/*.xlsx"), key=lambda p: p.stat().st_mtime)[-1]


def build(spec: FacilityDirectoryPipeline) -> Path:
    frame = parse_sheet(_latest_bronze(spec.dataset_id), spec)
    region = frame.loc[frame[spec.scope_column].str.strip().isin(spec.scope_values)]
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{spec.dataset_id}.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        region.to_excel(writer, sheet_name=spec.sheet, index=False)
    print(f"{spec.dataset_id}: {len(region)} rows -> {path.relative_to(REPO)}")
    return path


def main(dataset_ids: list[str]) -> None:
    pipelines = load_catalog().pipelines
    for dataset_id, spec in sorted(pipelines.items()):
        if isinstance(spec, FacilityDirectoryPipeline) and (
            not dataset_ids or dataset_id in dataset_ids
        ):
            build(spec)


if __name__ == "__main__":
    main(sys.argv[1:])
