"""Shared dependencies (engine is created once per process)."""

from functools import lru_cache

from sqlalchemy import Engine

from hi_api.settings import ApiSettings
from hi_db.session import make_engine


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return make_engine(ApiSettings().database_url)
