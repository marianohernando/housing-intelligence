"""Point facility pipelines (points_csv) on the generic runner."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine

from hi_contracts.catalog.pipeline import PointsPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.places.normalize import Places, normalize_places
from hi_ingestion.pipelines.places.publish import replace_places
from hi_ingestion.pipelines.places.quality import run_quality
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline

PARSER_VERSION = "places-1.0.0"


def _counts(places: Places) -> dict[str, Any]:
    by_sub = (
        places.frame["subcategory"].value_counts().head(10).to_dict() if len(places.frame) else {}
    )
    return {
        "places_normalized": len(places.frame),
        "quarantined": len(places.quarantine),
        "top_subcategories": by_sub,
    }


def write_places_silver(places: Places, directory: Path) -> Path:
    path = directory / "places.csv.gz"
    places.frame.to_csv(path, index=False)
    return path


def run_places_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: PointsPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    source_id = catalog.datasets[spec.dataset_id].source_id
    steps: PipelineSteps[Places] = PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=spec.csv,
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_places(frame, spec),
        quarantine=lambda places: places.quarantine,
        quality=lambda places: run_quality(places, spec).to_dict(),
        counts=_counts,
        write_silver=write_places_silver,
        publish=lambda session, places, version_id: replace_places(
            session, places, spec.dataset_id, source_id, version_id
        ),
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
