"""Public transport commute times (CORE-009, D-220).

Two Gold tables: `transit_hub` (rail stations and the population centre of each zone, where one
can say they work) and `commute_time` (minutes from each zone to each hub, arriving by 9:00).
Row level security on both (D-197) and read access for the API role (D-208).

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-12 12:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROLE = "vf_api_ro"
POLICY = "vf_api_ro_read"
# Tables the API reads (tests/unit/api/test_readonly_role.py).
API_TABLES = ("transit_hub", "commute_time")


def upgrade() -> None:
    op.create_table(
        "transit_hub",
        sa.Column("hub_id", sa.Text(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("label", sa.Text(), nullable=False),
        sa.Column("subcategory", sa.Text(), nullable=True),
        sa.Column("admin_unit_id", sa.Text(), nullable=True),
        sa.Column(
            "geom_4326",
            Geometry("POINT", srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column("method_version", sa.Text(), nullable=False),
        sa.Column(
            "inputs",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "computed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("kind IN ('station', 'zone')", name=op.f("ck_transit_hub_kind")),
        sa.PrimaryKeyConstraint("hub_id", name=op.f("pk_transit_hub")),
    )
    op.create_table(
        "commute_time",
        sa.Column("hub_id", sa.Text(), nullable=False),
        sa.Column("origin_admin_unit_id", sa.Text(), nullable=False),
        sa.Column("minutes", sa.Float(), nullable=True),
        sa.Column("sections", sa.Integer(), nullable=False),
        sa.Column("sections_reached", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hub_id"],
            ["transit_hub.hub_id"],
            name=op.f("fk_commute_time_hub_id_transit_hub"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("hub_id", "origin_admin_unit_id", name=op.f("pk_commute_time")),
    )
    for table in API_TABLES:
        op.execute(f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY')
        op.execute(f'GRANT SELECT ON public."{table}" TO {ROLE}')
        op.execute(f'CREATE POLICY {POLICY} ON public."{table}" FOR SELECT TO {ROLE} USING (true)')


def downgrade() -> None:
    op.drop_table("commute_time")
    op.drop_table("transit_hub")
