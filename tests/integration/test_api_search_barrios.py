"""POST /api/v1/search/barrios on the fixture database (D-232): the barrios of one Madrid
district ranked by the same engine as POST /search, with the district's trip as a declared
fallback and an unknown rent that says why."""

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from hi_api.deps import get_engine
from hi_api.main import app
from hi_api.services.barrios import DISTRICT_TRIP_NOTE
from hi_contracts.public.responses import BarrioSearchResponse
from hi_domain.fit import FIT_VERSION
from hi_features.commute import compute_commutes, persist
from hi_ingestion.catalog.loader import load_catalog

pytestmark = pytest.mark.db
FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "contracts"
CENTRO = "2807901"  # its sample barrios: Palacio (28079011) and Sol (28079016)


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def _family(limit: int | None = None) -> dict[str, Any]:
    scenario = json.loads((FIXTURES / "scenario_state.familia_castellana.fixture.json").read_text())
    for anchor in scenario["anchors"]:
        anchor["max_minutes"] = limit
    return scenario


def _search(client: TestClient, scenario: dict[str, Any], distrito: str = CENTRO) -> Any:
    return client.post("/api/v1/search/barrios", json={"scenario": scenario, "distrito": distrito})


def _barrios(client: TestClient, scenario: dict[str, Any]) -> BarrioSearchResponse:
    response = _search(client, scenario)
    assert response.status_code == 200, response.text
    return BarrioSearchResponse.model_validate(response.json())


def test_the_barrios_of_the_district_are_ranked_by_the_same_engine(client: TestClient) -> None:
    body = _barrios(client, _family())
    data = body.data
    assert body.meta.methodology_version == data.methodology_version == FIT_VERSION
    assert data.distrito.code == CENTRO and data.distrito.name == "Centro"
    assert {z.zone.code for z in data.all_zones} == {"28079011", "28079016"}
    assert {z.zone.name for z in data.all_zones} == {"Palacio", "Sol"}
    assert data.reality_check.zones_evaluated == 2
    for ranked in [*data.results, *data.near_misses]:
        assert ranked.gap_highlights == []  # «Qué falta» stays by district
        assert ranked.facts
        walk = [f for f in ranked.facts if f.indicator and f.indicator.level == "barrio"]
        assert walk, "the walking minutes are the barrio's own"
    assert any(d.dataset_id == "osm_red_peatonal" for d in data.datasets)


def test_a_barrio_without_rent_says_why_and_is_never_a_pass(client: TestClient) -> None:
    data = _barrios(client, _family()).data
    ranked = {r.zone.code: r for r in [*data.results, *data.near_misses]}
    unknown = [z for z in data.all_zones if not z.passes_all and not z.failed_constraints]
    for match in unknown:
        assert match.match_pct is None  # an UNKNOWN zone is never painted as a fit
    for code, zone in ranked.items():
        budget = next(c for c in zone.constraints if c.constraint_id == "budget")
        assert budget.status != "UNKNOWN", code  # ranked zones have a known rent


def test_an_unknown_district_is_404_and_a_bad_code_is_422(client: TestClient) -> None:
    missing = _search(client, _family(), "2807999")
    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "NOT_FOUND"
    assert _search(client, _family(), "2800101").status_code == 422  # not a Madrid district


def test_a_barrio_without_its_own_trip_takes_the_district_s_and_says_so(
    client: TestClient, migrated_engine: Engine
) -> None:
    """Before the barrio matrix is computed (or if a barrio is missing from it), the trip of
    its district stands in, with lower confidence and the fact saying so."""
    persist(migrated_engine, compute_commutes(migrated_engine, load_catalog()))
    free = _family() | {"budget": None, "nearby": []}  # no condition: both barrios rank
    own = _barrios(client, free).data
    assert len(own.results) == 2
    with migrated_engine.begin() as conn:
        conn.execute(text("DELETE FROM commute_time WHERE origin_admin_unit_id LIKE 'ES.28.BAR.%'"))
    try:
        body = _barrios(client, free)
        trips = [
            f
            for r in [*body.data.results, *body.data.near_misses]
            for f in r.facts
            if f.topic == "trayecto"
        ]
        assert trips and all(DISTRICT_TRIP_NOTE in f.text for f in trips)
        assert any("for the whole district" in w for w in body.warnings)
        assert not any(
            DISTRICT_TRIP_NOTE in f.text for r in [*own.results, *own.near_misses] for f in r.facts
        )
    finally:
        with migrated_engine.begin() as conn:
            conn.execute(text("DELETE FROM commute_time"))
            conn.execute(text("DELETE FROM transit_hub"))


def test_barrios_buy_with_an_estimate_anchored_to_their_district(client: TestClient) -> None:
    """D-234: buying works by barrio too: each barrio has its estimated price, said as an
    estimate «del barrio», and a tight budget fails instead of staying unknown."""
    buy = _family() | {"budget": {"kind": "buy", "amount_eur": 5000000}, "nearby": []}
    data = _barrios(client, buy).data
    assert {r.zone.code for r in data.results} == {"28079011", "28079016"}
    for ranked in data.results:
        budget = next(c for c in ranked.constraints if c.constraint_id == "budget")
        assert budget.status == "PASS" and budget.confidence == 0.5
        assert "precio estimado: valor tasado de Madrid" in budget.explanation
        assert "valor catastral del barrio" in budget.explanation
    tight = buy | {"budget": {"kind": "buy", "amount_eur": 100000}}
    zones = _barrios(client, tight).data.all_zones
    assert all(z.failed_constraints == ["budget"] for z in zones)
