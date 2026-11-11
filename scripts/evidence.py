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
CURRENT_BRANCH = subprocess.run(
    ["git", "branch", "--show-current"], cwd=REPO, capture_output=True, text=True, check=False
).stdout.strip()
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
            CURRENT_BRANCH,
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


def _rerun_ok(result: subprocess.CompletedProcess[str]) -> bool:
    statuses = [
        line.split(": ")[1].split()[0] for line in result.stdout.splitlines() if ": " in line
    ]
    return (
        result.returncode == 0
        and len(statuses) >= len(GATE_01_DATASETS)
        and all(s in {"SKIPPED", "SUCCESS"} for s in statuses)
    )


GEOGRAPHY_DATASETS = ["cm_secciones_censales"]
STAT_TABLE_DATASETS = [
    "cm_poblacion_edad_nacionalidad_sexo",
    "cm_hogares_tamano_censo_2021",
    "cm_viviendas_superficie",
    "cm_renta_disponible_municipal",
    "cm_alquiler_m2_municipios",
    "cm_alquiler_m2_codigo_postal_madrid",
    "cm_farmacias_municipios",
    "cm_unidades_escolares",
    "cm_nacidos_vivos_municipios",
    "cm_viviendas_tenencia_censo_2021",
]
FACILITY_DATASETS = [
    "cm_centros_educativos",
    "cm_centros_sanitarios",
    "cm_centros_atencion_social",
    "cm_oficinas_farmacia",
]
# Complementary (not CM): statistics the CM portal does not publish at the level needed (D-209).
COMPLEMENTARY_DATASETS = ["ayto_padron_municipal", "ayto_panel_indicadores_distritos_barrios"]
TRANSPORT_DATASETS = [
    "crtm_gtfs_metro",
    "crtm_gtfs_metro_ligero",
    "crtm_gtfs_cercanias",
    "crtm_gtfs_emt",
    "crtm_gtfs_autobuses_urbanos",
    "crtm_gtfs_interurbanos",
]
GATE_01_DATASETS = [
    *GEOGRAPHY_DATASETS,
    *STAT_TABLE_DATASETS,
    *FACILITY_DATASETS,
    *TRANSPORT_DATASETS,
    *COMPLEMENTARY_DATASETS,
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
            "tests/integration/test_gtfs_pipeline.py",
            "tests/integration/test_padron_pipeline.py",
            "tests/integration/test_district_panel_pipeline.py",
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
        "re-fetch every source: unchanged -> SKIPPED, changed -> new version, none FAILED",
        ["uv", "run", "hi-ingest", "run-all", "--no-evidence"],
        _rerun_ok,
    ),
    GATE_00[-1],  # CI green for HEAD
]

TRANSPORT_GEOMETRY_SQL = """
select count(*) filter (where not ST_IsValid(geom_4326) or not ST_IsValid(geom_25830))
    || '|' || count(*) filter (
           where not ST_Within(geom_4326, ST_MakeEnvelope(-4.58, 39.88, -3.05, 41.17, 4326)))
    || '|' || count(*) filter (
           where ST_Distance(ST_Transform(geom_4326, 25830), geom_25830) > 1)
    || '|' || count(*) filter (
           where seccion_admin_unit_id is null and exists (
               select 1 from geo_admin_unit u
                where u.level = 'seccion_censal' and ST_Contains(u.geom_25830, p.geom_25830)))
  from place_master p where category = 'transport'
"""
SECTION_ASSIGNMENT_SQL = """
select subcategory || '|' || count(seccion_admin_unit_id) || '|' || count(*)
  from place_master where category = 'transport' group by subcategory order by subcategory
"""
COLOCATED_SQL = """
select ds || '|' || count(*) from (
    select official_dataset_id as ds, ST_AsText(geom_4326) as wkt
      from place_master where category = 'transport'
     group by 1, 2 having count(*) > 1) d
 group by ds order by ds
"""
MANUAL_SAMPLE_SQL = """
select subcategory || '|' || canonical_name || '|' || coalesce(municipio_ine, '-')
    || '|' || round(ST_Y(geom_4326)::numeric, 5) || ',' || round(ST_X(geom_4326)::numeric, 5)
    || '|' || coalesce(attributes->>'headway_peak_min', '-')
    || '|' || coalesce(attributes->>'departures_day', '-')
  from place_master where category = 'transport'
 order by md5(canonical_place_id::text) limit 20
"""
MIN_SECTION_ASSIGNMENT = 0.95


