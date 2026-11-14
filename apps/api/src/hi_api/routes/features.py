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
    """One thing a context figure lists (D-241): a Plan Vive entry or a Madrid planning area."""

    code: str | None = Field(
        default=None, description="Its id in the source: the planning area's code («APR.06.02»)"
    )
    name: str | None = Field(
        default=None, description="What to call it: the area's name, or where the entry is"
    )
    stage: str | None = Field(
        default=None,
        description="Planning areas: obras | tramitacion | sin_empezar. Plan Vive: its phase "
        "as the page writes it («Entrega y construcción»)",
    )
    value: float | None = Field(
        default=None, description="Plan Vive: homes. Planning areas: surface in m²"
    )
    note: str | None = Field(
        default=None, description="A caveat that travels with the data, shown next to it"
    )


class FeatureValueDetail(BaseModel):
    """What a context figure says besides its value (D-241). Only the features that keep one
    (`feature_value.inputs.detail`) send it; any field may be absent:

    - a share over periods (`compraventas_obra_nueva_pct`): `numerator`, `denominator`,
      `period_end` and `provisional`;
    - the items behind a count or a sum (`plan_vive_viviendas`,
      `ambitos_residenciales_en_desarrollo`): `items`, empty when the zone has none (a
      confirmed 0);
    - the air quality station a value comes from (`no2_media_anual`, D-237): `station`,
      `station_code`, `own`, `distance_km` and `traffic`."""

    numerator: float | None = Field(default=None, description="Count behind the share's top")
    denominator: float | None = Field(default=None, description="Count behind the share's base")
    period_end: date | None = Field(
        default=None,
        description="Last day of the periods added up (the row's period_start is the first)",
    )
    provisional: bool | None = Field(
        default=None, description="True when any value added up is marked provisional"
    )
    items: list[ContextItem] | None = Field(
        default=None, description="The zone's items: stage order, then largest first"
    )
    station: str | None = Field(
        default=None, examples=["Getafe"], description="D-237: the air quality station's name"
    )
    station_code: str | None = Field(
        default=None, examples=["28065014"], description="D-237: its code in its network"
    )
    own: bool | None = Field(
        default=None, description="D-237: true when the station lies in the zone itself"
    )
    distance_km: float | None = Field(
        default=None, description="D-237: from the centre of the zone's residential streets"
    )
    traffic: bool | None = Field(
        default=None, description="D-237: a traffic station (its network's type), not background"
    )


class FeatureValueRow(BaseModel):
    territory_code: str
    admin_unit_id: str | None
    name: str | None
    period_start: date
    value: float | None
    null_reason: str | None
    confidence: float
    # Only the context features keep one; the rest leave it out (no `null` in every row)
    detail: FeatureValueDetail | None = Field(
        default=None,
        exclude_if=lambda d: d is None,
        description="Only in the rows of context features that keep one (D-241); absent otherwise",
    )


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
