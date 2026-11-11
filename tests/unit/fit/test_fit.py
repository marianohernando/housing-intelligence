"""CORE-003 Residential Fit on synthetic zones: conditions, % of fit, facts, Reality Check.

Fixtures here are synthetic (FIXTURE): made-up zones and values, never shown in the demo.
"""

from itertools import pairwise

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from hi_contracts.catalog.enums import GapRowKey, NullReason, TerritoryLevel
from hi_contracts.public import (
    Anchor,
    Budget,
    BudgetKind,
    ConstraintStatus,
    FactKind,
    Household,
    IndicatorValue,
    NearbyNeed,
    NeedKey,
    PriorityKey,
    ScenarioState,
    ZoneRef,
)
from hi_domain.fit import (
    ZoneData,
    criteria,
    evaluate,
    rank_weights,
    walk_utility,
)
from hi_domain.reality_check import budget_step, relaxed
from hi_domain.search import highlight_rows, run_search

CASTELLANA = Anchor(label="Paseo de la Castellana (Azca)", lon=-3.693, lat=40.45)


def _value(feature: str, value: float | None, confidence: float = 1.0) -> IndicatorValue:
    return IndicatorValue(
        feature_id=feature,
        label=feature,
        value=value,
        unit="min",
        confidence=confidence if value is not None else 0.0,
        null_reason=None if value is not None else NullReason.SOURCE_NO_COVERAGE,
        level=TerritoryLevel.MUNICIPIO,
        datasets=["osm_red_peatonal"],
    )


def zone(
    code: str,
    rent: float | None = 12.0,
    colegio: float | None = 5.0,
    transporte: float | None = 3.0,
    lon: float = -3.70,
    lat: float = 40.42,
) -> ZoneData:
    walk = {NeedKey.COLEGIO: _value("min_a_pie_colegio", colegio)}
    walk[NeedKey.TRANSPORTE] = _value("min_a_pie_transporte", transporte)
    return ZoneData(
        zone=ZoneRef(
            level=TerritoryLevel.MUNICIPIO,
            code=code,
            name=f"Zona {code}",
            center_lon=lon,
            center_lat=lat,
        ),
        rent=_value("alquiler_m2_mensual", rent),
        walk=walk,
    )


def family(budget: int | Budget = 1500, **update: object) -> ScenarioState:
    if isinstance(budget, int):
        budget = Budget(kind=BudgetKind.RENT, amount_eur=budget)
    base = ScenarioState(
        budget=budget,
        household=Household(adults=2, minors=2, minor_ages=[4, 8]),
        anchors=[CASTELLANA],
        nearby=[NearbyNeed(need=NeedKey.COLEGIO, max_walk_minutes=10)],
        priorities=[PriorityKey.COLEGIOS, PriorityKey.TRANSPORTE, PriorityKey.SALUD],
    )
    return base.model_copy(update=update)


def test_rank_weights_follow_the_order_and_add_up_to_one() -> None:
    for n in range(1, 8):
        weights = rank_weights(n)
        assert sum(weights) == pytest.approx(1.0)
        assert all(a > b for a, b in pairwise(weights))


@given(st.floats(min_value=0, max_value=500), st.integers(min_value=1, max_value=60))
def test_walk_utility_saturates_and_never_grows_with_minutes(minutes: float, target: int) -> None:
    u = walk_utility(minutes, target)
    assert 0.0 <= u <= 1.0
    assert walk_utility(minutes + 1, target) <= u
    if minutes <= target:
        assert u == 1.0
    if minutes >= 3 * target:
        assert u == 0.0


def test_criteria_order_priorities_then_work_then_budget() -> None:
    keys = [c.key for c in criteria(family())]
    assert keys == ["need:colegio", "need:transporte", "need:centro_salud", "work:0", "budget"]


def test_unknown_never_passes_and_is_not_a_result() -> None:
    zones = [zone("1"), zone("2", rent=None), zone("3", colegio=None)]
    outcome = run_search(family(), zones)
    assert [r.zone.code for r in outcome.results] == ["1"]
    assert outcome.reality_check.zones_unknown == 2
    assert all(r.failed_constraints == [] for r in outcome.results)
    for match in outcome.all_zones:
        assert match.passes_all == (match.zone.code == "1")
        assert (match.match_pct is None) == (match.zone.code != "1")  # never painted as a fit


def test_failing_one_condition_is_a_near_miss_with_its_reason() -> None:
    zones = [zone("1"), zone("2", rent=30.0), zone("3", rent=30.0, colegio=40.0)]
    outcome = run_search(family(), zones)
    assert [z.zone.code for z in outcome.near_misses] == ["2"]
    assert outcome.near_misses[0].failed_constraints == ["budget"]


