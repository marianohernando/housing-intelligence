"""Dataset provenance for the API: portal link and whether it counts as CM open data.

The CRTM GTFS datasets keep their CRTM landing page but are also published in the Comunidad de
Madrid portal (D-196); the result panels must link that portal page and count them as CM.

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-11 19:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("dataset_registry", sa.Column("portal_url", sa.Text(), nullable=True))
    op.add_column(
        "dataset_registry",
        sa.Column("is_cm_open_data", sa.Boolean(), server_default=sa.false(), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("dataset_registry", "is_cm_open_data")
    op.drop_column("dataset_registry", "portal_url")
