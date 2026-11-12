"""The connection pool of each process is sized from the environment.

On Vercel every API instance keeps its own pool, and the Supabase session pooler admits 15
clients in total, so production lowers the per-instance pool with DB_POOL_SIZE and
DB_MAX_OVERFLOW. Without them the SQLAlchemy defaults (5 and 10) apply.
"""

import pytest
from sqlalchemy.pool import QueuePool

from hi_db.session import make_engine

URL = "postgresql+psycopg://user:secret@localhost:1/nothing"  # never connected in these tests


def _pool(monkeypatch: pytest.MonkeyPatch, **env: str) -> QueuePool:
    for name in ("DB_POOL_SIZE", "DB_MAX_OVERFLOW"):
        monkeypatch.delenv(name, raising=False)
    for name, value in env.items():
        monkeypatch.setenv(name, value)
    pool = make_engine(URL).pool
    assert isinstance(pool, QueuePool)
    return pool


def test_without_variables_the_pool_keeps_the_sqlalchemy_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pool = _pool(monkeypatch)
    assert pool.size() == 5
    assert pool._max_overflow == 10


def test_production_can_shrink_the_pool_of_each_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    pool = _pool(monkeypatch, DB_POOL_SIZE="2", DB_MAX_OVERFLOW="1")
    assert pool.size() == 2
    assert pool._max_overflow == 1


@pytest.mark.parametrize(("name", "value"), [("DB_POOL_SIZE", "0"), ("DB_MAX_OVERFLOW", "-1")])
def test_a_pool_that_cannot_serve_a_request_is_rejected(
    monkeypatch: pytest.MonkeyPatch, name: str, value: str
) -> None:
    with pytest.raises(ValueError, match=name.lower()):
        _pool(monkeypatch, **{name: value})
