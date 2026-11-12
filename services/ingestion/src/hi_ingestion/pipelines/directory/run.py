"""Facility directories (facility_directory) on the generic runner: XLSX -> Silver, no DB rows."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine

from hi_contracts.catalog.pipeline import CsvFormat, FacilityDirectoryPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.directory.normalize import (
    Directory,
    normalize_directory,
    parse_sheet,
    published_capacities,
    write_directory_silver,
)
from hi_ingestion.pipelines.directory.quality import run_directory_quality
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline

PARSER_VERSION = "directory-1.1.0"


def _counts(directory: Directory) -> dict[str, Any]:
    frame = directory.frame
    return {
        "entries": len(frame),
        "quarantined": len(directory.quarantine),
        "with_capacity": len(published_capacities(directory)),
        "kinds": frame["kind"].value_counts().to_dict(),
    }


def run_directory_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: FacilityDirectoryPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    steps: PipelineSteps[Directory] = PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_directory(frame, spec),
        quarantine=lambda directory: directory.quarantine,
        quality=lambda directory: run_directory_quality(directory, spec).to_dict(),
        counts=_counts,
        write_silver=write_directory_silver,
        publish=lambda _session, directory, _version_id: {"entries": len(directory.frame)},
        parse=lambda path: parse_sheet(path, spec),
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
