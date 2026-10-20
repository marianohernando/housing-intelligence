"""Feature Dictionary contract (docs/02_data/36_feature_dictionary_contract.md)."""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hi_contracts.catalog.dataset import DATASET_ID_PATTERN
from hi_contracts.catalog.enums import Domain, GeoResolution, H3JoinMethod

FEATURE_ID_PATTERN = r"^[a-z][a-z0-9_]{2,95}$"


class FeatureSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    role: Literal["primary", "secondary", "denominator", "validation"] = "primary"


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

    @model_validator(mode="after")
    def _productive_features_are_tested(self) -> Self:
        if (self.public_use or self.pro_use) and not (self.tests and self.limitations):
            msg = f"{self.feature_id}: productive features need tests and limitations"
            raise ValueError(msg)
        return self
