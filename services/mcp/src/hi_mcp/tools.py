"""The MCP tools as plain functions over a connection (MCP-001, D-249).

Each one calls the same service as its API route and returns the same envelope, so an agent,
the web and the API read the same numbers. No SQL here (CLAUDE.md §3): the services own it.
"""

import re
from collections.abc import Sequence

from sqlalchemy import Connection

from hi_api.services import investors as investor_service
from hi_api.services.datasets import METHODOLOGY_VERSION as DATASETS_VERSION
from hi_api.services.datasets import dataset_list
from hi_api.services.explanation import explain_zone
from hi_api.services.gaps import zone_gap_list
from hi_api.services.scope import search
from hi_api.services.zones import LOOKUP_VERSION, find_zones
from hi_contracts.api.envelope import ErrorCode, Meta
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.pro.investors import ViabilityRequest
from hi_contracts.public import ScenarioState
from hi_contracts.public.responses import (
    DatasetListResponse,
    InvestorZoneResponse,
    SearchResponse,
    ViabilityResponse,
    ZoneExplanationResponse,
    ZoneGapListResponse,
    ZoneLookupResponse,
)
from hi_domain.geo.names import match_rank
from hi_domain.investors_pilot import PILOT_BARRIOS
from hi_domain.viability import VIABILITY_VERSION

# A Madrid barrio by its code or its admin_unit_id (the id GET /investors/zones/{id} takes)
BARRIO_CODE = re.compile(r"(?:ES\.28\.BAR\.)?(28079\d{3})")
MAX_LISTED = 10


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


class BarrioNotResolvedError(LookupError):
    """The text names no pilot barrio, or several equally well: the agent reads why."""


def _listed(barrios: Sequence[tuple[int, str, str, str]]) -> str:
    shown = [f"{name} ({district}, {code})" for _, name, code, district in barrios[:MAX_LISTED]]
    left_out = len(barrios) - len(shown)
    return ", ".join(shown) + (f" and {left_out} more" if left_out else "")


def resolve_barrio(query: str) -> tuple[str, list[str]]:
    """The admin_unit_id of a pilot barrio (D-247) from its code or its name, and a warning when
    other barrios also match. Names match as in encontrar_zona (hi_domain.geo.names.match_rank:
    no case, accents or punctuation; same name, then starts with it, a word, inside it); a tie
    for the best match is an error that lists them. The pilot is the list the service reads (D-247);
    a barrio outside it, given by its code, gets the service's 404 message."""
    typed = query.strip()
    if by_code := BARRIO_CODE.fullmatch(typed):
        return f"ES.28.BAR.{by_code.group(1)}", []
    ranked = sorted(
        (rank, name, code, district)
        for code, name, district in PILOT_BARRIOS
        if (rank := match_rank(typed, name)) is not None
    )
    if not ranked:
        msg = (
            f"No pilot barrio ({investor_service.PILOT_TEXT}) is called «{typed}». "
            "GET /api/v1/investors/zones lists them; a district or municipio goes to que_falta"
        )
        raise BarrioNotResolvedError(msg)
    best = [barrio for barrio in ranked if barrio[0] == ranked[0][0]]
    if len(best) > 1:
        msg = (
            f"«{typed}» matches {len(best)} pilot barrios: {_listed(best)}. "
            "Write more of the name, or its code"
        )
        raise BarrioNotResolvedError(msg)
    _, name, code, _ = best[0]
    others = ranked[1:]
    warnings = (
        [f"{len(others)} more pilot barrios match «{typed}» ({_listed(others)}): this is {name}"]
        if others
        else []
    )
    return f"ES.28.BAR.{code}", warnings


def investor_sheet(
    conn: Connection, admin_unit_id: str, *, warnings: Sequence[str] = ()
) -> InvestorZoneResponse:
    """GET /api/v1/investors/zones/{admin_unit_id} (D-248), after the warnings of resolving it."""
    sheet, found, data_version = investor_service.zone_sheet(conn, admin_unit_id)
    return InvestorZoneResponse(
        data=sheet,
        meta=Meta(methodology_version=VIABILITY_VERSION, data_version=data_version),
        warnings=[*warnings, *found],
    )


def viability(request: ViabilityRequest) -> ViabilityResponse:
    """POST /api/v1/investors/viability (D-248): the residual method, without a database."""
    result = investor_service.run_viability(request)
    return ViabilityResponse(data=result, meta=Meta(methodology_version=result.version))
