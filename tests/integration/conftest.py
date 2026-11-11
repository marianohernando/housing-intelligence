"""Integration fixtures: a migrated Postgres at TEST_DATABASE_URL."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, make_url, text

from hi_contracts.catalog.pipeline import (
    CmPostcodeConceptPipeline,
    CmStatTablePipeline,
    MadridDistrictPanelPipeline,
    MadridPadronPipeline,
    PointsPipeline,
)
from hi_db.session import make_engine
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.admin_boundaries.run import (
    local_inputs,
    run_admin_boundaries,
)
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.district_panel.run import run_panel_pipeline
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.padron.run import run_padron_pipeline
from hi_ingestion.pipelines.places.run import run_places_pipeline
from hi_ingestion.pipelines.stat_tables.run import run_metric_pipeline

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


@pytest.fixture(scope="session")
def fixtures_ingested(
    published: RunSummary, migrated_engine: Engine, tmp_path_factory: pytest.TempPathFactory
) -> None:
    assert published.status == "SUCCESS"
    catalog = load_catalog()
    tmp = tmp_path_factory.mktemp("features")
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
