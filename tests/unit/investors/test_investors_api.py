"""D-248 API without a database: the viability is pure, its request is bounded and a wrong
barrio id is refused before any connection (the unit tests point at an address where no
database answers)."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from hi_api.main import app
from hi_contracts.pro.investors import DemandRequest, ViabilityRequest
from hi_contracts.public.responses import ViabilityResponse
from hi_domain import viability as v

client = TestClient(app)
BODY = {
    "buildable_m2": 1000,
    "sale_price_m2": 4000,
    "rent_m2_month": 15,
    "pem_m2": 600,
    "cost_coefficient": 1.5,
    "sales_costs_pct": 10,
}


def test_viability_three_scenarios_without_land() -> None:
    response = client.post("/api/v1/investors/viability", json=BODY)
    assert response.status_code == 200, response.text
    body = ViabilityResponse.model_validate(response.json())
    assert body.meta.methodology_version == v.VIABILITY_VERSION
    data = body.data
    assert not data.land_known
    assert [s.key for s in data.scenarios] == ["base", "optimista", "pesimista"]
    base = data.scenarios[0]
    assert base.residual_land_value == pytest.approx(1_900_000)
    assert base.margin_pct is None and base.total_cost is None
    assert base.verdict is None
    assert base.headline.startswith("Lo máximo que se puede pagar por el suelo")
    assert data.demand is None
    assert data.notices[0].startswith("No es una tasación")


def test_viability_land_per_m2_and_demand_in_percent() -> None:
    body = BODY | {"land_eur_m2": 2200, "demand": {"household_income": 40_000}}
    data = ViabilityResponse.model_validate(
        client.post("/api/v1/investors/viability", json=body).json()
    ).data
    base = data.scenarios[0]
    assert base.land == pytest.approx(2_200_000)
    assert base.margin_pct == pytest.approx(12.5)
    assert base.verdict is not None and base.verdict.value == "ajustar"
    assert data.demand is not None
    assert data.demand.threshold_pct == pytest.approx(30)
    assert data.demand.monthly_rent == pytest.approx(80 * 15)


@pytest.mark.parametrize(
    "change",
    [
        {"buildable_m2": 0},
        {"sale_price_m2": 100},
        {"pem_m2": 10_000},
        {"cost_coefficient": 0.5},
        {"land_eur": 1, "land_eur_m2": 1},
        {"target_margin_pct": 5, "adjust_floor_pct": 10},
        {"unknown": 1},
    ],
)
def test_viability_refuses_inputs_out_of_bounds(change: dict[str, float]) -> None:
    response = client.post("/api/v1/investors/viability", json=BODY | change)
    assert response.status_code == 422


def test_request_defaults_are_the_domain_assumptions() -> None:
    """The contract cannot import the domain: its defaults are checked here."""
    request = ViabilityRequest(buildable_m2=1, sale_price_m2=1000, pem_m2=644)
    assert request.cost_coefficient == pytest.approx(v.COST_COEFFICIENT)
    assert request.sales_costs_pct == pytest.approx(v.SALES_COSTS_SHARE * 100)
    assert request.target_margin_pct == pytest.approx(v.TARGET_MARGIN * 100)
    assert request.adjust_floor_pct == pytest.approx(v.ADJUST_FLOOR * 100)
    demand = DemandRequest(household_income=30_000)
    assert demand.home_m2 == pytest.approx(v.HOME_M2)
    assert demand.ltv_pct == pytest.approx(v.LOAN_TO_VALUE * 100)
    assert demand.loan_years == v.LOAN_YEARS
    assert demand.loan_rate_pct == pytest.approx(v.LOAN_RATE * 100)
    assert demand.effort_threshold_pct == pytest.approx(v.EFFORT_THRESHOLD * 100)
    with pytest.raises(ValidationError):
        DemandRequest(household_income=1)


@pytest.mark.parametrize("admin_unit_id", ["ES.28.DIS.2807916", "foo", "ES.28.BAR.28005001"])
def test_sheet_refuses_what_is_not_a_madrid_barrio_before_connecting(admin_unit_id: str) -> None:
    response = client.get(f"/api/v1/investors/zones/{admin_unit_id}")
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "OUT_OF_COVERAGE"
