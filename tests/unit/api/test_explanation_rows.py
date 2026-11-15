"""MCP explicar_zona (D-243): the rows of «Qué falta» whose datasets the explanation cites."""

from hi_api.services.explanation import cited_rows
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public import (
    GapHighlight,
    GapStatus,
    Household,
    NearbyNeed,
    NeedKey,
    PriorityKey,
    ScenarioState,
    ZoneRef,
)
from hi_domain.fit import Supply, ZoneData

ZONE = ZoneRef(level=TerritoryLevel.DISTRITO, code="2807906", name="Tetuán")


def _zone(highlighted: list[GapRowKey], rows: list[GapRowKey]) -> ZoneData:
    gaps = [GapHighlight(row=r, label=r.value, status=GapStatus.JUSTO) for r in highlighted]
    supply = {r: Supply(GapStatus.JUSTO, 0.9) for r in rows}
    return ZoneData(zone=ZONE, gaps=gaps, supply=supply)


def test_the_rows_the_pct_reads_are_cited_with_the_highlighted_ones() -> None:
    """A marked service scores its capacity from its row (D-243), so the explanation cites that
    row too, even when it is not among the card's 3; an unmarked service row is not cited."""
    data = _zone(
        [GapRowKey.CENTRO_SALUD, GapRowKey.FARMACIA, GapRowKey.VIVIENDA],
        [GapRowKey.ESCUELA_INFANTIL, GapRowKey.CENTRO_SALUD, GapRowKey.MAYORES],
    )
    scenario = ScenarioState(
        household=Household(adults=1),
        nearby=[NearbyNeed(need=NeedKey.ESCUELA_INFANTIL, max_walk_minutes=10, required=False)],
        priorities=[PriorityKey.SALUD],
    )
    assert cited_rows(data, scenario) == {
        GapRowKey.CENTRO_SALUD,
        GapRowKey.FARMACIA,
        GapRowKey.VIVIENDA,
        GapRowKey.ESCUELA_INFANTIL,
    }


def test_a_marked_row_the_zone_lacks_is_not_cited() -> None:
    data = _zone([GapRowKey.COLEGIO], [])
    scenario = ScenarioState(priorities=[PriorityKey.COLEGIOS, PriorityKey.SALUD])
    assert cited_rows(data, scenario) == {GapRowKey.COLEGIO}
