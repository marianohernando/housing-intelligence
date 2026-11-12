"""CORE-003 Residential Fit on synthetic zones: conditions, % of fit, facts, Reality Check.

Fixtures here are synthetic (FIXTURE): made-up zones and values, never shown in the demo.
"""

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
from hi_domain.fit import (
    Commute,
    ZoneData,
    as_pct,
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


def test_commute_limit_is_unknown_without_travel_time() -> None:
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
    assert near.facts[0].text == "Parque urbano a 4 min andando desde la mitad de sus calles"
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
        "Estación de metro o tren accesible (sin escaleras) a 6 min andando "
        "desde la mitad de sus calles"
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


def test_only_security_is_still_without_data() -> None:
    outcome = evaluate(ScenarioState(priorities=[PriorityKey.SEGURIDAD]), zone("1"))
    assert [f.text for f in outcome.facts if f.kind is FactKind.UNKNOWN] == [
        "Seguridad: aún sin datos oficiales"
    ]
