"""Canonical geography endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.geo import MAX_SIMPLIFY_METERS, admin_units_geojson
from hi_contracts.api.envelope import Envelope, ErrorCode, Meta
from hi_contracts.catalog.enums import AdminLevel

router = APIRouter(prefix="/geo", tags=["geo"])
METHODOLOGY_VERSION = "admin_units-v1"


class AdminUnitsData(BaseModel):
    type: str
    features: list[dict[str, Any]]
    lineage: dict[str, Any]


@router.get("/admin-units")
def list_admin_units(
    engine: Annotated[Engine, Depends(get_engine)],
    level: AdminLevel = AdminLevel.MUNICIPIO,
    simplify_m: Annotated[float, Query(ge=0, le=MAX_SIMPLIFY_METERS)] = 25.0,
) -> Envelope[AdminUnitsData]:
    with engine.connect() as conn:
        result = admin_units_geojson(conn, level, simplify_m)
    features = result.feature_collection["features"]
    warnings = (
        []
        if features
        else [f"{ErrorCode.INSUFFICIENT_DATA.value}: no units for level {level.value}"]
    )
    return Envelope(
        data=AdminUnitsData(type="FeatureCollection", features=features, lineage=result.lineage),
        meta=Meta(methodology_version=METHODOLOGY_VERSION, data_version=result.data_version),
        warnings=warnings,
    )
