"""Investor version (D-248), additive: nothing here changes /search or /gaps.

GET  /api/v1/investors/zones: the pilot barrios (Madrid inside the M-40, D-247) with what they
     lack, their public land and their prices.
GET  /api/v1/investors/zones/{admin_unit_id}: one pilot barrio's sheet: demand, prices, what is
     missing, land and the viability defaults with their sources.
POST /api/v1/investors/viability: the residual method on the person's inputs (no database).
GET  /api/v1/investors/parcels?rc=|lat=&lon=|address= (D-250): one parcel of Madrid capital, its
     planning, its buildable m² and its barrio, from the Catastro and the Ayuntamiento (cached,
     with a per-IP guard on the calls to them and the demo sheets when they fail).
GET  /api/v1/investors/parcels/candidates?q= (D-250): the portals that match a typed address,
     for the person to pick one.
"""

import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.gaps import ZoneNotFoundError
from hi_api.services.investors import run_viability, zone_list, zone_sheet
from hi_api.services.parcel_sheet import (
    GEOCODER_SOURCE,
    ParcelLookupError,
    ParcelQuery,
    candidates_for,
    parcel_sheet,
)
from hi_api.services.parcels import UpstreamError
from hi_api.services.upstream_guard import RateLimitedError, client_ip
from hi_contracts.api.envelope import ErrorCode, Meta
from hi_contracts.pro.investors import ParcelCandidates, ParcelInput, ViabilityRequest
from hi_contracts.public.responses import (
    InvestorZoneListResponse,
    InvestorZoneResponse,
    ParcelCandidatesResponse,
    ParcelSheetResponse,
    ViabilityResponse,
)
from hi_domain.parcels import PARCELS_VERSION
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


# --- Search by parcel (D-250) ---

CACHED = "public, max-age=3600, s-maxage=86400"
# A typed address travels in the URL: no shared cache (the CDN) keeps it, only the browser
PRIVATE = "private, no-store"
PRIVATE_BOX = "private, max-age=600"
SOURCE_DOWN = {
    "catastro": "The Catastro does not answer now",
    "planning": "The Ayuntamiento does not answer now",
    "geocoder": "The address search (CartoCiudad) does not answer now",
}


def parcel_query(
    rc: str | None, lat: float | None, lon: float | None, address: str | None
) -> ParcelQuery:
    """Exactly one of rc, lat and lon together, or address; otherwise a validation error."""
    given = [rc is not None, lat is not None or lon is not None, address is not None]
    if sum(given) != 1 or (given[1] and (lat is None or lon is None)):
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["query"],
                    "msg": "pass exactly one of rc, lat and lon (both), or address",
                    "type": "value_error",
                }
            ],
        )
    if rc is not None:
        return ParcelQuery(ParcelInput.RC, rc=rc)
    if address is not None:
        return ParcelQuery(ParcelInput.ADDRESS, address=address)
    return ParcelQuery(ParcelInput.POINT, lat=lat, lon=lon)


def lookup_failure(exc: Exception) -> HTTPException:
    if isinstance(exc, ParcelLookupError):
        detail = {"code": exc.code.value, "message": exc.message, "details": exc.details}
        return HTTPException(status_code=exc.status, detail=detail)
    if isinstance(exc, RateLimitedError):
        return HTTPException(
            status_code=429,
            detail={
                "code": ErrorCode.RATE_LIMITED.value,
                "message": "Too many new parcel lookups from this address: wait and retry",
                "details": {"retry_after_s": exc.retry_after_s},
            },
            headers={"Retry-After": str(exc.retry_after_s)},
        )
    source = exc.source if isinstance(exc, UpstreamError) else "catastro"
    return HTTPException(
        status_code=503,
        detail={"code": ErrorCode.SOURCE_DEGRADED.value, "message": SOURCE_DOWN[source]},
        headers={"Retry-After": "30"},
    )


@router.get("/parcels")
async def get_parcel(
    request: Request,
    response: Response,
    engine: Annotated[Engine, Depends(get_engine)],
    rc: Annotated[str | None, Query(max_length=40, description="Cadastral reference")] = None,
    lat: Annotated[float | None, Query(ge=-90, le=90)] = None,
    lon: Annotated[float | None, Query(ge=-180, le=180)] = None,
    address: Annotated[str | None, Query(min_length=4, max_length=160)] = None,
) -> ParcelSheetResponse:
    query = parcel_query(rc, lat, lon, address)
    try:
        sheet, warnings, data_version = await parcel_sheet(query, client_ip(request), engine)
    except (ParcelLookupError, RateLimitedError, UpstreamError) as exc:
        raise lookup_failure(exc) from exc
    complete = sheet.fallback is None and not sheet.degraded
    if query.kind is ParcelInput.ADDRESS:
        response.headers["Cache-Control"] = PRIVATE
    else:
        response.headers["Cache-Control"] = CACHED if complete else "no-store"
    return ParcelSheetResponse(
        data=sheet,
        meta=Meta(methodology_version=PARCELS_VERSION, data_version=data_version),
        warnings=warnings,
    )


@router.get("/parcels/candidates")
async def get_parcel_candidates(
    request: Request,
    response: Response,
    q: Annotated[str, Query(min_length=4, max_length=160, description="Typed address")],
) -> ParcelCandidatesResponse:
    try:
        found, _ = await candidates_for(q, client_ip(request))
    except (RateLimitedError, UpstreamError) as exc:
        raise lookup_failure(exc) from exc
    response.headers["Cache-Control"] = PRIVATE_BOX
    return ParcelCandidatesResponse(
        data=ParcelCandidates(
            candidates=[c.candidate for c in found.portals],
            needs_number=found.streets_only,
            sources=[GEOCODER_SOURCE],
        ),
        meta=Meta(methodology_version=PARCELS_VERSION),
    )
