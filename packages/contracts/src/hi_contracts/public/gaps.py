"""Per-zone list of what is missing (GAP-001, D-194).

Each row compares the zone with the regional reference per population and says FALTA, JUSTO
or CUBIERTO; SIN_DATOS when the value is unknown (never 0). Proxies are declared per row.
"""

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hi_contracts.catalog.enums import GapRowKey, NullReason, TerritoryLevel
from hi_contracts.public.common import DatasetRef, IndicatorValue, ZoneRef

__all__ = [
    "GapMethod",
    "GapRow",
    "GapRowKey",
    "GapRowMap",
    "GapStatus",
    "GapStatusCounts",
    "ZoneGapList",
    "ZoneGapStatus",
]


class GapStatus(StrEnum):
    FALTA = "FALTA"
    JUSTO = "JUSTO"
    CUBIERTO = "CUBIERTO"
    SIN_DATOS = "SIN_DATOS"


class GapMethod(BaseModel):
    """How rows are classified: value / regional reference against declared cut-offs."""

    model_config = ConfigDict(extra="forbid")

    version: str = Field(examples=["gap-0.1"])
    reference: str = Field(examples=["Comunidad de Madrid: total de centros / población total"])
    falta_below: float = Field(gt=0, description="ratio to reference below this -> FALTA")
    cubierto_from: float = Field(gt=0, description="ratio at or above this -> CUBIERTO")
    confidence_level: float | None = Field(
        default=None,
        gt=0,
        lt=1,
        description="FALTA also needs a significant shortfall: the exact Poisson upper bound of "
        "the zone's count at this level below the count expected at the reference rate. "
        "None: the ratio alone decides",
    )

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if self.falta_below > self.cubierto_from:
            msg = "falta_below must not exceed cubierto_from"
            raise ValueError(msg)
        return self


class GapRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    row: GapRowKey
    label: str = Field(examples=["Colegios"])
    status: GapStatus
    indicator: IndicatorValue
    reference: float | None = Field(
        description="Same indicator for the zones the row is compared with (D-213: the "
        "municipios of its type in the region)"
    )
    reference_label: str = Field(examples=["Municipios urbanos de la Comunidad de Madrid"])
    regional_reference: float | None = Field(
        default=None, description="Same indicator for the whole Comunidad de Madrid (context)"
    )
    direction: Literal["higher_is_better", "lower_is_better"]
    ratio_to_reference: float | None = Field(
        default=None, ge=0, description="Oriented so that above 1 is better than the reference"
    )
    explanation: str = Field(
        examples=[
            "0,47 centros por cada 10.000 habitantes; en los municipios urbanos de la "
            "Comunidad de Madrid, 0,46 (en toda la Comunidad, 0,59)"
        ]
    )
    proxy_note: str | None = Field(
        default=None,
        examples=["Cuenta centros, no plazas: un centro grande y uno pequeño pesan igual"],
    )
    reliable: bool = Field(
        default=True,
        description="False when the zone is too small for this row: the count expected at the "
        "reference rate is under the 95 % bound of a zero count (3,7), so not even having none "
        "would be a significant shortfall. The status is then never FALTA; show it as "
        "«poco fiable» (D-213)",
    )
    extra_indicators: list[IndicatorValue] = Field(
        default_factory=list[IndicatorValue], description="e.g. walking minutes (CORE-005)"
    )
    datasets: list[DatasetRef]

    @model_validator(mode="after")
    def _status_matches_value(self) -> Self:
        unknown = self.indicator.value is None
        if unknown != (self.status is GapStatus.SIN_DATOS):
            msg = f"{self.row}: SIN_DATOS if and only if the value is unknown"
            raise ValueError(msg)
        if unknown and self.indicator.null_reason is None:
            msg = f"{self.row}: a missing value needs its null_reason"
            raise ValueError(msg)
        return self


class ZoneGapList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zone: ZoneRef
    method: GapMethod
    rows: list[GapRow]
    datasets: list[DatasetRef] = Field(description="Union of the rows' datasets")

    @model_validator(mode="after")
    def _one_row_per_key(self) -> Self:
        keys = [r.row for r in self.rows]
        if len(keys) != len(set(keys)):
            msg = "each row key appears at most once"
            raise ValueError(msg)
        return self


class ZoneGapStatus(BaseModel):
    """One zone of a row map: the status that colours it and the value behind it."""

    model_config = ConfigDict(extra="forbid")

    admin_unit_id: str = Field(
        description="promoteId of /api/v1/geo/admin-units", examples=["ES.28.DIS.2807905"]
    )
    code: str = Field(min_length=1, examples=["2807905"])
    name: str = Field(examples=["Chamartín"])
    status: GapStatus
    value: float | None
    reference: float | None = Field(
        default=None, description="What the zone is compared with: municipios of its type"
    )
    reference_label: str | None = Field(
        default=None, examples=["Municipios urbanos de la Comunidad de Madrid"]
    )
    ratio_to_reference: float | None = Field(
        default=None, ge=0, description="Oriented so that above 1 is better than the reference"
    )
    confidence: float = Field(ge=0, le=1)
    null_reason: NullReason | None = None
    reliable: bool = Field(
        default=True,
        description="False when the zone is too small for this row: the count expected at the "
        "reference rate is under the 95 % bound of a zero count (3,7), so not even having none "
        "would be a significant shortfall. The status is then never FALTA; show it as "
        "«poco fiable» (D-213)",
    )

    @model_validator(mode="after")
    def _status_matches_value(self) -> Self:
        unknown = self.value is None
        if unknown != (self.status is GapStatus.SIN_DATOS):
            msg = f"{self.code}: SIN_DATOS if and only if the value is unknown"
            raise ValueError(msg)
        if unknown and self.null_reason is None:
            msg = f"{self.code}: a missing value needs its null_reason"
            raise ValueError(msg)
        return self


class GapStatusCounts(BaseModel):
    model_config = ConfigDict(extra="forbid")

    falta: int = Field(ge=0)
    justo: int = Field(ge=0)
    cubierto: int = Field(ge=0)
    sin_datos: int = Field(ge=0)


class GapRowMap(BaseModel):
    """One row of the list for every zone of a level (GET /api/v1/gaps?level=&row=): the map.

    Same value, reference and cut-offs as the row in each zone's list. A row not computed at
    this level comes with no zones and a warning in the envelope.
    """

    model_config = ConfigDict(extra="forbid")

    row: GapRowKey
    label: str = Field(examples=["Colegios"])
    level: TerritoryLevel
    indicator_label: str = Field(description="Plain-language name of the indicator")
    unit: str
    direction: Literal["higher_is_better", "lower_is_better"]
    reference: float | None = Field(
        description="Same indicator for the whole region (each zone carries its own)"
    )
    reference_label: str = Field(examples=["Comunidad de Madrid"])
    proxy_note: str | None = None
    method: GapMethod
    counts: GapStatusCounts
    zones: list[ZoneGapStatus]
    datasets: list[DatasetRef]

    @model_validator(mode="after")
    def _consistent(self) -> Self:
        codes = [z.code for z in self.zones]
        if len(codes) != len(set(codes)):
            msg = "each zone appears at most once"
            raise ValueError(msg)
        tally = {s: sum(z.status is s for z in self.zones) for s in GapStatus}
        expected = {s: getattr(self.counts, s.value.lower()) for s in GapStatus}
        if tally != expected:
            msg = "counts must match the zones"
            raise ValueError(msg)
        return self
