"""Residential Fit (CORE-003, D-215): hard conditions, then a % of fit with tangible facts.

Pipeline (CLAUDE.md §14): every zone gets its conditions checked as PASS / FAIL / UNKNOWN
(UNKNOWN never counts as PASS), then a % of fit from what the person asked for: their «Me
importa» priorities in their order, where they work, the services they want at a walk and the
budget margin. Each criterion has a utility from 0 to 1 (piecewise linear), the weights follow
the order (rank sum: the first of n weighs n, the last 1) and the % is the weighted mean over
the criteria the zone has data for. Criteria without data never count as 0: they lower the
confidence and show up as «sin datos» facts. A marked service scores its nearness and its
capacity as «Qué falta» measures it (D-243), and three limits keep the % from contradicting
the card: an impossible trip halves it, a FALTA in a marked service keeps it under «muy
bien» and a trip of more than an hour under «bien».
"""

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace

from hi_contracts.catalog.enums import GapRowKey
from hi_contracts.public import (
    Anchor,
    AnchorKind,
    BudgetKind,
    ConstraintCheck,
    ConstraintStatus,
    Fact,
    FactKind,
    FactTopic,
    GapHighlight,
    GapStatus,
    IndicatorValue,
    MatchBand,
    NearbyNeed,
    NeedKey,
    PriorityKey,
    ScenarioState,
    ZoneGapStatus,
    ZoneRef,
)
from hi_contracts.public.scenario import LEISURE_NEEDS
from hi_domain.affordability import (
    PURCHASE_ESTIMATE_NOTE,
    PURCHASE_MISSING_IN_CITY,
    FloorArea,
    assumed_floor_area,
    budget_check,
    monthly_rent,
    purchase_cost,
    purchase_explanation,
    rent_explanation,
    rent_range_eur,
)
from hi_domain.gaps import es_number

# 0.3: park (D-222); 0.4: step-free station (D-223); 0.5: buying (D-227); 0.6: rent of new
# leases and walking minutes read as approximate (D-228); 0.7: barrios inside a district, with a
# trip measured for the whole district and the reason for an unknown rent said (D-232); 0.8: a
# trip made 1-2 days a week weighs half and one never made is not scored (D-240), buying
# inside Madrid with an estimated price, said as such (D-234), and leisure, scored only when
# «Ocio» is chosen (D-236): one version for the whole batch. 0.9: «cerca y plazas» (D-243): every
# minute counts, a must scores too, a service scores its nearness and its capacity, the budget
# keeps a floor and a tail, three limits, and the list goes by the % shown
FIT_VERSION = "fit-0.9"
# Walking windows of CORE-005 (D-210): what «cerca» means for each service by default.
DEFAULT_WALK_MINUTES: dict[NeedKey, int] = {
    NeedKey.ESCUELA_INFANTIL: 10,
    NeedKey.COLEGIO: 10,
    NeedKey.CENTRO_SALUD: 15,
    NeedKey.FARMACIA: 10,
    NeedKey.MAYORES: 10,
    NeedKey.TRANSPORTE: 5,
    NeedKey.BARES: 10,
    NeedKey.RESTAURANTES: 10,
    NeedKey.GIMNASIOS: 10,
    NeedKey.CULTURA: 10,
}
WALK_ZERO_AT = 3.0  # utility falls linearly to 0 at three times the window
# D-243: every minute counts, also inside the window: 1 at the door, this at its edge, 0 at
# WALK_ZERO_AT times it. The same curve scores the trip by public transport against its window.
WALK_UTILITY_AT_WINDOW = 0.9
NEAR_KM, FAR_KM = 2.0, 20.0  # straight line to a place of work: 1 within 2 km, 0 from 20 km
STRAIGHT_LINE_CONFIDENCE = 0.5  # declared proxy: distance is not travel time
# Public transport (CORE-009, D-220): its window is 30 min (or the person's limit), scored as a
# walk: 0,9 at the window and none from 90 (3x); D-243: every minute counts below it too.
DEFAULT_COMMUTE_MINUTES = 30
# Telework (D-240): a trip made 1-2 days a week weighs half in the % of fit; from 3 days it
# weighs as always. A place never gone to (0 days) is not scored, but its limit still applies.
FEW_DAYS_PER_WEEK = 2
FEW_DAYS_WEIGHT = 0.5
BUDGET_MARGIN_SHARE = 0.25  # full utility when the cost is 75 % of the budget or less
# D-243: spending the whole budget scores this (0,6, where «regular» starts), not 0; past the
# budget the score falls from it to 0 at BUDGET_OVERRUN_TO_ZERO more. The budget condition
# already leaves those zones out, so the tail only orders «Casi encajan».
BUDGET_UTILITY_AT_LIMIT = 0.6
BUDGET_OVERRUN_TO_ZERO = 0.25
# D-243: a marked service with a row in «Qué falta» scores (1 - CAPACITY_WEIGHT) x its nearness
# + CAPACITY_WEIGHT x its capacity: 0 at CAPACITY_RATIO_ZERO times the reference of the row, 1
# from the reference up, linear in between. The ratio is the one the row shows (D-217).
CAPACITY_WEIGHT = 0.4
CAPACITY_RATIO_ZERO = 0.4
# D-243: the % in words (MatchBand), from the % shown. The web derives the same band when an older
# API sends none: change these only together with it.
MUY_BIEN_FROM, BIEN_FROM, REGULAR_FROM = 90, 75, 60
# D-243: what limits the % whatever the rest scores. A trip made LIMIT_DAYS days a week or more
# that scores 0 (WALK_ZERO_AT times its window or more, or no arrival by 9:00) halves the fit; one
# over LONG_TRIP_WINDOWS times its window (60 min with the default 30) keeps it at LONG_TRIP_CAP,
# shown as 74 %, never «bien». FALTA in «Qué falta» for a service the person marks keeps it at
# SHORTAGE_CAP, shown as 89 %, never «muy bien».
LIMIT_DAYS = 3
UNREACHABLE_FACTOR = 0.5
LONG_TRIP_WINDOWS = 2.0
LONG_TRIP_CAP = 0.744
SHORTAGE_CAP = 0.894
MAX_WALK_SHOWN = 60

