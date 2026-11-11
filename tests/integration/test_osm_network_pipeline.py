"""OSM walking network on the generic runner: Silver graph, dataset version, idempotent rerun."""

from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import OsmWalkNetworkPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.osm_network.network import NETWORK_FILE, load_network
from hi_ingestion.pipelines.osm_network.run import run_osm_network_pipeline

pytestmark = pytest.mark.db
DATASET = "osm_red_peatonal"
EXTRACT = """<?xml version='1.0' encoding='UTF-8'?>
<osm version="0.6" generator="test">
  <node id="1" lat="40.4168" lon="-3.7038"/>
  <node id="2" lat="40.4177" lon="-3.7038"/>
  <node id="3" lat="40.4177" lon="-3.7026"/>
  <way id="10"><nd ref="1"/><nd ref="2"/><nd ref="3"/><tag k="highway" v="residential"/></way>
  <way id="11"><nd ref="1"/><nd ref="3"/><tag k="highway" v="motorway"/></way>
</osm>
"""
LAST_VALID_SQL = text(
    "SELECT version_label, quality_status, bronze_manifest_path FROM dataset_version "
    "WHERE dataset_id = :ds AND is_last_valid"
)


def _run(engine: Engine, tmp: Path, min_total_km: float, body: str = EXTRACT) -> RunSummary:
    catalog = load_catalog()
    spec = catalog.pipelines[DATASET]
    assert isinstance(spec, OsmWalkNetworkPipeline)
    tmp.mkdir(parents=True, exist_ok=True)
    extract = tmp / "extract.osm"
    extract.write_text(body)
    source = local_file(DATASET, "primary", extract)
    spec = spec.model_copy(update={"min_total_km": min_total_km})
    return run_osm_network_pipeline(engine, catalog, spec, source, evidence_root=tmp, data_dir=tmp)


def test_network_lands_in_silver_and_rerun_is_skipped(
    migrated_engine: Engine, tmp_path: Path
) -> None:
    result = _run(migrated_engine, tmp_path, min_total_km=0.1)
    assert result.status == "SUCCESS", result.quality
    assert result.counts["edges"] == 2
    with migrated_engine.connect() as conn:
        version = conn.execute(LAST_VALID_SQL, {"ds": DATASET}).mappings().one()
    assert version["quality_status"] == "PASSED"
    silver = tmp_path / "silver" / DATASET / result.checksum[:12] / NETWORK_FILE
    assert load_network(silver).n_edges == 2
    assert _run(migrated_engine, tmp_path, min_total_km=0.1).status == "SKIPPED"


def test_truncated_extract_fails_quality(migrated_engine: Engine, tmp_path: Path) -> None:
    other = EXTRACT.replace('generator="test"', 'generator="truncated"')  # new checksum
    result = _run(migrated_engine, tmp_path, min_total_km=10_000, body=other)
    assert result.status == "FAILED"
    failed = [c["name"] for c in result.quality["checks"] if not c["passed"]]
    assert failed == ["total_length_plausible"]
