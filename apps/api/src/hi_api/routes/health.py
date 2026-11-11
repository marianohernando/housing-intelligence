"""Liveness (process up) and readiness (database reachable and data visible) endpoints."""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from hi_api import deps
from hi_contracts.api.envelope import Envelope, ErrorCode

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)

# Every map view reads the geography. A role without a grant or row-level-security policy sees
# an empty table instead of an error, so readiness checks rows, not just the connection.
_GEOGRAPHY_VISIBLE = text("SELECT EXISTS (SELECT 1 FROM geo_admin_unit)")


class HealthStatus(BaseModel):
    status: str
    service: str


@router.get("/health")
def health() -> Envelope[HealthStatus]:
    return Envelope(data=HealthStatus(status="ok", service="hi-api"))


@router.get("/health/ready")
def ready() -> Envelope[HealthStatus]:
    # The engine is built inside the try: a malformed DATABASE_URL must answer 503, not 500.
    try:
        with deps.get_engine().connect() as conn:
            geography_visible = bool(conn.execute(_GEOGRAPHY_VISIBLE).scalar())
    except SQLAlchemyError as exc:
        logger.warning("readiness: database error %s", type(exc).__name__)
        raise HTTPException(
            status_code=503,
            detail={"code": ErrorCode.SOURCE_DEGRADED.value, "message": "Database unreachable"},
        ) from exc
    if not geography_visible:
        raise HTTPException(
            status_code=503,
            detail={
                "code": ErrorCode.INSUFFICIENT_DATA.value,
                "message": "No geography visible to the API database role",
            },
        )
    return Envelope(data=HealthStatus(status="ok", service="hi-api"))
