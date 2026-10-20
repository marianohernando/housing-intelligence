"""Response envelope shared by every API endpoint."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

API_VERSION = "v1"


class ErrorCode(StrEnum):
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    INVALID_PROFILE = "INVALID_PROFILE"
    OUT_OF_COVERAGE = "OUT_OF_COVERAGE"
    SOURCE_DEGRADED = "SOURCE_DEGRADED"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    CONSENT_REQUIRED = "CONSENT_REQUIRED"
    RATE_LIMITED = "RATE_LIMITED"
    NOT_FOUND = "NOT_FOUND"


class Meta(BaseModel):
    request_id: str = Field(default_factory=lambda: uuid4().hex)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    api_version: str = API_VERSION
    methodology_version: str | None = None
    data_version: str | None = None


class Envelope[T](BaseModel):
    data: T
    meta: Meta = Field(default_factory=Meta)
    warnings: list[str] = Field(default_factory=list[str])


class ErrorBody(BaseModel):
    code: ErrorCode
    message: str
    details: dict[str, Any] = Field(default_factory=dict[str, Any])


class ErrorEnvelope(BaseModel):
    error: ErrorBody
