"""Read-only role for the public demo API (OPS-001, from line C's infra/deploy/sql).

Tables keep row level security with no policy for anon/authenticated (D-197), so Supabase's
Data API stays closed. The API connects as `vf_api_ro`: read-only by default and by privileges,
with SELECT and one explicit FOR SELECT policy on each table it reads (a table without a policy
would look empty to it, not fail). Idempotent and without a password: Mariano sets it out of
band (ALTER ROLE vf_api_ro PASSWORD ...) and uses it only in the hosting's DATABASE_URL.

Roles are cluster-wide, so downgrade removes this database's grants and policies but keeps the
role (other databases on the same server may still use it).

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-11 21:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROLE = "vf_api_ro"
POLICY = "vf_api_ro_read"
# Every table the API queries (tests/unit/api/test_readonly_role.py keeps this in sync).
API_TABLES = (
    "dataset_registry",
    "dataset_version",
    "feature_registry",
    "feature_value",
    "geo_admin_unit",
    "place_master",
    "source_registry",
)


CREATE_ROLE_IF_MISSING = """
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'vf_api_ro') THEN
            CREATE ROLE vf_api_ro LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
        END IF;
    END
    $$
"""


def _role_exists() -> bool:
    found = op.get_bind().execute(
        sa.text("SELECT 1 FROM pg_roles WHERE rolname = :role"), {"role": ROLE}
    )
    return found.first() is not None


def upgrade() -> None:
    op.execute(CREATE_ROLE_IF_MISSING)
    op.execute(f"ALTER ROLE {ROLE} SET default_transaction_read_only = on")
    op.execute(f"ALTER ROLE {ROLE} SET statement_timeout = '15s'")
    op.execute(f"ALTER ROLE {ROLE} SET search_path = public, extensions")
    op.execute(f"GRANT USAGE ON SCHEMA public, extensions TO {ROLE}")
    for table in API_TABLES:
        op.execute(f'GRANT SELECT ON public."{table}" TO {ROLE}')
        op.execute(f'DROP POLICY IF EXISTS {POLICY} ON public."{table}"')
        op.execute(f'CREATE POLICY {POLICY} ON public."{table}" FOR SELECT TO {ROLE} USING (true)')


def downgrade() -> None:
    for table in API_TABLES:
        op.execute(f'DROP POLICY IF EXISTS {POLICY} ON public."{table}"')
    if not _role_exists():
        return
    for table in API_TABLES:
        # "REVOKE SELECT ... FROM" is not a query; table and role are module constants.
        op.execute(f'REVOKE SELECT ON public."{table}" FROM {ROLE}')  # noqa: S608
    op.execute(f"REVOKE USAGE ON SCHEMA public, extensions FROM {ROLE}")