NEED_TEXT: dict[NeedKey, tuple[str, str]] = {  # (fact label, «de …» in a sentence)
    NeedKey.ESCUELA_INFANTIL: ("Escuela infantil", "una escuela infantil"),
    NeedKey.COLEGIO: ("Colegio con primaria", "un colegio con primaria"),
    NeedKey.CENTRO_SALUD: ("Centro de salud", "un centro de salud"),
    NeedKey.FARMACIA: ("Farmacia", "una farmacia"),
    NeedKey.MAYORES: ("Centro de mayores", "un centro de mayores"),
    NeedKey.TRANSPORTE: ("Parada de transporte público", "una parada de transporte público"),
    NeedKey.BARES: ("Bares y cafeterías", "un bar o una cafetería"),
    NeedKey.RESTAURANTES: ("Restaurantes", "un restaurante"),
    NeedKey.GIMNASIOS: ("Gimnasios y deporte", "un gimnasio o un centro deportivo"),
    NeedKey.CULTURA: (
        "Cultura",
        "un museo, una biblioteca, un teatro, un cine o un centro cultural",
    ),
}
NEED_TOPIC: dict[NeedKey, FactTopic] = {
    NeedKey.ESCUELA_INFANTIL: FactTopic.COLEGIOS,
    NeedKey.COLEGIO: FactTopic.COLEGIOS,
    NeedKey.CENTRO_SALUD: FactTopic.SALUD,
    NeedKey.FARMACIA: FactTopic.SALUD,
    NeedKey.MAYORES: FactTopic.OTRO,
    NeedKey.TRANSPORTE: FactTopic.TRANSPORTE,
    NeedKey.BARES: FactTopic.OCIO,
    NeedKey.RESTAURANTES: FactTopic.OCIO,
    NeedKey.GIMNASIOS: FactTopic.OCIO,
    NeedKey.CULTURA: FactTopic.OCIO,
}
PRIORITY_NEED: dict[PriorityKey, NeedKey] = {
    PriorityKey.TRANSPORTE: NeedKey.TRANSPORTE,
    PriorityKey.SALUD: NeedKey.CENTRO_SALUD,
    PriorityKey.COLEGIOS: NeedKey.COLEGIO,
}
# D-243: the row of «Qué falta» that measures the capacity of each service (D-217). Transport and
# leisure have none.
NEED_ROW: dict[NeedKey, GapRowKey] = {
    NeedKey.ESCUELA_INFANTIL: GapRowKey.ESCUELA_INFANTIL,
    NeedKey.COLEGIO: GapRowKey.COLEGIO,
    NeedKey.CENTRO_SALUD: GapRowKey.CENTRO_SALUD,
    NeedKey.FARMACIA: GapRowKey.FARMACIA,
    NeedKey.MAYORES: GapRowKey.MAYORES,
}
# Each row inside a sentence, as `fila.lista.*` of pitch/textos_web.md
ROW_IN_TEXT: dict[GapRowKey, str] = {
    GapRowKey.ESCUELA_INFANTIL: "escuelas infantiles",
    GapRowKey.COLEGIO: "colegios",
    GapRowKey.CENTRO_SALUD: "centros de salud",
    GapRowKey.FARMACIA: "farmacias",
    GapRowKey.MAYORES: "centros de mayores",
}


