"""POST /api/v1/search on the fixture database (CORE-003): contract, UNKNOWN never PASS,
Reality Check that the web can apply, highlights equal to GET /gaps and provenance."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from hi_api.deps import get_engine
from hi_api.main import app
from hi_contracts.public.responses import SearchResponse
from hi_domain.fit import FIT_VERSION

pytestmark = pytest.mark.db
FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "contracts"


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def _family() -> dict[str, Any]:
    """The demo case, with the place of work as a preference."""
    scenario = json.loads((FIXTURES / "scenario_state.familia_castellana.fixture.json").read_text())
    for anchor in scenario["anchors"]:
        anchor["max_minutes"] = None
    return scenario


def _search(client: TestClient, scenario: dict[str, Any]) -> SearchResponse:
    response = client.post("/api/v1/search", json=scenario)
    assert response.status_code == 200, response.text
    return SearchResponse.model_validate(response.json())


def test_demo_case_ranks_zones_that_pass_every_condition(client: TestClient) -> None:
    body = _search(client, _family())
    data = body.data
    assert body.meta.methodology_version == data.methodology_version == FIT_VERSION
    assert body.meta.data_version
    codes = {z.zone.code for z in data.all_zones}
    assert "28079" not in codes  # Madrid capital is ranked by district (D-200)
    assert any(z.zone.level == "distrito" for z in data.all_zones)
    assert data.reality_check.zones_evaluated == len(data.all_zones)
    for ranked in data.results:
        assert all(c.status == "PASS" for c in ranked.constraints)
        assert ranked.facts and len(ranked.facts) <= 5
    passing = {z.zone.code for z in data.all_zones if z.passes_all}
    assert {r.zone.code for r in data.results} <= passing
    assert any(d.is_cm_open_data for d in data.datasets)


def test_unknown_never_counts_as_pass(client: TestClient) -> None:
    """No zone of the fixtures has a published appraised value (D-227): buying is UNKNOWN
    everywhere, never PASS, and more budget cannot add a zone without a price."""
    scenario = _family() | {"budget": {"kind": "buy", "amount_eur": 300000}, "nearby": []}
    data = _search(client, scenario).data
    assert data.results == []
    assert data.reality_check.zones_passing == 0
    assert data.reality_check.zones_unknown == data.reality_check.zones_evaluated
    assert all(not z.passes_all for z in data.all_zones)
    option = next(o for o in data.reality_check.relaxations if o.constraint_id == "budget")
    assert option.relaxed_scenario.budget is not None
    assert option.relaxed_scenario.budget.amount_eur == 330000
    assert option.added_zones == 0
    assert data.near_misses == []  # an UNKNOWN is never an explicit alternative either


def test_trip_limits_without_commute_times_are_unknown_and_say_why(client: TestClient) -> None:
    """Before `hi-features commute` (test_commute.py fills it later in the session)."""
    scenario = _family()
    scenario["anchors"][0]["max_minutes"] = 40
    body = _search(client, scenario)
    assert body.data.results == []
    assert any("trip by public transport" in w for w in body.warnings)


def test_a_relaxed_scenario_sent_back_gives_the_promised_zones(client: TestClient) -> None:
    scenario = _family() | {"budget": {"kind": "rent", "amount_eur": 600}}
    check = _search(client, scenario).data.reality_check
    for option in check.relaxations:
        again = _search(client, option.relaxed_scenario.model_dump(mode="json")).data
        assert again.reality_check.zones_passing == option.zones_if_relaxed


def test_highlights_match_the_gap_map(client: TestClient) -> None:
    data = _search(client, _family()).data
    ranked = [*data.results, *data.near_misses]
    assert ranked, "no ranked zone on fixtures"
    for zone in ranked:
        for highlight in zone.gap_highlights:
            params = {"level": zone.zone.level.value, "row": highlight.row.value}
            gap_map = client.get("/api/v1/gaps", params=params).json()["data"]
            status = {z["code"]: z["status"] for z in gap_map["zones"]}[zone.zone.code]
            assert highlight.status == status


def test_invalid_scenario_is_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/search", json={"budget": {"kind": "rent", "amount_eur": 5}})
    assert response.status_code == 422


AJALVIR = "28002"  # a fixture municipio without a published appraised value
_SEED_PRICE = text(
    "UPDATE feature_value SET value = :value, null_reason = :reason, confidence = :confidence "
    "WHERE feature_id = 'valor_tasado_vivienda_m2' AND territory_level = 'municipio' "
    "AND territory_code = :code"
)


def test_a_published_appraised_value_scores_buying(
    client: TestClient, migrated_engine: Engine
) -> None:
    """D-227 through the API: with a value, buying is PASS or FAIL on value x m² and cites the
    dataset; the explanation reads the purchase value to buy and the rent to rent."""
    from hi_api.services.explanation import explain_zone
    from hi_contracts.catalog.enums import TerritoryLevel
    from hi_contracts.public import ScenarioState

    seed = {"value": 3000.0, "reason": None, "confidence": 0.8, "code": AJALVIR}
    with migrated_engine.begin() as conn:
        assert conn.execute(_SEED_PRICE, seed).rowcount == 1
    try:
        buy = _family() | {"budget": {"kind": "buy", "amount_eur": 300000}, "nearby": []}
        data = _search(client, buy).data
        card = next(z for z in data.results if z.zone.code == AJALVIR)
        budget = next(c for c in card.constraints if c.constraint_id == "budget")
        assert budget.status == "PASS"
        assert budget.value == card.estimated_cost_eur == 231000  # 3.000 €/m² × 77 m²
        assert "cm_valor_tasado_vivienda_municipios" in {d.dataset_id for d in data.datasets}
        tight = buy | {"budget": {"kind": "buy", "amount_eur": 200000}}
        zones = {z.zone.code: z for z in _search(client, tight).data.all_zones}
        assert zones[AJALVIR].failed_constraints == ["budget"]
        with migrated_engine.connect() as conn:
            to_buy, _, _ = explain_zone(
                conn, TerritoryLevel.MUNICIPIO, AJALVIR, ScenarioState.model_validate(buy)
            )
            to_rent, _, _ = explain_zone(
                conn, TerritoryLevel.MUNICIPIO, AJALVIR, ScenarioState.model_validate(_family())
            )
        assert "valor_tasado_vivienda_m2" in {i.feature_id for i in to_buy.indicators}
        assert "alquiler_m2_mensual" not in {i.feature_id for i in to_buy.indicators}
        assert "valor_tasado_vivienda_m2" not in {i.feature_id for i in to_rent.indicators}
    finally:
        restore = {"value": None, "reason": "SOURCE_MISSING", "confidence": 0.0, "code": AJALVIR}
        with migrated_engine.begin() as conn:
            conn.execute(_SEED_PRICE, restore)
