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
    "GapImpact",
    "GapImpactRow",
    "GapImpactZone",
    "GapMethod",
    "GapRow",
    "GapRowKey",
    "GapRowMap",
    "GapStatus",
    "GapStatusCounts",
    "PeopleCount",
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


class ComparisonGroup(BaseModel):
    """A zone too small to compare alone, compared with its nearest same-type neighbours.

    gap-0.3 (D-217): the nearest municipios of the same type are added until the group expects
    3,69 cases at the reference rate (the floor of D-213). `status` is then the group's.
    """

    model_config = ConfigDict(extra="forbid")

    codes: list[str] = Field(min_length=2, description="The zone first, then its neighbours")
    names: list[str] = Field(min_length=2, examples=[["La Acebeda", "Robregordo"]])
    ratio_to_reference: float = Field(ge=0, description="Group total over its expected total")


class PeopleCount(BaseModel):
    """The population a row serves, living in the zone (D-229): its indicator's denominator."""

    model_config = ConfigDict(extra="forbid")

    count: int = Field(ge=0, examples=[6729])
    label: str = Field(examples=["niños de 0 a 4 años"])


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
        "«poco fiable» (D-213). True also when the test does not apply (no counts)",
    )
    comparison_group: ComparisonGroup | None = Field(
        default=None,
        description="Set when the zone is compared together with its nearest neighbours of "
        "the same type because it is too small alone (gap-0.3, D-217); `status` is the group's",
    )
    extra_indicators: list[IndicatorValue] = Field(
        default_factory=list[IndicatorValue], description="e.g. walking minutes (CORE-005)"
    )
    people: PeopleCount | None = Field(
        default=None,
        description="Who the row serves in this zone (children of 0 to 4, people of 65 or "
        "more, …): the denominator of its indicator. With FALTA, the people affected (D-229). "
        "None when the indicator keeps no counts",
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
        "«poco fiable» (D-213). True also when the test does not apply (no counts)",
    )
    comparison_group: ComparisonGroup | None = Field(
        default=None,
        description="Set when the zone is compared together with its nearest neighbours of "
        "the same type because it is too small alone (gap-0.3, D-217); `status` is the group's",
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


class GapImpactZone(BaseModel):
    """A zone in FALTA, with the people affected and how clear the shortfall is (D-229)."""

    model_config = ConfigDict(extra="forbid")

    admin_unit_id: str = Field(examples=["ES.28.DIS.2807913"])
    code: str = Field(min_length=1, examples=["2807913"])
    name: str = Field(examples=["Puente de Vallecas"])
    level: TerritoryLevel
    people: int = Field(ge=0, description="The row's target population living in the zone")
    ratio_to_reference: float = Field(
        ge=0, description="Supply over the reference (the group's when compared with neighbours)"
    )
    p_value: float | None = Field(
        ge=0,
        le=1,
        description="One-sided exact Poisson probability that a zone at the reference rate has "
        "this little or less; FALTA needs it below 0,025 (D-213). None when the row keeps no "
        "counts to test and the ratio alone decided",
    )
    comparison_group: ComparisonGroup | None = None
    explanation: str = Field(
        examples=[
            "Viven aquí 9.876 niños de 0 a 4 años. Tienen 62 por cada 100 que tienen los "
            "municipios parecidos, y una diferencia así sale por azar menos de 1 entre 1.000 "
            "veces"
        ]
    )


class GapImpactRow(BaseModel):
    """One row of the list: how many people live where it is missing, and where to invest."""

    model_config = ConfigDict(extra="forbid")

    row: GapRowKey
    label: str = Field(examples=["Escuelas infantiles"])
    people_label: str = Field(examples=["niños de 0 a 4 años"])
    madrid_level: TerritoryLevel = Field(
        description="Madrid capital counted by its 21 districts, or as one municipio when the "
        "row has no district values"
    )
    zones: int = Field(ge=0, description="Zones counted, whatever their status (SIN_DATOS too)")
    zones_in_falta: int = Field(ge=0)
    people_in_falta: int = Field(ge=0)
    people_total: int = Field(ge=0, description="The row's target population in the region")
    share_in_falta: float = Field(ge=0, le=1)
    summary: str = Field(
        examples=[
            "En la Comunidad de Madrid, 23.456 niños de 0 a 4 años (el 9,0 %) viven en 3 "
            "zonas donde faltan escuelas infantiles"
        ]
    )
    ranking: list[GapImpactZone] = Field(
        description="Where to invest first: zones in FALTA, most people affected first"
    )

    @model_validator(mode="after")
    def _consistent(self) -> Self:
        if len(self.ranking) != self.zones_in_falta:
            msg = f"{self.row}: one ranked zone per zone in FALTA"
            raise ValueError(msg)
        if sum(z.people for z in self.ranking) != self.people_in_falta:
            msg = f"{self.row}: people in FALTA must add up the ranked zones"
            raise ValueError(msg)
        people = [z.people for z in self.ranking]
        if people != sorted(people, reverse=True):
            msg = f"{self.row}: the ranking goes from most to fewest people"
            raise ValueError(msg)
        return self


class GapImpact(BaseModel):
    """GET /api/v1/gaps/impact: the people affected by each row, region-wide (D-229)."""

    model_config = ConfigDict(extra="forbid")

    version: str = Field(examples=["impact-0.1"])
    method: GapMethod
    zones_note: str = Field(
        description="Which zones are counted: the municipios and Madrid capital's districts"
    )
    rows: list[GapImpactRow]
    datasets: list[DatasetRef]
