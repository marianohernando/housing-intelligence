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


def test_rent_says_it_is_the_rent_of_a_lease_signed_in_2024(client: TestClient) -> None:
    """D-228: the budget condition and the cost fact use the rent of new leases and say so
    with the note that travels with the rent feature (`fit.note`), and cite the AEAT table."""
    data = _search(client, _family()).data
    budget = [
        c
        for z in [*data.results, *data.near_misses]
        for c in z.constraints
        if c.constraint_id == "budget" and c.value is not None
    ]
    assert budget
    assert all("contratos firmados en 2024" in c.explanation for c in budget)
    assert all("vigentes" not in c.explanation for c in budget)
    cited = {d.dataset_id: d for d in data.datasets}
    assert "aeat_alquiler_nuevos_contratos_codigo_postal" in cited
    assert cited["aeat_alquiler_nuevos_contratos_codigo_postal"].is_cm_open_data is False


LA_ACEBEDA = "28001"  # Sierra Norte: a village (D-238)


def _zones(client: TestClient, scope: str | None) -> dict[str, str]:
    """Code and level of every zone the search evaluates in a scope (None: not sent)."""
    scenario = _family() if scope is None else _family() | {"scope": scope}
    data = _search(client, scenario).data
    assert data.reality_check.zones_evaluated == len(data.all_zones)
    assert data.scenario.scope == (scope or "all")
    return {z.zone.code: z.zone.level.value for z in data.all_zones}


def test_a_search_without_scope_is_the_whole_region_as_before(client: TestClient) -> None:
    """D-238: the example and every shared link send no scope and must not change."""
    plain = _search(client, _family()).data
    explicit = _search(client, _family() | {"scope": "all"}).data
    assert plain.model_dump(exclude={"scenario"}) == explicit.model_dump(exclude={"scenario"})
    assert set(_zones(client, None).values()) == {"municipio", "distrito"}


def test_surroundings_and_villages_split_the_municipios_outside_madrid(
    client: TestClient,
) -> None:
    everywhere = _zones(client, None)
    around, villages = _zones(client, "alrededores"), _zones(client, "pueblos")
    assert around == {AJALVIR: "municipio"}  # Este Metropolitano
    assert villages == {LA_ACEBEDA: "municipio"}
    municipios = {code for code, level in everywhere.items() if level == "municipio"}
    assert set(around) | set(villages) == municipios


def test_madrid_capital_is_ranked_by_barrio(client: TestClient) -> None:
    everywhere = _zones(client, None)
    capital = _zones(client, "madrid")
    assert capital and set(capital.values()) == {"barrio"}
    districts = {code for code, level in everywhere.items() if level == "distrito"}
    assert {code[:7] for code in capital} <= districts  # each barrio inside a ranked district
    assert {"28079011", "28079016"} <= set(capital)  # Palacio and Sol
    data = _search(client, _family() | {"scope": "madrid"}).data
    for ranked in [*data.results, *data.near_misses]:
        assert ranked.gap_highlights == []  # «Qué falta» stays by district (D-232)
        assert ranked.zone.municipio_ine == "28079"


def test_a_relaxed_scenario_keeps_its_scope(client: TestClient) -> None:
    scenario = _family() | {"budget": {"kind": "rent", "amount_eur": 600}, "scope": "madrid"}
    check = _search(client, scenario).data.reality_check
    assert check.relaxations
    for option in check.relaxations:
        assert option.relaxed_scenario.scope == "madrid"
        again = _search(client, option.relaxed_scenario.model_dump(mode="json")).data
        assert again.reality_check.zones_passing == option.zones_if_relaxed
        assert {z.zone.level.value for z in again.all_zones} == {"barrio"}
