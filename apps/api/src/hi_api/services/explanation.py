"""One zone explained with its sources (MCP-001): the zone as POST /search sees it for one
scenario, with every indicator behind it and the datasets it reads (attribution included).

No new query: the zones, indicators, highlights and trips come from the search's own loader,
the facts from the same evaluation (hi_domain.fit.evaluate), the datasets of the highlighted
rows from the zone's own list (GET /gaps) and the rest from the same provenance as /search.
"""

from collections.abc import Iterable

from sqlalchemy import Connection

from hi_api.services.gaps import ZoneNotFoundError, dataset_refs, zone_gap_list
from hi_api.services.search import LEVELS, load, load_warnings
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.public import (
    DatasetRef,
    IndicatorValue,
    ScenarioState,
    ZoneExplanation,
)
from hi_domain.fit import FIT_VERSION, ZoneData, evaluate
from hi_domain.search import SPLIT_BY_DISTRICT


class ZoneNotInSearchError(LookupError):
    """The zone exists but the search does not rank it (Madrid capital goes by district)."""


def _indicators(data: ZoneData) -> list[IndicatorValue]:
    found = [data.rent, data.price, *data.walk.values(), *data.priority_walk.values()]
    return sorted((i for i in found if i is not None), key=lambda i: i.feature_id)


def _union(refs: Iterable[DatasetRef]) -> list[DatasetRef]:
    unique = {r.dataset_id: r for r in refs}
    return [unique[k] for k in sorted(unique)]


def _highlight_datasets(conn: Connection, data: ZoneData) -> list[DatasetRef]:
    """The datasets of the zone's highlighted rows, as its own list of what is missing cites
    them (the zone's level, its reference and the row's extras)."""
    if not data.gaps:
        return []
    rows = {h.row for h in data.gaps}
    gap_list, _, _ = zone_gap_list(conn, data.zone.level, data.zone.code)
    return [d for row in gap_list.rows if row.row in rows for d in row.datasets]


def _check_searchable(level: TerritoryLevel, code: str) -> None:
    if level not in LEVELS:
        msg = f"The search ranks municipios and Madrid districts, not {level.value}"
        raise ZoneNotInSearchError(msg)
    if level is TerritoryLevel.MUNICIPIO and code in SPLIT_BY_DISTRICT:
        msg = f"Municipio {code} is ranked by district: explain one of its districts"
        raise ZoneNotInSearchError(msg)


def explain_zone(
    conn: Connection, level: TerritoryLevel, code: str, scenario: ScenarioState
) -> tuple[ZoneExplanation, list[str], str | None]:
    """The explanation, the search warnings and the data version (latest computation)."""
    _check_searchable(level, code)
    loaded = load(conn, scenario)
    data = next((z for z in loaded.zones if z.zone.level == level and z.zone.code == code), None)
    if data is None:
        msg = f"No {level.value} with code {code}"
        raise ZoneNotFoundError(msg)
    fit = evaluate(scenario, data)
    indicators = _indicators(data)
    used = {d for i in indicators for d in i.datasets}
    versions = {d: v for d, v in loaded.versions.items() if d in used} | loaded.commute_versions
    datasets = _union([*dataset_refs(conn, versions), *_highlight_datasets(conn, data)])
    explanation = ZoneExplanation(
        zone=data.zone,
        scenario=scenario,
        match_pct=fit.match_pct,
        confidence=fit.confidence,
        facts=fit.facts,
        constraints=fit.constraints,
        estimated_cost_eur=fit.cost_eur,
        gap_highlights=list(data.gaps),
        indicators=indicators,
        datasets=datasets,
        cm_open_data_count=sum(d.is_cm_open_data for d in datasets),
        methodology_version=FIT_VERSION,
    )
    data_version = max(loaded.computed).date().isoformat() if loaded.computed else None
    return explanation, load_warnings(loaded), data_version
