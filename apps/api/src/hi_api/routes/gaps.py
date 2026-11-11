"""GET /api/v1/gaps/{level}/{code}: what a zone is missing against the regional reference."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.gaps import ZoneNotFoundError, zone_gap_list
from hi_contracts.api.envelope import ErrorCode, Meta
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.public.responses import ZoneGapListResponse

router = APIRouter(prefix="/gaps", tags=["gaps"])
ZONE_LEVELS = (TerritoryLevel.MUNICIPIO, TerritoryLevel.DISTRITO, TerritoryLevel.SECCION_CENSAL)


@router.get("/{level}/{code}")
def get_zone_gaps(
    level: TerritoryLevel, code: str, engine: Annotated[Engine, Depends(get_engine)]
) -> ZoneGapListResponse:
    if level not in ZONE_LEVELS:
        raise HTTPException(
            status_code=422,
            detail={
                "code": ErrorCode.OUT_OF_COVERAGE.value,
                "message": "The list is available for municipio, distrito and seccion_censal",
            },
        )
    with engine.connect() as conn:
        try:
            gaps, warnings, data_version = zone_gap_list(conn, level, code)
        except ZoneNotFoundError as exc:
            raise HTTPException(
                status_code=404, detail={"code": ErrorCode.NOT_FOUND.value, "message": str(exc)}
            ) from exc
    if not gaps.rows:
        warnings.append("No indicators computed at this level yet")
    return ZoneGapListResponse(
        data=gaps,
        meta=Meta(methodology_version=gaps.method.version, data_version=data_version),
        warnings=warnings,
    )
