"""GET /api/v1/gaps on the fixture database: real rows, regional reference, provenance."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from hi_api.deps import get_engine
from hi_api.main import app
from hi_contracts.public.responses import ZoneGapListResponse

pytestmark = pytest.mark.db


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def test_municipio_list_has_real_rows_against_the_region(
    client: TestClient, migrated_engine: Engine
) -> None:
    response = client.get("/api/v1/gaps/municipio/28079")
    assert response.status_code == 200
    body = ZoneGapListResponse.model_validate(response.json())
    assert body.data.zone.name == "Madrid"
    assert body.data.zone.admin_unit_id == "ES.28.MUN.28079"
    rows = {r.row.value: r for r in body.data.rows}
    assert {"colegio", "centro_salud"} <= set(rows)
    with migrated_engine.connect() as conn:
        region = conn.execute(
            text(
                "SELECT value FROM feature_value WHERE feature_id = 'centros_salud_por_10000_hab' "
                "AND territory_level = 'ccaa' AND territory_code = '28'"
            )
        ).scalar_one()
    health = rows["centro_salud"]
    assert health.reference == pytest.approx(region, rel=1e-3)
    assert health.indicator.value is not None
    assert health.ratio_to_reference == pytest.approx(health.indicator.value / region, rel=1e-2)
    assert health.proxy_note
    assert body.meta.methodology_version == body.data.method.version
    cm = [d for d in body.data.datasets if d.is_cm_open_data]
    assert {d.dataset_id for d in cm} >= {"cm_centros_sanitarios", "cm_centros_educativos"}
    assert all(d.url and d.url.host == "datos.comunidad.madrid" for d in cm)


def test_unknown_zone_is_404_and_unsupported_level_is_422(client: TestClient) -> None:
    assert client.get("/api/v1/gaps/municipio/28999").status_code == 404
    assert client.get("/api/v1/gaps/h3_r9/89390cb1b0bffff").status_code == 422
    assert client.get("/api/v1/gaps/planeta/1").status_code == 422


def test_level_without_computed_indicators_returns_no_rows(client: TestClient) -> None:
    """Rows not computed at a level are absent (not SIN_DATOS) until CORE-005 adds them."""
    response = client.get("/api/v1/gaps/seccion_censal/2807901006")  # in the admin fixture
    assert response.status_code == 200
    payload = ZoneGapListResponse.model_validate(response.json())
    assert payload.data.zone.name == "Sección 01-006 · Madrid"
    assert payload.data.rows == []
    assert payload.warnings
