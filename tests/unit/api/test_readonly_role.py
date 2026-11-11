"""The API's read-only role can read every table the API queries.

With row level security on, a table missing from the role's grants and policies does not fail:
it looks empty. This guard catches a new query against a table the role cannot see.

The role is created by migration 0005 (`API_TABLES`); a later migration that grants more tables
declares its own `API_TABLES`. `infra/deploy/sql/api_readonly_role.sql` is the same role as a
hand-run script and must list the same tables.
"""

import ast
import re
from pathlib import Path

API_SRC = Path("apps/api/src/hi_api")
MIGRATIONS = Path("infra/migrations/versions")
ROLE_MIGRATION = MIGRATIONS / "0005_api_readonly_role.py"
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
WRITE_GRANT = re.compile(r"GRANT\b[^;\n]*\b(INSERT|UPDATE|DELETE|TRUNCATE|ALL)\b", re.IGNORECASE)


def tables_in_sql(sql: str) -> set[str]:
    ctes = {name.lower() for name in CTE_NAME.findall(sql)}
    return {table.lower() for table in TABLE_IN_SQL.findall(sql)} - ctes


def _tables_queried_by_api(repo_root: Path) -> set[str]:
    tables: set[str] = set()
    for path in (repo_root / API_SRC).rglob("*.py"):
        for block, line in SQL_IN_TEXT_CALL.findall(path.read_text(encoding="utf-8")):
            tables |= tables_in_sql(block or line)
    return tables


def _api_tables(module: ast.Module) -> set[str]:
    for node in module.body:
        if (
            isinstance(node, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == "API_TABLES" for t in node.targets)
            and isinstance(node.value, ast.Tuple)
        ):
            return {str(ast.literal_eval(elt)) for elt in node.value.elts}
    return set()


def _tables_granted_by_migrations(repo_root: Path) -> set[str]:
    tables: set[str] = set()
    for path in sorted((repo_root / MIGRATIONS).glob("*.py")):
        tables |= _api_tables(ast.parse(path.read_text(encoding="utf-8")))
    return tables


def _tables_in_role_sql(repo_root: Path) -> set[str]:
    sql = (repo_root / ROLE_SQL).read_text(encoding="utf-8")
    match = ROLE_TABLES.search(sql)
    assert match, "the role SQL must list its tables in an ARRAY[...]"
    return set(re.findall(r"'([a-z_]\w*)'", match.group(1)))


def _upgrade_source(path: Path) -> str:
    """Only the statements the migration runs; the module docstring may mention PASSWORD."""
    source = path.read_text(encoding="utf-8")
    for node in ast.parse(source).body:
        if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
            return ast.get_source_segment(source, node) or ""
    raise AssertionError(f"{path} has no upgrade()")


def test_parser_handles_schemas_functions_ctes_and_case() -> None:
    sql = """
        WITH recent AS (SELECT * FROM public.feature_value)
        select r.x from recent r
          join geo_admin_unit u ON true
          CROSS JOIN LATERAL jsonb_array_elements(u.tags) t
    """
    assert tables_in_sql(sql) == {"feature_value", "geo_admin_unit"}


def test_write_grant_detection_covers_privilege_lists() -> None:
    assert WRITE_GRANT.search("GRANT SELECT, INSERT ON public.x TO r")
    assert WRITE_GRANT.search("grant all on schema public to r")
    assert not WRITE_GRANT.search("GRANT SELECT ON public.x TO r")


def test_role_can_read_every_table_the_api_queries(repo_root: Path) -> None:
    queried = _tables_queried_by_api(repo_root)
    assert "geo_admin_unit" in queried  # the parser still finds the API's SQL
    missing = queried - _tables_granted_by_migrations(repo_root)
    assert not missing, f"grant {sorted(missing)} to vf_api_ro in a migration (API_TABLES)"


def test_hand_run_role_sql_matches_the_migrations(repo_root: Path) -> None:
    assert _tables_in_role_sql(repo_root) == _tables_granted_by_migrations(repo_root)


def test_role_has_no_password_and_is_read_only(repo_root: Path) -> None:
    sql = (repo_root / ROLE_SQL).read_text(encoding="utf-8")
    script = "\n".join(line for line in sql.splitlines() if not line.lstrip().startswith("--"))
    for statements in (script, _upgrade_source(repo_root / ROLE_MIGRATION)):
        assert "PASSWORD" not in statements.upper()
        assert "default_transaction_read_only = on" in statements
        assert not WRITE_GRANT.search(statements)
