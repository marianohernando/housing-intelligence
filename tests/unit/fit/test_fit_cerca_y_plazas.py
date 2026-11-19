"""fit-0.9 «cerca y plazas» (D-243) on synthetic zones: the budget floor and tail, a must that
scores, nearness and capacity, the three limits and their facts, the order by the % shown and
the % in words. Property tests for the monotonicity the formula promises.

Fixtures here are synthetic (FIXTURE): made-up zones and values, never shown in the demo.
"""

from dataclasses import replace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from hi_contracts.catalog.enums import GapRowKey, NullReason, TerritoryLevel
from hi_contracts.public import (
    Budget,
    BudgetKind,
    ComparisonGroup,
    FactKind,
    FactTopic,
    GapStatus,
    Household,
    MatchBand,
    NearbyNeed,
    NeedKey,
    PriorityKey,
    RankedZone,
    ScenarioState,
    ZoneGapStatus,
    ZoneMatch,
    ZoneRef,
)
from hi_domain.fit import (
    LONG_TRIP_CAP,
    MAX_FACTS,
    SHORTAGE_CAP,
    Commute,
    Supply,
    ZoneData,
    as_pct,
    budget_utility,
    criteria,
    evaluate,
    match_band,
    supply,
)
from hi_domain.search import run_search
from tests.unit.fit.test_fit import CASTELLANA, _value, family, zone


def status_of(ratio: float) -> GapStatus:
    """The cut-offs of D-213, without the significance test: enough for synthetic zones."""
    if ratio >= 1:
        return GapStatus.CUBIERTO
    return GapStatus.FALTA if ratio < 0.8 else GapStatus.JUSTO


def with_supply(data: ZoneData, district: str | None = None, /, **ratios: float) -> ZoneData:
    rows = {
        GapRowKey(row): Supply(status_of(ratio), ratio, 0.9, district)
        for row, ratio in ratios.items()
    }
    return replace(data, supply=rows)


def with_trip(data: ZoneData, minutes: float | None, confidence: float = 0.7) -> ZoneData:
    return replace(data, commute={0: Commute(minutes=minutes, confidence=confidence)})


def going(days: int, max_minutes: int | None = None) -> ScenarioState:
    anchor = CASTELLANA.model_copy(update={"days_per_week": days, "max_minutes": max_minutes})
    return family(anchors=[anchor])


# ---- budget: floor at the limit and tail beyond it -------------------------------------------


@pytest.mark.parametrize(
    ("cost", "utility"),
    [(500, 1.0), (750, 1.0), (875, 0.8), (1000, 0.6), (1125, 0.3), (1250, 0.0), (2000, 0.0)],
)
def test_the_budget_keeps_a_floor_at_its_limit_and_a_tail_beyond(cost: int, utility: float) -> None:
    """1 up to 75 % of the budget, 0,6 spending all of it, 0 at 25 % more (D-243)."""
    assert budget_utility(cost, 1000) == pytest.approx(utility)


@given(st.floats(0, 3000), st.floats(0, 3000), st.floats(100, 5000))
def test_a_cheaper_zone_never_scores_worse_on_budget(a: float, b: float, budget: float) -> None:
    low, high = sorted((a, b))
    assert budget_utility(low, budget) >= budget_utility(high, budget)
    assert 0.0 <= budget_utility(high, budget) <= 1.0


def test_a_zone_just_over_the_budget_is_a_near_miss_not_a_zero() -> None:
    """Spending it all reads «regular» at worst; 10 % over still keeps some of the edge."""
    scenario = ScenarioState(
        budget=Budget(kind=BudgetKind.RENT, amount_eur=900),
        household=Household(adults=2, minors=2, minor_ages=[4, 8]),
    )
    outcome = run_search(scenario, [zone("1", rent=12.81)])  # 77 m² ≈ 986 €: 9,6 % over
    assert outcome.near_misses[0].failed_constraints == ["budget"]
    assert outcome.near_misses[0].match_pct == 37  # 0,6 x (1 - 0,096 / 0,25)


# ---- a must scores too -------------------------------------------------------------------


