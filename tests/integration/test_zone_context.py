"""D-241 on the fixture database: new housing and what is coming, from the source subsets to the
API, as context that never scores."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from hi_api.deps import get_engine
from hi_api.main import app

pytestmark = pytest.mark.db


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def _values(client: TestClient, feature_id: str, level: str) -> dict[str, dict[str, Any]]:
    response = client.get(f"/api/v1/features/{feature_id}/values", params={"level": level})
    assert response.status_code == 200, response.text
    return {r["territory_code"]: r for r in response.json()["data"]["values"]}


def test_sales_of_new_homes_add_up_the_last_four_quarters(client: TestClient) -> None:
    """The sample's last quarter is 2026 T2 (provisional): Madrid sold 1.512 new homes of
    40.086 between July 2025 and June 2026, as the CM table gives it."""
    rows = _values(client, "compraventas_obra_nueva_pct", "municipio")
    madrid = rows["28079"]
    assert madrid["detail"] == {
        "numerator": 1512.0,
        "denominator": 40086.0,
        "period_end": "2026-06-30",
        "provisional": True,
        "items": None,
    }
    assert madrid["period_start"] == "2025-07-01"
    assert round(madrid["value"], 1) == 3.8
    assert rows["28001"]["null_reason"] == "NOT_APPLICABLE"  # La Acebeda: no sales, not a 0 %


def test_new_and_used_appraisals_are_two_figures_of_the_same_year(client: TestClient) -> None:
    new = _values(client, "valor_tasado_vivienda_nueva_m2", "municipio")
    used = _values(client, "valor_tasado_vivienda_usada_m2", "municipio")
    assert (new["28079"]["value"], used["28079"]["value"]) == (5458.5, 4987.9)
    assert new["28079"]["period_start"] == used["28079"]["period_start"] == "2025-01-01"
    assert new["28001"]["value"] is None and new["28001"]["null_reason"]  # never 0


def test_planning_areas_list_what_is_unfinished_by_district(client: TestClient) -> None:
    rows = _values(client, "ambitos_residenciales_en_desarrollo", "distrito")
    tetuan = rows["2807906"]
    first = tetuan["detail"]["items"][0]
    assert (first["name"], first["stage"], first["code"]) == (
        "Paseo de la Dirección",
        "obras",
        "APR.06.02",
    )
    assert tetuan["value"] == len(tetuan["detail"]["items"])
    assert tetuan["period_start"] == "2026-07-01"
    # Every district of the sample has a row: VEDA lists all of Madrid, so none is a gap
    assert set(rows) == {"2807901", "2807905", "2807906"}
    assert all(r["null_reason"] is None for r in rows.values())


def test_plan_vive_is_in_its_municipio_and_a_zero_elsewhere(client: TestClient) -> None:
    rows = _values(client, "plan_vive_viviendas", "municipio")
    item = rows["28079"]["detail"]["items"][0]
    assert rows["28079"]["value"] == 1616.0
    assert (item["name"], item["stage"]) == ("Valdebebas y Los Ahijones", "Entrega y construcción")
    assert rows["28002"]["value"] == 0.0 and rows["28002"]["detail"]["items"] == []


def test_other_features_carry_no_detail(client: TestClient) -> None:
    rows = _values(client, "alquiler_m2_mensual", "municipio")
    assert all("detail" not in r for r in rows.values())


def test_context_never_reaches_the_search_or_the_gap_list(
    client: TestClient, migrated_engine: Engine
) -> None:
    """No `fit` and no `gap_row`: the search reads none of these features."""
    with migrated_engine.connect() as conn:
        bound = conn.execute(
            text(
                "SELECT feature_id FROM feature_registry WHERE feature_id = ANY(:ids) "
                "AND ((spec->'fit') IS NOT NULL AND spec->'fit' <> 'null'::jsonb "
                "OR (spec->'gap_row') IS NOT NULL AND spec->'gap_row' <> 'null'::jsonb)"
            ),
            {
                "ids": [
                    "compraventas_obra_nueva_pct",
                    "valor_tasado_vivienda_nueva_m2",
                    "valor_tasado_vivienda_usada_m2",
                    "plan_vive_viviendas",
                    "ambitos_residenciales_en_desarrollo",
                ]
            },
        ).all()
    assert bound == []
