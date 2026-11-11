"""Source / dataset / version / run registries (docs/02_data/11 and 12)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from hi_contracts.catalog.enums import (
    ApiType,
    DatasetStatus,
    LicenseStatus,
    PipelineStage,
    Priority,
    RunStatus,
    TrustTier,
)
from hi_db.base import Base
from hi_db.checks import in_enum


def _created() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class SourceRegistry(Base):
    __tablename__ = "source_registry"
    __table_args__ = (
        in_enum("trust_tier", TrustTier, "trust_tier"),
        in_enum("license_status", LicenseStatus, "license_status"),
        in_enum("api_type", ApiType, "api_type"),
    )

    source_id: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(Text, nullable=False)
    api_type: Mapped[str] = mapped_column(Text, nullable=False)
    base_url: Mapped[str | None] = mapped_column(Text)
    catalog_url: Mapped[str | None] = mapped_column(Text)
    license_name: Mapped[str | None] = mapped_column(Text)
    license_url: Mapped[str | None] = mapped_column(Text)
    license_status: Mapped[str] = mapped_column(Text, nullable=False)
    attribution_text: Mapped[str | None] = mapped_column(Text)
    commercial_use: Mapped[bool | None] = mapped_column(Boolean)
    redistribution_allowed: Mapped[bool | None] = mapped_column(Boolean)
    trust_tier: Mapped[str] = mapped_column(Text, nullable=False)
    default_confidence: Mapped[float | None] = mapped_column(Numeric(4, 3))
    update_frequency: Mapped[str | None] = mapped_column(Text)
    geographic_scope: Mapped[str | None] = mapped_column(Text)
    terms_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = _created()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class DatasetRegistry(Base):
    __tablename__ = "dataset_registry"
    __table_args__ = (
        in_enum("status", DatasetStatus, "status"),
        in_enum("priority", Priority, "priority"),
        in_enum("license_status", LicenseStatus, "license_status"),
    )

    dataset_id: Mapped[str] = mapped_column(Text, primary_key=True)
    source_id: Mapped[str] = mapped_column(
        ForeignKey("source_registry.source_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(Text, nullable=False)
    geography: Mapped[str] = mapped_column(Text, nullable=False)
    geo_resolution: Mapped[str] = mapped_column(Text, nullable=False)
    temporal_resolution: Mapped[str | None] = mapped_column(Text)
    refresh_policy: Mapped[str] = mapped_column(Text, nullable=False)
    landing_url: Mapped[str | None] = mapped_column(Text)
    license_status: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(Text, nullable=False)
    scorecard: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    catalog_yaml_path: Mapped[str | None] = mapped_column(Text)
    portal_url: Mapped[str | None] = mapped_column(Text)  # CM portal page when there is one
    is_cm_open_data: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = _created()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class DatasetVersion(Base):
    __tablename__ = "dataset_version"
    __table_args__ = (UniqueConstraint("dataset_id", "checksum_sha256"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_registry.dataset_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    version_label: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_modified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    checksum_sha256: Mapped[str] = mapped_column(Text, nullable=False)
    byte_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer)
    schema_hash: Mapped[str | None] = mapped_column(Text)
    parser_version: Mapped[str] = mapped_column(Text, nullable=False)
    quality_status: Mapped[str | None] = mapped_column(Text)
    bronze_manifest_path: Mapped[str] = mapped_column(Text, nullable=False)
    is_last_valid: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = _created()


class IngestionRun(Base):
    __tablename__ = "ingestion_run"
    __table_args__ = (
        in_enum("stage", PipelineStage, "stage"),
        in_enum("status", RunStatus, "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_registry.dataset_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    dataset_version_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("dataset_version.id", ondelete="SET NULL")
    )
    correlation_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    stage: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metrics: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    error: Mapped[str | None] = mapped_column(Text)
