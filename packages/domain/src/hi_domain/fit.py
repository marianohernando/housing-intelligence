"""Residential Fit (CORE-003, D-215): hard conditions, then a % of fit with tangible facts.

Pipeline (CLAUDE.md §14): every zone gets its conditions checked as PASS / FAIL / UNKNOWN
(UNKNOWN never counts as PASS), then a % of fit from what the person asked for: their «Me
importa» priorities in their order, where they work and the budget margin. Each criterion
has a utility from 0 to 1 that saturates (piecewise linear), the weights follow the order
(rank sum: the first of n weighs n, the last 1) and the % is the weighted mean over the
criteria the zone has data for. Criteria without data never count as 0: they lower the
confidence and show up as «sin datos» facts. The personal % is kept apart from the
territorial reference (the gap highlights come from GAP-001).
"""

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace

from hi_contracts.public import (
    Anchor,
    BudgetKind,
    ConstraintCheck,
    ConstraintStatus,
    Fact,
    FactKind,
    FactTopic,
    GapHighlight,
    IndicatorValue,
    NearbyNeed,
    NeedKey,
    PriorityKey,
    ScenarioState,
    ZoneRef,
)
from hi_domain.affordability import (
    FloorArea,
    assumed_floor_area,
    budget_check,
    monthly_rent,
    purchase_cost,
    purchase_explanation,
    rent_explanation,
)
from hi_domain.gaps import es_number

# 0.3: park (D-222); 0.4: step-free station (D-223); 0.5: buying (D-227); 0.6: rent of new
# leases and walking minutes read as approximate (D-228); 0.7: barrios inside a district, with a
# trip measured for the whole district and the reason for an unknown rent said (D-232); 0.8: a
# trip made 1-2 days a week weighs half and one never made is not scored (D-240)
FIT_VERSION = "fit-0.8"
# Walking windows of CORE-005 (D-210): what «cerca» means for each service by default.
DEFAULT_WALK_MINUTES: dict[NeedKey, int] = {
    NeedKey.ESCUELA_INFANTIL: 10,
    NeedKey.COLEGIO: 10,
    NeedKey.CENTRO_SALUD: 15,
    NeedKey.FARMACIA: 10,
    NeedKey.MAYORES: 10,
    NeedKey.TRANSPORTE: 5,
}
WALK_ZERO_AT = 3.0  # utility falls linearly to 0 at three times the window
NEAR_KM, FAR_KM = 2.0, 20.0  # straight line to a place of work: 1 within 2 km, 0 from 20 km
STRAIGHT_LINE_CONFIDENCE = 0.5  # declared proxy: distance is not travel time
# Public transport (CORE-009, D-220): full utility up to 30 min, none from 90 (3x, as walking).
DEFAULT_COMMUTE_MINUTES = 30
# Telework (D-240): a trip made 1-2 days a week weighs half in the % of fit; from 3 days it
# weighs as always. A place never gone to (0 days) is not scored, but its limit still applies.
FEW_DAYS_PER_WEEK = 2
FEW_DAYS_WEIGHT = 0.5
BUDGET_MARGIN_SHARE = 0.25  # full utility when the cost is 75 % of the budget or less
MAX_WALK_SHOWN = 60

NEED_TEXT: dict[NeedKey, tuple[str, str]] = {  # (fact label, «de …» in a sentence)
    NeedKey.ESCUELA_INFANTIL: ("Escuela infantil", "una escuela infantil"),
    NeedKey.COLEGIO: ("Colegio con primaria", "un colegio con primaria"),
    NeedKey.CENTRO_SALUD: ("Centro de salud", "un centro de salud"),
    NeedKey.FARMACIA: ("Farmacia", "una farmacia"),
    NeedKey.MAYORES: ("Centro de mayores", "un centro de mayores"),
    NeedKey.TRANSPORTE: ("Parada de transporte público", "una parada de transporte público"),
}
NEED_TOPIC: dict[NeedKey, FactTopic] = {
    NeedKey.ESCUELA_INFANTIL: FactTopic.COLEGIOS,
    NeedKey.COLEGIO: FactTopic.COLEGIOS,
    NeedKey.CENTRO_SALUD: FactTopic.SALUD,
    NeedKey.FARMACIA: FactTopic.SALUD,
    NeedKey.MAYORES: FactTopic.OTRO,
    NeedKey.TRANSPORTE: FactTopic.TRANSPORTE,
}
PRIORITY_NEED: dict[PriorityKey, NeedKey] = {
    PriorityKey.TRANSPORTE: NeedKey.TRANSPORTE,
    PriorityKey.SALUD: NeedKey.CENTRO_SALUD,
    PriorityKey.COLEGIOS: NeedKey.COLEGIO,
}


