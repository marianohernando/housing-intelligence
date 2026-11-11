"""GTFS feeds on real fixture subsets against the test DB (needs the published admin fixture)."""

import zipfile
from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import GtfsFeedPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.gtfs.feed import GtfsFeedError
from hi_ingestion.pipelines.gtfs.run import run_gtfs_pipeline

pytestmark = pytest.mark.db
FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "golden" / "gtfs_sample"
DATASETS = sorted(d for d, s in load_catalog().pipelines.items() if isinstance(s, GtfsFeedPipeline))
STATS_SQL = text(
    """
    SELECT count(*) AS n,
           count(DISTINCT subcategory) AS modes,
           min(subcategory) AS mode,
           count(*) FILTER (WHERE category <> 'transport') AS not_transport,
           count(*) FILTER (WHERE NOT ST_IsValid(geom_4326)) AS invalid,
           count(*) FILTER (WHERE (attributes->>'departures_day')::int <= 0) AS without_departures,
           count(*) FILTER (
               WHERE seccion_admin_unit_id IS NULL AND EXISTS (
                   SELECT 1 FROM geo_admin_unit u
                    WHERE u.level = 'seccion_censal' AND ST_Contains(u.geom_25830, p.geom_25830)
               )
           ) AS missed
      FROM place_master p
     WHERE official_dataset_id = :ds
    """
)
LAST_VALID_SQL = text("SELECT id FROM dataset_version WHERE dataset_id = :ds AND is_last_valid")


def _run(engine: Engine, dataset_id: str, tmp: Path, path: Path | None = None) -> RunSummary:
    catalog = load_catalog()
    spec = catalog.pipelines[dataset_id]
    assert isinstance(spec, GtfsFeedPipeline)
    source = local_file(dataset_id, "primary", path or FIXTURES / f"{dataset_id}.zip")
    return run_gtfs_pipeline(engine, catalog, spec, source, evidence_root=tmp, data_dir=tmp)


@pytest.mark.parametrize("dataset_id", DATASETS)
def test_feed_publishes_transport_places(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path, dataset_id: str
) -> None:
    assert published.status == "SUCCESS"
    result = _run(migrated_engine, dataset_id, tmp_path)
    assert result.status in {"SUCCESS", "SKIPPED"}, result.quality
    spec = load_catalog().pipelines[dataset_id]
    assert isinstance(spec, GtfsFeedPipeline)
    with migrated_engine.connect() as conn:
        row = conn.execute(STATS_SQL, {"ds": dataset_id}).mappings().one()
    assert row["n"] > 0
    assert (row["modes"], row["mode"]) == (1, spec.mode)
    assert row["not_transport"] == 0
    assert row["invalid"] == 0
    assert row["without_departures"] == 0  # stops without service are filtered, never zeros
    assert row["missed"] == 0


def test_rerun_of_the_same_feed_is_skipped(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    _run(migrated_engine, "crtm_gtfs_metro_ligero", tmp_path)
    assert _run(migrated_engine, "crtm_gtfs_metro_ligero", tmp_path).status == "SKIPPED"


def _snapshot(engine: Engine, dataset_id: str) -> tuple[object, object]:
    with engine.connect() as conn:
        version = conn.execute(LAST_VALID_SQL, {"ds": dataset_id}).scalar()
        places = conn.execute(STATS_SQL, {"ds": dataset_id}).mappings().one()["n"]
    return version, places


def test_unreadable_feed_keeps_last_valid(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    _run(migrated_engine, "crtm_gtfs_metro", tmp_path)
    before = _snapshot(migrated_engine, "crtm_gtfs_metro")
    broken = tmp_path / "broken.zip"
    broken.write_bytes(b"PK\x03\x04 truncated download")
    with pytest.raises(GtfsFeedError):
        _run(migrated_engine, "crtm_gtfs_metro", tmp_path, broken)
    assert _snapshot(migrated_engine, "crtm_gtfs_metro") == before


def test_implausible_service_fails_quality_and_keeps_last_valid(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    _run(migrated_engine, "crtm_gtfs_metro", tmp_path)
    before = _snapshot(migrated_engine, "crtm_gtfs_metro")
    bad = tmp_path / "every_second.zip"
    with (
        zipfile.ZipFile(FIXTURES / "crtm_gtfs_metro.zip") as src,
        zipfile.ZipFile(bad, "w") as dst,
    ):
        for name in src.namelist():
            body = src.read(name).decode("utf-8")
            if name == "frequencies.txt":  # a headway of 1 s: 3,600 trains an hour
                lines = body.splitlines()
                rows = [
                    ",".join([*line.split(",")[:3], "1", *line.split(",")[4:]])
                    for line in lines[1:]
                ]
                body = "\n".join([lines[0], *rows]) + "\n"
            dst.writestr(name, body)
    result = _run(migrated_engine, "crtm_gtfs_metro", tmp_path, bad)
    assert result.status == "FAILED"
    failed = [c["name"] for c in result.quality["checks"] if not c["passed"]]
    assert "peak_departures_plausible" in failed
    assert _snapshot(migrated_engine, "crtm_gtfs_metro") == before