def test_a_service_marked_as_a_must_also_scores_before_the_budget() -> None:
    scenario = ScenarioState(
        budget=Budget(kind=BudgetKind.RENT, amount_eur=1500),
        nearby=[
            NearbyNeed(need=NeedKey.FARMACIA, max_walk_minutes=10),
            NearbyNeed(need=NeedKey.MAYORES, max_walk_minutes=15, required=False),
        ],
    )
    keys = [c.key for c in criteria(scenario)]
    assert keys == ["need:mayores", "need:farmacia", "budget"]  # wished, then musts, then budget


def test_a_must_already_among_the_priorities_is_not_counted_twice() -> None:
    assert [c.key for c in criteria(family())].count("need:colegio") == 1


def test_leisure_as_a_must_stays_one_criterion() -> None:
    """D-236: «Ocio» is one criterion whatever its boxes, also when they are a must; without
    «Ocio» they are ignored, never a criterion."""
    bars = NearbyNeed(need=NeedKey.BARES, max_walk_minutes=10)
    with_ocio = ScenarioState(nearby=[bars], priorities=[PriorityKey.OCIO])
    assert [c.key for c in criteria(with_ocio)] == ["priority:ocio"]
    assert criteria(ScenarioState(nearby=[bars])) == []


# ---- nearness and capacity ---------------------------------------------------------------


def _gap(
    ratio: float | None, *, reliable: bool = True, group: float | None = None
) -> ZoneGapStatus:
    return ZoneGapStatus(
        admin_unit_id="ES.28.MUN.28001",
        code="28001",
        name="Zona",
        status=GapStatus.JUSTO if ratio is not None else GapStatus.SIN_DATOS,
        value=None if ratio is None else ratio,
        ratio_to_reference=ratio,
        confidence=0.8,
        null_reason=None if ratio is not None else NullReason.SOURCE_NO_COVERAGE,
        reliable=reliable,
        comparison_group=None
        if group is None
        else ComparisonGroup(codes=["28001", "28002"], names=["A", "B"], ratio_to_reference=group),
    )


@pytest.mark.parametrize(
    ("gap", "ratio"),
    [
        (_gap(0.9), 0.9),
        (_gap(4.1, reliable=False), None),  # too small alone: only its nearness counts
        (_gap(4.1, reliable=False, group=1.2), 1.2),  # compared with its neighbours (D-217)
        (_gap(None), None),
    ],
)
def test_the_capacity_reads_the_ratio_the_row_shows(
    gap: ZoneGapStatus, ratio: float | None
) -> None:
    assert supply(gap).ratio == ratio


@pytest.mark.parametrize(
    ("ratio", "pct"), [(None, 95), (2.0, 97), (1.0, 97), (0.7, 77), (0.4, 57), (0.1, 57)]
)
def test_a_service_scores_its_nearness_and_its_capacity(ratio: float | None, pct: int) -> None:
    """Colegio at 5 of 10 min (0,95): 0,6 x 0,95 + 0,4 x capacity, 1 from the reference up and 0
    at 0,4 of it; without a ratio, nearness alone."""
    scenario = ScenarioState(priorities=[PriorityKey.COLEGIOS])
    data = zone("1") if ratio is None else with_supply(zone("1"), colegio=ratio)
    assert evaluate(scenario, data).match_pct == pct


def test_capacity_never_scores_a_service_without_walking_data() -> None:
    scenario = ScenarioState(priorities=[PriorityKey.COLEGIOS])
    fit = evaluate(scenario, with_supply(zone("1", colegio=None), colegio=2.0))
    assert fit.utility is None


# ---- the three limits ----------------------------------------------------------------------


def test_a_trip_that_scores_zero_three_days_a_week_halves_the_fit() -> None:
    usual = evaluate(going(3), with_trip(zone("1"), 85.0))
    far = evaluate(going(3), with_trip(zone("1"), 90.0))
    assert far.utility == pytest.approx(0.5 * (usual.utility or 0), abs=0.05)
    assert far.facts[0].text == (
        "Tardas 1 h 30 o más en llegar a Paseo de la Castellana (Azca): el % se queda en la mitad"
    )
    assert far.facts[0].kind is FactKind.WEAKNESS and far.facts[0].topic is FactTopic.TRAYECTO
    assert any(f.text.startswith("90 min en transporte público") for f in far.facts)