@dataclass(frozen=True)
class PriorityWalk:
    """A priority measured by walking to a kind of place (D-222): what the fact calls it, the
    window (WALK_UTILITY_AT_WINDOW at its edge, D-243) and what to say beyond the walking range
    (WALK_ZERO_AT x window), where the place is not at a walk but what the person means may be
    (the countryside)."""

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
# D-239: what breaks an exact tie of the fit, the six everyday services measured on foot (marked
# or not). Never the leisure groups (D-236): they only count when the person marks «Ocio».
EVERYDAY_NEEDS = (
    NeedKey.ESCUELA_INFANTIL,
    NeedKey.COLEGIO,
    NeedKey.CENTRO_SALUD,
    NeedKey.FARMACIA,
    NeedKey.MAYORES,
    NeedKey.TRANSPORTE,
)
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
class Supply:
    """One service's row of «Qué falta» in the zone, as the % reads it (D-243): its status and
    the ratio to the reference that scores its capacity. `district`: a barrio has no row of its
    own and takes its district's, named here (a declared proxy, as on its card, D-238 §7)."""

    status: GapStatus
    ratio: float | None  # None: too small to compare, with no group of neighbours (never 0)
    confidence: float = 1.0
    district: str | None = None


def supply(row: ZoneGapStatus, district: str | None = None) -> Supply:
    """The ratio the row's status comes from: its group's when the zone is compared with its
    neighbours (D-217); none when the zone alone is too small to compare (D-213), so that only
    its nearness counts. The same ratio «Qué falta» shows, so the % and the card agree."""
    ratio = row.ratio_to_reference
    if ratio is not None and row.comparison_group is not None:
        ratio = row.comparison_group.ratio_to_reference
    elif not row.reliable:
        ratio = None
    return Supply(row.status, None if ratio is None else float(ratio), row.confidence, district)


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
    price_estimated: bool = False  # `price` is an estimate, not a published value (D-234)
    rent_note: str | None = None  # what the rent figure is, from its feature (D-228)
    rent_missing: str | None = None  # why there is no rent here, in plain words (D-232)
    # Walking minutes to a bus stop and to a Metro/Cercanías station, by mode ("bus", "metro").
    # They only word the transport fact, never score it (D-233); empty until the data is synced.
    transit: Mapping[str, IndicatorValue] = field(default_factory=dict[str, IndicatorValue])
    # D-242: with the Ministry's rent reference (where the CM publishes none), the 25th and 75th
    # percentiles per m² scaled as the rent, and who publishes them and when (the card label)
    rent_range: tuple[float, float] | None = None
    rent_source: str | None = None
    # D-243: «Qué falta» of every service row (NEED_ROW), whether the person marks it or not: the
    # capacity of a marked service and FALTA in it shape the %. Empty: nearness alone, no limit.
    supply: Mapping[GapRowKey, Supply] = field(default_factory=dict[GapRowKey, Supply])


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
class Limit:
    """What limited the % of a zone (D-243), said first on its card. `pinned`: the facts that
    must stay with it (itself, and the trip it speaks of); `replaces`: a fact it says again,
    left out (the trip that does not arrive by 9:00)."""

    utility: float
    fact: Fact
    pinned: tuple[Fact, ...] = ()
    replaces: tuple[Fact, ...] = ()


@dataclass(frozen=True)
class ZoneFit:
    data: ZoneData
    constraints: list[ConstraintCheck]
    utility: float | None  # unrounded % / 100: ranks before the rounding
    confidence: float
    facts: list[Fact]
    cost_eur: float | None
    cost_confidence: float | None = None  # how sure `cost_eur` is: its price or rent's
    # D-242: where half the leases fall for the household's area (€/month) and its source
    cost_range: tuple[float, float] | None = None
    cost_source: str | None = None
    # Index in `anchors` of the place whose minutes break ties (lead_trip, D-240); None = none
    lead_trip: int | None = 0

    @property
    def match_pct(self) -> int | None:
        return as_pct(self.utility)

    @property
    def match_band(self) -> MatchBand | None:
        """The % in words, only for a zone that passes every condition (D-243): one that fails
        (a near miss) or cannot be checked reads by what it misses, never «muy bien». Its
        `match_pct` stays, for the order and the API."""
        return match_band(self.match_pct) if self.passes_all else None

    @property
    def failed(self) -> list[str]:
        return [c.constraint_id for c in self.constraints if c.status is ConstraintStatus.FAIL]

    @property
    def passes_all(self) -> bool:
        return all(c.status is ConstraintStatus.PASS for c in self.constraints)


def clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def walk_utility(minutes: float, target: float) -> float:
    """D-243: 1 at the door, WALK_UTILITY_AT_WINDOW at the edge of the window and 0 at
    WALK_ZERO_AT times it, linear in between: every minute counts, so zones within the window
    no longer all tie at 1."""
    if minutes <= target:
        return 1 - (1 - WALK_UTILITY_AT_WINDOW) * max(minutes, 0.0) / target
    zero_at = WALK_ZERO_AT * target
    return clamp01(WALK_UTILITY_AT_WINDOW * (zero_at - minutes) / ((WALK_ZERO_AT - 1) * target))


def distance_utility(km: float) -> float:
    return clamp01((FAR_KM - km) / (FAR_KM - NEAR_KM))


