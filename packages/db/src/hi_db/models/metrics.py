"""Metric Registry and observations (docs/02_data/14, 26_null_and_missingness_contract)."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from hi_contracts.catalog.enums import AggregationMethod, Direction, NullReason, TerritoryLevel
from hi_db.base import Base
from hi_db.checks import in_enum


class MetricRegistry(Base):
    __tablename__ = "metric_registry"
    __table_args__ = (
        in_enum("direction", Direction, "direction"),
        in_enum("aggregation_method", AggregationMethod, "aggregation_method"),
        in_enum("geo_resolution_min", TerritoryLevel, "geo_resolution_min"),
    )

    metric_id: Mapped[str] = mapped_column(Text, primary_key=True)
    human_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    aggregation_method: Mapped[str] = mapped_column(Text, nullable=False)
    geo_resolution_min: Mapped[str] = mapped_column(Text, nullable=False)
    temporal_resolution: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_registry.dataset_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    dimensions: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, server_default=text("'[]'::jsonb")
    )
    null_policy: Mapped[str] = mapped_column(Text, nullable=False)
    public_visible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    pro_visible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sensitive: Mapped[bool] = mapped_column(Boolean, nullable=False)
    methodology_version: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class MetricObservation(Base):
    """One observed value, or an explicit null reason (never both, never neither)."""

    __tablename__ = "metric_observation"
    __table_args__ = (
        in_enum("territory_level", TerritoryLevel, "territory_level"),
        in_enum("null_reason", NullReason, "null_reason", nullable=True),
        CheckConstraint("(value IS NULL) <> (null_reason IS NULL)", name="value_xor_null_reason"),
        UniqueConstraint(
            "metric_id", "territory_level", "territory_code", "period_start", "dims_key"
        ),
        Index("ix_metric_observation_lookup", "metric_id", "territory_level", "period_start"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    metric_id: Mapped[str] = mapped_column(
        ForeignKey("metric_registry.metric_id", ondelete="CASCADE"), nullable=False
    )
    territory_level: Mapped[str] = mapped_column(Text, nullable=False)
    territory_code: Mapped[str] = mapped_column(Text, nullable=False)
    territory_name: Mapped[str | None] = mapped_column(Text)
    admin_unit_id: Mapped[str | None] = mapped_column(
        ForeignKey("geo_admin_unit.admin_unit_id", ondelete="SET NULL"), index=True
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    dims: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    dims_key: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("''"))
    value: Mapped[float | None] = mapped_column(Float)
    null_reason: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None] = mapped_column(Text)
    raw_value: Mapped[str | None] = mapped_column(Text)
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dataset_version.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
