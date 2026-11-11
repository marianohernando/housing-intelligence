"""Canonical places (facilities) as GeoJSON."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services import places
from hi_contracts.api.envelope import Envelope, ErrorCode
from hi_contracts.catalog.enums import PlaceCategory

router = APIRouter(prefix="/places", tags=["places"])


class PlacesData(BaseModel):
    type: str
    features: list[dict[str, Any]]


@router.get("")
def get_places(
    engine: Annotated[Engine, Depends(get_engine)],
    category: PlaceCategory,
    admin_unit_id: Annotated[
        str | None, Query(description="Only places in this municipio, distrito or seccion_censal")
    ] = None,
    subcategory: Annotated[
        list[str] | None, Query(description="Repeat to keep several (e.g. metro and cercanias)")
    ] = None,
) -> Envelope[PlacesData]:
    with engine.connect() as conn:
        try:
            result = places.places_geojson(conn, category, admin_unit_id, subcategory)
        except places.ZoneNotFoundError as exc:
            raise HTTPException(
                status_code=404, detail={"code": ErrorCode.NOT_FOUND.value, "message": str(exc)}
            ) from exc
        except places.UnsupportedZoneLevelError as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": ErrorCode.OUT_OF_COVERAGE.value, "message": str(exc)},
            ) from exc
    warnings = (
        [
            f"{ErrorCode.INSUFFICIENT_DATA.value}: only the first {places.MAX_PLACES} places; "
            "filter by admin_unit_id or subcategory"
        ]
        if result.truncated
        else []
    )
    return Envelope(data=PlacesData.model_validate(result.collection), warnings=warnings)