def budget_utility(cost: float, budget: float) -> float:
    """1 up to the budget minus its margin (a cheaper zone is not better, D-239), down to
    BUDGET_UTILITY_AT_LIMIT spending all of it, then to 0 at BUDGET_OVERRUN_TO_ZERO more (D-243):
    a zone just over the budget is a near miss, not a 0 %."""
    share = cost / budget
    knee = 1 - BUDGET_MARGIN_SHARE
    if share <= knee:
        return 1.0
    if share <= 1:
        return 1 - (1 - BUDGET_UTILITY_AT_LIMIT) * (share - knee) / (1 - knee)
    return clamp01(BUDGET_UTILITY_AT_LIMIT * (1 - (share - 1) / BUDGET_OVERRUN_TO_ZERO))


def match_band(pct: int | None) -> MatchBand | None:
    """The % shown in words (D-243): muy bien from 90, bien from 75, regular from 60, else
    poco. None for an unknown %. A zone gets it only when it passes every condition
    (ZoneFit.match_band)."""
    if pct is None:
        return None
    if pct >= MUY_BIEN_FROM:
        return MatchBand.MUY_BIEN
    if pct >= BIEN_FROM:
        return MatchBand.BIEN
    if pct >= REGULAR_FROM:
        return MatchBand.REGULAR
    return MatchBand.POCO


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


def leisure_needs(scenario: ScenarioState) -> list[NearbyNeed]:
    """The leisure groups the person ticked under «Ocio», in the order of its configurator."""
    chosen = {n.need: n for n in scenario.nearby}
    return [chosen[need] for need in LEISURE_NEEDS if need in chosen]


def ignored_leisure(scenario: ScenarioState) -> list[NeedKey]:
    """Leisure groups in `nearby` without the priority «ocio», as the API or the MCP may send
    them (D-236): never a criterion nor a condition (`required` is True by default, so they would
    filter). The API says so in a warning."""
    if PriorityKey.OCIO in scenario.priorities:
        return []
    return [n.need for n in scenario.nearby if n.need in LEISURE_NEEDS]


def counted_nearby(scenario: ScenarioState) -> list[NearbyNeed]:
    """`nearby` as the search reads it: without the ignored leisure groups."""
    ignored = set(ignored_leisure(scenario))
    return [n for n in scenario.nearby if n.need not in ignored]


def _criteria_keys(scenario: ScenarioState) -> list[Criterion]:
    """The person's criteria in order of importance, before weighting: priorities, places, the
    services wished at a walk, those marked as a must (D-243: they score too, not only filter)
    and the budget. «Ocio» is one criterion for all its groups (D-236), so four boxes never
    outweigh the other priorities, also as a must; without a group there is nothing to measure
    and it adds no criterion."""
    keys: list[Criterion] = []
    covered: set[NeedKey] = set()
    nearby_counted = counted_nearby(scenario)
    windows = {n.need: n.max_walk_minutes for n in nearby_counted}
    for priority in scenario.priorities:
        if priority is PriorityKey.OCIO:
            groups = leisure_needs(scenario)
            covered.update(n.need for n in groups)
            if groups:
                keys.append(Criterion(f"priority:{priority.value}", 0.0, priority=priority))
            continue
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
    wished = [n for n in nearby_counted if n.need not in covered]  # not among the priorities
    for nearby in [*(n for n in wished if not n.required), *(n for n in wished if n.required)]:
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


# The places one has to reach by a time: work and study. To family or home one goes at other
# hours, so their trip does not say «llegando a las 9:00» (D-245), although it is measured the
# same way, with the timetables of a weekday arriving at 9:00 (D-220, D-240 §proxy).
ARRIVE_BY_NINE = frozenset({AnchorKind.WORK, AnchorKind.STUDY})


def at_nine(anchor: Anchor) -> str:
    """« a las 9:00» for the places one has to reach by then (work, study); nothing otherwise."""
    return " a las 9:00" if anchor.kind in ARRIVE_BY_NINE else ""


def commute_text(minutes: float, anchor: Anchor, note: str | None = None) -> str:
    shown = "más de 2 h" if minutes > MAX_COMMUTE_SHOWN else f"{es_number(minutes, 0)} min"
    by_nine = ", llegando a las 9:00" if anchor.kind in ARRIVE_BY_NINE else ""
    return with_note(f"{shown} en transporte público hasta {anchor.label}{by_nine}", note)


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
            else f"Con los horarios publicados no se llega a {anchor.label}{at_nine(anchor)}"
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
            explanation=commute_text(trip.minutes, anchor, trip.note),
        )
    passed = anchor.max_minutes is not None and trip.minutes <= anchor.max_minutes
    return ConstraintCheck(
        **base,
        status=ConstraintStatus.PASS if passed else ConstraintStatus.FAIL,
        value=round(trip.minutes, 1),
        confidence=trip.confidence,
        explanation=commute_text(trip.minutes, anchor, trip.note),
    )


