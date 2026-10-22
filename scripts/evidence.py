"""Generate a Quality Gate evidence folder (docs/11_engineering/23_evidence_artifact_standard.md).

Usage: uv run python scripts/evidence.py --gate 00 [--date YYYY-MM-DD]
Every check runs a real command; its output is stored next to summary.md.
"""

import argparse
import json
import os
import platform
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DB_ENV = {
    "TEST_DATABASE_URL": os.environ.get(
        "TEST_DATABASE_URL", "postgresql+psycopg://housing:housing@localhost:5440/housing_test"
    ),
    "DATABASE_URL": os.environ.get(
        "DATABASE_URL", "postgresql+psycopg://housing:housing@localhost:5440/housing"
    ),
}


@dataclass(frozen=True)
class Check:
    check_id: str
    criterion: str
    command: list[str]
    validate: Callable[[subprocess.CompletedProcess[str]], bool] = lambda r: r.returncode == 0


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ | DB_ENV
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, env=env, check=False)


def _head() -> str:
    return _run(["git", "rev-parse", "HEAD"]).stdout.strip()


def _ci_green_for_head(result: subprocess.CompletedProcess[str]) -> bool:
    if result.returncode != 0:
        return False
    runs = json.loads(result.stdout or "[]")
    return any(r["headSha"] == _head() and r["conclusion"] == "success" for r in runs)


GATE_00 = [
    Check("lint", "lint (ruff + eslint)", ["make", "lint"]),
    Check("typecheck", "typecheck (pyright + tsc)", ["make", "typecheck"]),
    Check(
        "unit",
        "unit test scaffold",
        ["uv", "run", "pytest", "tests/unit", "tests/data", "-q", "-p", "no:randomly"],
    ),
    Check("web-unit", "web unit tests", ["npm", "run", "-w", "apps/web", "test", "--", "--run"]),
    Check(
        "migrations",
        "migrations up/down + no model drift",
        ["uv", "run", "pytest", "-m", "db", "tests/integration/test_migrations.py", "-q"],
    ),
    Check(
        "docker-boot",
        "Docker/local boot (db + redis healthy)",
        ["docker", "compose", "ps", "--format", "{{.Name}} {{.Status}}"],
        lambda r: r.returncode == 0 and r.stdout.count("(healthy)") >= 2,
    ),
    Check(
        "db-extensions",
        "PostGIS + pgvector available",
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            "housing",
            "-d",
            "housing",
            "-Atc",
            "select postgis_full_version(); "
            "select extversion from pg_extension where extname='vector'",
        ],
    ),
    Check("secret-scan", "secret scan (gitleaks, full history)", ["make", "secret-scan"]),
    Check(
        "ci",
        "CI green for HEAD",
        [
            "gh",
            "run",
            "list",
            "--branch",
            "claude/sprint-p0",
            "--limit",
            "10",
            "--json",
            "databaseId,headSha,conclusion,status,url,workflowName",
        ],
        _ci_green_for_head,
    ),
]


def _quality_report_passed(result: subprocess.CompletedProcess[str]) -> bool:
    try:
        return result.returncode == 0 and json.loads(result.stdout)["passed"] is True
    except (json.JSONDecodeError, KeyError):
        return False


GATE_01_DATASETS = [
    "cm_secciones_censales",
    "cm_poblacion_edad_nacionalidad_sexo",
    "cm_hogares_tamano_censo_2021",
    "cm_viviendas_superficie",
    "cm_renta_disponible_municipal",
    "cm_alquiler_m2_municipios",
    "cm_alquiler_m2_codigo_postal_madrid",
    "cm_centros_educativos",
    "cm_centros_sanitarios",
    "cm_centros_atencion_social",
]
PSQL = ["docker", "compose", "exec", "-T", "db", "psql", "-U", "housing", "-d", "housing", "-Atc"]
LAST_VALID_SQL = (
    "select count(*) from dataset_version where is_last_valid and quality_status = 'PASSED'"
)
GATE_01 = [
    Check(
        "registry",
        "Source/dataset/metric/pipeline registry valid",
        ["uv", "run", "hi-ingest", "catalog", "validate"],
    ),
    Check(
        "pipeline-unit",
        "parsers deterministic, QA, null semantics, privacy filters (fixtures)",
        ["uv", "run", "pytest", "tests/unit/pipelines", "tests/unit/harvester", "-q"],
    ),
    Check(
        "pipeline-integration",
        "Bronze->Silver->PostGIS, skip on same checksum, last-valid survives broken ingestion",
        [
            "uv",
            "run",
            "pytest",
            "-m",
            "db",
            "tests/integration/geo",
            "tests/integration/test_stat_pipelines.py",
            "tests/integration/test_places_pipeline.py",
            "-q",
        ],
    ),
    Check(
        "real-run-quality",
        f"latest full-region QA report PASS for {len(GATE_01_DATASETS)} datasets",
        ["uv", "run", "python", "scripts/check_quality_reports.py", *GATE_01_DATASETS],
    ),
    Check(
        "last-valid-versions",
        "every dataset has a last-valid version with QA PASSED",
        [*PSQL, LAST_VALID_SQL],
        lambda r: r.returncode == 0 and int(r.stdout.strip() or 0) >= len(GATE_01_DATASETS),
    ),
    Check(
        "idempotent-rerun",
        "re-fetch + rerun of every pipeline with same content is SKIPPED",
        ["uv", "run", "hi-ingest", "run-all", "--no-evidence"],
        lambda r: r.returncode == 0 and r.stdout.count("SKIPPED") >= len(GATE_01_DATASETS),
    ),
    GATE_00[-1],  # CI green for HEAD
]

