"""Metric pipelines on fixtures against the migrated test DB (needs published admin fixture)."""

from pathlib import Path

import pytest
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import CmPostcodeConceptPipeline, CmStatTablePipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import RunSummary
from hi_ingestion.pipelines.fetch import local_file
from hi_ingestion.pipelines.stat_tables.run import run_metric_pipeline

pytestmark = pytest.mark.db
FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "golden" / "stat_sample"


def _run(engine: Engine, dataset_id: str, tmp: Path, path: Path | None = None) -> RunSummary:
    catalog = load_catalog()
    spec = catalog.pipelines[dataset_id]
    assert isinstance(spec, CmStatTablePipeline | CmPostcodeConceptPipeline)
    source = local_file(dataset_id, "primary", path or FIXTURES / f"{dataset_id}.csv")
    return run_metric_pipeline(
        engine, catalog, spec, source, evidence_root=tmp / "ev", data_dir=tmp / "data"
    )


@pytest.mark.parametrize(
    "dataset_id",
    [
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
    ],
)
def test_fixture_publishes_and_reruns_are_skipped(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path, dataset_id: str
) -> None:
    assert published.status == "SUCCESS"
    first = _run(migrated_engine, dataset_id, tmp_path)
    assert first.status in {"SUCCESS", "SKIPPED"}, first.quality
    assert _run(migrated_engine, dataset_id, tmp_path).status == "SKIPPED"


def test_null_semantics_survive_to_the_database(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    _run(migrated_engine, "cm_alquiler_m2_municipios", tmp_path)
    with migrated_engine.connect() as conn:
        bad = conn.execute(
            text(
                "SELECT count(*) FROM metric_observation "
                "WHERE (value IS NULL) = (null_reason IS NULL)"
            )
        ).scalar()
        zero_from_missing = conn.execute(
            text(
                "SELECT count(*) FROM metric_observation "
                "WHERE raw_value = '-' AND value IS NOT NULL"
            )
        ).scalar()
    assert bad == 0
    assert zero_from_missing == 0


def test_broken_file_keeps_last_valid_observations(
    published: RunSummary, migrated_engine: Engine, tmp_path: Path
) -> None:
    assert published.status == "SUCCESS"
    dataset_id = "cm_hogares_tamano_censo_2021"
    _run(migrated_engine, dataset_id, tmp_path)
    with migrated_engine.connect() as conn:
        before = conn.execute(
            text("SELECT count(*) FROM metric_observation WHERE metric_id = 'hogares_por_tamano'")
        ).scalar()
    broken = tmp_path / "broken.csv"
    content = (
        (FIXTURES / f"{dataset_id}.csv").read_text(encoding="latin-1").replace(";0796;", ";9999;")
    )
    broken.write_text(content, encoding="latin-1")
    result = _run(migrated_engine, dataset_id, tmp_path, broken)
    assert result.status == "FAILED"
    with migrated_engine.connect() as conn:
        after = conn.execute(
            text("SELECT count(*) FROM metric_observation WHERE metric_id = 'hogares_por_tamano'")
        ).scalar()
    assert after == before
