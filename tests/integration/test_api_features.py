"""Feature and places API on the fixture database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.main import app

pytestmark = pytest.mark.db


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def test_feature_catalogue_lists_public_features(client: TestClient) -> None:
    body = client.get("/api/v1/features").json()
    ids = {f["feature_id"] for f in body["data"]}
    assert {"renta_per_capita", "poblacion_65_mas_pct"} <= ids  # gitleaks:allow (feature ids)
    assert all(f["limitations"] for f in body["data"] if f["public_use"])


def test_values_include_unknowns_and_lineage(client: TestClient) -> None:
    body = client.get("/api/v1/features/alquiler_m2_mensual/values").json()
    rows = body["data"]["values"]
    assert {r["territory_code"] for r in rows} == {"28079", "28001", "28002"}
    small = [r for r in rows if r["territory_code"] in {"28001", "28002"}]
    assert all(r["value"] is None and r["null_reason"] for r in small)  # never 0
    assert body["meta"]["data_version"]
    assert "cm_alquiler_m2_municipios" in body["data"]["lineage"]["dataset_versions"]


def test_values_carry_readable_names(client: TestClient) -> None:
    rows = client.get("/api/v1/features/alquiler_m2_mensual/values").json()["data"]["values"]
    names = {r["territory_code"]: r["name"] for r in rows}
    assert names["28001"] == "La Acebeda"  # source: "ACEBEDA, LA" or "Acebeda (La)" (D-212)
    assert names["28079"] == "Madrid"


def test_unknown_feature_is_404(client: TestClient) -> None:
    assert client.get("/api/v1/features/no_existe/values").status_code == 404


def test_places_geojson(client: TestClient) -> None:
    body = client.get("/api/v1/places", params={"category": "education"}).json()
    features = body["data"]["features"]
    assert features
    assert all(f["geometry"]["type"] == "Point" for f in features)
    assert all(set(f["properties"]) >= {"name", "subcategory"} for f in features)


def test_lineage_is_the_one_of_the_requested_level(client: TestClient) -> None:
    """CORE-006: district rent cites the postcode dataset, municipio rent the municipal one."""
    body = client.get(
        "/api/v1/features/alquiler_m2_mensual/values", params={"level": "distrito"}
    ).json()
    cited = body["data"]["lineage"]["dataset_versions"]
    assert "cm_alquiler_m2_codigo_postal_madrid" in cited
    assert "cm_alquiler_m2_municipios" not in cited
