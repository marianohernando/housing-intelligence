"""Gold layer: feature registry and computed feature values (docs/02_data/36)."""

from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_db.base import Base
from hi_db.checks import in_enum


class FeatureRegistry(Base):
    __tablename__ = "feature_registry"

    feature_id: Mapped[str] = mapped_column(Text, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    human_name: Mapped[str] = mapped_column(Text, nullable=False)
    domain: Mapped[str] = mapped_column(Text, nullable=False)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    direction: Mapped[str] = mapped_column(Text, nullable=False)
    geo_level: Mapped[str] = mapped_column(Text, nullable=False)
    spec: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class FeatureValue(Base):
    __tablename__ = "feature_value"
    __table_args__ = (
        in_enum("territory_level", TerritoryLevel, "territory_level"),
        in_enum("null_reason", NullReason, "null_reason", nullable=True),
        CheckConstraint("(value IS NULL) <> (null_reason IS NULL)", name="value_xor_null_reason"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
        UniqueConstraint(
            "feature_id", "feature_version", "territory_level", "territory_code", "period_start"
        ),
        Index("ix_feature_value_lookup", "feature_id", "territory_level", "period_start"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    feature_id: Mapped[str] = mapped_column(
        ForeignKey("feature_registry.feature_id", ondelete="CASCADE"), nullable=False
    )
    feature_version: Mapped[int] = mapped_column(Integer, nullable=False)
    territory_level: Mapped[str] = mapped_column(Text, nullable=False)
    territory_code: Mapped[str] = mapped_column(Text, nullable=False)
    admin_unit_id: Mapped[str | None] = mapped_column(
        ForeignKey("geo_admin_unit.admin_unit_id", ondelete="SET NULL"), index=True
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[float | None] = mapped_column(Float)
    null_reason: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    inputs: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