@dataclass(frozen=True)
class PriorityWalk:
    """A priority measured by walking to a kind of place (D-222): what the fact calls it, the
    window that scores 1 and what to say beyond the walking range (WALK_ZERO_AT x window),
    where the place is not at a walk but what the person means may be (the countryside)."""

    name: str  # the priority, as the web says it
    label: str  # the place
    topic: FactTopic
    target_minutes: int
    out_of_range: str


PRIORITY_WALK: dict[PriorityKey, PriorityWalk] = {
    PriorityKey.ZONAS_VERDES: PriorityWalk(
        name="Zonas verdes",
        label="Parque urbano",
        topic=FactTopic.ZONAS_VERDES,
        target_minutes=10,
        out_of_range="Sin parque urbano de 1 ha o más a un paseo (el campo no cuenta)",
    ),
    # Opt-in functional need (CLAUDE.md §13): a station the CRTM grades as fully accessible.
    PriorityKey.SIN_ESCALERAS: PriorityWalk(
        name="Sin escaleras",
        label="Estación de metro o tren accesible (sin escaleras)",
        topic=FactTopic.ACCESIBILIDAD,
        target_minutes=10,
        out_of_range=(
            "Sin estación de metro o tren accesible a un paseo "
            "(no mide autobuses, aceras ni portales)"
        ),
    ),
}
# Priorities the search does not score, never as 0. Safety: no official measure of it for
# whoever lives in each zone (D-224, D-226); Madrid districts show the residents' view as context.
NO_DATA_PRIORITY: dict[PriorityKey, tuple[FactTopic, str]] = {
    PriorityKey.SEGURIDAD: (
        FactTopic.SEGURIDAD,
        "Seguridad: no la puntuamos (no hay un dato oficial que la mida para quien vive en "
        "cada zona)",
    ),
}
# D-239: what breaks an exact tie of the fit, every service measured on foot (marked or not).
EVERYDAY_NEEDS = tuple(NeedKey)
CONTEXT_NEEDS = (NeedKey.TRANSPORTE, NeedKey.CENTRO_SALUD, NeedKey.COLEGIO, NeedKey.FARMACIA)
MIN_FACTS, MAX_FACTS = 3, 5


@dataclass(frozen=True)
class Commute:
    """Minutes by public transport to one place of work, arriving by 9:00 (D-220). None: with
    the published timetables most of the zone cannot make it; as a preference that is the worst
    score, as a hard limit it stays UNKNOWN (the timetables have declared gaps). `note`: where
    the trip was measured when it is not the zone itself (D-232: a barrio without its own trip
    takes its district's), said after the minutes."""

    minutes: float | None
    confidence: float
    note: str | None = None


@dataclass(frozen=True)
class ZoneData:
    """What the search knows about one zone: rent and appraised purchase value per m², walking
    minutes by service and, per place of work (index in `anchors`), the trip by public
    transport when it was computed."""

    zone: ZoneRef
    rent: IndicatorValue | None = None
    walk: Mapping[NeedKey, IndicatorValue] = field(default_factory=dict[NeedKey, IndicatorValue])
    gaps: Sequence[GapHighlight] = ()
    # Walking minutes behind a «me importa» priority (PRIORITY_WALK): the park, for green areas.
    priority_walk: Mapping[PriorityKey, IndicatorValue] = field(
        default_factory=dict[PriorityKey, IndicatorValue]
    )
    commute: Mapping[int, Commute] = field(default_factory=dict[int, Commute])
    price: IndicatorValue | None = None  # appraised value per m² to buy (D-227)
    rent_note: str | None = None  # what the rent figure is, from its feature (D-228)
    rent_missing: str | None = None  # why there is no rent here, in plain words (D-232)
    # Walking minutes to a bus stop and to a Metro/Cercanías station, by mode ("bus", "metro").
    # They only word the transport fact, never score it (D-233); empty until the data is synced.
    transit: Mapping[str, IndicatorValue] = field(default_factory=dict[str, IndicatorValue])


