"""«Entorno» of a zone on the fixture database (D-237): street noise only in Madrid, NO2 always
with its station, and car parks with their spaces and fee through the API."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from hi_api.deps import get_engine
from hi_api.main import app

pytestmark = pytest.mark.db

_VALUES = text(
    """
    SELECT territory_level, territory_code, value, null_reason, inputs->'detail' AS detail
      FROM feature_value WHERE feature_id = :feature_id
    """
)


def _rows(engine: Engine, feature_id: str) -> dict[tuple[str, str], dict[str, Any]]:
    with engine.connect() as conn:
        rows = conn.execute(_VALUES, {"feature_id": feature_id}).mappings().all()
    return {(r["territory_level"], r["territory_code"]): dict(r) for r in rows}


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def test_street_noise_is_madrid_only_and_never_zero_elsewhere(
    features_computed: None, migrated_engine: Engine
) -> None:
    """The synthetic map is loud in the west half of the grid: Madrid gets a share between 0
    and 100, and the municipios without a map get SOURCE_NO_COVERAGE."""
    for feature_id in ("pct_calle_ruido_dia", "pct_calle_ruido_noche"):
        rows = _rows(migrated_engine, feature_id)
        madrid = rows[("municipio", "28079")]
        assert madrid["value"] is not None and 0 < madrid["value"] < 100, feature_id
        for code in ("28001", "28002"):
            outside = rows[("municipio", code)]
            assert outside["value"] is None, (feature_id, code)
            assert outside["null_reason"] == "SOURCE_NO_COVERAGE"
        districts = [r for (level, _), r in rows.items() if level == "distrito"]
        assert any(r["value"] is not None for r in districts)


def test_no2_always_names_its_station(features_computed: None, migrated_engine: Engine) -> None:
    rows = _rows(migrated_engine, "no2_media_anual")
    madrid_districts = [
        r for (level, code), r in rows.items() if level == "distrito" and code[:5] == "28079"
    ]
    assert any(r["value"] is not None for r in madrid_districts)
    for row in rows.values():
        if row["value"] is None:
            assert row["null_reason"] == "SOURCE_NO_COVERAGE" and row["detail"] is None
            continue
        assert {"station", "station_code", "own", "distance_km"} <= set(row["detail"])
    # Madrid districts only take the Ayuntamiento's stations (air quality zone 1)
    for row in madrid_districts:
        if row["value"] is not None:
            assert row["detail"]["station_code"].startswith("28079")


def test_a_municipio_without_a_station_of_its_air_zone_is_unknown(
    features_computed: None, migrated_engine: Engine
) -> None:
    """La Acebeda (Sierra Norte) and Ajalvir (Corredor del Henares) have no station of their
    zone inside the sample's geography: unknown, never the nearest of another zone."""
    rows = _rows(migrated_engine, "no2_media_anual")
    for code in ("28001", "28002"):
        assert rows[("municipio", code)]["value"] is None


def test_the_api_serves_the_station_and_the_car_park_fee(client: TestClient) -> None:
    response = client.get("/api/v1/features/no2_media_anual/values", params={"level": "distrito"})
    assert response.status_code == 200, response.text
    known = [r for r in response.json()["data"]["values"] if r["value"] is not None]
    assert known and all(r["detail"]["station"] for r in known)
    response = client.get(
        "/api/v1/places",
        params={"category": "other", "subcategory": "Aparcamiento disuasorio"},
    )
    assert response.status_code == 200, response.text
    crtm = [
        f["properties"]
        for f in response.json()["data"]["features"]
        if f["properties"]["capacity"] is not None
    ]
    assert crtm, "no park-and-ride car park with its spaces"
    for properties in crtm:
        assert properties["capacity"]["unit"] == "plazas"
        assert properties["access_fee"] in {"free", "paid", "mixed"}
