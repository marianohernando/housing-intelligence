"""Pharmacies get their own place category (D-216, T1 data audit).

Pharmacies were `health`, so any client asking for the health-care layer (primary care and
hospitals) also got 2,953 pharmacies. The category check gains `pharmacy`; the places
themselves move when `cm_oficinas_farmacia` is ingested again. Downgrade moves them back.

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-12 01:00:00.000000+00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CONSTRAINT = "ck_place_master_category"
BEFORE = (
    "education",
    "health",
    "social",
    "transport",
    "commerce",
    "culture",
    "sport",
    "administration",
    "green",
    "other",
)
AFTER = ("education", "health", "pharmacy", *BEFORE[2:])


def _check(values: tuple[str, ...]) -> str:
    return "category IN (" + ", ".join(f"'{v}'" for v in values) + ")"


def upgrade() -> None:
    op.drop_constraint(op.f(CONSTRAINT), "place_master", type_="check")
    op.create_check_constraint(op.f(CONSTRAINT), "place_master", _check(AFTER))


def downgrade() -> None:
    op.execute("UPDATE place_master SET category = 'health' WHERE category = 'pharmacy'")
    op.drop_constraint(op.f(CONSTRAINT), "place_master", type_="check")
    op.create_check_constraint(op.f(CONSTRAINT), "place_master", _check(BEFORE))
