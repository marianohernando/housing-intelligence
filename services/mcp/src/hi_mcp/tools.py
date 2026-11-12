"""The MCP tools as plain functions over a connection (MCP-001).

Each one calls the same service as its API route and returns the same envelope, so an agent,
the web and the API read the same numbers. No SQL here (CLAUDE.md §3): the services own it.
"""

from sqlalchemy import Connection

from hi_api.services.datasets import METHODOLOGY_VERSION as DATASETS_VERSION
from hi_api.services.datasets import dataset_list
from hi_api.services.explanation import explain_zone
from hi_api.services.gaps import zone_gap_list
from hi_api.services.search import search
from hi_api.services.zones import LOOKUP_VERSION, find_zones
from hi_contracts.api.envelope import ErrorCode, Meta
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.public import ScenarioState
from hi_contracts.public.responses import (
    DatasetListResponse,
    SearchResponse,
    ZoneExplanationResponse,
    ZoneGapListResponse,
    ZoneLookupResponse,
)


def search_zones(conn: Connection, scenario: ScenarioState, *, include_map: bool) -> SearchResponse:
    """POST /api/v1/search. Without the map, `all_zones` (every zone for the choropleth, about
    half of the answer) comes back empty; everything else is the same."""
    result, warnings, data_version = search(conn, scenario)
    if not include_map:
        result = result.model_copy(update={"all_zones": []})
    return SearchResponse(
        data=result,
        meta=Meta(methodology_version=result.methodology_version, data_version=data_version),
        warnings=warnings,
    )


def zone_gaps(conn: Connection, level: TerritoryLevel, code: str) -> ZoneGapListResponse:
    """GET /api/v1/gaps/{level}/{code}."""
    gaps, warnings, data_version = zone_gap_list(conn, level, code)
    return ZoneGapListResponse(
        data=gaps,
        meta=Meta(methodology_version=gaps.method.version, data_version=data_version),
        warnings=warnings,
    )


def zone_explanation(
    conn: Connection, level: TerritoryLevel, code: str, scenario: ScenarioState
) -> ZoneExplanationResponse:
    """The zone as its card in POST /api/v1/search, with its indicators and datasets."""
    explanation, warnings, data_version = explain_zone(conn, level, code, scenario)
    return ZoneExplanationResponse(
        data=explanation,
        meta=Meta(methodology_version=explanation.methodology_version, data_version=data_version),
        warnings=warnings,
    )


def zone_lookup(conn: Connection, name: str) -> ZoneLookupResponse:
    """Municipios and Madrid districts by name, with the codes the other tools take."""
    lookup = find_zones(conn, name)
    if not lookup.zones:
        warnings = [
            f"{ErrorCode.NOT_FOUND.value}: no municipio or Madrid district matches «{name}»"
        ]
    elif lookup.total > len(lookup.zones):
        left_out = lookup.total - len(lookup.zones)
        warnings = [f"{left_out} more zones match «{name}»: write more of the name"]
    else:
        warnings = []
    return ZoneLookupResponse(
        data=lookup, meta=Meta(methodology_version=LOOKUP_VERSION), warnings=warnings
    )


def datasets(conn: Connection, *, cm_only: bool) -> DatasetListResponse:
    """GET /api/v1/datasets."""
    return DatasetListResponse(
        data=dataset_list(conn, cm_only=cm_only), meta=Meta(methodology_version=DATASETS_VERSION)
    )
