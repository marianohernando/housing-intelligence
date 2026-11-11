"""Per-zone list of what is missing (GAP-001, D-194).

Each row compares the zone with the regional reference per population and says FALTA, JUSTO
or CUBIERTO; SIN_DATOS when the value is unknown (never 0). Proxies are declared per row.
"""

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hi_contracts.public.common import DatasetRef, IndicatorValue, ZoneRef


class GapStatus(StrEnum):
    FALTA = "FALTA"
    JUSTO = "JUSTO"
    CUBIERTO = "CUBIERTO"
    SIN_DATOS = "SIN_DATOS"


class GapRowKey(StrEnum):
    ESCUELA_INFANTIL = "escuela_infantil"
    COLEGIO = "colegio"
    CENTRO_SALUD = "centro_salud"
    MAYORES = "mayores"
    FARMACIA = "farmacia"
    VIVIENDA = "vivienda"


class GapMethod(BaseModel):
    """How rows are classified: value / regional reference against declared cut-offs."""

    model_config = ConfigDict(extra="forbid")

    version: str = Field(examples=["gap-0.1"])
    reference: str = Field(examples=["Comunidad de Madrid: total de centros / población total"])
    falta_below: float = Field(gt=0, description="ratio to reference below this -> FALTA")
    cubierto_from: float = Field(gt=0, description="ratio at or above this -> CUBIERTO")

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
    reference: float | None = Field(description="Same indicator for the whole region")
    reference_label: str = Field(examples=["Comunidad de Madrid"])
    direction: Literal["higher_is_better", "lower_is_better"]
    ratio_to_reference: float | None = Field(
        default=None, ge=0, description="Oriented so that above 1 is better than the region"
    )
    explanation: str = Field(
        examples=["2,1 colegios públicos por cada 1.000 menores; la región tiene 2,6"]
    )
    proxy_note: str | None = Field(
        default=None,
        examples=["Cuenta centros, no plazas: un centro grande y uno pequeño pesan igual"],
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
