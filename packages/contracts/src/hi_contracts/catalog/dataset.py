"""Dataset contract + selection scorecard (docs/02_data/12 and 38)."""

from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from hi_contracts.catalog.enums import (
    DatasetStatus,
    Domain,
    GeoResolution,
    H3JoinMethod,
    LicenseStatus,
    NullReason,
    Priority,
)
from hi_contracts.catalog.source import SOURCE_ID_PATTERN

DATASET_ID_PATTERN = r"^[a-z][a-z0-9_]{2,95}$"
Score = int | None  # 0..5, None = needs human review


class Scorecard(BaseModel):
    """Every criterion is 0-5 and higher is better.

    `ingestion_ease` is the doc's "ingestion difficulty" expressed so that 5 = easiest,
    keeping every criterion in the same direction.
    """

    model_config = ConfigDict(extra="forbid")

    datamad_relevance: Score = Field(default=None, ge=0, le=5)
    product_impact: Score = Field(default=None, ge=0, le=5)
    geographic_granularity: Score = Field(default=None, ge=0, le=5)
    temporal_depth: Score = Field(default=None, ge=0, le=5)
    freshness: Score = Field(default=None, ge=0, le=5)
    coverage: Score = Field(default=None, ge=0, le=5)
    quality: Score = Field(default=None, ge=0, le=5)
    license_clarity: Score = Field(default=None, ge=0, le=5)
    ingestion_ease: Score = Field(default=None, ge=0, le=5)
    uniqueness: Score = Field(default=None, ge=0, le=5)
    demo_visibility: Score = Field(default=None, ge=0, le=5)
    notes: str | None = None
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None

    def pending_criteria(self) -> list[str]:
        scores = self.model_dump(exclude={"notes", "reviewed_by", "reviewed_at"})
        return sorted(k for k, v in scores.items() if v is None)


class ResourceSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    format: str
    url: HttpUrl
    role: str = Field(
        default="primary", description="primary | names | cross_check | docs | cm_portal"
    )
    file_name: str | None = Field(
        default=None,
        pattern=r"^[\w.\-]+$",
        description="Bronze file name when the URL does not end in one (e.g. ArcGIS /data)",
    )


class ColumnSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    description: str | None = None
    unit: str | None = None
    nullable: bool = True
    null_reason_default: NullReason | None = None


class TableSchemaSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary_key: list[str] = Field(default_factory=list[str])
    columns: dict[str, ColumnSpec] = Field(default_factory=dict[str, ColumnSpec])


class GeoSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resolution: GeoResolution
    crs_expected: str | None = Field(default=None, pattern=r"^EPSG:\d{4,5}$")
    geometry_type: str | None = None
    h3_join_method: H3JoinMethod | None = None


class DiscoverySpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    harvested_from: str
    external_id: str
    harvested_at: datetime


class DatasetSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    dataset_id: str = Field(pattern=DATASET_ID_PATTERN)
    source_id: str = Field(pattern=SOURCE_ID_PATTERN)
    name: str
    domain: Domain
    owner: str
    format: str
    geography: str = Field(description="polygon | point | line | table | none")
    geo: GeoSpec
    temporal_resolution: str | None = None
    refresh_policy: str
    landing_url: HttpUrl | None = None
    resources: list[ResourceSpec] = Field(default_factory=list[ResourceSpec])
    license_status: LicenseStatus
    status: DatasetStatus = DatasetStatus.DISCOVERED
    priority: Priority
    scorecard: Scorecard = Field(default_factory=Scorecard)
    table_schema: TableSchemaSpec = Field(default_factory=TableSchemaSpec, alias="schema")
    feeds_features: list[str] = Field(default_factory=list[str])
    discovery: DiscoverySpec | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _gates(self) -> Self:
        if self.priority is Priority.P0 and not self.scorecard.reviewed_by:
            msg = f"{self.dataset_id}: P0 requires a reviewed scorecard"
            raise ValueError(msg)
        if self.status is DatasetStatus.PRODUCTION:
            problems: list[str] = []
            if self.license_status is not LicenseStatus.CLEAR:
                problems.append("license_status must be CLEAR")
            if not self.table_schema.primary_key:
                problems.append("schema.primary_key required")
            if not self.scorecard.reviewed_by:
                problems.append("scorecard.reviewed_by required")
            if not self.resources:
                problems.append("at least one resource required")
            if problems:
                msg = f"{self.dataset_id}: PRODUCTION gate failed: {problems}"
                raise ValueError(msg)
        return self
