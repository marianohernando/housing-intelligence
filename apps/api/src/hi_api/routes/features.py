"""Feature catalogue and values for maps and analysis."""

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Engine

from hi_api.deps import get_engine
from hi_api.services.features import feature_values, list_features
from hi_contracts.api.envelope import Envelope, ErrorCode, Meta
from hi_contracts.catalog.enums import GeoResolution

router = APIRouter(prefix="/features", tags=["features"])


class FeatureInfo(BaseModel):
    feature_id: str
    version: int
    human_name: str
    domain: str
    unit: str
    direction: str
    geo_level: str
    public_use: bool
    limitations: list[str]
    sources: list[dict[str, Any]]


class FeatureValueRow(BaseModel):
    territory_code: str
    admin_unit_id: str | None
    name: str | None
    period_start: date
    value: float | None
    null_reason: str | None
    confidence: float


class FeatureValues(BaseModel):
    feature_id: str
    level: str
    values: list[FeatureValueRow]
    lineage: dict[str, Any]


@router.get("")
def get_features(
    engine: Annotated[Engine, Depends(get_engine)], level: GeoResolution = GeoResolution.MUNICIPIO
) -> Envelope[list[FeatureInfo]]:
    with engine.connect() as conn:
        rows = list_features(conn, level.value)
    return Envelope(data=[FeatureInfo.model_validate(r) for r in rows])


@router.get("/{feature_id}/values")
def get_feature_values(
    feature_id: str,
    engine: Annotated[Engine, Depends(get_engine)],
    level: GeoResolution = GeoResolution.MUNICIPIO,
) -> Envelope[FeatureValues]:
    with engine.connect() as conn:
        rows, lineage = feature_values(conn, feature_id, level.value)
    if not rows:
        raise HTTPException(
            status_code=404,
            detail={
                "code": ErrorCode.NOT_FOUND.value,
                "message": f"No values for {feature_id} at {level.value}",
            },
        )
    versions = lineage.get("dataset_versions", {})
    return Envelope(
        data=FeatureValues(
            feature_id=feature_id,
            level=level.value,
            values=[FeatureValueRow.model_validate(r) for r in rows],
            lineage=lineage,
        ),
        meta=Meta(
            methodology_version=f"{feature_id}@{lineage.get('method', '?')}",
            data_version=",".join(sorted(versions.values())) or None,
        ),
    )
