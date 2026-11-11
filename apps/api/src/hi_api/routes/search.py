"""People search: POST /api/v1/search with a ScenarioState (CORE-003, D-215)."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.search import search
from hi_contracts.api.envelope import Meta
from hi_contracts.public import ScenarioState
from hi_contracts.public.responses import SearchResponse

router = APIRouter(prefix="/search", tags=["search"])


@router.post("")
def post_search(
    scenario: ScenarioState, engine: Annotated[Engine, Depends(get_engine)]
) -> SearchResponse:
    with engine.connect() as conn:
        result, warnings, data_version = search(conn, scenario)
    return SearchResponse(
        data=result,
        meta=Meta(methodology_version=result.methodology_version, data_version=data_version),
        warnings=warnings,
    )
