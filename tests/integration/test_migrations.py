"""Gate 0: migrations up/down/up and no drift between ORM models and migrations."""

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from geoalchemy2 import alembic_helpers
from sqlalchemy import Engine, create_engine, inspect, text

import hi_db.models  # noqa: F401
from hi_db.base import Base
from tests.integration.conftest import alembic_config

pytestmark = pytest.mark.db

EXPECTED_TABLES = {
    "source_registry",
    "dataset_registry",
    "dataset_version",
    "ingestion_run",
    "geo_admin_unit",
    "h3_cell",
    "h3_cell_admin_unit",
}


def test_upgrade_downgrade_upgrade(test_db_url: str) -> None:
    cfg = alembic_config(test_db_url)
    engine = create_engine(test_db_url)

    command.downgrade(cfg, "base")
    assert EXPECTED_TABLES.isdisjoint(inspect(engine).get_table_names())

    command.upgrade(cfg, "head")
    assert set(inspect(engine).get_table_names()) >= EXPECTED_TABLES

    command.downgrade(cfg, "base")
    assert EXPECTED_TABLES.isdisjoint(inspect(engine).get_table_names())

    command.upgrade(cfg, "head")
    engine.dispose()


def test_extensions_available(migrated_engine: Engine) -> None:
    with migrated_engine.connect() as conn:
        assert conn.execute(text("SELECT postgis_version()")).scalar()
        assert conn.execute(text("SELECT '[1,2,3]'::vector::text")).scalar() == "[1,2,3]"


def test_models_match_migrations(migrated_engine: Engine) -> None:
    with migrated_engine.connect() as conn:
        ctx = MigrationContext.configure(
            conn,
            opts={
                "compare_type": True,
                "include_object": alembic_helpers.include_object,
            },
        )
        diff = compare_metadata(ctx, Base.metadata)
    assert diff == [], f"ORM models drifted from migrations: {diff}"