@dataclass(frozen=True)
class Criterion:
    key: str  # need:<need>, priority:<priority>, work:<i> or budget
    weight: float
    need: NeedKey | None = None
    target_minutes: int | None = None
    priority: PriorityKey | None = None
    anchor: Anchor | None = None
    anchor_index: int | None = None  # position in ScenarioState.anchors


@dataclass(frozen=True)
class Score:
    utility: float | None  # None = no data, never 0
    confidence: float
    fact: Fact


@dataclass(frozen=True)
class ZoneFit:
    data: ZoneData
    constraints: list[ConstraintCheck]
    utility: float | None  # unrounded % / 100: ranks before the rounding
    confidence: float
    facts: list[Fact]
    cost_eur: float | None
    # Index in `anchors` of the place whose minutes break ties (lead_trip, D-240); None = none
    lead_trip: int | None = 0

    @property
    def match_pct(self) -> int | None:
        return as_pct(self.utility)

    @property
    def failed(self) -> list[str]:
        return [c.constraint_id for c in self.constraints if c.status is ConstraintStatus.FAIL]

    @property
    def passes_all(self) -> bool:
        return all(c.status is ConstraintStatus.PASS for c in self.constraints)


def clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def walk_utility(minutes: float, target: float) -> float:
    return clamp01((WALK_ZERO_AT * target - minutes) / ((WALK_ZERO_AT - 1) * target))


def distance_utility(km: float) -> float:
    return clamp01((FAR_KM - km) / (FAR_KM - NEAR_KM))


def budget_utility(cost: float, budget: float) -> float:
    return clamp01((budget - cost) / (BUDGET_MARGIN_SHARE * budget))


def km_between(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Great-circle distance (haversine, mean Earth radius)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(a))


def anchor_km(zone: ZoneRef, anchor: Anchor) -> float | None:
    if zone.center_lon is None or zone.center_lat is None:
        return None
    return km_between(zone.center_lon, zone.center_lat, anchor.lon, anchor.lat)


def about_minutes(minutes: float) -> str:
    """«unos 9 min»: a zone's median walk is approximate (the web explains it once)."""
    if minutes > MAX_WALK_SHOWN:
        return f"más de {MAX_WALK_SHOWN} min"
    rounded = round(minutes)
    return "1 min o menos" if rounded <= 1 else f"unos {rounded} min"


def minutes_text(minutes: float) -> str:
    if minutes > MAX_WALK_SHOWN:
        return f"más de {MAX_WALK_SHOWN} min"
    return f"{es_number(minutes, 0)} min"


def rank_weights(n: int) -> list[float]:
    """Rank-sum weights: the first of n criteria weighs n, the last 1, normalised to 1."""
    total = n * (n + 1) / 2
    return [(n - i) / total for i in range(n)]


def counts(anchor: Anchor) -> bool:
    """False for a place the person never goes to (0 days a week: full telework, D-240): its
    trip is not scored. A limit on it (`max_minutes`) is still a condition."""
    return anchor.days_per_week > 0


def days_weight(anchor: Anchor) -> float:
    """Share of its rank weight a trip keeps (D-240): half when made 1-2 days a week."""
    return FEW_DAYS_WEIGHT if anchor.days_per_week <= FEW_DAYS_PER_WEEK else 1.0


