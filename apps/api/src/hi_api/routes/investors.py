"""Investor version (D-248), additive: nothing here changes /search or /gaps.

GET  /api/v1/investors/zones: the pilot barrios (Madrid inside the M-40, D-247) with what they
     lack, their public land and their prices.
GET  /api/v1/investors/zones/{admin_unit_id}: one pilot barrio's sheet: demand, prices, what is
     missing, land and the viability defaults with their sources.
POST /api/v1/investors/viability: the residual method on the person's inputs (no database).
"""

import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.gaps import ZoneNotFoundError
from hi_api.services.investors import run_viability, zone_list, zone_sheet
from hi_contracts.api.envelope import ErrorCode, Meta
from hi_contracts.pro.investors import ViabilityRequest
from hi_contracts.public.responses import (
    InvestorZoneListResponse,
    InvestorZoneResponse,
    ViabilityResponse,
)
from hi_domain.viability import VIABILITY_VERSION

router = APIRouter(prefix="/investors", tags=["investors"])
ADMIN_UNIT_PATTERN = r"^ES\.28\.BAR\.28079\d{3}$"


@router.get("/zones")
def get_zones(engine: Annotated[Engine, Depends(get_engine)]) -> InvestorZoneListResponse:
    with engine.connect() as conn:
        zones, warnings, data_version = zone_list(conn)
    return InvestorZoneListResponse(
        data=zones,
        meta=Meta(methodology_version=VIABILITY_VERSION, data_version=data_version),
        warnings=warnings,
    )


@router.get("/zones/{admin_unit_id}")
def get_zone(
    admin_unit_id: str, engine: Annotated[Engine, Depends(get_engine)]
) -> InvestorZoneResponse:
    # Checked before any connection: a wrong id never reaches the database
    if not re.fullmatch(ADMIN_UNIT_PATTERN, admin_unit_id):
        raise HTTPException(
            status_code=422,
            detail={
                "code": ErrorCode.OUT_OF_COVERAGE.value,
                "message": "The investor sheet is for the barrios of Madrid (ES.28.BAR.28079nnn)",
            },
        )
    with engine.connect() as conn:
        try:
            sheet, warnings, data_version = zone_sheet(conn, admin_unit_id)
        except ZoneNotFoundError as exc:
            raise HTTPException(
                status_code=404, detail={"code": ErrorCode.NOT_FOUND.value, "message": str(exc)}
            ) from exc
    return InvestorZoneResponse(
        data=sheet,
        meta=Meta(methodology_version=VIABILITY_VERSION, data_version=data_version),
        warnings=warnings,
    )


@router.post("/viability")
def post_viability(request: ViabilityRequest) -> ViabilityResponse:
    result = run_viability(request)
    return ViabilityResponse(data=result, meta=Meta(methodology_version=result.version))