def _assignment_ok(result: subprocess.CompletedProcess[str]) -> bool:
    rows = [line.split("|") for line in result.stdout.split()]
    assigned = sum(int(r[1]) for r in rows)
    total = sum(int(r[2]) for r in rows)
    return result.returncode == 0 and total > 0 and assigned / total >= MIN_SECTION_ASSIGNMENT


GATE_02 = [
    Check(
        "geo-unit",
        "CRS, bounds, H3, coordinate parsing and GTFS stop/station rules (unit + fixtures)",
        [
            "uv",
            "run",
            "pytest",
            "tests/unit/geo",
            "tests/unit/pipelines/test_places.py",
            "tests/unit/pipelines/test_gtfs.py",
            "-q",
        ],
    ),
    Check(
        "geo-integration",
        "places and stops assigned to the section that contains them; no invalid geometry",
        [
            "uv",
            "run",
            "pytest",
            "-m",
            "db",
            "tests/integration/geo",
            "tests/integration/test_places_pipeline.py",
            "tests/integration/test_gtfs_pipeline.py",
            "-q",
        ],
    ),
    Check(
        "transport-golden",
        "golden stations: near the public landmark, right municipio and section, plausible service",
        ["uv", "run", "python", "scripts/check_transport_golden.py"],
    ),
    Check(
        "transport-geometry",
        "transport stops: 0 invalid, 0 outside region bounds, 0 CRS mismatch >1 m, "
        "0 missed sections",
        [*PSQL, TRANSPORT_GEOMETRY_SQL],
        lambda r: r.returncode == 0 and r.stdout.strip() == "0|0|0|0",
    ),
    Check(
        "section-assignment",
        f"at least {MIN_SECTION_ASSIGNMENT:.0%} of transport stops inside a census section "
        "(the rest lie outside the region)",
        [*PSQL, SECTION_ASSIGNMENT_SQL],
        _assignment_ok,
    ),
    Check(
        "colocated-stops",
        "duplicate control: official ids unique by constraint; co-located stops per feed reported",
        [*PSQL, COLOCATED_SQL],
    ),
    Check(
        "manual-sample",
        "20 stops sampled deterministically (md5 of id) for manual review",
        [*PSQL, MANUAL_SAMPLE_SQL],
        lambda r: r.returncode == 0 and len(r.stdout.strip().splitlines()) == 20,
    ),
    GATE_00[-1],
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
# Features with rows for the 21 districts of Madrid (D-200/D-209): 7 expected today.
DISTRICT_COVERAGE_SQL = """
select count(*) from (
  select feature_id from feature_value where territory_level = 'distrito'
   group by 1 having count(*) = 21
) d
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
        "12 features with at least the 179 municipios, null contract and lineage in the dev DB",
        [*PSQL, FEATURE_COVERAGE_SQL],
        lambda r: r.returncode == 0 and r.stdout.strip() == "12|0|0|179",
    ),
    Check(
        "district-coverage",
        "7 features with the 21 districts of Madrid (D-200, D-209)",
        [*PSQL, DISTRICT_COVERAGE_SQL],
        lambda r: r.returncode == 0 and r.stdout.strip() == "7",
    ),
    GATE_00[-1],
]

GATES: dict[str, list[Check]] = {"00": GATE_00, "01": GATE_01, "02": GATE_02, "03": GATE_03}
SCOPES = {
    "00": "Repository / foundation.",
    "01": f"Source / Bronze ingestion — {len(GATE_01_DATASETS) - len(COMPLEMENTARY_DATASETS)} "
    f"datasets of the Comunidad de Madrid open data portal (geography, "
    f"{len(STAT_TABLE_DATASETS)} statistical tables, {len(FACILITY_DATASETS)} facility "
    f"registers, {len(TRANSPORT_DATASETS)} CRTM GTFS feeds) and {len(COMPLEMENTARY_DATASETS)} "
    "complementary datasets of the Ayuntamiento de Madrid (padrón and households by district).",
    "02": "Geospatial QA — transport stops and stations from the CRTM GTFS feeds "
    "(the 2026-10-20 geography QA lives in gate-01/2026-10-20).",
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
