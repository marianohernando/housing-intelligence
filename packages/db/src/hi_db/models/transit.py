"""Gold layer: public transport commute times to the places one can say they work (CORE-009)."""

from datetime import datetime
from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from hi_db.base import Base


class TransitHub(Base):
    """A destination of the commute: a rail station or the population centre of a zone."""

    __tablename__ = "transit_hub"
    __table_args__ = (CheckConstraint("kind IN ('station', 'zone')", name="kind"),)

    hub_id: Mapped[str] = mapped_column(Text, primary_key=True)
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    subcategory: Mapped[str | None] = mapped_column(Text)
    admin_unit_id: Mapped[str | None] = mapped_column(Text)
    geom_4326 = mapped_column(Geometry("POINT", srid=4326, spatial_index=False), nullable=False)
    method_version: Mapped[str] = mapped_column(Text, nullable=False)
    inputs: Mapped[dict[str, Any]] = mapped_column(
        JSONB, nullable=False, server_default=text("'{}'::jsonb")
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class CommuteTime(Base):
    """Minutes by public transport from a zone (median of its census sections) to a hub."""

    __tablename__ = "commute_time"

    hub_id: Mapped[str] = mapped_column(
        ForeignKey("transit_hub.hub_id", ondelete="CASCADE"), primary_key=True
    )
    origin_admin_unit_id: Mapped[str] = mapped_column(Text, primary_key=True)
    minutes: Mapped[float | None] = mapped_column(Float)  # None: not reachable in the window
    sections: Mapped[int] = mapped_column(Integer, nullable=False)
    sections_reached: Mapped[int] = mapped_column(Integer, nullable=False)
