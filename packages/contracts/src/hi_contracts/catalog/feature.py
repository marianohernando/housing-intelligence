"""Feature Dictionary contract (docs/02_data/36_feature_dictionary_contract.md)."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hi_contracts.catalog.dataset import DATASET_ID_PATTERN
from hi_contracts.catalog.enums import Domain, GapRowKey, GeoResolution, H3JoinMethod

FEATURE_ID_PATTERN = r"^[a-z][a-z0-9_]{2,95}$"


class FeatureSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    role: Literal["primary", "secondary", "denominator", "validation"] = "primary"
    levels: list[GeoResolution] | None = Field(
        default=None,
        description="Levels whose computation uses this dataset (the feature's geo_level or a "
        "key of formula.levels); None means every level. Each row cites only its own.",
    )


class FeatureFormula(BaseModel):
    model_config = ConfigDict(extra="allow")

    method: str


class NullPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    no_coverage: Literal["unknown", "not_applicable"] = "unknown"
    confirmed_zero: Literal[0, "unknown"] = 0


class FeatureConfidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    inputs: list[str] = Field(default_factory=list[str])


class GapRowBinding(BaseModel):
    """Where the feature shows up in the per-zone list (GAP-001): the row's main indicator,
    or an extra one next to it (e.g. walking minutes)."""

    model_config = ConfigDict(extra="forbid")

    row: GapRowKey
    role: Literal["primary", "extra"] = "primary"
    label: str | None = Field(default=None, description="Row title; required for primary")
    phrase: str = Field(description="Unit in words, e.g. 'colegios por cada 1.000 menores'")
    proxy_note: str | None = Field(default=None, description="What the indicator does not measure")

    @model_validator(mode="after")
    def _primary_has_label(self) -> Self:
        if self.role == "primary" and not self.label:
            msg = f"{self.row}: a primary indicator needs the row label"
            raise ValueError(msg)
        return self


class FitBinding(BaseModel):
    """Where the people search (CORE-003) reads the feature: the rent or the appraised purchase
    value per m² of the budget condition (D-227), or the walking minutes to the nearest place
    of a kind, either a service (a ScenarioState NeedKey) or what a «me importa» priority
    measures (a PriorityKey: the park for «Zonas verdes», D-222). The search has no feature id
    written in its code."""

    model_config = ConfigDict(extra="forbid")

    role: Literal["rent_m2", "price_m2", "walk_minutes"]
    need: str | None = Field(
        default=None, pattern=r"^[a-z_]+$", description="NeedKey, only for walk_minutes"
    )
    priority: str | None = Field(
        default=None, pattern=r"^[a-z_]+$", description="PriorityKey, only for walk_minutes"
    )

    @model_validator(mode="after")
    def _one_target_only_for_walking(self) -> Self:
        targets = (self.need is not None) + (self.priority is not None)
        if (self.role == "walk_minutes") != (targets == 1) or (
            self.role != "walk_minutes" and targets
        ):
            msg = "walk_minutes needs one of `need` or `priority`; rent_m2 and price_m2 take none"
            raise ValueError(msg)
        return self


class FeatureSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    feature_id: str = Field(pattern=FEATURE_ID_PATTERN)
    version: int = Field(ge=1)
    human_name: str
    domain: Domain
    type: Literal["raw", "derived", "aggregate", "model_output"]
    unit: str
    direction: Literal["higher_is_better", "lower_is_better", "neutral", "target_range"]
    geo_level: GeoResolution
    h3_join_method: H3JoinMethod | None = None
    time_semantics: Literal["current", "snapshot", "period", "forecast", "scenario"]
    sources: list[FeatureSource] = Field(min_length=1)
    formula: FeatureFormula
    null_policy: NullPolicy = Field(default_factory=NullPolicy)
    confidence: FeatureConfidence = Field(default_factory=FeatureConfidence)
    public_use: bool = False
    pro_use: bool = False
    models: list[str] = Field(default_factory=list[str])
    tests: list[str] = Field(default_factory=list[str])
    limitations: list[str] = Field(default_factory=list[str])
    gap_row: GapRowBinding | None = None
    fit: FitBinding | None = None

    @model_validator(mode="after")
    def _productive_features_are_tested(self) -> Self:
        if (self.public_use or self.pro_use) and not (self.tests and self.limitations):
            msg = f"{self.feature_id}: productive features need tests and limitations"
            raise ValueError(msg)
        return self
