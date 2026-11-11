"""Readiness answers 200 only when the API's database role can see the geography.

Uses an in-memory SQLite engine: a real database round trip without Postgres.
"""

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import StaticPool

from hi_api import deps
from hi_api.main import app


def _sqlite(*statements: str) -> Engine:
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
    return engine


def _ready(monkeypatch: pytest.MonkeyPatch, engine_factory: Callable[[], Engine]) -> Response:
    monkeypatch.setattr(deps, "get_engine", engine_factory)
    return TestClient(app).get("/api/v1/health/ready")


def test_ready_when_geography_is_visible(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = _sqlite(
        "CREATE TABLE geo_admin_unit (admin_unit_id TEXT)",
        "INSERT INTO geo_admin_unit VALUES ('municipio:28079')",
    )
    response = _ready(monkeypatch, lambda: engine)
    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok", "service": "hi-api"}


def test_not_ready_when_the_role_sees_no_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    # Row-level security without a policy for the role looks exactly like an empty table.
    engine = _sqlite("CREATE TABLE geo_admin_unit (admin_unit_id TEXT)")
    response = _ready(monkeypatch, lambda: engine)
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "INSUFFICIENT_DATA"


def test_not_ready_when_the_query_fails_without_leaking_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _sqlite()  # no table: the query raises
    response = _ready(monkeypatch, lambda: engine)
    assert response.status_code == 503
    assert response.json()["detail"] == {
        "code": "SOURCE_DEGRADED",
        "message": "Database unreachable",
    }


def test_not_ready_when_the_database_url_is_malformed(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _ready(monkeypatch, lambda: create_engine("nodriver://user:secret@host/db"))
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "SOURCE_DEGRADED"
    assert "secret" not in response.text


def test_liveness_never_touches_the_database(monkeypatch: pytest.MonkeyPatch) -> None:
    def unreachable() -> Engine:
        raise AssertionError("/health must not build an engine")

    monkeypatch.setattr(deps, "get_engine", unreachable)
    assert TestClient(app).get("/api/v1/health").status_code == 200