def _criteria_keys(scenario: ScenarioState) -> list[Criterion]:
    """The person's criteria in order of importance, before weighting."""
    keys: list[Criterion] = []
    covered: set[NeedKey] = set()
    windows = {n.need: n.max_walk_minutes for n in scenario.nearby}
    for priority in scenario.priorities:
        need = PRIORITY_NEED.get(priority)
        if need is None:
            keys.append(Criterion(f"priority:{priority.value}", 0.0, priority=priority))
            continue
        covered.add(need)
        target = windows.get(need, DEFAULT_WALK_MINUTES[need])
        keys.append(Criterion(f"need:{need.value}", 0.0, need=need, target_minutes=target))
    for i, anchor in enumerate(scenario.anchors):
        if counts(anchor):
            keys.append(Criterion(f"work:{i}", 0.0, anchor=anchor, anchor_index=i))
    for nearby in scenario.nearby:  # a wished service not already among the priorities
        if not nearby.required and nearby.need not in covered:
            target = nearby.max_walk_minutes
            keys.append(Criterion(f"need:{nearby.need.value}", 0.0, nearby.need, target))
    if scenario.budget is not None:
        keys.append(Criterion("budget", 0.0))
    return keys


def criteria(scenario: ScenarioState) -> list[Criterion]:
    """Rank-sum weights by order; a trip made few days a week keeps a share of its own
    (D-240). The weights need not add up to 1: the % divides by the weight with data."""
    keys = _criteria_keys(scenario)
    weights = rank_weights(len(keys))
    return [
        replace(c, weight=w if c.anchor is None else w * days_weight(c.anchor))
        for c, w in zip(keys, weights, strict=True)
    ]


def near_check(nearby: NearbyNeed, walk: IndicatorValue | None) -> ConstraintCheck:
    label, of = NEED_TEXT[nearby.need]
    base = {
        "constraint_id": f"near:{nearby.need.value}",
        "label": f"{label} a {nearby.max_walk_minutes} min andando como mucho",
        "threshold": float(nearby.max_walk_minutes),
        "unit": "min",
    }
    if walk is None or walk.value is None:
        return ConstraintCheck(
            **base,
            status=ConstraintStatus.UNKNOWN,
            confidence=0.0,
            explanation=f"Sin datos de la distancia a pie hasta {of} en esta zona",
        )
    passed = walk.value <= nearby.max_walk_minutes
    return ConstraintCheck(
        **base,
        status=ConstraintStatus.PASS if passed else ConstraintStatus.FAIL,
        value=round(walk.value, 1),
        confidence=walk.confidence,
        explanation=f"A {about_minutes(walk.value)} andando de {of} "
        "(lo que tarda la mitad de la zona)",
    )


MAX_COMMUTE_SHOWN = 120


def commute_text(minutes: float, label: str, note: str | None = None) -> str:
    shown = "más de 2 h" if minutes > MAX_COMMUTE_SHOWN else f"{es_number(minutes, 0)} min"
    return with_note(f"{shown} en transporte público hasta {label}, llegando a las 9:00", note)


def with_note(text: str, note: str | None) -> str:
    return text if note is None else f"{text} ({note})"


def commute_check(i: int, anchor: Anchor, data: ZoneData) -> ConstraintCheck:
    """PASS/FAIL on the minutes by public transport (D-220); UNKNOWN without them, and with a
    trip measured elsewhere (`note`, D-232: a barrio's district), which says nothing sure about
    this zone's limit."""
    base = {
        "constraint_id": f"commute:{i}",
        "label": f"Trayecto a {anchor.label} de {anchor.max_minutes} min como mucho",
        "threshold": float(anchor.max_minutes or 0),
        "unit": "min",
    }
    trip = data.commute.get(i)
    if trip is None or trip.minutes is None:
        km = anchor_km(data.zone, anchor)
        where = "" if km is None else f"; está a {es_number(km, 1)} km en línea recta"
        why = (
            "Sin datos del trayecto en transporte público"
            if trip is None
            else f"Con los horarios publicados no se llega a {anchor.label} a las 9:00"
        )
        explanation = with_note(f"{why}{where}", None if trip is None else trip.note)
        return ConstraintCheck(
            **base, status=ConstraintStatus.UNKNOWN, confidence=0.0, explanation=explanation
        )
    if trip.note is not None:
        return ConstraintCheck(
            **base,
            status=ConstraintStatus.UNKNOWN,
            value=round(trip.minutes, 1),
            confidence=0.0,
            explanation=commute_text(trip.minutes, anchor.label, trip.note),
        )
    passed = anchor.max_minutes is not None and trip.minutes <= anchor.max_minutes
    return ConstraintCheck(
        **base,
        status=ConstraintStatus.PASS if passed else ConstraintStatus.FAIL,
        value=round(trip.minutes, 1),
        confidence=trip.confidence,
        explanation=commute_text(trip.minutes, anchor.label, trip.note),
    )