def test_no_arrival_by_9_halves_the_fit_and_says_so() -> None:
    fit = evaluate(going(5), with_trip(zone("1"), None))
    assert fit.facts[0].text == (
        "No llegas a Paseo de la Castellana (Azca) a las 9:00 en transporte público: el % se "
        "queda en la mitad"
    )
    # said once: the trip's own fact («Con los horarios publicados no se llega…») is replaced
    assert not any("horarios publicados" in f.text for f in fit.facts)
    assert sum(f.topic is FactTopic.TRAYECTO for f in fit.facts) == 1


@pytest.mark.parametrize("days", [0, 1, 2])
def test_a_trip_made_one_or_two_days_never_limits_the_fit(days: int) -> None:
    fit = evaluate(going(days), with_trip(zone("1"), 150.0))
    assert not any("encaje" in f.text or "como mucho" in f.text for f in fit.facts)


def test_without_a_computed_trip_nothing_limits_the_fit() -> None:
    fit = evaluate(going(5), zone("1"))  # no trip: the straight line scores, never a limit
    assert not any("mitad" in f.text or "como mucho" in f.text for f in fit.facts)


# School and stop at the door (1 and 1, weights 3 and 2 of 6): the trip (1 of 6) decides the rest
NEAR_AND_WORK = ScenarioState(
    priorities=[PriorityKey.COLEGIOS, PriorityKey.TRANSPORTE], anchors=[CASTELLANA]
)
AT_THE_DOOR = zone("1", colegio=0.0, transporte=0.0)


def test_more_than_an_hour_three_days_a_week_keeps_the_fit_under_bien() -> None:
    sixty = evaluate(NEAR_AND_WORK, with_trip(AT_THE_DOOR, 60.0))  # (3 + 2 + 0,45) / 6
    over = evaluate(NEAR_AND_WORK, with_trip(AT_THE_DOOR, 61.0))
    assert sixty.match_pct == 91 and not sixty.facts[0].text.startswith("Más de")
    assert over.match_pct == as_pct(LONG_TRIP_CAP) == 74
    assert over.match_band is MatchBand.REGULAR
    assert over.facts[0].text == (
        "Más de 1 h de trayecto hasta Paseo de la Castellana (Azca): como mucho 74 %"
    )


def test_the_trip_limits_follow_the_person_s_own_limit() -> None:
    """With «como mucho 45 min» the window is 45: 90 min caps it, 135 halves it."""
    limit = CASTELLANA.model_copy(update={"max_minutes": 45})
    scenario = NEAR_AND_WORK.model_copy(update={"anchors": [limit]})
    assert evaluate(scenario, with_trip(AT_THE_DOOR, 89.0)).match_pct == 91
    capped = evaluate(scenario, with_trip(AT_THE_DOOR, 91.0))
    assert capped.match_pct == 74
    assert capped.facts[0].text.startswith("Más de 1 h 30 de trayecto")
    halved = evaluate(scenario, with_trip(AT_THE_DOOR, 135.0))
    assert halved.match_pct == 42  # 5/6 halved
    assert halved.facts[0].text.startswith("Tardas 2 h 15 o más")


def test_a_shortage_in_a_marked_service_keeps_the_fit_under_muy_bien() -> None:
    scenario = family(anchors=[])
    plenty = with_supply(zone("1", colegio=0.0, transporte=0.0), colegio=1.5, centro_salud=1.2)
    # FALTA at 0,79 of the reference: the school scores 0,86, the zone (4 x 0,86 + 3 + 1) / 8
    short = with_supply(zone("1", colegio=0.0, transporte=0.0), colegio=0.79, centro_salud=1.2)
    assert evaluate(scenario, plenty).match_pct == 100
    fit = evaluate(scenario, short)
    assert fit.match_pct == as_pct(SHORTAGE_CAP) == 89
    assert fit.match_band is MatchBand.BIEN
    assert fit.facts[0].text == "Faltan colegios: como mucho 89 %"
    assert fit.facts[0].topic is FactTopic.COLEGIOS


def test_a_shortage_in_a_service_nobody_marked_limits_nothing() -> None:
    scenario = family(anchors=[])
    data = with_supply(zone("1", colegio=0.0, transporte=0.0), farmacia=0.3, mayores=0.2)
    assert evaluate(scenario, data).match_pct == 100


