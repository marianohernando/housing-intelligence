"""Row level security on every public table, without policies (D-197).

Supabase exposes schema public through its Data API to the anon and authenticated roles. The
product never uses that API: the backend connects as the table owner, which bypasses RLS. With
RLS on and no policies, the Data API sees no rows and cannot write.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-11 11:30:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = (
    "alembic_version",
    "source_registry",
    "dataset_registry",
    "dataset_version",
    "ingestion_run",
    "geo_admin_unit",
    "h3_cell",
    "h3_cell_admin_unit",
    "metric_registry",
    "metric_observation",
    "place_master",
    "place_source_alias",
    "feature_registry",
    "feature_value",
)


def upgrade() -> None:
    for table in TABLES:
        op.execute(f'ALTER TABLE public."{table}" ENABLE ROW LEVEL SECURITY')


def downgrade() -> None:
    for table in TABLES:
        op.execute(f'ALTER TABLE public."{table}" DISABLE ROW LEVEL SECURITY')
