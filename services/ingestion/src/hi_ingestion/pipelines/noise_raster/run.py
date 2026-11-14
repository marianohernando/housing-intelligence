"""Noise rasters on the generic runner: Bronze ZIP -> Silver grid, nothing in the DB (D-237)."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine

from hi_contracts.catalog.pipeline import CsvFormat, NoiseRasterPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.noise_raster.grid import GRID_FILE, save_grid
from hi_ingestion.pipelines.noise_raster.normalize import NoiseResult, normalize_rasters
from hi_ingestion.pipelines.noise_raster.parse import parse_rasters
from hi_ingestion.pipelines.noise_raster.quality import run_noise_quality
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline

# 1.1: the layers are read from the pipeline spec again (Ld instead of Lden, R-02 of PR #65)
PARSER_VERSION = "noise-raster-1.1.0"


def _counts(result: NoiseResult) -> dict[str, Any]:
    shape = result.grid.shape if result.grid else (0, 0)
    return {
        "rows": shape[0],
        "columns": shape[1],
        "quarantined": len(result.problems),
        **{f"cells_{name}": n for name, n in result.cells_with_level().items()},
    }


def _write_silver(result: NoiseResult, directory: Path) -> Path:
    if result.grid is None:  # the runner only writes Silver after the quality gate passed
        msg = "no noise grid to write"
        raise ValueError(msg)
    return save_grid(result.grid, directory)


def run_noise_raster_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: NoiseRasterPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    steps: PipelineSteps[NoiseResult] = PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_rasters(frame, spec),
        quarantine=lambda result: result.problems,
        quality=lambda result: run_noise_quality(result, spec).to_dict(),
        counts=_counts,
        write_silver=_write_silver,
        publish=lambda _session, result, _version_id: _counts(result),
        parse=lambda path: parse_rasters(path, spec),
    )
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        steps,
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )


__all__ = ["GRID_FILE", "PARSER_VERSION", "run_noise_raster_pipeline"]
