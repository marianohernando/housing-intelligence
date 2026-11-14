"""ScenarioState v2 (CORE-001, decisions of 11 Nov): the single state chips, filters and map edit.

Budget to rent (€/month) or to buy (€), the household, where they work, what matters to them
and services wanted within walking distance. The search ranks the region by municipio with
Madrid capital split into its 21 districts. Sensitive needs are not part of this version;
«sin escaleras» is a functional preference, never a disability label (CLAUDE.md §13).
"""

from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

RENT_RANGE_EUR = (100, 20_000)
BUY_RANGE_EUR = (10_000, 5_000_000)


class BudgetKind(StrEnum):
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
    """«Me importa» chips. Seguridad only counts when chosen; sin escaleras is optional."""

    TRANSPORTE = "transporte"
    SALUD = "salud"
    COLEGIOS = "colegios"
    ZONAS_VERDES = "zonas_verdes"
    SEGURIDAD = "seguridad"
    SIN_ESCALERAS = "sin_escaleras"


class AnchorKind(StrEnum):
    WORK = "work"
    STUDY = "study"
    FAMILY = "family"
    OTHER = "other"


class Budget(BaseModel):
    """Rent in €/month or purchase price in €; the purchase result is always «orientativo»."""

    model_config = ConfigDict(extra="forbid")

    kind: BudgetKind
    amount_eur: int = Field(gt=0, description="€/month when kind=rent, € when kind=buy")

    @model_validator(mode="after")
    def _plausible(self) -> Self:
        low, high = RENT_RANGE_EUR if self.kind is BudgetKind.RENT else BUY_RANGE_EUR
        if not low <= self.amount_eur <= high:
            msg = f"{self.kind} budget must be between {low} and {high} €"
            raise ValueError(msg)
        return self


class Household(BaseModel):
    """«Tu hogar»: adults, children and older people they look after (all live together)."""

    model_config = ConfigDict(extra="forbid")

    adults: int = Field(default=1, ge=1, le=8)
    minors: int = Field(default=0, ge=0, le=8)
    minor_ages: list[int] = Field(default_factory=list[int], description="0-17, optional")
    seniors_in_care: int = Field(default=0, ge=0, le=4, description="People aged 65+ cared for")

    @model_validator(mode="after")
    def _coherent(self) -> Self:
        if self.minor_ages and len(self.minor_ages) != self.minors:
            msg = "minor_ages must list every minor or be empty"
            raise ValueError(msg)
        if any(not 0 <= age <= 17 for age in self.minor_ages):
            msg = "minor_ages must be between 0 and 17"
            raise ValueError(msg)
        return self

    @property
    def people(self) -> int:
        return self.adults + self.minors + self.seniors_in_care


class Anchor(BaseModel):
    """A place the household travels to often: where they work, or family and friends."""

    model_config = ConfigDict(extra="forbid")

    kind: AnchorKind = AnchorKind.WORK
    label: str = Field(min_length=1, max_length=80, examples=["Paseo de la Castellana (Azca)"])
    lon: float = Field(ge=-4.58, le=-3.05)
    lat: float = Field(ge=39.88, le=41.17)
    days_per_week: int = Field(
        default=5,
        ge=0,
        le=7,
        description="Days they go there in a week; 0 = never (full telework): the trip does "
        "not count (D-240)",
    )
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

    schema_version: Literal[2] = 2
    budget: Budget | None = Field(default=None, description="None = no budget limit")
    min_floor_area_m2: int | None = Field(
        default=None, ge=15, le=400, description="None = derived from the household size"
    )
    household: Household = Field(default_factory=Household)
    anchors: list[Anchor] = Field(default_factory=list[Anchor], max_length=3)
    nearby: list[NearbyNeed] = Field(default_factory=list[NearbyNeed], max_length=6)
    priorities: list[PriorityKey] = Field(
        default_factory=list[PriorityKey], max_length=6, description="Most important first"
    )

    @model_validator(mode="after")
    def _unique(self) -> Self:
        needs = [n.need for n in self.nearby]
        if len(needs) != len(set(needs)):
            msg = "each nearby need can appear once"
            raise ValueError(msg)
        if len(self.priorities) != len(set(self.priorities)):
            msg = "priorities must be unique"
            raise ValueError(msg)
        return self
