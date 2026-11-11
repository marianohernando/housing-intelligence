"""Padrón pipeline on its fixture against the migrated test DB (needs the admin fixture)."""

from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import MadridPadronPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.padron.run import run_padron_pipeline
from tests.integration.conftest import GOLDEN, MADRID_SAMPLE_DISTRICTS

pytestmark = pytest.mark.db
DATASET = "ayto_padron_municipal"
FIXTURE = GOLDEN / "padron_sample" / f"{DATASET}.csv"


def _run(engine: Engine, tmp: Path, expected_districts: int, path: Path = FIXTURE) -> RunSummary:
    catalog = load_catalog()
    spec = catalog.pipelines[DATASET]
    assert isinstance(spec, MadridPadronPipeline)
    sample = spec.model_copy(update={"expected_districts": expected_districts})
    source = local_file(DATASET, "primary", path)
    return run_padron_pipeline(
        engine, catalog, sample, source, evidence_root=tmp / "ev", data_dir=tmp / "data"
    )


def test_padron_publishes_district_bands_and_reruns_are_skipped(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    first = _run(migrated_engine, tmp_path, MADRID_SAMPLE_DISTRICTS)
    assert first.status in {"SUCCESS", "SKIPPED"}, first.quality
    assert _run(migrated_engine, tmp_path, MADRID_SAMPLE_DISTRICTS).status == "SKIPPED"
    with migrated_engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT territory_code, admin_unit_id, count(*) AS n, "
                "sum(value) FILTER (WHERE dims->>'edad' <> 'total') AS bands, "
                "sum(value) FILTER (WHERE dims->>'edad' = 'total') AS total "
                "FROM metric_observation WHERE metric_id = 'poblacion_padron' "
                "AND territory_level = 'distrito' GROUP BY 1, 2 ORDER BY 1"
            )
        ).all()
    assert [r.territory_code for r in rows] == ["2807901", "2807905", "2807906"]
    for row in rows:
        assert row.admin_unit_id == f"ES.28.DIS.{row.territory_code}"
        assert row.n == 22  # 21 CM age bands + total
        assert row.bands == row.total > 0


def test_a_file_missing_districts_keeps_the_last_valid_observations(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    assert _run(migrated_engine, tmp_path, MADRID_SAMPLE_DISTRICTS).status in {
        "SUCCESS",
        "SKIPPED",
    }
    lines = FIXTURE.read_text(encoding="utf-8-sig").splitlines()
    partial = tmp_path / "only_centro.csv"
    partial.write_text(
        "\n".join([lines[0], *(line for line in lines[1:] if line.startswith("1;"))]) + "\n",
        encoding="utf-8-sig",
    )
    summary = _run(migrated_engine, tmp_path, MADRID_SAMPLE_DISTRICTS, partial)
    assert summary.status == "FAILED"
    failed = {c["name"] for c in summary.quality["checks"] if not c["passed"]}
    assert "district_coverage" in failed
    with migrated_engine.connect() as conn:
        districts = conn.execute(
            text(
                "SELECT count(DISTINCT territory_code) FROM metric_observation "
                "WHERE metric_id = 'poblacion_padron'"
            )
        ).scalar()
    assert districts == MADRID_SAMPLE_DISTRICTS