def test_match_is_the_weighted_mean_of_the_criteria_with_data() -> None:
    scenario = ScenarioState(priorities=[PriorityKey.COLEGIOS, PriorityKey.TRANSPORTE])
    fit = evaluate(scenario, zone("1", colegio=5.0, transporte=15.0))  # utilities 1 and 0
    assert fit.match_pct == 67  # weights 2/3 and 1/3


def test_a_criterion_without_data_lowers_confidence_not_the_match() -> None:
    scenario = ScenarioState(priorities=[PriorityKey.ZONAS_VERDES, PriorityKey.COLEGIOS])
    fit = evaluate(scenario, zone("1", colegio=5.0))
    assert fit.match_pct == 100
    assert fit.confidence == pytest.approx(1 / 3, abs=1e-3)  # rounded to 3 decimals
    assert fit.facts[-1].kind is FactKind.UNKNOWN
    assert fit.facts[-1].text.startswith("Zonas verdes")


def test_facts_are_three_to_five_with_known_ones_first() -> None:
    fit = evaluate(family(), zone("1", colegio=75.0))
    assert 3 <= len(fit.facts) <= 5
    assert "más de 60 min" in fit.facts[0].text
    kinds = [f.kind is FactKind.UNKNOWN for f in fit.facts]
    assert kinds == sorted(kinds)


def test_closer_to_work_ranks_higher_all_else_equal() -> None:
    near = zone("near", lon=-3.69, lat=40.46)
    far = zone("far", lon=-3.80, lat=40.25)
    outcome = run_search(family(), [far, near])
    assert [r.zone.code for r in outcome.results] == ["near", "far"]
    assert outcome.results[0].match_pct > outcome.results[1].match_pct


def test_commute_limit_is_unknown_until_travel_time_exists() -> None:
    scenario = family(anchors=[CASTELLANA.model_copy(update={"max_minutes": 40})])
    outcome = run_search(scenario, [zone("1"), zone("2")])
    assert outcome.results == []
    assert outcome.reality_check.zones_unknown == 2
    option = next(o for o in outcome.reality_check.relaxations if o.constraint_id == "commute:0")
    assert option.added_zones == 2
    assert option.relaxed_scenario.anchors[0].max_minutes is None


def test_purchase_budget_is_unknown_and_relaxing_drops_it() -> None:
    scenario = family(budget=Budget(kind=BudgetKind.BUY, amount_eur=300_000))
    outcome = run_search(scenario, [zone("1")])
    assert outcome.results == []
    assert outcome.reality_check.relaxations[0].relaxed_scenario.budget is None


def test_relaxations_step_budget_and_minutes() -> None:
    label, more = relaxed(family(budget=1500), "budget") or ("", family())
    assert more.budget is not None
    assert more.budget.amount_eur == 1500 + budget_step(1500) == 1650
    assert label == "+150 €/mes"
    _, walk = relaxed(family(), "near:colegio") or ("", family())
    assert walk.nearby[0].max_walk_minutes == 15
    at_limit = family(nearby=[NearbyNeed(need=NeedKey.COLEGIO, max_walk_minutes=60)])
    _, wish = relaxed(at_limit, "near:colegio") or ("", family())
    assert wish.nearby[0].required is False


zone_strategy = st.builds(
    zone,
    code=st.text(alphabet="0123456789", min_size=1, max_size=4),
    rent=st.one_of(st.none(), st.floats(min_value=8, max_value=25)),
    colegio=st.one_of(st.none(), st.floats(min_value=0, max_value=40)),
)


@settings(max_examples=60)
@given(st.lists(zone_strategy, min_size=1, max_size=12), st.integers(min_value=400, max_value=3000))
def test_relaxing_a_condition_never_removes_zones(zones: list[ZoneData], budget: int) -> None:
    check = run_search(family(budget=budget), zones).reality_check
    assert check.zones_passing + check.zones_unknown <= check.zones_evaluated
    for option in check.relaxations:
        assert option.added_zones >= 0
        assert option.zones_if_relaxed == check.zones_passing + option.added_zones


@settings(max_examples=60)
@given(st.lists(zone_strategy, min_size=1, max_size=12))
def test_every_result_passes_every_condition(zones: list[ZoneData]) -> None:
    outcome = run_search(family(), zones)
    for result in outcome.results:
        assert all(c.status is ConstraintStatus.PASS for c in result.constraints)
        assert 0 <= result.match_pct <= 100


def test_highlights_follow_the_household() -> None:
    assert highlight_rows(family()) == [
        GapRowKey.COLEGIO,
        GapRowKey.CENTRO_SALUD,
        GapRowKey.FARMACIA,
    ]
    baby = family(household=Household(adults=2, minors=1, minor_ages=[1]))
    assert highlight_rows(baby)[:2] == [GapRowKey.ESCUELA_INFANTIL, GapRowKey.COLEGIO]
    carer = family(household=Household(adults=1, seniors_in_care=1))
    assert highlight_rows(carer) == [GapRowKey.MAYORES, GapRowKey.CENTRO_SALUD, GapRowKey.FARMACIA]