def constraint_checks(
    scenario: ScenarioState, data: ZoneData, area: FloorArea
) -> list[ConstraintCheck]:
    checks: list[ConstraintCheck] = []
    if scenario.budget is not None:
        checks.append(
            budget_check(
                scenario.budget,
                data.rent,
                area,
                data.price,
                data.rent_note,
                data.rent_missing,
                purchase_note(data),
                purchase_missing(data),
                data.rent_range,
            )
        )
    for nearby in counted_nearby(scenario):
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
    """Walking minutes to the place a priority measures, as any walk (walk_utility): 0,9 at the
    window and 0 at the walking range (WALK_ZERO_AT x window). Beyond it, 0 with `out_of_range`
    as the fact and low confidence; never UNKNOWN, which would rank a zone without the place
    above one with it far."""
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


@dataclass(frozen=True)
class LeisureGroup:
    """One group of «Ocio» in a zone: how the fact says it and, with data, its score."""

    text: str
    walk: IndicatorValue | None = None  # None: no data
    utility: float = 0.0
    confidence: float = 0.0
    near: bool = False  # within the minutes the person asked for


def leisure_group(nearby: NearbyNeed, walk: IndicatorValue | None) -> LeisureGroup:
    """Beyond the walking range a group scores 0 with low confidence: in OpenStreetMap the
    place may exist and not be mapped (D-236)."""
    name = NEED_TEXT[nearby.need][0].lower()
    if walk is None or walk.value is None:
        return LeisureGroup(f"{name}: sin datos")
    target = nearby.max_walk_minutes
    out_of_range = walk.value > WALK_ZERO_AT * target
    return LeisureGroup(
        text=f"{name} a {about_minutes(walk.value)}",
        walk=walk,
        utility=walk_utility(walk.value, target),
        confidence=min(walk.confidence, OUT_OF_RANGE_CONFIDENCE)
        if out_of_range
        else walk.confidence,
        near=walk.value <= target,
    )


def leisure_fact(groups: Sequence[NearbyNeed], walk: Mapping[NeedKey, IndicatorValue]) -> Score:
    """«Ocio» (D-236): the mean utility of the ticked groups that have data, each against its
    own minutes, in one fact («Ocio a pie: bares y cafeterías a unos 3 min, gimnasios a unos
    12 min»). A group without data lowers the confidence, never the score nor the kind: a strength
    when every group with data is within its minutes; the indicator is the farthest group's."""
    parts = [leisure_group(n, walk.get(n.need)) for n in groups]
    known = [g for g in parts if g.walk is not None]
    if not known:
        text = "Ocio: sin datos de distancia a pie en esta zona"
        fact = Fact(kind=FactKind.UNKNOWN, topic=FactTopic.OCIO, text=text, confidence=0.0)
        return Score(None, 0.0, fact)
    confidence = round(sum(g.confidence for g in known) / len(parts), 3)
    farthest = max(known, key=lambda g: (g.walk and g.walk.value) or 0.0)
    fact = Fact(
        kind=FactKind.STRENGTH if all(g.near for g in known) else FactKind.WEAKNESS,
        topic=FactTopic.OCIO,
        text="Ocio a pie: " + ", ".join(g.text for g in parts),
        confidence=confidence,
        indicator=farthest.walk,
    )
    return Score(sum(g.utility for g in known) / len(known), confidence, fact)


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
            f"Con los horarios publicados no se llega a {anchor.label}{at_nine(anchor)} "
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
        text=commute_text(trip.minutes, anchor, trip.note),
        confidence=trip.confidence,
    )
    return Score(walk_utility(trip.minutes, target), trip.confidence, fact)


def cost_fact(
    rent: IndicatorValue | None,
    area: FloorArea,
    budget: float | None,
    note: str | None = None,
    missing: str | None = None,
    range_m2: tuple[float, float] | None = None,
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
        text=rent_explanation(rent.value, area, note, range_m2),
        confidence=rent.confidence,
        indicator=rent,
    )
    utility = None if budget is None else budget_utility(cost, budget)
    return Score(utility, rent.confidence, fact)


def purchase_note(data: ZoneData) -> str | None:
    """What the purchase price of the zone is when it is an estimate (D-234); None for a
    published appraised value."""
    if not data.price_estimated:
        return None
    zone = "del barrio" if data.zone.level.value == "barrio" else "del distrito"
    return PURCHASE_ESTIMATE_NOTE.format(city=data.zone.municipio_name or "la ciudad", zone=zone)


def purchase_missing(data: ZoneData) -> str | None:
    """Why a district or barrio has no purchase price (D-234): the city's appraised value is not
    published by district, and the estimate is missing (not synced yet, or no cadastral data).
    None for a municipio, which keeps the usual reason."""
    if data.zone.level.value not in {"distrito", "barrio"}:
        return None
    return PURCHASE_MISSING_IN_CITY.format(city=data.zone.municipio_name or "la ciudad")


