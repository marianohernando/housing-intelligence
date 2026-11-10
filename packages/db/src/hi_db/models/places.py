"""Canonical places and their source aliases (docs/02_data/13_entity_resolution_spec.md)."""

import uuid
from datetime import datetime
from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, Index, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from hi_contracts.catalog.enums import PlaceCategory, PlaceStatus
from hi_db.base import Base
from hi_db.checks import in_enum


class PlaceMaster(Base):
    __tablename__ = "place_master"
    __table_args__ = (
        in_enum("category", PlaceCategory, "category"),
        in_enum("status", PlaceStatus, "status"),
        UniqueConstraint("official_dataset_id", "official_entity_id"),
        Index("ix_place_master_geom_4326", "geom_4326", postgresql_using="gist"),
        Index("ix_place_master_geom_25830", "geom_25830", postgresql_using="gist"),
        Index("ix_place_master_category", "category", "subcategory"),
    )

    canonical_place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    canonical_name: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    subcategory: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    geom_4326 = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)
    geom_25830 = mapped_column(Geometry("POINT", srid=25830, spatial_index=False), nullable=False)
    municipio_ine: Mapped[str | None] = mapped_column(Text)
    seccion_admin_unit_id: Mapped[str | None] = mapped_column(
        ForeignKey("geo_admin_unit.admin_unit_id", ondelete="SET NULL"), index=True
    )
    h3_r9: Mapped[str | None] = mapped_column(Text, index=True)
    official_source_id: Mapped[str] = mapped_column(
        ForeignKey("source_registry.source_id", ondelete="RESTRICT"), nullable=False
    )
    official_dataset_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_registry.dataset_id", ondelete="RESTRICT"), nullable=False
    )
    official_entity_id: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    attributes: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dataset_version.id", ondelete="RESTRICT"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class PlaceSourceAlias(Base):
    __tablename__ = "place_source_alias"

    dataset_id: Mapped[str] = mapped_column(
        ForeignKey("dataset_registry.dataset_id", ondelete="RESTRICT"), primary_key=True
    )
    external_id: Mapped[str] = mapped_column(Text, primary_key=True)
    canonical_place_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("place_master.canonical_place_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[str] = mapped_column(
        ForeignKey("source_registry.source_id", ondelete="RESTRICT"), nullable=False
    )
    source_name: Mapped[str | None] = mapped_column(Text)
    source_address: Mapped[str | None] = mapped_column(Text)
    source_geom = mapped_column(Geometry("POINT", srid=4326, spatial_index=False))
    match_method: Mapped[str] = mapped_column(Text, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
