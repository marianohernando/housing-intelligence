"""Gate 1/2: admin boundaries Bronze -> Silver -> PostGIS on the real fixture."""

import json
import shutil
from pathlib import Path

import geopandas as gpd
import pytest
from shapely import affinity
from sqlalchemy import Engine, text

from hi_ingestion.pipelines.admin_boundaries.run import load_zones
from hi_ingestion.pipelines.common import RunSummary
from tests.integration.conftest import FIXTURE, run_fixture

pytestmark = pytest.mark.db


def _scalar(engine: Engine, sql: str, **params: object) -> object:
    with engine.connect() as conn:
        return conn.execute(text(sql), params).scalar()


def test_fixture_run_succeeds_with_all_levels(published: RunSummary) -> None:
    assert published.status == "SUCCESS", published.quality
    assert published.counts["municipio"] == 3
    assert published.counts["seccion_censal"] == 19
    assert published.counts["barrio"] >= 2
    assert published.quality["passed"]


def test_published_geometries_valid_in_both_crs(
    published: RunSummary, migrated_engine: Engine
) -> None:
    assert published.status == "SUCCESS"
    invalid = _scalar(
        migrated_engine,
        "SELECT count(*) FROM geo_admin_unit "
        "WHERE NOT ST_IsValid(geom_4326) OR NOT ST_IsValid(geom_25830)",
    )
    assert invalid == 0
    assert (
        _scalar(migrated_engine, "SELECT count(DISTINCT ST_SRID(geom_4326)) FROM geo_admin_unit")
        == 1
    )


def test_golden_zones_resolve_to_frozen_sections(
    published: RunSummary, migrated_engine: Engine
) -> None:
    assert published.status == "SUCCESS"
    for zone in load_zones():
        if zone["municipio_ine"] != "28079":
            continue  # fixture only contains Madrid capital + two small municipalities
        code = _scalar(
            migrated_engine,
            "SELECT code_official FROM geo_admin_unit WHERE level = 'seccion_censal' AND "
            "ST_Contains(geom_4326, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))",
            lon=zone["lon"],
            lat=zone["lat"],
        )
        assert code == zone["expected_seccion_censal"], zone["zone_id"]


def test_hierarchy_and_h3_invariants(published: RunSummary, migrated_engine: Engine) -> None:
    assert published.status == "SUCCESS"
    orphans = _scalar(
        migrated_engine,
        "SELECT count(*) FROM geo_admin_unit "
        "WHERE level <> 'municipio' AND parent_admin_unit_id IS NULL",
    )
    assert orphans == 0
    over = _scalar(
        migrated_engine,
        "SELECT count(*) FROM (SELECT h3_index, sum(overlap_share) s FROM h3_cell_admin_unit l "
        "JOIN geo_admin_unit u USING (admin_unit_id) "
        "WHERE method = 'overlap' AND u.level = 'seccion_censal' "
        "GROUP BY h3_index) t WHERE s > 1.000001",
    )
    assert over == 0
    unmapped = _scalar(
        migrated_engine,
        "SELECT count(*) FROM geo_admin_unit u WHERE level = 'seccion_censal' AND NOT EXISTS "
        "(SELECT 1 FROM h3_cell_admin_unit l JOIN h3_cell c USING (h3_index) "
        "WHERE l.admin_unit_id = u.admin_unit_id AND c.resolution = 9 AND l.method = 'overlap')",
    )
    assert unmapped == 0


def test_lineage_and_stage_tracking(published: RunSummary, migrated_engine: Engine) -> None:
    assert published.status == "SUCCESS"
    stages = _scalar(
        migrated_engine,
        "SELECT string_agg(stage || ':' || status, ',' ORDER BY started_at) FROM ingestion_run "
        "WHERE correlation_id = :cid",
        cid=published.correlation_id,
    )
    expected = ["PARSE", "NORMALIZE", "QUALITY_CHECK", "GEO_RESOLVE", "PUBLISH_SILVER"]
    assert stages == ",".join(f"{stage}:SUCCESS" for stage in expected)
    assert published.evidence_dir is not None
    lineage = json.loads((published.evidence_dir / "lineage.json").read_text())
    assert {i["role"] for i in lineage["inputs"]} == {"primary", "names"}
    assert all(len(i["sha256"]) == 64 for i in lineage["inputs"])


def test_rerun_same_input_is_skipped(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    again = run_fixture(migrated_engine, FIXTURE, tmp_path)
    assert again.status == "SKIPPED"
    assert again.version_label == published.version_label


def test_broken_ingestion_keeps_last_valid(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    """Gate 1: last-valid snapshot survives a broken new ingestion."""
    assert published.status == "SUCCESS"
    broken = tmp_path / "broken"
    shutil.copytree(FIXTURE, broken)
    sections = gpd.read_file(broken / "sections.gpkg")
    sections["geometry"] = sections.geometry.map(lambda g: affinity.translate(g, xoff=2_000_000))
    (broken / "sections.gpkg").unlink()
    sections.to_file(broken / "sections.gpkg", driver="GPKG")
    before = _scalar(migrated_engine, "SELECT count(*) FROM geo_admin_unit")

    result = run_fixture(migrated_engine, broken, tmp_path)

    assert result.status == "FAILED"
    failed = {c["name"] for c in result.quality["checks"] if c["critical"] and not c["passed"]}
    assert "within_madrid_bounds_and_not_swapped" in failed
    assert _scalar(migrated_engine, "SELECT count(*) FROM geo_admin_unit") == before
    assert (
        _scalar(migrated_engine, "SELECT version_label FROM dataset_version WHERE is_last_valid")
        == published.version_label
    )
    assert (
        _scalar(
            migrated_engine,
            "SELECT status FROM ingestion_run "
            "WHERE correlation_id = :cid AND stage = 'PUBLISH_SILVER'",
            cid=result.correlation_id,
        )
        == "SKIPPED"
    )