def purchase_fact(
    price: IndicatorValue | None, area: FloorArea, budget: float, note: str | None = None
) -> Score:
    """Buying (D-227): the appraised value for the needed area against the budget; `note` says
    so when the price is an estimate (D-234)."""
    if price is None or price.value is None:
        text = "Compra: sin precio publicado para esta zona"
        fact = Fact(kind=FactKind.UNKNOWN, topic=FactTopic.COSTE, text=text, confidence=0.0)
        return Score(None, 0.0, fact)
    cost = purchase_cost(price.value, area.m2)
    fact = Fact(
        kind=FactKind.STRENGTH if cost <= budget else FactKind.WEAKNESS,
        topic=FactTopic.COSTE,
        text=purchase_explanation(price.value, area, note),
        confidence=price.confidence,
        indicator=price,
    )
    return Score(budget_utility(cost, budget), price.confidence, fact)


def capacity_utility(ratio: float) -> float:
    """0 at CAPACITY_RATIO_ZERO times the reference, 1 from the reference up (D-243)."""
    return clamp01((ratio - CAPACITY_RATIO_ZERO) / (1 - CAPACITY_RATIO_ZERO))


def with_capacity(walked: Score, need: NeedKey, data: ZoneData) -> Score:
    """A service scores its nearness and its capacity (D-243), when its row of «Qué falta»
    gives a ratio; otherwise its nearness alone. The fact still says the walking minutes."""
    row = NEED_ROW.get(need)
    found = None if row is None else data.supply.get(row)
    if walked.utility is None or found is None or found.ratio is None:
        return walked
    capacity = capacity_utility(found.ratio)
    return replace(
        walked, utility=(1 - CAPACITY_WEIGHT) * walked.utility + CAPACITY_WEIGHT * capacity
    )


def score(criterion: Criterion, scenario: ScenarioState, data: ZoneData, area: FloorArea) -> Score:
    if criterion.need is not None:
        target = criterion.target_minutes or DEFAULT_WALK_MINUTES[criterion.need]
        walked = walk_fact(criterion.need, data.walk.get(criterion.need), target, data.transit)
        return with_capacity(walked, criterion.need, data)
    if criterion.anchor is not None:
        trip = None if criterion.anchor_index is None else data.commute.get(criterion.anchor_index)
        return work_fact(criterion.anchor, data, trip)
    if criterion.priority is PriorityKey.OCIO:
        return leisure_fact(leisure_needs(scenario), data.walk)
    if criterion.priority is not None:
        measured = PRIORITY_WALK.get(criterion.priority)
        if measured is not None:
            return priority_walk_fact(measured, data.priority_walk.get(criterion.priority))
        topic, text = NO_DATA_PRIORITY[criterion.priority]
        return Score(None, 0.0, Fact(kind=FactKind.UNKNOWN, topic=topic, text=text, confidence=0))
    if scenario.budget is not None and scenario.budget.kind is BudgetKind.BUY:
        return purchase_fact(
            data.price, area, float(scenario.budget.amount_eur), purchase_note(data)
        )
    budget = None if scenario.budget is None else float(scenario.budget.amount_eur)
    return cost_fact(data.rent, area, budget, data.rent_note, data.rent_missing, data.rent_range)


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


def capped(ordered: list[Fact], pinned: Sequence[Fact] = ()) -> list[Fact]:
    """At most MAX_FACTS, in order of importance. The cost (it only exists with a budget) and
    the `pinned` facts always stay: if they would fall, the least important of the others go
    instead (D-240: with three priorities, work and family the cost was the sixth)."""
    cost = next((i for i, f in enumerate(ordered) if f.topic is FactTopic.COSTE), None)
    keep = {i for i, f in enumerate(ordered) if any(f is p for p in pinned)}
    keep |= set() if cost is None else {cost}
    others = [i for i in range(len(ordered)) if i not in keep]
    chosen = keep | set(others[: max(MAX_FACTS - len(keep), 0)])
    return [ordered[i] for i in sorted(chosen)]


def facts(
    scores: Sequence[Score],
    data: ZoneData,
    trips: Sequence[Fact] = (),
    limit: Limit | None = None,
) -> list[Fact]:
    """3-5 facts: what limits the % (D-243), the criteria with data in order of importance,
    the minutes to a limited place nobody goes to (`trips`, without weight), then context
    (walking minutes) when the person asked for fewer than three things, then the criteria
    without data («sin datos»). The limit and the trip it speaks of always stay. Rent only
    shows up with a rent budget: without one there is nothing to say whether it is good or bad
    for this person."""
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
    if limit is None:
        return capped([*known, *unknown])
    kept = [f for f in [*known, *unknown] if not any(f is r for r in limit.replaces)]
    return capped([limit.fact, *kept], limit.pinned)


def cost_indicator(scenario: ScenarioState, data: ZoneData) -> IndicatorValue | None:
    """What the estimated cost comes from: the price per m² to buy, else the rent."""
    if scenario.budget is not None and scenario.budget.kind is BudgetKind.BUY:
        return data.price
    return data.rent


