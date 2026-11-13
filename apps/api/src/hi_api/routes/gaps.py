"""What is missing against the regional reference: per zone and per row for the map.

GET /api/v1/gaps/{level}/{code}: every row for one zone.
GET /api/v1/gaps?level=&row=: one row for every zone of a level (GAP-001 F4).
GET /api/v1/gaps/impact: people affected by each row and where to invest first (D-229).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.gap_impact import gap_impact
from hi_api.services.gap_map import RowNotBoundError, gap_row_map
from hi_api.services.gaps import ZoneNotFoundError, zone_gap_list
from hi_contracts.api.envelope import ErrorCode, Meta
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public.responses import (
    GapImpactResponse,
    GapRowMapResponse,
    ZoneGapListResponse,
)

router = APIRouter(prefix="/gaps", tags=["gaps"])
ZONE_LEVELS = (TerritoryLevel.MUNICIPIO, TerritoryLevel.DISTRITO, TerritoryLevel.SECCION_CENSAL)


def _check_level(level: TerritoryLevel) -> None:
    if level not in ZONE_LEVELS:
        raise HTTPException(
            status_code=422,
            detail={
                "code": ErrorCode.OUT_OF_COVERAGE.value,
                "message": "The list is available for municipio, distrito and seccion_censal",
            },
        )


@router.get("")
def get_row_map(
    level: TerritoryLevel, row: GapRowKey, engine: Annotated[Engine, Depends(get_engine)]
) -> GapRowMapResponse:
    _check_level(level)
    with engine.connect() as conn:
        try:
            gap_map, warnings, data_version = gap_row_map(conn, level, row)
        except RowNotBoundError as exc:
            raise HTTPException(
                status_code=404, detail={"code": ErrorCode.NOT_FOUND.value, "message": str(exc)}
            ) from exc
    return GapRowMapResponse(
        data=gap_map,
        meta=Meta(methodology_version=gap_map.method.version, data_version=data_version),
        warnings=warnings,
    )


@router.get("/impact")
def get_impact(engine: Annotated[Engine, Depends(get_engine)]) -> GapImpactResponse:
    with engine.connect() as conn:
        impact, warnings, data_version = gap_impact(conn)
    return GapImpactResponse(
        data=impact,
        meta=Meta(methodology_version=impact.version, data_version=data_version),
        warnings=warnings,
    )


@router.get("/{level}/{code}")
def get_zone_gaps(
    level: TerritoryLevel, code: str, engine: Annotated[Engine, Depends(get_engine)]
) -> ZoneGapListResponse:
    _check_level(level)
    with engine.connect() as conn:
        try:
            gaps, warnings, data_version = zone_gap_list(conn, level, code)
        except ZoneNotFoundError as exc:
            raise HTTPException(
                status_code=404, detail={"code": ErrorCode.NOT_FOUND.value, "message": str(exc)}
            ) from exc
    return ZoneGapListResponse(
        data=gaps,
        meta=Meta(methodology_version=gaps.method.version, data_version=data_version),
        warnings=warnings,
    )
