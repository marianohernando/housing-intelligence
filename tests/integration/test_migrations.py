"""Gate 0: migrations up/down/up and no drift between ORM models and migrations."""

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from geoalchemy2 import alembic_helpers
from sqlalchemy import Engine, create_engine, func, inspect, select, table, text
from sqlalchemy.exc import ProgrammingError

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


API_ROLE = "vf_api_ro"


def test_api_readonly_role_reads_the_api_tables_and_writes_nothing(
    migrated_engine: Engine,
) -> None:
    """OPS-001: the demo API connects as vf_api_ro, read-only by setting and by privileges."""
    with migrated_engine.connect() as conn:
        role = conn.execute(
            text(
                "SELECT r.rolsuper, r.rolbypassrls, r.rolcreaterole, r.rolcreatedb, r.rolconfig, "
                "a.rolpassword IS NULL AS no_password "
                "FROM pg_roles r JOIN pg_authid a ON a.oid = r.oid WHERE r.rolname = :role"
            ),
            {"role": API_ROLE},
        ).one()
        policies = set(
            conn.execute(
                text(
                    "SELECT tablename FROM pg_policies WHERE policyname = 'vf_api_ro_read' "
                    "AND cmd = 'SELECT' AND :role = ANY(roles)"
                ),
                {"role": API_ROLE},
            ).scalars()
        )
    with migrated_engine.connect() as conn, conn.begin():
        conn.execute(text(f"SET LOCAL ROLE {API_ROLE}"))
        for name in sorted(policies):
            count = select(func.count()).select_from(table(name, schema="public"))
            assert conn.execute(count).scalar() is not None
        with pytest.raises(ProgrammingError, match="permission denied"), conn.begin_nested():
            conn.execute(text("SELECT count(*) FROM metric_observation"))
        with pytest.raises(ProgrammingError, match="permission denied"), conn.begin_nested():
            conn.execute(text("DELETE FROM source_registry"))
    assert not (role.rolsuper or role.rolbypassrls or role.rolcreaterole or role.rolcreatedb)
    assert "default_transaction_read_only=on" in role.rolconfig
    assert role.no_password, "the password is set out of band, never in a migration"
    assert {"geo_admin_unit", "feature_value", "dataset_registry"} <= policies


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
