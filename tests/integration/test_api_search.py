"""POST /api/v1/search on the fixture database (CORE-003): contract, UNKNOWN never PASS,
Reality Check that the web can apply, highlights equal to GET /gaps and provenance."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.main import app
from hi_contracts.public.responses import SearchResponse

pytestmark = pytest.mark.db
FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "contracts"


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def _family() -> dict[str, Any]:
    """The demo case, with the place of work as a preference (no travel times yet)."""
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
    assert body.meta.methodology_version == data.methodology_version == "fit-0.1"
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
    scenario = _family() | {"budget": {"kind": "buy", "amount_eur": 300000}, "nearby": []}
    data = _search(client, scenario).data
    assert data.results == []
    assert data.reality_check.zones_passing == 0
    assert data.reality_check.zones_unknown == data.reality_check.zones_evaluated
    assert all(not z.passes_all for z in data.all_zones)
    option = data.reality_check.relaxations[0]
    assert option.constraint_id == "budget"
    assert option.relaxed_scenario.budget is None
    assert option.added_zones == data.reality_check.zones_evaluated


def test_trip_limits_are_unknown_and_say_why(client: TestClient) -> None:
    scenario = _family()
    scenario["anchors"][0]["max_minutes"] = 40
    body = _search(client, scenario)
    assert body.data.results == []
    assert any("travel time" in w for w in body.warnings)


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
