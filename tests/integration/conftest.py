"""Integration fixtures: a migrated Postgres at TEST_DATABASE_URL."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, make_url, text

from hi_db.session import make_engine
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.admin_boundaries.run import (
    local_inputs,
    run_admin_boundaries,
)
from hi_ingestion.pipelines.common import RunSummary

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