def constraint_checks(
    scenario: ScenarioState, data: ZoneData, area: FloorArea
) -> list[ConstraintCheck]:
    checks: list[ConstraintCheck] = []
    if scenario.budget is not None:
        checks.append(
            budget_check(
                scenario.budget, data.rent, area, data.price, data.rent_note, data.rent_missing
            )
        )
    for nearby in scenario.nearby:
        if nearby.required:
            checks.append(near_check(nearby, data.walk.get(nearby.need)))
    for i, anchor in enumerate(scenario.anchors):
        if anchor.max_minutes is not None:  # whatever the days, even none (D-240)
            checks.append(commute_check(i, anchor, data))
    return checks


def _walk_shown(walk: IndicatorValue | None) -> float | None:
    if walk is None or walk.value is None or walk.value > MAX_WALK_SHOWN:
        return None
    return walk.value


def transit_walk_text(transit: Mapping[str, IndicatorValue], fallback: str) -> str:
    """The transport fact by mode (D-233): «Parada de autobús a unos 2 min andando · Metro o
    Cercanías a unos 8 min». A mode without minutes, or beyond MAX_WALK_SHOWN (the nearest
    Metro of a village is the one in the next town: not a walk), is left out; none at all, or
    no feature yet in the database, gives `fallback`: the text of always."""
    bus_min, metro_min = (_walk_shown(transit.get(mode)) for mode in ("bus", "metro"))
    if bus_min is not None and metro_min is not None:
        return (
            f"Parada de autobús a {about_minutes(bus_min)} andando"
            f" · Metro o Cercanías a {about_minutes(metro_min)}"
        )
    if bus_min is not None:
        return f"Parada de autobús a {about_minutes(bus_min)} andando"
    if metro_min is not None:
        return f"Metro o Cercanías a {about_minutes(metro_min)} andando"
    return fallback


def walk_fact(
    need: NeedKey,
    walk: IndicatorValue | None,
    target: int,
    transit: Mapping[str, IndicatorValue] | None = None,
) -> Score:
    label = NEED_TEXT[need][0]
    if walk is None or walk.value is None:
        text = f"{label}: sin datos de distancia a pie en esta zona"
        fact = Fact(kind=FactKind.UNKNOWN, topic=NEED_TOPIC[need], text=text, confidence=0.0)
        return Score(None, 0.0, fact)
    kind = FactKind.STRENGTH if walk.value <= target else FactKind.WEAKNESS
    text = f"{label} a {about_minutes(walk.value)} andando"
    if need is NeedKey.TRANSPORTE and transit:
        text = transit_walk_text(transit, text)
    fact = Fact(
        kind=kind,
        topic=NEED_TOPIC[need],
        text=text,
        confidence=walk.confidence,
        indicator=walk,
    )
    return Score(walk_utility(walk.value, target), walk.confidence, fact)


# Beyond its walking range a priority measured on foot scores 0, as any walk does, but the
# place may not be what the person means (a village's countryside is not a park, D-222 §7).
OUT_OF_RANGE_CONFIDENCE = 0.5


def priority_walk_fact(measured: PriorityWalk, walk: IndicatorValue | None) -> Score:
    """Walking minutes to the place a priority measures: 1 up to the window, 0 at the walking
    range (WALK_ZERO_AT x window). Beyond it, 0 with `out_of_range` as the fact and low
    confidence; never UNKNOWN, which would rank a zone without the place above one with it far."""
    if walk is None or walk.value is None:
        text = f"{measured.name}: sin datos de distancia a pie en esta zona"
        fact = Fact(kind=FactKind.UNKNOWN, topic=measured.topic, text=text, confidence=0.0)
        return Score(None, 0.0, fact)
    utility = walk_utility(walk.value, measured.target_minutes)
    shown_indicator: IndicatorValue | None = walk
    if walk.value > WALK_ZERO_AT * measured.target_minutes:
        confidence = min(walk.confidence, OUT_OF_RANGE_CONFIDENCE)
        text = measured.out_of_range
        shown_indicator = None  # the text has no minutes: the web tells walks by the indicator
    else:
        confidence = walk.confidence
        text = f"{measured.label} a {about_minutes(walk.value)} andando"
    kind = FactKind.STRENGTH if walk.value <= measured.target_minutes else FactKind.WEAKNESS
    fact = Fact(
        kind=kind,
        topic=measured.topic,
        text=text,
        confidence=confidence,
        indicator=shown_indicator,
    )
    return Score(utility, confidence, fact)


