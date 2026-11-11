"""The API's read-only role can read every table the API queries.

With row level security on, a table missing from the role's grants and policies does not fail:
it looks empty. This guard catches a new query against a table the role cannot see.
"""

import re
from pathlib import Path

API_SRC = Path("apps/api/src/hi_api")
ROLE_SQL = Path("infra/deploy/sql/api_readonly_role.sql")
TABLE_IN_SQL = re.compile(r"\b(?:FROM|JOIN)\s+([a-z_][a-z0-9_]*)")
ROLE_TABLES = re.compile(r"ARRAY\[(.*?)\]", re.DOTALL)


def _tables_queried_by_api(repo_root: Path) -> set[str]:
    sources = (p.read_text(encoding="utf-8") for p in (repo_root / API_SRC).rglob("*.py"))
    return {table for source in sources for table in TABLE_IN_SQL.findall(source)}


def _tables_granted(repo_root: Path) -> set[str]:
    sql = (repo_root / ROLE_SQL).read_text(encoding="utf-8")
    match = ROLE_TABLES.search(sql)
    assert match, "the role SQL must list its tables in an ARRAY[...]"
    return set(re.findall(r"'([a-z_][a-z0-9_]*)'", match.group(1)))


def test_role_can_read_every_table_the_api_queries(repo_root: Path) -> None:
    queried = _tables_queried_by_api(repo_root)
    assert "geo_admin_unit" in queried  # the parser still finds the API's SQL
    missing = queried - _tables_granted(repo_root)
    assert not missing, f"add {sorted(missing)} to {ROLE_SQL}"


def test_role_sql_has_no_password_and_is_read_only(repo_root: Path) -> None:
    sql = (repo_root / ROLE_SQL).read_text(encoding="utf-8")
    statements = "\n".join(line for line in sql.splitlines() if not line.lstrip().startswith("--"))
    assert "PASSWORD" not in statements.upper()
    assert "default_transaction_read_only = on" in statements
    assert not re.search(r"GRANT\s+(INSERT|UPDATE|DELETE|ALL)", statements, re.IGNORECASE)
