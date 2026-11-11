"""Readiness answers 200 only when the API's database role can see the geography.

Uses an in-memory SQLite engine: a real database round trip without Postgres.
"""

from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.pool import StaticPool

from hi_api.deps import get_engine
from hi_api.main import app


def _engine(*statements: str) -> Engine:
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
    return engine


def _ready(engine: Engine) -> Response:
    app.dependency_overrides[get_engine] = lambda: engine
    try:
        return TestClient(app).get("/api/v1/health/ready")
    finally:
        app.dependency_overrides.clear()


def test_ready_when_geography_is_visible() -> None:
    engine = _engine(
        "CREATE TABLE geo_admin_unit (admin_unit_id TEXT)",
        "INSERT INTO geo_admin_unit VALUES ('municipio:28079')",
    )
    response = _ready(engine)
    assert response.status_code == 200
    assert response.json()["data"] == {"status": "ok", "service": "hi-api"}


def test_not_ready_when_the_role_sees_no_rows() -> None:
    # Row-level security without a policy for the role looks exactly like an empty table.
    response = _ready(_engine("CREATE TABLE geo_admin_unit (admin_unit_id TEXT)"))
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "INSUFFICIENT_DATA"


def test_not_ready_when_the_database_fails_without_leaking_details() -> None:
    response = _ready(_engine())  # no table: the query raises
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail == {"code": "SOURCE_DEGRADED", "message": "Database unreachable"}


def test_liveness_never_touches_the_database() -> None:
    app.dependency_overrides[get_engine] = lambda: _engine()
    try:
        assert TestClient(app).get("/api/v1/health").status_code == 200
    finally:
        app.dependency_overrides.clear()
