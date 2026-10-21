"""Geo API against the migrated test DB (runs after the admin pipeline fixture tests)."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.main import app
from hi_ingestion.pipelines.common import RunSummary

pytestmark = pytest.mark.db


def _first_position(coords: Any) -> tuple[float, float]:
    """First (lon, lat) of any GeoJSON coordinate nesting (Polygon or MultiPolygon)."""
    while isinstance(coords[0], list):
        coords = coords[0]
    return float(coords[0]), float(coords[1])


@pytest.fixture
def client(migrated_engine: Engine) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def test_municipalities_geojson_with_lineage(published: RunSummary, client: TestClient) -> None:
    assert published.status == "SUCCESS"
    body = client.get("/api/v1/geo/admin-units", params={"level": "municipio"}).json()
    features = body["data"]["features"]
    assert {f["properties"]["code"] for f in features} == {"28079", "28001", "28002"}
    assert all(f["geometry"]["type"] in {"Polygon", "MultiPolygon"} for f in features)
    for feature in features:
        lon, lat = _first_position(feature["geometry"]["coordinates"])
        assert -4.6 < lon < -3.0 and 39.8 < lat < 41.2
    assert body["meta"]["data_version"] == published.version_label
    assert "CC BY" in body["data"]["lineage"]["attribution_text"]
    assert body["warnings"] == []
