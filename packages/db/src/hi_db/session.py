"""Engine and session factories."""

from typing import Any

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from hi_db.settings import DatabaseSettings

SEARCH_PATH_SQL = "SET search_path TO public, extensions"


def _set_search_path(dbapi_connection: Any, _record: Any) -> None:
    with dbapi_connection.cursor() as cursor:
        cursor.execute(SEARCH_PATH_SQL)
    dbapi_connection.commit()


def _connect_args(settings: DatabaseSettings) -> dict[str, Any]:
    # psycopg disables prepared statements on a connection with prepare_threshold=None.
    return {} if settings.db_prepared_statements else {"prepare_threshold": None}


def make_engine(url: str | None = None) -> Engine:
    settings = DatabaseSettings()
    engine = create_engine(
        url or settings.database_url,
        pool_pre_ping=True,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        connect_args=_connect_args(settings),
    )
    event.listen(engine, "connect", _set_search_path)
    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
