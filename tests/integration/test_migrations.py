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
    "metric_registry",
    "metric_observation",
    "place_master",
    "place_source_alias",
    "feature_registry",
    "feature_value",
}


def test_upgrade_downgrade_upgrade(scratch_db_url: str) -> None:
    cfg = alembic_config(scratch_db_url)
    engine = create_engine(scratch_db_url)

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


def test_every_public_table_has_row_level_security(migrated_engine: Engine) -> None:
    """D-197: Supabase's Data API must never read or write a table; new tables need RLS too."""
    tables_without_rls = text(
        "SELECT c.relname FROM pg_class c "
        "JOIN pg_namespace n ON n.oid = c.relnamespace "
        "WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p') AND NOT c.relrowsecurity "
        "ORDER BY 1"
    )
    with migrated_engine.connect() as conn:
        without_rls = conn.execute(tables_without_rls).scalars().all()
    assert without_rls == [], f"tables without row level security: {without_rls}"


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
