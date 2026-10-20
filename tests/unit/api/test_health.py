from fastapi.testclient import TestClient

from hi_api.main import app


def test_health_returns_envelope() -> None:
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["data"] == {"status": "ok", "service": "hi-api"}
    assert body["meta"]["api_version"] == "v1"
    assert body["meta"]["request_id"]
    assert body["warnings"] == []
