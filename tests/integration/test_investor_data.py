"""D-247 on the fixture database: the investor data, from the source samples to the API, as
context that never scores."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.main import app

pytestmark = pytest.mark.db
PALACIO, CASTILLEJOS, ALMENARA = "28079011", "28079063", "28079064"


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def _values(client: TestClient, feature_id: str, level: str) -> dict[str, dict[str, Any]]:
    response = client.get(f"/api/v1/features/{feature_id}/values", params={"level": level})
    assert response.status_code == 200, response.text
    return {r["territory_code"]: r for r in response.json()["data"]["values"]}


def test_premises_per_1000_residents_use_the_padron_of_the_barrio(client: TestClient) -> None:
    """Palacio's sample: its open premises over the people of the padrón sample in Palacio."""
    rows = _values(client, "locales_abiertos_1000hab", "barrio")
    palacio = rows[PALACIO]
    assert palacio["value"] is not None and palacio["value"] > 0
    shops = _values(client, "comercio_proximidad_1000hab", "barrio")[PALACIO]
    assert 0 < shops["value"] < palacio["value"]  # proximity shops are some of the open ones
    closed = _values(client, "locales_cerrados_pct", "barrio")[CASTILLEJOS]
    assert 0 < closed["value"] < 100


def test_buildable_area_lists_each_area_in_its_barrio(client: TestClient) -> None:
    rows = _values(client, "edificabilidad_remanente_residencial_m2", "barrio")
    tetuan = [r for code, r in rows.items() if code.startswith("2807906") and r["value"]]
    items = [i for r in tetuan for i in r["detail"]["items"]]
    assert sum(r["value"] for r in tetuan) == pytest.approx(sum(i["value"] for i in items))
    assert {i["stage"] for i in items} <= {"edificacion", "gestion_urbanizacion"}
    assert any(i.get("note") for i in items)  # an area mostly in another barrio says so
    assert rows[PALACIO]["value"] == 0 and rows[PALACIO]["detail"]["items"] == []


def test_the_pilot_is_one_or_zero_in_every_barrio(client: TestClient) -> None:
    rows = _values(client, "piloto_inversores_m40", "barrio")
    assert rows[CASTILLEJOS]["value"] == 1 and rows[PALACIO]["value"] == 0
    almenara = rows[ALMENARA]["detail"]["items"][0]
    assert almenara["stage"] == "borde" and almenara["note"]


def test_cm_commercial_units_and_vacant_land_by_municipio(client: TestClient) -> None:
    units = _values(client, "unidades_comerciales_1000hab", "municipio")
    assert units["28079"]["value"] > 0
    vacant = _values(client, "suelo_vacante_unidades", "municipio")
    assert vacant["28079"]["value"] > 0
