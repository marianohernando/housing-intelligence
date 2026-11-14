"""Feature catalogue and values for maps and analysis."""

from datetime import date
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
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


class ContextItem(BaseModel):
    """One thing a context figure lists (D-241): a planning area, a Plan Vive promotion."""

    code: str | None = None
    name: str | None = None
    stage: str | None = None
    value: float | None = None
    note: str | None = None


class FeatureValueDetail(BaseModel):
    """What a context figure says besides its value (D-241), only for the features that keep
    it: the two counts of a share, the last day of its period, whether it is provisional, and
    the items behind a count."""

    numerator: float | None = None
    denominator: float | None = None
    period_end: date | None = None
    provisional: bool | None = None
    items: list[ContextItem] | None = None


class FeatureValueRow(BaseModel):
    territory_code: str
    admin_unit_id: str | None
    name: str | None
    period_start: date
    value: float | None
    null_reason: str | None
    confidence: float
    # Only the context features keep one; the rest leave it out (no `null` in every row)
    detail: FeatureValueDetail | None = Field(default=None, exclude_if=lambda d: d is None)


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
