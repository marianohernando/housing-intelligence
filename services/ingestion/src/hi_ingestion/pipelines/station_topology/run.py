"""Station topologies (station_topology) on the generic runner: ArcGIS JSON -> Silver only."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine

from hi_contracts.catalog.pipeline import CsvFormat, StationTopologyPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline
from hi_ingestion.pipelines.station_topology.normalize import (
    Topology,
    normalize_topology,
    parse_layer,
    write_topology_silver,
)
from hi_ingestion.pipelines.station_topology.quality import run_topology_quality

PARSER_VERSION = "topology-1.0.0"


def _counts(topology: Topology) -> dict[str, Any]:
    return {
        "stations": len(topology.frame),
        "quarantined": len(topology.quarantine),
        "by_reading": topology.frame["step_free"].value_counts().to_dict(),  # pyright: ignore[reportUnknownMemberType]
    }


def run_topology_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: StationTopologyPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    steps: PipelineSteps[Topology] = PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),
        resource_role=spec.resource_role,
        normalize=lambda frame: normalize_topology(frame, spec),
        quarantine=lambda topology: topology.quarantine,
        quality=lambda topology: run_topology_quality(topology, spec).to_dict(),
        counts=_counts,
        write_silver=write_topology_silver,
        publish=lambda _session, topology, _version_id: {"stations": len(topology.frame)},
        parse=parse_layer,
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