def estimated_cost(scenario: ScenarioState, data: ZoneData, area: FloorArea) -> float | None:
    """The purchase price to buy, else the monthly rent (also without a budget)."""
    source = cost_indicator(scenario, data)
    if source is None or source.value is None:
        return None
    if scenario.budget is not None and scenario.budget.kind is BudgetKind.BUY:
        return float(purchase_cost(source.value, area.m2))
    return float(round(monthly_rent(source.value, area.m2)))


def cost_range(
    scenario: ScenarioState, data: ZoneData, area: FloorArea
) -> tuple[float, float] | None:
    """Where half the leases fall for the household's area (D-242): only renting (or without a
    budget) and only with the quartiles of the Ministry's reference."""
    buying = scenario.budget is not None and scenario.budget.kind is BudgetKind.BUY
    if buying or data.rent_range is None or data.rent is None or data.rent.value is None:
        return None
    return rent_range_eur(data.rent_range, area)


def es_list(items: Sequence[str]) -> str:
    """«a», «a y b», «a, b y c»."""
    if len(items) <= 1:
        return "".join(items)
    return f"{', '.join(items[:-1])} y {items[-1]}"


def duration_text(minutes: float) -> str:
    """«45 min», «1 h», «1 h 30»."""
    hours, rest = divmod(round(minutes), 60)
    if not hours:
        return f"{rest} min"
    return f"{hours} h" if not rest else f"{hours} h {rest}"


def trip_window(anchor: Anchor) -> int:
    """The minutes a trip is measured against: the person's limit, else 30 (D-220)."""
    return anchor.max_minutes or DEFAULT_COMMUTE_MINUTES


def frequent_trips(scenario: ScenarioState, data: ZoneData) -> list[tuple[int, Anchor, Commute]]:
    """The computed trips to the places gone to LIMIT_DAYS days a week or more: only they limit
    the % (D-243). A place without a computed trip limits nothing (never read as a 0)."""
    return [
        (i, anchor, trip)
        for i, anchor in enumerate(scenario.anchors)
        if anchor.days_per_week >= LIMIT_DAYS and (trip := data.commute.get(i)) is not None
    ]


def unreachable(anchor: Anchor, trip: Commute) -> bool:
    """The trip scores 0: no arrival by 9:00, or WALK_ZERO_AT times its window or more."""
    return trip.minutes is None or trip.minutes >= WALK_ZERO_AT * trip_window(anchor)


def too_long(anchor: Anchor, trip: Commute) -> bool:
    """More than LONG_TRIP_WINDOWS times its window: over an hour with the default 30 min."""
    return trip.minutes is None or trip.minutes > LONG_TRIP_WINDOWS * trip_window(anchor)


def marked_rows(scenario: ScenarioState) -> list[GapRowKey]:
    """The rows of «Qué falta» of the services the person marks, in «Me importa» or at a walk
    (a must or not), in the person's order (D-243)."""
    needs = [PRIORITY_NEED[p] for p in scenario.priorities if p in PRIORITY_NEED]
    needs += [n.need for n in counted_nearby(scenario)]
    return list(dict.fromkeys(NEED_ROW[n] for n in needs if n in NEED_ROW))


def short_rows(scenario: ScenarioState, data: ZoneData) -> list[GapRowKey]:
    """The marked rows where «Qué falta» says FALTA (a barrio: its district's)."""
    return [
        row
        for row in marked_rows(scenario)
        if (found := data.supply.get(row)) is not None and found.status is GapStatus.FALTA
    ]


def unreachable_fact(anchor: Anchor, trip: Commute) -> Fact:
    if trip.minutes is None:
        why = f"No llegas a {anchor.label}{at_nine(anchor)} en transporte público"
    else:
        limit = duration_text(WALK_ZERO_AT * trip_window(anchor))
        why = f"Tardas {limit} o más en llegar a {anchor.label}"
    # In plain words (review R-09 of PR #79): the card no longer says «encaje»
    text = f"{why}: el % se queda en la mitad"
    return Fact(
        kind=FactKind.WEAKNESS, topic=FactTopic.TRAYECTO, text=text, confidence=trip.confidence
    )


def long_trip_fact(anchor: Anchor, trip: Commute) -> Fact:
    over = duration_text(LONG_TRIP_WINDOWS * trip_window(anchor))
    text = f"Más de {over} de trayecto hasta {anchor.label}: como mucho {as_pct(LONG_TRIP_CAP)} %"
    return Fact(
        kind=FactKind.WEAKNESS, topic=FactTopic.TRAYECTO, text=text, confidence=trip.confidence
    )


def shortage_fact(rows: Sequence[GapRowKey], data: ZoneData) -> Fact:
    found = [data.supply[row] for row in rows]
    district = found[0].district
    where = "" if district is None else f" en {district}"
    names = es_list([ROW_IN_TEXT[row] for row in rows])
    first = next(need for need, row in NEED_ROW.items() if row == rows[0])
    return Fact(
        kind=FactKind.WEAKNESS,
        topic=NEED_TOPIC[first],
        text=f"Faltan {names}{where}: como mucho {as_pct(SHORTAGE_CAP)} %",
        confidence=min(s.confidence for s in found),
    )


