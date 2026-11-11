"""District panel pipeline on its fixture against the migrated test DB (needs the admin fixture)."""

from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import MadridDistrictPanelPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.district_panel.run import run_panel_pipeline
from hi_ingestion.pipelines.fetch import local_file
from tests.integration.conftest import GOLDEN, MADRID_SAMPLE_DISTRICTS

pytestmark = pytest.mark.db
DATASET = "ayto_panel_indicadores_distritos_barrios"
FIXTURE = GOLDEN / "panel_sample" / f"{DATASET}.csv"


def _run(engine: Engine, tmp: Path, path: Path = FIXTURE) -> RunSummary:
    catalog = load_catalog()
    spec = catalog.pipelines[DATASET]
    assert isinstance(spec, MadridDistrictPanelPipeline)
    sample = spec.model_copy(update={"expected_districts": MADRID_SAMPLE_DISTRICTS})
    return run_panel_pipeline(
        engine,
        catalog,
        sample,
        local_file(DATASET, "primary", path),
        evidence_root=tmp / "ev",
        data_dir=tmp / "data",
    )


def _districts(engine: Engine) -> int:
    with engine.connect() as conn:
        return int(
            conn.execute(
                text(
                    "SELECT count(DISTINCT territory_code) FROM metric_observation "
                    "WHERE metric_id = 'hogares_padron' AND territory_level = 'distrito'"
                )
            ).scalar_one()
        )


def test_panel_publishes_and_reruns_are_skipped(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    assert _run(migrated_engine, tmp_path).status in {"SUCCESS", "SKIPPED"}
    assert _run(migrated_engine, tmp_path).status == "SKIPPED"
    assert _districts(migrated_engine) == MADRID_SAMPLE_DISTRICTS


def test_a_panel_missing_districts_keeps_the_last_valid_observations(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    assert _run(migrated_engine, tmp_path).status in {"SUCCESS", "SKIPPED"}
    lines = FIXTURE.read_text(encoding="utf-8-sig").splitlines()
    only_centro = [line for line in lines[1:] if ";Ciudad de Madrid;1;" in line]
    partial = tmp_path / "only_centro.csv"
    partial.write_text("\n".join([lines[0], *only_centro]) + "\n", encoding="utf-8-sig")
    summary = _run(migrated_engine, tmp_path, partial)
    assert summary.status == "FAILED"
    assert "district_coverage" in {c["name"] for c in summary.quality["checks"] if not c["passed"]}
    assert _districts(migrated_engine) == MADRID_SAMPLE_DISTRICTS
