"""OSM parks on the generic runner: Bronze extract -> Silver CSV -> places (category green)."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine

from hi_contracts.catalog.pipeline import CsvFormat, OsmParksPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.osm_parks.inclusions import INCLUSIONS_FILE, load_inclusions
from hi_ingestion.pipelines.osm_parks.parks import normalize_parks
from hi_ingestion.pipelines.osm_parks.parse import parse_parks
from hi_ingestion.pipelines.osm_parks.quality import run_parks_quality
from hi_ingestion.pipelines.places.corrections import corrections_input
from hi_ingestion.pipelines.places.normalize import Places
from hi_ingestion.pipelines.places.publish import replace_places
from hi_ingestion.pipelines.places.run import write_places_silver
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline

# 1.1: public parks OSM tags otherwise, listed with an official source (D-222 §5);
# 1.1.1: only the polygons of an invalid outline
PARSER_VERSION = "osm-parks-1.1.1"


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
    inclusions_file: Path = INCLUSIONS_FILE,
) -> RunSummary:
    source_id = catalog.datasets[spec.dataset_id].source_id
    inclusions = {p.osm_id: p for p in load_inclusions(inclusions_file).parks}
    extra = [corrections_input(spec.dataset_id, inclusions_file)] if inclusions else []
    steps: PipelineSteps[Places] = PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_parks(frame, spec, inclusions),
        quarantine=lambda places: places.quarantine,
        quality=lambda places: run_parks_quality(places, spec, list(inclusions)).to_dict(),
        counts=_counts,
        write_silver=write_places_silver,
        publish=lambda session, places, version_id: replace_places(
            session, places, spec.dataset_id, source_id, version_id
        ),
        parse=lambda path: parse_parks(path, spec, list(inclusions)),
    )
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        steps,
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
        extra_inputs=extra,
    )