def work_fact(anchor: Anchor, data: ZoneData, trip: Commute | None) -> Score:
    """Minutes by public transport when computed (D-220); otherwise the straight line (D-215)."""
    if trip is not None:
        return transit_fact(anchor, trip)
    zone = data.zone
    km = anchor_km(zone, anchor)
    if km is None:
        text = f"Distancia a {anchor.label}: sin datos"
        fact = Fact(kind=FactKind.UNKNOWN, topic=FactTopic.TRAYECTO, text=text, confidence=0.0)
        return Score(None, 0.0, fact)
    utility = distance_utility(km)
    fact = Fact(
        kind=FactKind.STRENGTH if utility >= 0.5 else FactKind.WEAKNESS,
        topic=FactTopic.TRAYECTO,
        text=f"A {es_number(km, 1)} km en línea recta de {anchor.label}",
        confidence=STRAIGHT_LINE_CONFIDENCE,
    )
    return Score(utility, STRAIGHT_LINE_CONFIDENCE, fact)


def transit_fact(anchor: Anchor, trip: Commute) -> Score:
    if trip.minutes is None:
        text = with_note(
            f"Con los horarios publicados no se llega a {anchor.label} a las 9:00 "
            "en transporte público",
            trip.note,
        )
        fact = Fact(
            kind=FactKind.WEAKNESS, topic=FactTopic.TRAYECTO, text=text, confidence=trip.confidence
        )
        return Score(0.0, trip.confidence, fact)
    target = anchor.max_minutes or DEFAULT_COMMUTE_MINUTES
    fact = Fact(
        kind=FactKind.STRENGTH if trip.minutes <= target else FactKind.WEAKNESS,
        topic=FactTopic.TRAYECTO,
        text=commute_text(trip.minutes, anchor.label, trip.note),
        confidence=trip.confidence,
    )
    return Score(walk_utility(trip.minutes, target), trip.confidence, fact)


def cost_fact(
    rent: IndicatorValue | None,
    area: FloorArea,
    budget: float | None,
    note: str | None = None,
    missing: str | None = None,
) -> Score:
    if rent is None or rent.value is None:
        text = missing or "Alquiler: sin datos publicados para esta zona"
        fact = Fact(kind=FactKind.UNKNOWN, topic=FactTopic.COSTE, text=text, confidence=0.0)
        return Score(None, 0.0, fact)
    cost = round(monthly_rent(rent.value, area.m2))
    fits = budget is None or cost <= budget
    fact = Fact(
        kind=FactKind.STRENGTH if fits else FactKind.WEAKNESS,
        topic=FactTopic.COSTE,
        text=rent_explanation(rent.value, area, note),
        confidence=rent.confidence,
        indicator=rent,
    )
    utility = None if budget is None else budget_utility(cost, budget)
    return Score(utility, rent.confidence, fact)


def purchase_fact(price: IndicatorValue | None, area: FloorArea, budget: float) -> Score:
    """Buying (D-227): the appraised value for the needed area against the budget."""
    if price is None or price.value is None:
        text = "Compra: sin precio publicado para esta zona"
        fact = Fact(kind=FactKind.UNKNOWN, topic=FactTopic.COSTE, text=text, confidence=0.0)
        return Score(None, 0.0, fact)
    cost = purchase_cost(price.value, area.m2)
    fact = Fact(
        kind=FactKind.STRENGTH if cost <= budget else FactKind.WEAKNESS,
        topic=FactTopic.COSTE,
        text=purchase_explanation(price.value, area),
        confidence=price.confidence,
        indicator=price,
    )
    return Score(budget_utility(cost, budget), price.confidence, fact)