def test_a_barrio_says_the_shortage_is_its_district_s() -> None:
    scenario = ScenarioState(
        priorities=[PriorityKey.TRANSPORTE, PriorityKey.SALUD],
        nearby=[NearbyNeed(need=NeedKey.COLEGIO, max_walk_minutes=10)],
    )
    data = with_supply(
        zone("1", colegio=0.0, transporte=0.0),
        "Puente de Vallecas",
        colegio=0.79,
        centro_salud=0.79,
    )
    data = replace(data, walk={**data.walk, NeedKey.CENTRO_SALUD: _value("cs", 0.0)})
    fact = evaluate(scenario, data).facts[0]
    assert fact.text == "Faltan centros de salud y colegios en Puente de Vallecas: como mucho 89 %"


def test_below_a_cap_the_card_says_nothing_of_it() -> None:
    scenario = family(anchors=[])
    data = with_supply(zone("1", colegio=25.0), colegio=0.5)  # far and short: well under 89
    fit = evaluate(scenario, data)
    assert (fit.match_pct or 0) < 89
    assert not any("como mucho" in f.text for f in fit.facts)


def test_once_halved_no_cap_is_reached_and_one_fact_explains_the_pct() -> None:
    data = with_supply(with_trip(zone("1", colegio=0.0, transporte=0.0), 200.0), colegio=0.5)
    fit = evaluate(going(5), data)
    limits = [f for f in fit.facts if "mitad" in f.text or "como mucho" in f.text]
    assert [f.text.split(":")[0] for f in limits] == [
        "Tardas 1 h 30 o más en llegar a Paseo de la Castellana (Azca)"
    ]


def test_a_trip_cap_keeps_its_minutes_and_the_cost_on_a_full_card() -> None:
    """Three priorities, the trip, a wished service and the budget are six facts: with the limit
    first, the least important criterion goes, never the trip it speaks of nor the cost."""
    scenario = family(
        nearby=[NearbyNeed(need=NeedKey.FARMACIA, max_walk_minutes=10, required=False)]
    )
    fit = evaluate(scenario, with_trip(zone("1", colegio=0.0, transporte=0.0), 70.0))
    texts = [f.text for f in fit.facts]
    assert len(texts) == MAX_FACTS
    assert texts[0].startswith("Más de 1 h de trayecto")
    assert any(t.startswith("70 min en transporte público") for t in texts)
    assert any(f.topic is FactTopic.COSTE for f in fit.facts)


# ---- the order by the % shown and the % in words -----------------------------------------


@pytest.mark.parametrize(
    ("pct", "band"),
    [
        (100, MatchBand.MUY_BIEN),
        (90, MatchBand.MUY_BIEN),
        (89, MatchBand.BIEN),
        (75, MatchBand.BIEN),
        (74, MatchBand.REGULAR),
        (60, MatchBand.REGULAR),
        (59, MatchBand.POCO),
        (0, MatchBand.POCO),
        (None, None),
    ],
)
def test_the_pct_in_words(pct: int | None, band: MatchBand | None) -> None:
    assert match_band(pct) is band


def test_only_a_zone_that_passes_everything_reads_in_words() -> None:
    """D-243: a near miss (or a zone with a condition that cannot be checked) has no band, so it
    never reads «muy bien» while over the budget; its % stays, for the order and the API."""
    zones = [zone("1"), zone("2", rent=13.0), zone("3", rent=None)]  # 2: 1.001 € for 1.000 €
    outcome = run_search(family(budget=1000, anchors=[]), zones)
    assert [r.match_band for r in outcome.results] == [match_band(outcome.results[0].match_pct)]
    assert outcome.results[0].match_band is not None
    near = outcome.near_misses[0]
    assert near.failed_constraints == ["budget"] and near.match_pct >= 60
    assert near.match_band is None
    bands = {z.zone.code: (z.match_pct, z.match_band) for z in outcome.all_zones}
    assert bands["1"][1] is match_band(bands["1"][0])
    assert bands["2"] == (near.match_pct, None)
    assert bands["3"] == (None, None)
    assert all(z.match_band is None for z in outcome.all_zones if not z.passes_all)


