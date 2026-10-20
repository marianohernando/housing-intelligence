"""Integration fixtures: a migrated Postgres at TEST_DATABASE_URL."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine

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
def migrated_engine(test_db_url: str) -> Iterator[Engine]:
    cfg = alembic_config(test_db_url)
    command.downgrade(cfg, "base")
    command.upgrade(cfg, "head")
    engine = create_engine(test_db_url)
    yield engine
    engine.dispose()
