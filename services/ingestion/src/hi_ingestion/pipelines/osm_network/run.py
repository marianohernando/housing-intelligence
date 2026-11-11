"""OSM walking network on the generic runner: Bronze extract -> Silver graph, nothing in the DB."""

from pathlib import Path
from typing import Any

from sqlalchemy import Engine

from hi_contracts.catalog.pipeline import CsvFormat, OsmWalkNetworkPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.osm_network.network import (
    NetworkResult,
    normalize_segments,
    save_network,
)
from hi_ingestion.pipelines.osm_network.parse import parse_extract
from hi_ingestion.pipelines.osm_network.quality import run_network_quality
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline

PARSER_VERSION = "osm-walk-1.0.1"


def _counts(result: NetworkResult) -> dict[str, Any]:
    network = result.network
    return {
        "nodes": network.n_nodes,
        "edges": network.n_edges,
        "total_km": round(network.total_km, 1),
        "quarantined": len(result.quarantine),
    }


def run_osm_network_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: OsmWalkNetworkPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    steps: PipelineSteps[NetworkResult] = PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),
        resource_role=spec.resource_role,
        normalize=normalize_segments,
        quarantine=lambda result: result.quarantine,
        quality=lambda result: run_network_quality(result, spec).to_dict(),
        counts=_counts,
        write_silver=lambda result, directory: save_network(result.network, directory),
        publish=lambda _session, result, _version_id: _counts(result),
        parse=lambda path: parse_extract(path, spec),
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
