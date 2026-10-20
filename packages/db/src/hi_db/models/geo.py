"""Canonical geography: admin units and H3 cells (docs/02_data/04 and 16)."""

import uuid
from datetime import date, datetime

from geoalchemy2 import Geometry
from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    SmallInteger,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from hi_contracts.catalog.enums import AdminLevel, H3JoinMethod
from hi_db.base import Base
from hi_db.checks import in_enum

H3_RESOLUTIONS = (7, 8, 9, 10)


class GeoAdminUnit(Base):
    __tablename__ = "geo_admin_unit"
    __table_args__ = (
        in_enum("level", AdminLevel, "level"),
        UniqueConstraint("level", "code_official"),
        Index("ix_geo_admin_unit_geom_4326", "geom_4326", postgresql_using="gist"),
        Index("ix_geo_admin_unit_geom_25830", "geom_25830", postgresql_using="gist"),
    )

    admin_unit_id: Mapped[str] = mapped_column(Text, primary_key=True)
    level: Mapped[str] = mapped_column(Text, nullable=False)
    code_official: Mapped[str] = mapped_column(Text, nullable=False)
    code_source: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(Text)
    parent_admin_unit_id: Mapped[str | None] = mapped_column(
        ForeignKey("geo_admin_unit.admin_unit_id", ondelete="RESTRICT"), index=True
    )
    geom_4326 = mapped_column(
        Geometry("MULTIPOLYGON", srid=4326, spatial_index=False), nullable=False
    )
    geom_25830 = mapped_column(
        Geometry("MULTIPOLYGON", srid=25830, spatial_index=False), nullable=False
    )
    area_m2: Mapped[float] = mapped_column(Float, nullable=False)
    source_id: Mapped[str] = mapped_column(
        ForeignKey("source_registry.source_id", ondelete="RESTRICT"), nullable=False
    )
    dataset_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dataset_version.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class H3Cell(Base):
    __tablename__ = "h3_cell"
    __table_args__ = (
        CheckConstraint(f"resolution IN {H3_RESOLUTIONS}", name="resolution"),
        Index("ix_h3_cell_geom_4326", "geom_4326", postgresql_using="gist"),
        Index("ix_h3_cell_resolution", "resolution"),
    )

    h3_index: Mapped[str] = mapped_column(Text, primary_key=True)
    resolution: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    geom_4326 = mapped_column(Geometry("POLYGON", srid=4326, spatial_index=False), nullable=False)
    centroid_4326 = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)


class H3CellAdminUnit(Base):
    __tablename__ = "h3_cell_admin_unit"
    __table_args__ = (
        in_enum("method", H3JoinMethod, "method"),
        CheckConstraint("overlap_share > 0 AND overlap_share <= 1.000001", name="overlap_share"),
    )

    h3_index: Mapped[str] = mapped_column(
        ForeignKey("h3_cell.h3_index", ondelete="CASCADE"), primary_key=True
    )
    admin_unit_id: Mapped[str] = mapped_column(
        ForeignKey("geo_admin_unit.admin_unit_id", ondelete="CASCADE"), primary_key=True, index=True
    )
    method: Mapped[str] = mapped_column(Text, primary_key=True)
    overlap_share: Mapped[float] = mapped_column(Float, nullable=False)
