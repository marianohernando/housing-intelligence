"""Engine and session factories."""

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from hi_db.settings import DatabaseSettings


def make_engine(url: str | None = None) -> Engine:
    return create_engine(url or DatabaseSettings().database_url, pool_pre_ping=True)


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False)
