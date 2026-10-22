"""Canonical places (facilities) as GeoJSON."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.places import places_geojson
from hi_contracts.api.envelope import Envelope
from hi_contracts.catalog.enums import PlaceCategory

router = APIRouter(prefix="/places", tags=["places"])


class PlacesData(BaseModel):
    type: str
    features: list[dict[str, Any]]


@router.get("")
def get_places(
    engine: Annotated[Engine, Depends(get_engine)], category: PlaceCategory
) -> Envelope[PlacesData]:
    with engine.connect() as conn:
        collection = places_geojson(conn, category)
    return Envelope(data=PlacesData.model_validate(collection))
