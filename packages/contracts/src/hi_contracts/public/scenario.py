"""ScenarioState (CORE-001): the single state that chips, filters and map edit together.

Minimal for the DATAMAD demo: budget, household, places of reference and services needed
nearby. Sensitive needs are not part of this version (opt-in later, CLAUDE.md §13).
"""

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hi_contracts.catalog.enums import TerritoryLevel


class Tenure(StrEnum):
    RENT = "rent"
    BUY = "buy"


class NeedKey(StrEnum):
    """Everyday services the search and the per-zone list both talk about."""

    ESCUELA_INFANTIL = "escuela_infantil"
    COLEGIO = "colegio"
    CENTRO_SALUD = "centro_salud"
    FARMACIA = "farmacia"
    MAYORES = "mayores"
    TRANSPORTE = "transporte"


class PriorityKey(StrEnum):
    COSTE = "coste"
    TRAYECTO = "trayecto"
    ESCUELA_INFANTIL = "escuela_infantil"
    COLEGIO = "colegio"
    CENTRO_SALUD = "centro_salud"
    FARMACIA = "farmacia"
    MAYORES = "mayores"
    TRANSPORTE = "transporte"


class AnchorKind(StrEnum):
    WORK = "work"
    STUDY = "study"
    FAMILY = "family"
    OTHER = "other"


class Household(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adults: int = Field(default=1, ge=1, le=8)
    children: int = Field(default=0, ge=0, le=8)
    children_ages: list[int] = Field(default_factory=list[int], description="0-17, optional")
    seniors: int = Field(default=0, ge=0, le=8, description="People aged 65+, counted in adults")

    @model_validator(mode="after")
    def _coherent(self) -> Self:
        if self.children_ages and len(self.children_ages) != self.children:
            msg = "children_ages must list every child or be empty"
            raise ValueError(msg)
        if any(not 0 <= age <= 17 for age in self.children_ages):
            msg = "children_ages must be between 0 and 17"
            raise ValueError(msg)
        if self.seniors > self.adults:
            msg = "seniors are counted among adults"
            raise ValueError(msg)
        return self

    @property
    def size(self) -> int:
        return self.adults + self.children


class Anchor(BaseModel):
    """A place the household travels to often (work, school, family)."""

    model_config = ConfigDict(extra="forbid")

    kind: AnchorKind = AnchorKind.WORK
    label: str = Field(min_length=1, max_length=80, examples=["Paseo de la Castellana (Azca)"])
    lon: float = Field(ge=-4.58, le=-3.05)
    lat: float = Field(ge=39.88, le=41.17)
    days_per_week: int = Field(default=5, ge=1, le=7)
    max_minutes: int | None = Field(
        default=None, ge=5, le=120, description="Hard limit for the trip; None = preference only"
    )


class NearbyNeed(BaseModel):
    """A service the household wants within walking distance (e.g. «colegio cerca»)."""

    model_config = ConfigDict(extra="forbid")

    need: NeedKey
    max_walk_minutes: int = Field(default=10, ge=1, le=60)
    required: bool = Field(default=True, description="True = hard constraint (PASS/FAIL/UNKNOWN)")


class ScenarioState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    tenure: Tenure = Tenure.RENT
    budget_monthly_eur: int | None = Field(
        default=None, ge=100, le=20_000, description="Maximum monthly rent; None = no limit"
    )
    min_floor_area_m2: int | None = Field(
        default=None, ge=15, le=400, description="None = derived from the household size"
    )
    household: Household = Field(default_factory=Household)
    anchors: list[Anchor] = Field(default_factory=list[Anchor], max_length=3)
    nearby: list[NearbyNeed] = Field(default_factory=list[NearbyNeed], max_length=6)
    priorities: list[PriorityKey] = Field(
        default_factory=list[PriorityKey], max_length=5, description="Most important first"
    )
    zone_level: TerritoryLevel = Field(
        default=TerritoryLevel.MUNICIPIO, description="Granularity of the ranking"
    )

    @model_validator(mode="after")
    def _unique_and_supported(self) -> Self:
        needs = [n.need for n in self.nearby]
        if len(needs) != len(set(needs)):
            msg = "each nearby need can appear once"
            raise ValueError(msg)
        if len(self.priorities) != len(set(self.priorities)):
            msg = "priorities must be unique"
            raise ValueError(msg)
        if self.zone_level not in {TerritoryLevel.MUNICIPIO, TerritoryLevel.SECCION_CENSAL}:
            msg = "zone_level must be municipio or seccion_censal"
            raise ValueError(msg)
        return self
