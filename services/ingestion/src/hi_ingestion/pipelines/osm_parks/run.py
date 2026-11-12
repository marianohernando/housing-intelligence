"""OSM parks on the generic runner: Bronze extract -> Silver CSV -> places (category green)."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine

from hi_contracts.catalog.pipeline import CsvFormat, OsmParksPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.osm_parks.parks import normalize_parks
from hi_ingestion.pipelines.osm_parks.parse import parse_parks
from hi_ingestion.pipelines.osm_parks.quality import run_parks_quality
from hi_ingestion.pipelines.places.normalize import Places
from hi_ingestion.pipelines.places.publish import replace_places
from hi_ingestion.pipelines.places.run import write_places_silver
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline

PARSER_VERSION = "osm-parks-1.0.0"


def _counts(places: Places) -> dict[str, Any]:
    return {
        "parks": len(places.frame),
        "quarantined": len(places.quarantine),
        **places.filtered_out,
    }


def run_osm_parks_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: OsmParksPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    source_id = catalog.datasets[spec.dataset_id].source_id
    steps: PipelineSteps[Places] = PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_parks(frame, spec),
        quarantine=lambda places: places.quarantine,
        quality=lambda places: run_parks_quality(places, spec).to_dict(),
        counts=_counts,
        write_silver=write_places_silver,
        publish=lambda session, places, version_id: replace_places(
            session, places, spec.dataset_id, source_id, version_id
        ),
        parse=lambda path: parse_parks(path, spec),
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
