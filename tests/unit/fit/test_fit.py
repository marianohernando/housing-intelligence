"""CORE-003 Residential Fit on synthetic zones: conditions, % of fit, facts, Reality Check.

Fixtures here are synthetic (FIXTURE): made-up zones and values, never shown in the demo.
"""

from dataclasses import replace
from itertools import pairwise
from random import Random

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from hi_contracts.catalog.enums import GapRowKey, NullReason, TerritoryLevel
from hi_contracts.public import (
    Anchor,
    Budget,
    BudgetKind,
    ConstraintCheck,
    ConstraintStatus,
    FactKind,
    FactTopic,
    Household,
    IndicatorValue,
    NearbyNeed,
    NeedKey,
    PriorityKey,
    ScenarioState,
    ZoneRef,
)
from hi_domain.affordability import FloorArea
from hi_domain.fit import (
    Commute,
    ZoneData,
    about_minutes,
    as_pct,
    cost_fact,
    criteria,
    evaluate,
    everyday_walk,
    rank_weights,
    ranking_key,
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
    price: float | None = None,
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
        price=None if price is None else _value("valor_tasado_vivienda_m2", price, 0.8),
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


def test_the_walk_condition_says_the_zone_median_without_streets_jargon() -> None:
    evaluation = evaluate(family(), zone("1", colegio=6.4))
    check = next(c for c in evaluation.constraints if c.constraint_id == "near:colegio")
    assert check.explanation == (
        "A unos 6 min andando de un colegio con primaria (lo que tarda la mitad de la zona)"
    )


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


def test_commute_limit_is_unknown_without_travel_time() -> None:
    scenario = family(anchors=[CASTELLANA.model_copy(update={"max_minutes": 40})])
    outcome = run_search(scenario, [zone("1"), zone("2")])
    assert outcome.results == []
    assert outcome.reality_check.zones_unknown == 2
    option = next(o for o in outcome.reality_check.relaxations if o.constraint_id == "commute:0")
    assert option.added_zones == 2
    assert option.relaxed_scenario.anchors[0].max_minutes is None


BUY_300K = Budget(kind=BudgetKind.BUY, amount_eur=300_000)


def test_purchase_scores_with_the_appraised_value_and_unknown_never_passes() -> None:
    """DATA-021 (D-227): 77 m² for a family of four; 3.000 €/m² fits 300.000 €, 4.500 does
    not and a zone without a published price is UNKNOWN, never a result."""
    scenario = family(budget=BUY_300K, anchors=[])
    outcome = run_search(
        scenario, [zone("1", price=3000.0), zone("2", price=4500.0), zone("3", price=None)]
    )
    assert [r.zone.code for r in outcome.results] == ["1"]
    card = outcome.results[0]
    assert card.estimated_cost_eur == 231_000
    budget = next(c for c in card.constraints if c.constraint_id == "budget")
    assert budget.status is ConstraintStatus.PASS
    cost = next(f for f in card.facts if f.topic is FactTopic.COSTE)
    assert "valor tasado" in cost.text
    by_code = {z.zone.code: z for z in outcome.all_zones}
    assert by_code["2"].failed_constraints == ["budget"]
    assert by_code["3"].match_pct is None and not by_code["3"].passes_all
    assert outcome.reality_check.zones_unknown == 1


def test_a_purchase_budget_relaxes_by_ten_percent_in_thousands() -> None:
    label, more = relaxed(family(budget=BUY_300K), "budget") or ("", family())
    assert more.budget is not None
    assert more.budget.kind is BudgetKind.BUY
    assert more.budget.amount_eur == 330_000
    assert label == "+30.000 €"
    top = Budget(kind=BudgetKind.BUY, amount_eur=5_000_000)
    assert relaxed(family(budget=top), "budget") is None
    odd_budget = Budget(kind=BudgetKind.BUY, amount_eur=305_000)
    label, odd = relaxed(family(budget=odd_budget), "budget") or ("", family())
    assert odd.budget is not None and odd.budget.amount_eur == 345_000  # rounded up to 10.000
    assert label == "+40.000 €"
    near = Budget(kind=BudgetKind.BUY, amount_eur=4_990_000)
    _, capped = relaxed(family(budget=near), "budget") or ("", family())
    assert capped.budget is not None and capped.budget.amount_eur == 5_000_000


def test_the_estimated_cost_is_the_price_to_buy_and_the_rent_otherwise() -> None:
    priced = zone("1", rent=12.0, price=3000.0)
    assert evaluate(family(budget=BUY_300K, anchors=[]), priced).cost_eur == 231_000
    assert evaluate(family(budget=BUY_300K, anchors=[]), zone("2", rent=12.0)).cost_eur is None
    no_budget = family(anchors=[]).model_copy(update={"budget": None})
    assert evaluate(no_budget, priced).cost_eur == 924  # 12 €/m² × 77 m²


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
    price=st.one_of(st.none(), st.floats(min_value=1500, max_value=9000)),
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


scenario_strategy = st.builds(
    lambda budget, buy, minutes, required, limit: family(
        budget=Budget(kind=BudgetKind.BUY, amount_eur=300_000) if buy else budget,
        nearby=[NearbyNeed(need=NeedKey.COLEGIO, max_walk_minutes=minutes, required=required)],
        anchors=[CASTELLANA.model_copy(update={"max_minutes": limit})],
    ),
    budget=st.sampled_from([400, 1500, 19_000, 20_000]),
    buy=st.booleans(),
    minutes=st.sampled_from([5, 10, 58, 60]),
    required=st.booleans(),
    limit=st.sampled_from([None, 40]),
)


@settings(max_examples=80)
@given(st.lists(zone_strategy, min_size=1, max_size=8), scenario_strategy)
def test_every_relaxation_is_valid_and_keeps_every_passing_zone(
    zones: list[ZoneData], scenario: ScenarioState
) -> None:
    outcome = run_search(scenario, zones)
    before = {z.zone.code for z in outcome.all_zones if z.passes_all}
    for option in outcome.reality_check.relaxations:
        again = ScenarioState.model_validate(option.relaxed_scenario.model_dump())
        after = run_search(again, zones)
        assert before <= {z.zone.code for z in after.all_zones if z.passes_all}
        assert after.reality_check.zones_passing == option.zones_if_relaxed


def test_zones_passing_without_data_to_score_are_counted_not_ranked() -> None:
    scenario = ScenarioState(priorities=[PriorityKey.ZONAS_VERDES])
    outcome = run_search(scenario, [zone("1")])
    assert outcome.results == []
    assert outcome.unscored_passing == 1
    assert outcome.all_zones[0].passes_all
    assert outcome.all_zones[0].match_pct is None


def test_facts_never_exceed_five_with_many_criteria() -> None:
    scenario = family(
        priorities=list(PriorityKey),
        nearby=[NearbyNeed(need=n, required=False) for n in NeedKey],
    )
    fit = evaluate(scenario, zone("1"))
    assert len(fit.facts) == 5
    assert fit.facts[0].text.startswith("Parada")  # transporte is the first priority


def _with_transit(base: ZoneData, bus: float | None = None, metro: float | None = None) -> ZoneData:
    transit = {
        mode: _value(f"min_a_pie_{mode}", minutes)
        for mode, minutes in (("bus", bus), ("metro", metro))
        if minutes is not None
    }
    return replace(base, transit=transit)


def _transport_text(zone_data: ZoneData) -> str:
    fit = evaluate(family(), zone_data)
    return next(f.text for f in fit.facts if f.topic is FactTopic.TRANSPORTE)


def test_transport_fact_says_the_bus_and_the_metro_apart() -> None:
    """D-233: both features, two parts; one of them, only that one; none, the text of always."""
    base = zone("1", transporte=2.0)
    assert _transport_text(_with_transit(base, bus=2.2, metro=8.4)) == (
        "Parada de autobús a unos 2 min andando · Metro o Cercanías a unos 8 min"
    )
    assert _transport_text(_with_transit(base, bus=2.2)) == "Parada de autobús a unos 2 min andando"
    assert _transport_text(_with_transit(base, metro=8.4)) == (
        "Metro o Cercanías a unos 8 min andando"
    )
    assert _transport_text(base) == "Parada de transporte público a unos 2 min andando"


def test_transport_fact_leaves_out_a_metro_that_is_not_a_walk() -> None:
    """A village's nearest Metro is in another town: beyond what is shown it is not a walk."""
    base = zone("1", transporte=5.7)
    assert _transport_text(_with_transit(base, bus=5.7, metro=93.4)) == (
        "Parada de autobús a unos 6 min andando"
    )
    unknown = replace(base, transit={"bus": _value("min_a_pie_bus", None)})
    assert _transport_text(unknown) == "Parada de transporte público a unos 6 min andando"


def test_transport_fact_keeps_the_walking_indicator_the_web_looks_for() -> None:
    fit = evaluate(family(), _with_transit(zone("1"), bus=2.0, metro=8.0))
    fact = next(f for f in fit.facts if f.topic is FactTopic.TRANSPORTE)
    assert fact.indicator is not None
    assert fact.indicator.feature_id == "min_a_pie_transporte"


def test_the_transit_by_mode_never_moves_the_score() -> None:
    """D-233: the transport need scores with min_a_pie_transporte; the modes only word the fact."""
    plain = zone("1", transporte=11.0)
    modes = _with_transit(plain, bus=30.0, metro=1.0)
    before, after = evaluate(family(), plain), evaluate(family(), modes)
    assert after.utility == before.utility
    assert after.match_pct == before.match_pct
    assert after.confidence == before.confidence
    assert after.constraints == before.constraints
    assert [f.kind for f in after.facts] == [f.kind for f in before.facts]


def test_match_rounds_half_up() -> None:
    assert as_pct(0.005) == 1
    assert as_pct(0.125) == 13
    assert as_pct(None) is None


def with_commute(data: ZoneData, minutes: float | None, confidence: float = 0.7) -> ZoneData:
    trip = Commute(minutes=minutes, confidence=confidence)
    return ZoneData(data.zone, data.rent, data.walk, data.gaps, commute={0: trip})


def test_commute_limit_passes_or_fails_on_public_transport_minutes() -> None:
    scenario = family(anchors=[CASTELLANA.model_copy(update={"max_minutes": 40})])
    zones = {
        "1": with_commute(zone("1"), 35.0),
        "2": with_commute(zone("2"), 52.0),
        "3": with_commute(zone("3"), None),
    }

    def commute(data: ZoneData) -> ConstraintCheck:
        return next(
            c for c in evaluate(scenario, data).constraints if c.constraint_id == "commute:0"
        )

    assert {code: commute(data).status for code, data in zones.items()} == {
        "1": ConstraintStatus.PASS,
        "2": ConstraintStatus.FAIL,
        "3": ConstraintStatus.UNKNOWN,  # no trip by 9:00 is never a pass
    }
    assert commute(zones["1"]).value == 35.0
    assert "35 min en transporte público" in commute(zones["1"]).explanation
    outcome = run_search(scenario, list(zones.values()))
    assert [r.zone.code for r in outcome.results] == ["1"]


def test_fewer_minutes_by_public_transport_beat_a_shorter_straight_line() -> None:
    """Near in a straight line but badly connected loses to a farther zone on the metro."""
    near_badly_served = with_commute(zone("near", lon=-3.69, lat=40.46), 70.0)
    far_on_the_metro = with_commute(zone("far", lon=-3.80, lat=40.25), 25.0)
    outcome = run_search(family(), [near_badly_served, far_on_the_metro])
    assert [r.zone.code for r in outcome.results] == ["far", "near"]
    facts = [f.text for f in outcome.results[0].facts]
    assert any("25 min en transporte público" in t for t in facts)


def test_a_zone_that_cannot_arrive_by_9_scores_the_worst_on_work_but_its_limit_is_unknown() -> None:
    """Measured with the published timetables, not missing; but they have gaps (D-220)."""
    stranded = with_commute(zone("s"), None, confidence=0.5)
    connected = with_commute(zone("c"), 30.0)
    outcome = run_search(family(), [stranded, connected])
    assert [r.zone.code for r in outcome.results] == ["c", "s"]
    work = [f for f in outcome.results[1].facts if f.topic.value == "trayecto"]
    assert work and work[0].kind is FactKind.WEAKNESS
    limit = family(anchors=[CASTELLANA.model_copy(update={"max_minutes": 40})])
    check = next(c for c in evaluate(limit, stranded).constraints if c.constraint_id == "commute:0")
    assert check.status is ConstraintStatus.UNKNOWN


def test_ties_go_to_fewer_minutes_then_to_the_zone_id() -> None:
    """Same % and confidence: the shorter trip first, then a fixed id (the demo never reorders)."""
    a = with_commute(zone("2807915"), 33.0)
    b = with_commute(zone("2807916"), 32.0)
    c = with_commute(zone("2807901"), 32.0)
    plain = [zone("2807915"), zone("2807916"), zone("2807901")]
    outcome = run_search(family(anchors=[]), plain)  # everything equal: the zone id decides
    assert [r.zone.code for r in outcome.results] == ["2807901", "2807915", "2807916"]
    tied = run_search(family(), [a, b, c])
    assert [r.zone.code for r in tied.results][:2] == ["2807901", "2807916"]


WALKS = {
    NeedKey.ESCUELA_INFANTIL: 6.0,
    NeedKey.COLEGIO: 5.0,
    NeedKey.CENTRO_SALUD: 9.0,
    NeedKey.FARMACIA: 4.0,
    NeedKey.MAYORES: 8.0,
    NeedKey.TRANSPORTE: 3.0,
}
# D-239, the case of the user test: so much budget that every zone scores 100 %, nothing marked.
PLENTY = ScenarioState(
    budget=Budget(kind=BudgetKind.RENT, amount_eur=10_000), household=Household(adults=2)
)


def served(code: str, **minutes: float | None) -> ZoneData:
    """A zone with every everyday service inside its window, except what `minutes` says."""
    base = zone(code)
    walks = WALKS | {NeedKey(need): value for need, value in minutes.items()}
    walk = {n: _value(f"min_a_pie_{n.value}", m) for n, m in walks.items() if m is not None}
    return ZoneData(zone=base.zone, rent=base.rent, walk=walk)


def _codes(scenario: ScenarioState, zones: list[ZoneData]) -> list[str]:
    return [r.zone.code for r in run_search(scenario, zones).results]


def test_an_exact_tie_goes_to_the_zone_with_more_everyday_services_at_a_walk() -> None:
    """Nobody marked the pharmacy or the day centre, and they still tell the zones apart: the
    order of a tie is no longer the INE code (alphabetical), D-239."""
    village = served("28001", farmacia=28.0, mayores=45.0)
    town = served("28002", mayores=20.0)
    city = served("28003")
    fits = [evaluate(PLENTY, z) for z in (village, town, city)]
    assert {f.utility for f in fits} == {1.0}  # an exact tie, before any rounding
    assert _codes(PLENTY, [village, town, city]) == ["28003", "28002", "28001"]


def test_zones_equally_served_go_by_fewer_walking_minutes_then_as_before() -> None:
    close = served("28003", farmacia=2.0)
    closer = served("28004", farmacia=1.0, colegio=2.0)
    assert everyday_walk(close) == (1.0, pytest.approx(5.5))
    assert _codes(PLENTY, [served("28002"), close, closer, served("28001")]) == [
        "28004",
        "28003",
        "28001",  # same services at the same minutes: the fixed id, as before D-239
        "28002",
    ]


def test_a_zone_without_walking_data_goes_after_the_ties_that_have_it() -> None:
    unknown = ZoneData(zone=zone("28001").zone, rent=zone("28001").rent)
    assert everyday_walk(unknown) is None
    assert _codes(PLENTY, [unknown, served("28002", farmacia=40.0)]) == ["28002", "28001"]


def test_the_tie_break_never_outranks_a_better_fit_however_small() -> None:
    """Only exact ties of the unrounded fit: 97.6 % and 98.4 % both read 98 %, and the worse
    served zone still goes first."""
    scenario = PLENTY.model_copy(update={"priorities": [PriorityKey.TRANSPORTE]})
    worse_served = served("28001", farmacia=30.0, mayores=30.0, transporte=5.1)
    better_served = served("28002", transporte=5.2)
    first, second = (evaluate(scenario, z) for z in (worse_served, better_served))
    assert first.match_pct == second.match_pct and (first.utility or 0) > (second.utility or 0)
    assert _codes(scenario, [better_served, worse_served]) == ["28001", "28002"]


def test_near_misses_keep_breaking_ties_by_confidence_not_by_walks() -> None:
    """«Casi encajan» (D-239): every near miss fails something, so an exact tie there still
    goes to the surer figure, as before; the services at a walk only order «Zonas que encajan».
    The demo's near misses (five at 93 %) keep the order the pitch reads."""
    poor = PLENTY.model_copy(update={"budget": Budget(kind=BudgetKind.RENT, amount_eur=300)})
    unsure_rent = _value("alquiler_m2_mensual", 12.0, confidence=0.8)
    better_served = replace(served("28001"), rent=unsure_rent)
    surer = served("28002", farmacia=28.0, mayores=45.0)
    fits = [evaluate(poor, z) for z in (better_served, surer)]
    assert all(f.failed == ["budget"] for f in fits)
    assert fits[0].utility == fits[1].utility and fits[0].confidence < fits[1].confidence
    outcome = run_search(poor, [better_served, surer])
    assert [r.zone.code for r in outcome.near_misses] == ["28002", "28001"]
    assert sorted(fits, key=ranking_key)[0].data.zone.code == "28001"  # «Zonas que encajan»


@settings(max_examples=60)
@given(st.lists(zone_strategy, min_size=2, max_size=10, unique_by=lambda z: z.zone.code))
def test_without_exact_ties_the_order_is_the_fit_alone(zones: list[ZoneData]) -> None:
    """The demo case has no exact tie in its top 10, so D-239 cannot move it: with different
    unrounded fits the order is the one of the fit, whatever the walks say."""
    fits = [f for z in zones if (f := evaluate(family(), z)).utility is not None]
    ordered = sorted(fits, key=ranking_key)
    assert all(a.utility >= b.utility for a, b in pairwise(ordered))  # type: ignore[operator]


@settings(max_examples=40)
@given(
    st.lists(zone_strategy, min_size=2, max_size=10, unique_by=lambda z: z.zone.code), st.randoms()
)
def test_the_ranking_never_depends_on_the_order_zones_arrive_in(
    zones: list[ZoneData], rng: Random
) -> None:
    shuffled = list(zones)
    rng.shuffle(shuffled)
    first = [r.zone.code for r in run_search(family(), zones).results]
    again = [r.zone.code for r in run_search(family(), shuffled).results]
    assert first == again


def _park_zone(minutes: float | None) -> ZoneData:
    base = zone("1")
    park = {PriorityKey.ZONAS_VERDES: _value("min_a_pie_parque", minutes)}
    return ZoneData(zone=base.zone, rent=base.rent, walk=base.walk, priority_walk=park)


GREEN = ScenarioState(priorities=[PriorityKey.ZONAS_VERDES])


def test_green_areas_score_the_walk_to_an_urban_park() -> None:
    """D-222: utility 1 up to 10 minutes to the edge of a park of 1 ha, 0 at 30."""
    near = evaluate(GREEN, _park_zone(4.0))
    assert near.match_pct == 100
    assert near.facts[0].kind is FactKind.STRENGTH
    assert near.facts[0].text == "Parque urbano a unos 4 min andando"
    middle = evaluate(GREEN, _park_zone(20.0))
    assert middle.match_pct == 50
    assert middle.facts[0].kind is FactKind.WEAKNESS


def test_without_an_urban_park_at_a_walk_green_areas_say_the_countryside_is_not_measured() -> None:
    """D-222 §7: beyond 30 minutes there is no urban park at a walk. It scores 0 like any walk
    beyond its range (an UNKNOWN would let a village with no park outrank a town with one at 25
    minutes), with low confidence and a fact that says the countryside is not measured."""
    far = evaluate(GREEN, _park_zone(45.0))
    assert far.match_pct == 0
    green = next(f for f in far.facts if f.topic is FactTopic.ZONAS_VERDES)
    assert green.kind is FactKind.WEAKNESS
    assert green.text == "Sin parque urbano de 1 ha o más a un paseo (el campo no cuenta)"
    assert green.confidence <= 0.5
    assert green.indicator is None  # no minutes in the text, so no walk indicator (hasWalkingFact)
    near = next(
        f for f in evaluate(GREEN, _park_zone(20.0)).facts if f.topic is FactTopic.ZONAS_VERDES
    )
    assert near.indicator is not None and near.indicator.feature_id == "min_a_pie_parque"
    missing = evaluate(GREEN, _park_zone(None))
    assert missing.match_pct is None
    green = next(f for f in missing.facts if f.topic is FactTopic.ZONAS_VERDES)
    assert green.kind is FactKind.UNKNOWN
    assert green.text == "Zonas verdes: sin datos de distancia a pie en esta zona"


@settings(max_examples=200, deadline=None)
@given(
    st.floats(min_value=0, max_value=400),
    st.floats(min_value=0, max_value=400),
    st.floats(min_value=0, max_value=1),
)
def test_a_farther_park_never_raises_the_match(a: float, b: float, transporte: float) -> None:
    """All else equal, more minutes to the park never rank a zone higher (D-222 §7)."""
    near, far = sorted((a, b))
    scenario = ScenarioState(priorities=[PriorityKey.ZONAS_VERDES, PriorityKey.TRANSPORTE])

    def utility(minutes: float) -> float | None:
        base = _park_zone(minutes)
        walk = dict(base.walk) | {NeedKey.TRANSPORTE: _value("t", 5.0 + 10.0 * transporte)}
        zone_data = ZoneData(
            zone=base.zone, rent=base.rent, walk=walk, priority_walk=base.priority_walk
        )
        return evaluate(scenario, zone_data).utility

    near_u, far_u = utility(near), utility(far)
    assert near_u is not None and far_u is not None
    assert near_u >= far_u


def _step_free_zone(minutes: float | None) -> ZoneData:
    base = zone("1")
    station = {PriorityKey.SIN_ESCALERAS: _value("min_a_pie_estacion_sin_escaleras", minutes)}
    return ZoneData(zone=base.zone, rent=base.rent, walk=base.walk, priority_walk=station)


STEP_FREE = ScenarioState(priorities=[PriorityKey.SIN_ESCALERAS])


def test_step_free_scores_the_walk_to_an_accessible_station() -> None:
    """D-223: «sin escaleras» (opt-in) reads the minutes to a metro, Metro Ligero or Cercanías
    station that the CRTM grades as fully accessible: 1 up to 10 minutes, 0 at 30."""
    near = evaluate(STEP_FREE, _step_free_zone(6.0))
    assert near.match_pct == 100
    assert near.facts[0].kind is FactKind.STRENGTH
    assert near.facts[0].topic is FactTopic.ACCESIBILIDAD
    assert near.facts[0].text == (
        "Estación de metro o tren accesible (sin escaleras) a unos 6 min andando"
    )
    assert evaluate(STEP_FREE, _step_free_zone(20.0)).match_pct == 50


def test_without_an_accessible_station_at_a_walk_step_free_says_buses_are_not_measured() -> None:
    far = evaluate(STEP_FREE, _step_free_zone(45.0))
    assert far.match_pct == 0
    fact = next(f for f in far.facts if f.topic is FactTopic.ACCESIBILIDAD)
    assert fact.kind is FactKind.WEAKNESS
    assert fact.text == (
        "Sin estación de metro o tren accesible a un paseo (no mide autobuses, aceras ni portales)"
    )
    assert fact.confidence <= 0.5
    missing = evaluate(STEP_FREE, _step_free_zone(None))
    fact = next(f for f in missing.facts if f.topic is FactTopic.ACCESIBILIDAD)
    assert fact.kind is FactKind.UNKNOWN
    assert fact.text == "Sin escaleras: sin datos de distancia a pie en esta zona"


def test_security_never_scores_and_says_so() -> None:
    """D-224, D-226: no official measure of safety for whoever lives in each zone; the fact
    no longer promises data and the priority never counts as 0."""
    outcome = evaluate(ScenarioState(priorities=[PriorityKey.SEGURIDAD]), zone("1"))
    assert [f.text for f in outcome.facts if f.kind is FactKind.UNKNOWN] == [
        "Seguridad: no la puntuamos (no hay un dato oficial que la mida para quien vive en "
        "cada zona)"
    ]
    assert outcome.match_pct is None


@pytest.mark.parametrize(
    ("minutes", "text"),
    [(0.4, "1 min o menos"), (1.4, "1 min o menos"), (9.2, "unos 9 min"), (75.0, "más de 60 min")],
)
def test_walking_minutes_read_as_approximate(minutes: float, text: str) -> None:
    """Fase de mejora (D's texts): «a unos 9 min andando»; the median is explained once on the
    web («unos vecinos lo tienen más cerca y otros más lejos»), not in every fact."""
    assert about_minutes(minutes) == text


def test_rent_fact_says_what_the_figure_is_from_the_data() -> None:
    """D-228: the note comes with the rent feature (`fit.note`); without it, the old mean of
    the leases in force, so new code on old data never mislabels the number."""
    area = FloorArea(77, from_household=True)
    rent = _value("alquiler_m2_mensual", 16.5)
    new = cost_fact(
        rent, area, 1500.0, "contratos firmados en 2024; un anuncio de hoy puede pedir más"
    )
    assert new.fact.text == (
        "Alquiler ≈ 1.270 €/mes por 77 m² (16,5 €/m², contratos firmados en 2024; un anuncio "
        "de hoy puede pedir más)"
    )
    old = cost_fact(rent, area, 1500.0)
    assert old.fact.text.startswith("Alquiler medio ≈ 1.270 €/mes")
    assert old.fact.text.endswith("media de los contratos vigentes; uno nuevo suele costar más)")


# D-232 (fit-0.7): the search inside a district ranks its barrios with the same engine.
def test_a_trip_measured_for_the_whole_district_says_so() -> None:
    """A barrio without its own trip takes its district's: the fact and the condition say it
    in plain words, and the lower confidence travels with them."""
    note = "trayecto medido para todo el distrito"
    trip = Commute(minutes=35.0, confidence=0.56, note=note)
    barrio = ZoneData(zone("b").zone, zone("b").rent, zone("b").walk, commute={0: trip})
    fit = evaluate(family(), barrio)  # the place of work as a preference
    work = next(f for f in fit.facts if f.topic is FactTopic.TRAYECTO)
    assert work.text.startswith("35 min en transporte público")
    assert work.text.endswith(f"({note})")
    assert work.confidence == pytest.approx(0.56)
    own = evaluate(family(), with_commute(zone("o"), 35.0))
    assert not any(note in f.text for f in own.facts if f.topic is FactTopic.TRAYECTO)


@pytest.mark.parametrize("minutes", [35.0, 52.0, None])
def test_a_borrowed_trip_never_decides_a_trip_limit(minutes: float | None) -> None:
    """The district's trip says nothing sure about one of its barrios: under a hard limit it
    is UNKNOWN, never PASS or FAIL (UNKNOWN is never a pass nor an explicit alternative)."""
    scenario = family(anchors=[CASTELLANA.model_copy(update={"max_minutes": 40})])
    note = "trayecto medido para todo el distrito"
    trip = Commute(minutes=minutes, confidence=0.56, note=note)
    barrio = ZoneData(zone("b").zone, zone("b").rent, zone("b").walk, commute={0: trip})
    check = next(
        c for c in evaluate(scenario, barrio).constraints if c.constraint_id == "commute:0"
    )
    assert check.status is ConstraintStatus.UNKNOWN
    assert check.explanation.endswith(f"({note})")


def test_an_unknown_rent_gives_the_reason_the_data_has_for_it() -> None:
    """Without rent the budget is UNKNOWN; a barrio with no place carrying a postcode says
    why in plain words instead of the generic «the source only publishes…»."""
    why = "Sin datos de alquiler para este barrio: ningún lugar del barrio lleva código postal"
    base = zone("s", rent=None)
    barrio = ZoneData(base.zone, base.rent, base.walk, rent_missing=why)
    fit = evaluate(family(), barrio)
    budget = next(c for c in fit.constraints if c.constraint_id == "budget")
    assert budget.status is ConstraintStatus.UNKNOWN
    assert budget.explanation == why
    cost = next(f for f in fit.facts if f.topic is FactTopic.COSTE)
    assert cost.kind is FactKind.UNKNOWN and cost.text == why
    plain = evaluate(family(), zone("m", rent=None))
    generic = next(c for c in plain.constraints if c.constraint_id == "budget")
    assert generic.explanation.startswith("Sin datos de alquiler para esta zona")