def score(criterion: Criterion, scenario: ScenarioState, data: ZoneData, area: FloorArea) -> Score:
    if criterion.need is not None:
        target = criterion.target_minutes or DEFAULT_WALK_MINUTES[criterion.need]
        return walk_fact(criterion.need, data.walk.get(criterion.need), target, data.transit)
    if criterion.anchor is not None:
        trip = None if criterion.anchor_index is None else data.commute.get(criterion.anchor_index)
        return work_fact(criterion.anchor, data, trip)
    if criterion.priority is not None:
        measured = PRIORITY_WALK.get(criterion.priority)
        if measured is not None:
            return priority_walk_fact(measured, data.priority_walk.get(criterion.priority))
        topic, text = NO_DATA_PRIORITY[criterion.priority]
        return Score(None, 0.0, Fact(kind=FactKind.UNKNOWN, topic=topic, text=text, confidence=0))
    if scenario.budget is not None and scenario.budget.kind is BudgetKind.BUY:
        return purchase_fact(data.price, area, float(scenario.budget.amount_eur))
    budget = None if scenario.budget is None else float(scenario.budget.amount_eur)
    return cost_fact(data.rent, area, budget, data.rent_note, data.rent_missing)


def match_and_confidence(
    weighted: Sequence[tuple[float, Score]],
) -> tuple[float | None, float]:
    """Weighted mean utility (0-1) over the criteria with data; confidence counts the missing
    ones as 0. No criteria at all: the zone fits everything that was asked (1)."""
    if not weighted:
        return 1.0, 1.0
    known = [(w, s) for w, s in weighted if s.utility is not None]
    total = sum(w for w, _ in weighted)
    confidence = sum(w * s.confidence for w, s in known) / total
    known_weight = sum(w for w, _ in known)
    if known_weight <= 0:
        return None, 0.0
    utility = sum(w * (s.utility or 0.0) for w, s in known) / known_weight
    return utility, round(confidence, 3)


def as_pct(utility: float | None) -> int | None:
    """Half up (0.5 -> 1), not to even: the shown % is what the person reads."""
    return None if utility is None else math.floor(100 * utility + 0.5)


def limited_trips(scenario: ScenarioState, data: ZoneData) -> list[Fact]:
    """The trip to a place never gone to (0 days) that keeps a limit (D-240): its minutes as
    context, without weight, so the card says how far it is. Without them, the condition says
    why."""
    return [
        transit_fact(anchor, trip).fact
        for i, anchor in enumerate(scenario.anchors)
        if not counts(anchor)
        and anchor.max_minutes is not None
        and (trip := data.commute.get(i)) is not None
    ]


def capped(ordered: list[Fact]) -> list[Fact]:
    """At most MAX_FACTS, in order of importance. The cost always stays when there is one (it
    only exists with a budget): if it would fall, the least important of the others goes
    instead (D-240: with three priorities, work and family it was the sixth)."""
    cost = next((i for i, f in enumerate(ordered) if f.topic is FactTopic.COSTE), None)
    if cost is None or cost < MAX_FACTS:
        return ordered[:MAX_FACTS]
    return [*ordered[: MAX_FACTS - 1], ordered[cost]]


def facts(scores: Sequence[Score], data: ZoneData, trips: Sequence[Fact] = ()) -> list[Fact]:
    """3-5 facts: the criteria with data in order of importance, the minutes to a limited
    place nobody goes to (`trips`, without weight), then context (walking minutes) when the
    person asked for fewer than three things, then the criteria without data («sin datos»).
    Rent only shows up with a rent budget: without one there is nothing to say whether it is
    good or bad for this person."""
    known = [s.fact for s in scores if s.utility is not None]
    known += trips
    unknown = [s.fact for s in scores if s.utility is None]
    context = [
        walk_fact(n, data.walk.get(n), DEFAULT_WALK_MINUTES[n], data.transit) for n in CONTEXT_NEEDS
    ]
    shown = {f.topic for f in known} | {f.topic for f in unknown}
    for extra in context:
        if len(known) + len(unknown) >= MIN_FACTS:
            break
        if extra.fact.kind is not FactKind.UNKNOWN and extra.fact.topic not in shown:
            known.append(extra.fact)
            shown.add(extra.fact.topic)
    return capped([*known, *unknown])


