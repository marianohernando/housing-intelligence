"""GET /api/v1/datasets: the datasets behind the product, for the footer counter and provenance."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.datasets import METHODOLOGY_VERSION, dataset_list
from hi_contracts.api.envelope import Meta
from hi_contracts.public.responses import DatasetListResponse

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("")
def get_datasets(
    engine: Annotated[Engine, Depends(get_engine)], cm_only: bool = False
) -> DatasetListResponse:
    with engine.connect() as conn:
        datasets = dataset_list(conn, cm_only=cm_only)
    return DatasetListResponse(data=datasets, meta=Meta(methodology_version=METHODOLOGY_VERSION))
