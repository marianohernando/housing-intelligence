"""The API's read-only role can read every table the API queries.

With row level security on, a table missing from the role's grants and policies does not fail:
it looks empty. This guard catches a new query against a table the role cannot see.
"""

import re
from pathlib import Path

API_SRC = Path("apps/api/src/hi_api")
ROLE_SQL = Path("infra/deploy/sql/api_readonly_role.sql")

# SQL lives in sqlalchemy text("...") calls; prose in docstrings and comments is ignored.
SQL_IN_TEXT_CALL = re.compile(r'\btext\(\s*(?:"""(.*?)"""|"([^"\n]*)")', re.DOTALL)
# Table after FROM/JOIN (optionally LATERAL/ONLY, optionally schema-qualified); set-returning
# functions such as jsonb_array_elements(...) are skipped.
TABLE_IN_SQL = re.compile(
    r"\b(?:FROM|JOIN)\s+(?:(?:LATERAL|ONLY)\s+)?(?!(?:LATERAL|ONLY)\b)"
    r"(?:[a-z_]\w*\.)?([a-z_]\w*)\b(?!\s*\()",
    re.IGNORECASE,
)
CTE_NAME = re.compile(r"\b([a-z_]\w*)\s+AS\s*(?:NOT\s+)?(?:MATERIALIZED\s+)?\(", re.IGNORECASE)
ROLE_TABLES = re.compile(r"ARRAY\[(.*?)\]", re.DOTALL)


def tables_in_sql(sql: str) -> set[str]:
    ctes = {name.lower() for name in CTE_NAME.findall(sql)}
    return {table.lower() for table in TABLE_IN_SQL.findall(sql)} - ctes


def _tables_queried_by_api(repo_root: Path) -> set[str]:
    tables: set[str] = set()
    for path in (repo_root / API_SRC).rglob("*.py"):
        for block, line in SQL_IN_TEXT_CALL.findall(path.read_text(encoding="utf-8")):
            tables |= tables_in_sql(block or line)
    return tables


def _tables_granted(repo_root: Path) -> set[str]:
    sql = (repo_root / ROLE_SQL).read_text(encoding="utf-8")
    match = ROLE_TABLES.search(sql)
    assert match, "the role SQL must list its tables in an ARRAY[...]"
    return set(re.findall(r"'([a-z_]\w*)'", match.group(1)))


def test_parser_handles_schemas_functions_ctes_and_case() -> None:
    sql = """
        WITH recent AS (SELECT * FROM public.feature_value)
        select r.x from recent r
          join geo_admin_unit u ON true
          CROSS JOIN LATERAL jsonb_array_elements(u.tags) t
    """
    assert tables_in_sql(sql) == {"feature_value", "geo_admin_unit"}


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
