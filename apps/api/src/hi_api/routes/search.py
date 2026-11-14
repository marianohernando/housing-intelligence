"""People search: POST /api/v1/search with a ScenarioState (CORE-003, D-215), and inside one
district of Madrid, POST /api/v1/search/barrios (D-232)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.barrios import search_barrios
from hi_api.services.gaps import ZoneNotFoundError
from hi_api.services.scope import search
from hi_contracts.api.envelope import ErrorCode, Meta
from hi_contracts.public import BarrioSearchRequest, ScenarioState
from hi_contracts.public.responses import BarrioSearchResponse, SearchResponse

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


@router.post("/barrios")
def post_search_barrios(
    request: BarrioSearchRequest, engine: Annotated[Engine, Depends(get_engine)]
) -> BarrioSearchResponse:
    with engine.connect() as conn:
        try:
            result, warnings, data_version = search_barrios(
                conn, request.scenario, request.distrito
            )
        except ZoneNotFoundError as exc:
            raise HTTPException(
                status_code=404, detail={"code": ErrorCode.NOT_FOUND.value, "message": str(exc)}
            ) from exc
    return BarrioSearchResponse(
        data=result,
        meta=Meta(methodology_version=result.methodology_version, data_version=data_version),
        warnings=warnings,
    )
