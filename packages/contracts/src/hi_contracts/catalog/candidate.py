"""Harvested dataset candidate (output of catalog harvesters, input of scoring)."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CandidateResource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    format: str | None = None
    url: str | None = None


class BronzeRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    sha256: str


class CandidateRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate_id: str
    source_id: str
    external_id: str
    name: str
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=list[str])
    formats: list[str] = Field(default_factory=list[str])
    landing_url: str | None = None
    resources: list[CandidateResource] = Field(default_factory=list[CandidateResource])
    publisher: str | None = None
    license_id: str | None = None
    license_title: str | None = None
    modified_at: datetime | None = None
    geographic_coverage: str | None = None
    update_frequency: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict[str, Any])
    bronze_ref: BronzeRef | None = None
