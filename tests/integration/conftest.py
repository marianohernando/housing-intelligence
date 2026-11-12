"""Integration fixtures: a migrated Postgres at TEST_DATABASE_URL."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from pyproj import Transformer
from sqlalchemy import Engine, create_engine, make_url, text

from hi_contracts.catalog.pipeline import (
    CmPostcodeConceptPipeline,
    CmStatTablePipeline,
    FacilityDirectoryPipeline,
    GtfsFeedPipeline,
    MadridDistrictPanelPipeline,
    MadridPadronPipeline,
    OsmParksPipeline,
    OsmWalkNetworkPipeline,
    PointsPipeline,
    StationTopologyPipeline,
)
from hi_db.session import make_engine
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.admin_boundaries.run import (
    local_inputs,
    run_admin_boundaries,
)
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.directory.run import run_directory_pipeline
from hi_ingestion.pipelines.district_panel.run import run_panel_pipeline
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.gtfs.run import run_gtfs_pipeline
from hi_ingestion.pipelines.osm_network.run import run_osm_network_pipeline
from hi_ingestion.pipelines.osm_parks.run import run_osm_parks_pipeline
from hi_ingestion.pipelines.padron.run import run_padron_pipeline
from hi_ingestion.pipelines.places.run import run_places_pipeline
from hi_ingestion.pipelines.stat_tables.run import run_metric_pipeline
from hi_ingestion.pipelines.station_topology.run import run_topology_pipeline

ALEMBIC_INI = Path(__file__).resolve().parents[2] / "infra" / "migrations" / "alembic.ini"


def _test_url() -> str:
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL not set")
    return url


def alembic_config(url: str) -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.cmd_opts = None
    cfg.attributes["url"] = url
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


@pytest.fixture(scope="session")
def test_db_url() -> str:
    return _test_url()


@pytest.fixture(scope="session")
def scratch_db_url(test_db_url: str) -> Iterator[str]:
    """A throwaway database for destructive migration tests (up/down/up)."""
    url = make_url(test_db_url)
    name = f"{url.database}_migrations"
    admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{name}"'))
        conn.execute(text(f'CREATE DATABASE "{name}"'))
    yield url.set(database=name).render_as_string(hide_password=False)
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
    admin.dispose()


@pytest.fixture(scope="session")
def migrated_engine(test_db_url: str) -> Iterator[Engine]:
    cfg = alembic_config(test_db_url)
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    engine = make_engine(test_db_url)  # same connection setup as the application
    yield engine
    engine.dispose()


FIXTURE = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "golden" / "admin_sample"


def run_fixture(engine: Engine, inputs_dir: Path, tmp: Path) -> RunSummary:
    return run_admin_boundaries(
        engine,
        load_catalog(),
        local_inputs(inputs_dir),
        evidence_root=tmp / "evidence",
        data_dir=tmp / "data",
    )


@pytest.fixture(scope="session")
def published(migrated_engine: Engine, tmp_path_factory: pytest.TempPathFactory) -> RunSummary:
    with migrated_engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE h3_cell_admin_unit, h3_cell, geo_admin_unit, ingestion_run, "
                "dataset_version CASCADE"
            )
        )
    return run_fixture(migrated_engine, FIXTURE, tmp_path_factory.mktemp("valid"))


GOLDEN = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "golden"
MADRID_SAMPLE_DISTRICTS = 3  # Madrid fixtures keep Centro, Chamartín and Tetuán


# The Madrid sections of the admin sample (EPSG:25830), plus a margin; the other municipios of
# the sample get no street, so their walking features must come out as explicit nulls.
WALK_GRID_BOUNDS = (439_500.0, 4_473_900.0, 442_550.0, 4_480_400.0)
WALK_GRID_STEP_M = 100.0
TO_WGS84 = Transformer.from_crs("EPSG:25830", "EPSG:4326", always_xy=True)


def walk_grid_extract(path: Path) -> Path:
    """A synthetic OSM extract: residential streets every 100 m over the Madrid sample."""
    x0, y0, x1, y1 = WALK_GRID_BOUNDS
    columns = int((x1 - x0) // WALK_GRID_STEP_M) + 1
    rows = int((y1 - y0) // WALK_GRID_STEP_M) + 1
    node = {(i, j): 1 + i * rows + j for i in range(columns) for j in range(rows)}
    lines = ["<?xml version='1.0' encoding='UTF-8'?>", '<osm version="0.6" generator="test">']
    for (i, j), node_id in node.items():
        lon, lat = TO_WGS84.transform(x0 + i * WALK_GRID_STEP_M, y0 + j * WALK_GRID_STEP_M)
        lines.append(f'  <node id="{node_id}" lat="{lat:.7f}" lon="{lon:.7f}"/>')
    way = 1
    for (i, j), node_id in node.items():
        for neighbour in ((i + 1, j), (i, j + 1)):
            if neighbour in node:
                lines.append(
                    f'  <way id="{way}"><nd ref="{node_id}"/><nd ref="{node[neighbour]}"/>'
                    '<tag k="highway" v="residential"/></way>'
                )
                way += 1
    path.write_text("\n".join([*lines, "</osm>"]) + "\n")
    return path


# Two 150 m x 150 m parks (2.25 ha) inside the walking grid (D-222).
PARK_CORNERS_25830 = ((440_000.0, 4_474_500.0), (441_500.0, 4_477_000.0))
PARK_SIDE_M = 150.0


def parks_extract(path: Path) -> Path:
    """A synthetic OSM extract with two leisure=park squares over the Madrid sample."""
    lines = ["<?xml version='1.0' encoding='UTF-8'?>", '<osm version="0.6" generator="test">']
    ways: list[str] = []
    for k, (x, y) in enumerate(PARK_CORNERS_25830):
        corners = [
            (x, y),
            (x + PARK_SIDE_M, y),
            (x + PARK_SIDE_M, y + PARK_SIDE_M),
            (x, y + PARK_SIDE_M),
        ]
        ids = [100 * (k + 1) + i for i in range(4)]
        for node_id, (cx, cy) in zip(ids, corners, strict=True):
            lon, lat = TO_WGS84.transform(cx, cy)
            lines.append(f'  <node id="{node_id}" lat="{lat:.7f}" lon="{lon:.7f}"/>')
        refs = "".join(f'<nd ref="{i}"/>' for i in [*ids, ids[0]])
        ways.append(
            f'  <way id="{k + 1}">{refs}<tag k="leisure" v="park"/>'
            f'<tag k="name" v="Parque {k + 1}"/></way>'
        )
    path.write_text("\n".join([*lines, *ways, "</osm>"]) + "\n")
    return path


def ingest_directories(engine: Engine, data_dir: Path) -> None:
    catalog = load_catalog()
    for dataset_id, spec in sorted(catalog.pipelines.items()):
        if isinstance(spec, FacilityDirectoryPipeline):
            src = local_file(
                dataset_id, "primary", GOLDEN / "directory_sample" / f"{dataset_id}.xlsx"
            )
            result = run_directory_pipeline(
                engine, catalog, spec, src, evidence_root=None, data_dir=data_dir
            )
            assert result.status in {"SUCCESS", "SKIPPED"}, (dataset_id, result.quality)
        elif isinstance(spec, StationTopologyPipeline):  # before the GTFS feeds (D-223)
            src = local_file(
                dataset_id, "primary", GOLDEN / "topology_sample" / f"{dataset_id}.json"
            )
            sample = spec.model_copy(update={"min_rows": 1})
            result = run_topology_pipeline(
                engine, catalog, sample, src, evidence_root=None, data_dir=data_dir
            )
            assert result.status in {"SUCCESS", "SKIPPED"}, (dataset_id, result.quality)


@pytest.fixture(scope="session")
def fixtures_ingested(
    published: RunSummary, migrated_engine: Engine, tmp_path_factory: pytest.TempPathFactory
) -> None:
    assert published.status == "SUCCESS"
    catalog = load_catalog()
    tmp = tmp_path_factory.mktemp("features")
    ingest_directories(migrated_engine, tmp)  # before the registers they name (D-218, D-223)
    for dataset_id, spec in sorted(catalog.pipelines.items()):
        if isinstance(spec, PointsPipeline):
            src = local_file(dataset_id, "primary", GOLDEN / "places_sample" / f"{dataset_id}.csv")
            result = run_places_pipeline(
                migrated_engine, catalog, spec, src, evidence_root=None, data_dir=tmp
            )
        elif isinstance(spec, CmStatTablePipeline | CmPostcodeConceptPipeline):
            src = local_file(dataset_id, "primary", GOLDEN / "stat_sample" / f"{dataset_id}.csv")
            result = run_metric_pipeline(
                migrated_engine, catalog, spec, src, evidence_root=None, data_dir=tmp
            )
        elif isinstance(spec, MadridPadronPipeline):
            src = local_file(dataset_id, "primary", GOLDEN / "padron_sample" / f"{dataset_id}.csv")
            sample = spec.model_copy(update={"expected_districts": MADRID_SAMPLE_DISTRICTS})
            result = run_padron_pipeline(
                migrated_engine, catalog, sample, src, evidence_root=None, data_dir=tmp
            )
        elif isinstance(spec, GtfsFeedPipeline):  # stops: destinations of the walking features
            src = local_file(dataset_id, "primary", GOLDEN / "gtfs_sample" / f"{dataset_id}.zip")
            result = run_gtfs_pipeline(
                migrated_engine, catalog, spec, src, evidence_root=None, data_dir=tmp
            )
        elif isinstance(spec, OsmWalkNetworkPipeline):
            src = local_file(dataset_id, "primary", walk_grid_extract(tmp / "walk_grid.osm"))
            result = run_osm_network_pipeline(
                migrated_engine,
                catalog,
                spec.model_copy(update={"min_total_km": 1}),
                src,
                evidence_root=None,
                data_dir=tmp,
            )
        elif isinstance(spec, OsmParksPipeline):
            src = local_file(dataset_id, "primary", parks_extract(tmp / "parks.osm"))
            result = run_osm_parks_pipeline(
                migrated_engine,
                catalog,
                spec.model_copy(update={"min_parks": 1}),
                src,
                evidence_root=None,
                data_dir=tmp,
                inclusions_file=tmp / "no_inclusions.yaml",  # the real ones are not in the grid
            )
        elif isinstance(spec, MadridDistrictPanelPipeline):
            src = local_file(dataset_id, "primary", GOLDEN / "panel_sample" / f"{dataset_id}.csv")
            sample = spec.model_copy(update={"expected_districts": MADRID_SAMPLE_DISTRICTS})
            result = run_panel_pipeline(
                migrated_engine, catalog, sample, src, evidence_root=None, data_dir=tmp
            )
        else:
            continue
        assert result.status in {"SUCCESS", "SKIPPED"}, (dataset_id, result.quality)


@pytest.fixture(scope="session")
def features_computed(fixtures_ingested: None, migrated_engine: Engine) -> None:
    from hi_features.compute import METHODS, compute, persist

    for spec in load_catalog().features.values():
        if spec.formula.method in METHODS:
            persist(migrated_engine, spec, compute(migrated_engine, spec))
