"""People search result (CORE-003): ranked zones with readable reasons and a Reality Check.

Hard constraints are PASS / FAIL / UNKNOWN and UNKNOWN never counts as PASS (CLAUDE.md §14).
Zones that fail one constraint are only shown as explicit near misses.
"""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.public.common import DatasetRef, IndicatorValue, ZoneRef
from hi_contracts.public.scenario import ScenarioState


class ConstraintStatus(StrEnum):
    PASS = "PASS"  # noqa: S105 - constraint status, not a credential
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class ConstraintCheck(BaseModel):
    """One hard condition of the scenario evaluated on one zone."""

    model_config = ConfigDict(extra="forbid")

    constraint_id: str = Field(
        pattern=r"^(budget|near:[a-z_]+|commute:\d)$",
        examples=["budget", "near:colegio", "commute:0"],
    )
    label: str = Field(examples=["Alquiler hasta 1.500 €/mes"])
    status: ConstraintStatus
    value: float | None = None
    threshold: float | None = None
    unit: str | None = None
    confidence: float = Field(ge=0, le=1)
    explanation: str = Field(examples=["Un piso de 90 m² cuesta unos 1.420 €/mes aquí"])


class ReasonKind(StrEnum):
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    UNKNOWN = "unknown"


class Reason(BaseModel):
    """A plain-language «why» line, always traceable to an indicator and its datasets."""

    model_config = ConfigDict(extra="forbid")

    kind: ReasonKind
    text: str = Field(examples=["Hay un colegio a 6 minutos a pie desde la mitad de sus calles"])
    indicator: IndicatorValue | None = None


class RankedZone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int = Field(ge=1)
    zone: ZoneRef
    score: float = Field(ge=0, le=100, description="Personal fit, not a territorial grade")
    confidence: float = Field(ge=0, le=1)
    constraints: list[ConstraintCheck]
    reasons: list[Reason] = Field(max_length=6)
    estimated_rent_eur: float | None = Field(
        default=None, ge=0, description="Monthly rent for the needed floor area"
    )
    failed_constraints: list[str] = Field(
        default_factory=list[str], description="constraint_id values with FAIL (near misses)"
    )


class Relaxation(BaseModel):
    """How many more zones appear when one condition is relaxed and the rest stay."""

    model_config = ConfigDict(extra="forbid")

    constraint_id: str
    label: str = Field(examples=["Colegio a 15 minutos en vez de 10"])
    relaxed_to: float | None = Field(default=None, description="None = condition removed")
    unit: str | None = None
    zones_if_relaxed: int = Field(ge=0)
    added_zones: int = Field(ge=0)


class RealityCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zones_evaluated: int = Field(ge=0)
    zones_passing: int = Field(ge=0, description="Every constraint PASS")
    zones_unknown: int = Field(ge=0, description="No FAIL but some UNKNOWN: not counted as passing")
    binding_constraint: str | None = Field(
        default=None, description="constraint_id that removes the most zones"
    )
    relaxations: list[Relaxation] = Field(description="Sorted by added_zones, largest first")

    @model_validator(mode="after")
    def _counts_add_up(self) -> Self:
        if self.zones_passing + self.zones_unknown > self.zones_evaluated:
            msg = "passing + unknown zones cannot exceed the evaluated zones"
            raise ValueError(msg)
        for relaxation in self.relaxations:
            if relaxation.zones_if_relaxed != self.zones_passing + relaxation.added_zones:
                msg = f"{relaxation.constraint_id}: zones_if_relaxed = passing + added"
                raise ValueError(msg)
        return self


class SearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: ScenarioState
    zone_level: TerritoryLevel
    results: list[RankedZone] = Field(description="Zones passing every constraint, best first")
    near_misses: list[RankedZone] = Field(
        default_factory=list[RankedZone], description="Explicit alternatives failing one condition"
    )
    reality_check: RealityCheck
    datasets: list[DatasetRef] = Field(description="Every dataset behind this result")
    methodology_version: str