def test_an_answer_without_bands_still_reads() -> None:
    """Additive: a result of an API before fit-0.9 (no `match_band`) validates as ever."""
    ref = ZoneRef(level=TerritoryLevel.MUNICIPIO, code="28001", name="Zona")
    old = {"rank": 1, "zone": ref.model_dump(), "match_pct": 93, "confidence": 1, "facts": []}
    assert RankedZone.model_validate({**old, "constraints": []}).match_band is None
    assert (
        ZoneMatch.model_validate({"zone": ref.model_dump(), "passes_all": True}).match_band is None
    )


# ---- monotonicity (CLAUDE.md §14: property-based tests) -----------------------------------

minutes = st.one_of(st.none(), st.floats(min_value=0, max_value=120))
ratio = st.floats(min_value=0, max_value=3)
SCENARIOS = st.sampled_from(
    [
        family(),
        family(anchors=[]),
        going(2),
        family(budget=Budget(kind=BudgetKind.RENT, amount_eur=900)),
        family(
            priorities=[PriorityKey.SALUD],
            nearby=[NearbyNeed(need=NeedKey.ESCUELA_INFANTIL, max_walk_minutes=10)],
        ),
    ]
)


@st.composite
def zones(draw: st.DrawFn, code: str = "1") -> ZoneData:
    data = zone(
        code,
        rent=draw(st.floats(min_value=6, max_value=25)),
        colegio=draw(minutes),
        transporte=draw(minutes),
    )
    walk = {**data.walk, NeedKey.CENTRO_SALUD: _value("cs", draw(minutes))}
    walk[NeedKey.ESCUELA_INFANTIL] = _value("ei", draw(minutes))
    rows = {"colegio": draw(ratio), "centro_salud": draw(ratio), "escuela_infantil": draw(ratio)}
    data = with_supply(replace(data, walk=walk), **rows)
    return with_trip(data, draw(st.one_of(st.none(), st.floats(min_value=5, max_value=200))))


EPS = 1e-12


@settings(max_examples=150, deadline=None)
@given(zones(), SCENARIOS, st.sampled_from(list(NeedKey)[:6]), st.floats(0.1, 0.99))
def test_closer_never_scores_worse(
    data: ZoneData, scenario: ScenarioState, need: NeedKey, factor: float
) -> None:
    walk = data.walk.get(need)
    if walk is None or walk.value is None:
        return
    closer = replace(
        data, walk={**data.walk, need: walk.model_copy(update={"value": walk.value * factor})}
    )
    before, after = evaluate(scenario, data).utility, evaluate(scenario, closer).utility
    assert before is None or (after or 0) >= before - EPS


@settings(max_examples=150, deadline=None)
@given(zones(), SCENARIOS, st.floats(0.1, 0.99))
def test_a_shorter_trip_never_scores_worse(
    data: ZoneData, scenario: ScenarioState, factor: float
) -> None:
    trip = data.commute[0]
    shorter = with_trip(data, None if trip.minutes is None else trip.minutes * factor)
    before, after = evaluate(scenario, data).utility, evaluate(scenario, shorter).utility
    assert before is None or (after or 0) >= before - EPS


@settings(max_examples=150, deadline=None)
@given(
    zones(),
    SCENARIOS,
    st.sampled_from(["colegio", "centro_salud", "escuela_infantil"]),
    st.floats(1.01, 4),
)
def test_more_capacity_never_scores_worse(
    data: ZoneData, scenario: ScenarioState, row: str, factor: float
) -> None:
    """More places for as many people: the ratio, and with it the status, only go up."""
    key = GapRowKey(row)
    found = data.supply[key]
    more = (found.ratio or 0) * factor
    richer = replace(data, supply={**data.supply, key: Supply(status_of(more), more, 0.9)})
    before, after = evaluate(scenario, data).utility, evaluate(scenario, richer).utility
    assert before is None or (after or 0) >= before - EPS


@settings(max_examples=60, deadline=None)
@given(st.lists(zones(), min_size=1, max_size=8), st.integers(400, 3000), st.floats(1.01, 2))
def test_more_budget_never_takes_zones_away(
    data: list[ZoneData], budget: int, factor: float
) -> None:
    coded = [
        replace(z, zone=z.zone.model_copy(update={"code": str(i)})) for i, z in enumerate(data)
    ]
    before = {r.zone.code for r in run_search(family(budget=budget), coded).results}
    richer = family(budget=round(budget * factor))
    after = {z.zone.code for z in run_search(richer, coded).all_zones if z.passes_all}
    assert before <= after