def estimated_cost(scenario: ScenarioState, data: ZoneData, area: FloorArea) -> float | None:
    """The purchase price to buy, else the monthly rent (also without a budget)."""
    if scenario.budget is not None and scenario.budget.kind is BudgetKind.BUY:
        price = data.price.value if data.price is not None else None
        return None if price is None else float(purchase_cost(price, area.m2))
    rent = data.rent.value if data.rent is not None else None
    return None if rent is None else float(round(monthly_rent(rent, area.m2)))


def evaluate(scenario: ScenarioState, data: ZoneData) -> ZoneFit:
    area = assumed_floor_area(scenario)
    checks = constraint_checks(scenario, data, area)
    weighted = [(c.weight, score(c, scenario, data, area)) for c in criteria(scenario)]
    utility, confidence = match_and_confidence(weighted)
    if not weighted:  # nothing to score: the zone is as sure as its conditions
        confidence = min((c.confidence for c in checks), default=1.0)
    cost = estimated_cost(scenario, data, area)
    return ZoneFit(
        data=data,
        constraints=checks,
        utility=utility,
        confidence=confidence,
        facts=facts([s for _, s in weighted], data, limited_trips(scenario, data)),
        cost_eur=cost,
        lead_trip=lead_trip(scenario),
    )


def statuses(scenario: ScenarioState, data: ZoneData) -> list[ConstraintStatus]:
    """Only the conditions (no scoring): what the Reality Check recounts for each option."""
    area = assumed_floor_area(scenario)
    return [c.status for c in constraint_checks(scenario, data, area)]


def everyday_walk(data: ZoneData) -> tuple[float, float] | None:
    """How well the zone is served on foot in general (D-239): over every service the search
    measures (EVERYDAY_NEEDS, marked by the person or not) with data here, the mean utility
    with the default windows and the mean walking minutes. None without any of them."""
    measured = [
        (walk.value, DEFAULT_WALK_MINUTES[need])
        for need in EVERYDAY_NEEDS
        if (walk := data.walk.get(need)) is not None and walk.value is not None
    ]
    if not measured:
        return None
    utility = sum(walk_utility(minutes, window) for minutes, window in measured)
    shown = sum(min(minutes, MAX_WALK_SHOWN) for minutes, _ in measured)
    return utility / len(measured), shown / len(measured)


def lead_trip(scenario: ScenarioState) -> int | None:
    """The place whose minutes break ties (D-220): the first the person goes to; with full
    telework there, the first that keeps a limit (D-240). None if no trip counts at all."""
    places = list(enumerate(scenario.anchors))
    going = (i for i, anchor in places if counts(anchor))
    limited = (i for i, anchor in places if anchor.max_minutes is not None)
    return next(going, next(limited, None))


def near_miss_key(fit: ZoneFit) -> tuple[float, float, float, str]:
    """«Casi encajan»: best unrounded fit first; ties: more confidence, fewer minutes by public
    transport to the lead place (`lead_trip`: the first one the person goes to), then the zone
    id (D-220, D-240). Every near miss fails something, so the services at a walk do not
    reorder them (D-239). Never depends on the order the zones arrive in."""
    trip = None if fit.lead_trip is None else fit.data.commute.get(fit.lead_trip)
    minutes = trip.minutes if trip is not None and trip.minutes is not None else math.inf
    zone = fit.data.zone
    return (
        -(fit.utility if fit.utility is not None else -1.0),
        -fit.confidence,
        minutes,
        zone.admin_unit_id or f"{zone.level.value}:{zone.code}",
    )


def ranking_key(fit: ZoneFit) -> tuple[float, float, float, float, float, str]:
    """«Zonas que encajan»: best unrounded fit first. Only exact ties of it go on (D-239): more
    everyday services at a walk, then fewer walking minutes to them and, after them, as
    near_miss_key (confidence, minutes to the lead place, zone id)."""
    utility, confidence, minutes, zone_id = near_miss_key(fit)
    served, walk_minutes = everyday_walk(fit.data) or (-1.0, math.inf)
    return (utility, -served, walk_minutes, confidence, minutes, zone_id)