FEATURE_COVERAGE_SQL = """
select count(distinct feature_id)
    || '|' || count(*) filter (where (value is null) = (null_reason is null))
    || '|' || count(*) filter (where not (inputs ? 'dataset_versions'))
    || '|' || min(n)
  from feature_value v
  join (select feature_id as fid, count(*) as n from feature_value group by 1) c
    on c.fid = v.feature_id
"""
GATE_03 = [
    Check(
        "dictionary",
        "Feature Dictionary entries valid; no protected characteristics; methods implemented",
        ["uv", "run", "pytest", "tests/data/test_catalog.py", "-q"],
    ),
    Check(
        "methods",
        "deterministic methods, null propagation, monotonicity (property tests)",
        ["uv", "run", "pytest", "tests/unit/features", "-q"],
    ),
    Check(
        "invariants",
        "computed values satisfy the invariants declared in each dictionary entry",
        [
            "uv",
            "run",
            "pytest",
            "-m",
            "db",
            "tests/integration/test_features.py",
            "tests/integration/test_api_features.py",
            "-q",
        ],
    ),
    Check(
        "coverage",
        "12 features x 179 municipios, null contract and lineage in the dev DB",
        [*PSQL, FEATURE_COVERAGE_SQL],
        lambda r: r.returncode == 0 and r.stdout.strip() == "12|0|0|179",
    ),
    GATE_00[-1],
]

GATES: dict[str, list[Check]] = {"00": GATE_00, "01": GATE_01, "03": GATE_03}
SCOPES = {
    "00": "Repository / foundation.",
    "01": f"Source / Bronze ingestion — {len(GATE_01_DATASETS)} datasets "
    "(geography, 6 statistical tables, 3 facility registers).",
    "03": "Metrics / Feature Store — started: 12 municipal features (target 75–125 for Sprint P1).",
}


def environment() -> dict[str, str]:
    def out(cmd: list[str]) -> str:
        r = _run(cmd)
        return (r.stdout or r.stderr).strip().splitlines()[0] if (r.stdout or r.stderr) else ""

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "git_head": _head(),
        "git_branch": out(["git", "branch", "--show-current"]),
        "platform": platform.platform(),
        "python": out(["uv", "run", "python", "--version"]),
        "uv": out(["uv", "--version"]),
        "node": out(["node", "--version"]),
        "npm": out(["npm", "--version"]),
        "docker": out(["docker", "--version"]),
        "compose": out(["docker", "compose", "version"]),
        "gitleaks": out(["gitleaks", "version"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", default="00", choices=sorted(GATES))
    parser.add_argument("--date", default=date.today().isoformat())
    args = parser.parse_args()

    out_dir = REPO / "evidence" / f"gate-{args.gate}" / args.date
    out_dir.mkdir(parents=True, exist_ok=True)
    env = environment()
    (out_dir / "environment.json").write_text(json.dumps(env, indent=2) + "\n")

    rows: list[tuple[str, str, bool]] = []
    for check in GATES[args.gate]:
        result = _run(check.command)
        passed = check.validate(result)
        header = f"$ {' '.join(check.command)}\n# exit {result.returncode}\n\n"
        log = header + f"{result.stdout}\n{result.stderr}"
        (out_dir / f"{check.check_id}.txt").write_text(log)
        rows.append((check.check_id, check.criterion, passed))
        print(f"{'PASS' if passed else 'FAIL'}  {check.criterion}")

    verdict = "PASS" if all(p for _, _, p in rows) else "FAIL"
    table = "\n".join(f"| {cid} | {crit} | {'PASS' if p else 'FAIL'} |" for cid, crit, p in rows)
    summary = (
        f"# Gate {args.gate} — {verdict}\n\n"
        f"- Fecha: {args.date}\n- Commit: `{env['git_head']}` ({env['git_branch']})\n"
        f"- Generado: {env['generated_at']} por `scripts/evidence.py`\n\n"
        f"- Alcance: {SCOPES[args.gate]}\n\n"
        f"| Check | Criterio | Resultado |\n|---|---|---|\n{table}\n\n"
        "Cada fila tiene su salida completa en `<check>.txt`. Entorno en `environment.json`.\n"
    )
    (out_dir / "summary.md").write_text(summary)
    print(f"Gate {args.gate}: {verdict} -> {out_dir.relative_to(REPO)}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
