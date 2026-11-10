"""Metric Registry contract (docs/02_data/14_metric_registry_spec.md).

A metric is an observed quantity published by a source (not a derived score).
"""

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hi_contracts.catalog.dataset import DATASET_ID_PATTERN
from hi_contracts.catalog.enums import AggregationMethod, Direction, Domain, TerritoryLevel

METRIC_ID_PATTERN = r"^[a-z][a-z0-9_]{2,95}$"


class MetricSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    metric_id: str = Field(pattern=METRIC_ID_PATTERN)
    human_name: str
    description: str
    domain: Domain
    unit: str
    direction: Direction = Direction.NEUTRAL
    aggregation_method: AggregationMethod
    geo_resolution_min: TerritoryLevel
    temporal_resolution: str
    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    dimensions: list[str] = Field(default_factory=list[str])
    null_policy: str = "do_not_impute"
    public_visible: bool = True
    pro_visible: bool = True
    sensitive: bool = False
    methodology_version: str = "1"

    @model_validator(mode="after")
    def _sensitive_metrics_are_not_public(self) -> Self:
        if self.sensitive and self.public_visible:
            msg = f"{self.metric_id}: sensitive metrics cannot be public_visible"
            raise ValueError(msg)
        return self