Scored = Sequence[tuple[Criterion, Score]]


def trip_limit(
    found: tuple[int, Anchor, Commute], utility: float, fact: Fact, scored: Scored
) -> Limit:
    """A limit set by a trip keeps on the card the fact with its minutes (its place's score).
    Without minutes (no arrival by 9:00) that fact would say the same again: the limit replaces
    it."""
    own = tuple(s.fact for c, s in scored if c.anchor_index == found[0])
    if found[2].minutes is None:
        return Limit(utility, fact, (fact,), own)
    return Limit(utility, fact, (fact, *own))


def limit(
    scenario: ScenarioState, data: ZoneData, utility: float | None, scored: Scored
) -> Limit | None:
    """D-243, in this order: a trip of LIMIT_DAYS days or more that scores 0 halves the fit; FALTA
    in a marked service keeps it at SHORTAGE_CAP; a trip of LIMIT_DAYS days or more over
    LONG_TRIP_WINDOWS times its window keeps it at LONG_TRIP_CAP. The card says the one that sets
    the % (once halved, no cap is reached). None when nothing limits it."""
    if utility is None:
        return None
    trips = frequent_trips(scenario, data)
    found: Limit | None = None
    far = next((t for t in trips if unreachable(t[1], t[2])), None)
    if far is not None:
        utility *= UNREACHABLE_FACTOR
        found = trip_limit(far, utility, unreachable_fact(far[1], far[2]), scored)
    short = short_rows(scenario, data)
    if short and utility > SHORTAGE_CAP:
        utility = SHORTAGE_CAP
        fact = shortage_fact(short, data)
        found = Limit(utility, fact, (fact,))
    long = next((t for t in trips if too_long(t[1], t[2])), None)
    if long is not None and utility > LONG_TRIP_CAP:
        utility = LONG_TRIP_CAP
        found = trip_limit(long, utility, long_trip_fact(long[1], long[2]), scored)
    return found


def evaluate(scenario: ScenarioState, data: ZoneData) -> ZoneFit:
    area = assumed_floor_area(scenario)
    checks = constraint_checks(scenario, data, area)
    scored = [(c, score(c, scenario, data, area)) for c in criteria(scenario)]
    utility, confidence = match_and_confidence([(c.weight, s) for c, s in scored])
    if not scored:  # nothing to score: the zone is as sure as its conditions
        confidence = min((c.confidence for c in checks), default=1.0)
    scores = [s for _, s in scored]
    limited = limit(scenario, data, utility, scored)
    cost = estimated_cost(scenario, data, area)
    source = cost_indicator(scenario, data)
    spread = cost_range(scenario, data, area)
    return ZoneFit(
        data=data,
        constraints=checks,
        utility=utility if limited is None else limited.utility,
        confidence=confidence,
        facts=facts(scores, data, limited_trips(scenario, data), limited),
        cost_eur=cost,
        cost_confidence=None if cost is None or source is None else source.confidence,
        cost_range=spread,
        cost_source=data.rent_source if spread is not None else None,
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


def near_miss_key(fit: ZoneFit) -> tuple[float, float, float, float, str]:
    """«Casi encajan»: best unrounded fit first; ties: more confidence, fewer minutes by public
    transport to the lead place (`lead_trip`: the first one the person goes to; D-220, D-240),
    the lower cost (D-234: from 25 % over a budget to buy, the zones all score 0 on it, so the
    one closest to it comes first), then the zone id. Every near miss fails something, so the
    services at a walk do not reorder them (D-239). Never depends on the order the zones arrive
    in."""
    trip = None if fit.lead_trip is None else fit.data.commute.get(fit.lead_trip)
    minutes = trip.minutes if trip is not None and trip.minutes is not None else math.inf
    zone = fit.data.zone
    return (
        -(fit.utility if fit.utility is not None else -1.0),
        -fit.confidence,
        minutes,
        fit.cost_eur if fit.cost_eur is not None else math.inf,
        zone.admin_unit_id or f"{zone.level.value}:{zone.code}",
    )


def ranking_key(fit: ZoneFit) -> tuple[float, float, float, float, float, float, str]:
    """«Zonas que encajan»: the best % shown first (D-243: two zones read at the same % are a
    tie, so a hair of unrounded fit no longer puts a less served zone ahead). Ties go on (D-239):
    more everyday services at a walk, fewer walking minutes to them, then the unrounded fit and,
    as near_miss_key, confidence, minutes to the lead place and zone id, without the cost: with
    plenty of budget the cheapest zones would be the towns again (D-239)."""
    utility, confidence, minutes, _cost, zone_id = near_miss_key(fit)
    served, walk_minutes = everyday_walk(fit.data) or (-1.0, math.inf)
    pct = -(fit.match_pct if fit.match_pct is not None else -1)
    return (pct, -served, walk_minutes, utility, confidence, minutes, zone_id)
