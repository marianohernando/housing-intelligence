"""People search (CORE-003): rank the zones that pass every condition, show the near misses
apart and recount what each relaxed condition would add (Reality Check). Pure: the API
service loads the zones and their indicators; this module decides.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from hi_contracts.catalog.enums import GapRowKey
from hi_contracts.public import (
    ConstraintStatus,
    RankedZone,
    RealityCheck,
    ScenarioState,
    ZoneMatch,
)
from hi_domain.fit import ZoneData, ZoneFit, evaluate, near_miss_key, ranking_key
from hi_domain.reality_check import reality_check

RESULT_LIMIT, NEAR_MISS_LIMIT = 10, 5
# D-200: the search ranks municipios, with Madrid capital split into its 21 districts.
SPLIT_BY_DISTRICT = ("28079",)
HIGHLIGHTS = 3
INFANT_MAX_AGE = 2  # escuela infantil (0-3): first cycle of educación infantil


def highlight_rows(scenario: ScenarioState) -> list[GapRowKey]:
    """The 3 rows of «Qué falta aquí» that matter most to this household."""
    household = scenario.household
    ages = household.minor_ages
    rows: list[GapRowKey] = []
    if household.minors and (not ages or min(ages) <= INFANT_MAX_AGE):
        rows.append(GapRowKey.ESCUELA_INFANTIL)
    if household.minors:
        rows.append(GapRowKey.COLEGIO)
    if household.seniors_in_care:
        rows.append(GapRowKey.MAYORES)
    rows += [GapRowKey.CENTRO_SALUD, GapRowKey.FARMACIA, GapRowKey.VIVIENDA]
    return rows[:HIGHLIGHTS]


@dataclass(frozen=True)
class SearchOutcome:
    results: list[RankedZone]
    near_misses: list[RankedZone]
    all_zones: list[ZoneMatch]
    reality_check: RealityCheck
    unscored_passing: int  # zones passing every condition with no data to score them


def _ranked(
    fits: Sequence[ZoneFit], limit: int, key: Callable[[ZoneFit], tuple[float | str, ...]]
) -> list[RankedZone]:
    ordered = sorted((f for f in fits if f.match_pct is not None), key=key)
    return [
        RankedZone(
            rank=i,
            zone=fit.data.zone,
            match_pct=fit.match_pct or 0,
            confidence=fit.confidence,
            facts=fit.facts,
            constraints=fit.constraints,
            failed_constraints=fit.failed,
            estimated_cost_eur=fit.cost_eur,
            gap_highlights=list(fit.data.gaps),
        )
        for i, fit in enumerate(ordered[:limit], start=1)
    ]


def is_near_miss(fit: ZoneFit) -> bool:
    """Fails exactly one condition and passes the rest (an UNKNOWN is not an alternative)."""
    statuses = [c.status for c in fit.constraints]
    return statuses.count(ConstraintStatus.FAIL) == 1 and all(
        s is not ConstraintStatus.UNKNOWN for s in statuses
    )


def painted_match(fit: ZoneFit) -> int | None:
    """The % painted on the map. A zone with an UNKNOWN condition and no FAIL may or may not
    fit, so it is never painted as a fit (None); a zone that fails keeps its % to compare."""
    if not fit.failed and not fit.passes_all:
        return None
    return fit.match_pct


def run_search(scenario: ScenarioState, zones: Sequence[ZoneData]) -> SearchOutcome:
    fits = [evaluate(scenario, zone) for zone in zones]
    passing = [f for f in fits if f.passes_all]
    return SearchOutcome(
        results=_ranked(passing, RESULT_LIMIT, ranking_key),
        near_misses=_ranked([f for f in fits if is_near_miss(f)], NEAR_MISS_LIMIT, near_miss_key),
        all_zones=[
            ZoneMatch(
                zone=f.data.zone,
                match_pct=painted_match(f),
                passes_all=f.passes_all,
                failed_constraints=f.failed,
            )
            for f in fits
        ],
        reality_check=reality_check(scenario, zones, fits),
        unscored_passing=sum(f.match_pct is None for f in passing),
    )
