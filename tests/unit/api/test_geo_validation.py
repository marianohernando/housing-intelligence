"""Input validation of the geo endpoint (no database needed)."""

from fastapi.testclient import TestClient

from hi_api.main import app


def test_rejects_unknown_level() -> None:
    response = TestClient(app).get("/api/v1/geo/admin-units", params={"level": "planet"})
    assert response.status_code == 422


def test_rejects_out_of_range_simplification() -> None:
    response = TestClient(app).get("/api/v1/geo/admin-units", params={"simplify_m": 10_000})
    assert response.status_code == 422


def test_openapi_documents_geo_route() -> None:
    spec = TestClient(app).get("/api/v1/openapi.json").json()
    assert "/api/v1/geo/admin-units" in spec["paths"]


def test_places_requires_a_known_category() -> None:
    client = TestClient(app)
    assert client.get("/api/v1/places").status_code == 422
    assert client.get("/api/v1/places", params={"category": "casinos"}).status_code == 422


def test_feature_routes_are_documented() -> None:
    paths = TestClient(app).get("/api/v1/openapi.json").json()["paths"]
    assert "/api/v1/features" in paths
    assert "/api/v1/features/{feature_id}/values" in paths
