"""Alembic environment. URL comes from DATABASE_URL (or -x url=...)."""

from logging.config import fileConfig
from typing import Any

from alembic import context
from geoalchemy2 import alembic_helpers
from sqlalchemy import engine_from_config, pool

import hi_db.models  # noqa: F401  (registers every table on Base.metadata)
from hi_db.base import Base
from hi_db.session import SEARCH_PATH_SQL
from hi_db.settings import DatabaseSettings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

override_url = context.get_x_argument(as_dictionary=True).get("url") or config.attributes.get("url")
database_url = override_url or DatabaseSettings().database_url
# ConfigParser interpolates "%": escape it so percent-encoded passwords survive.
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
target_metadata = Base.metadata


def _configure_kwargs() -> dict[str, Any]:
    return {
        "target_metadata": target_metadata,
        "compare_type": True,
        "include_object": alembic_helpers.include_object,
        "process_revision_directives": alembic_helpers.writer,
        "render_item": alembic_helpers.render_item,
    }


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **_configure_kwargs(),
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        # Extensions live in schema `extensions` (Supabase convention); never rely on DB defaults.
        connection.exec_driver_sql(SEARCH_PATH_SQL)
        connection.commit()
        context.configure(connection=connection, **_configure_kwargs())
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
