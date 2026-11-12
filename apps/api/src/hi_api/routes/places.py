"""Canonical places (facilities) as GeoJSON."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services import places
from hi_contracts.api.envelope import ErrorCode
from hi_contracts.catalog.enums import PlaceCategory
from hi_contracts.public.places import PlaceCollection
from hi_contracts.public.responses import PlacesResponse

router = APIRouter(prefix="/places", tags=["places"])


def _next_page_warning(result: places.PlacesResult) -> list[str]:
    if result.page >= result.pages:
        return []
    return [
        f"{ErrorCode.INSUFFICIENT_DATA.value}: page {result.page} of {result.pages} "
        f"({result.total} places); ask for ?page={result.page + 1} or filter by admin_unit_id "
        "or subcategory"
    ]


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
    page: Annotated[int, Query(ge=1, description=f"{places.PAGE_SIZE} places per page")] = 1,
) -> PlacesResponse:
    with engine.connect() as conn:
        try:
            result = places.places_geojson(conn, category, admin_unit_id, subcategory, page)
        except places.ZoneNotFoundError as exc:
            raise HTTPException(
                status_code=404, detail={"code": ErrorCode.NOT_FOUND.value, "message": str(exc)}
            ) from exc
        except (places.UnsupportedZoneLevelError, places.PageOutOfRangeError) as exc:
            raise HTTPException(
                status_code=422,
                detail={"code": ErrorCode.OUT_OF_COVERAGE.value, "message": str(exc)},
            ) from exc
    data = PlaceCollection.model_validate(
        {**result.collection, "total": result.total, "page": result.page, "pages": result.pages}
    )
    return PlacesResponse(data=data, warnings=_next_page_warning(result))
