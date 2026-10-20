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


TODAY = date.today().isoformat()
GATE_01_DATASET = "cm_secciones_censales"
GATE_01 = [
    Check(
        "registry",
        "Source/dataset registry valid",
        ["uv", "run", "hi-ingest", "catalog", "validate"],
    ),
    Check(
        "pipeline-unit",
        "parser deterministic + QA + H3 invariants (fixture)",
        ["uv", "run", "pytest", "tests/unit/pipelines", "tests/unit/harvester", "-q"],
    ),
    Check(
        "pipeline-integration",
        "Bronze->Silver->PostGIS, skip on same checksum, last-valid survives broken ingestion",
        ["uv", "run", "pytest", "-m", "db", "tests/integration/geo", "-q"],
    ),
    Check(
        "real-run-quality",
        f"{GATE_01_DATASET} full-region QA report PASS",
        ["cat", f"evidence/gate-01/{TODAY}/{GATE_01_DATASET}/quality_report.json"],
        _quality_report_passed,
    ),
    Check(
        "last-valid-version",
        "dataset_version marked last valid with QA PASSED",
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
            "select version_label, parser_version, quality_status, is_last_valid "
            "from dataset_version where dataset_id = 'cm_secciones_censales' and is_last_valid",
        ],
        lambda r: r.returncode == 0 and "|PASSED|t" in r.stdout,
    ),
    Check(
        "idempotent-rerun",
        "re-fetch + rerun with same content is SKIPPED",
        ["uv", "run", "hi-ingest", "run", GATE_01_DATASET, "--no-evidence"],
        lambda r: r.returncode == 0 and '"status": "SKIPPED"' in r.stdout,
    ),
    GATE_00[-1],  # CI green for HEAD
]

GATES: dict[str, list[Check]] = {"00": GATE_00, "01": GATE_01}
SCOPES = {
    "00": "Repository / foundation.",
    "01": f"Source / Bronze ingestion — scope: {GATE_01_DATASET} (1 of 17 P0 datasets). "
    "Remaining P0 datasets are registered and licensed but not yet ingested.",
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
