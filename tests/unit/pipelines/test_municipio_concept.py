"""Tables that name their municipios by hand (cm_municipio_concept, D-235): the known criminal
offences of the Ministerio del Interior, on the rows of the real table (no database)."""

from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError

from hi_contracts.catalog.pipeline import CmMunicipioConceptPipeline
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.pipelines.common import read_csv
from hi_ingestion.pipelines.stat_tables.normalize import clean_name, normalize
from hi_ingestion.pipelines.stat_tables.run import metric_counts, run_metric_quality

GOLDEN = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "golden"
DATASET = "cm_infracciones_penales_municipios"
# Every row the pipeline reads (the totals, 2016-2025) plus the rows with a misspelt name.
NAMES = GOLDEN / "municipio_names_sample" / f"{DATASET}.csv"
MUNICIPIOS = 37


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return load_catalog()


@pytest.fixture(scope="module")
def spec(catalog: Catalog) -> CmMunicipioConceptPipeline:
    pipeline = catalog.pipelines[DATASET]
    assert isinstance(pipeline, CmMunicipioConceptPipeline)
    return pipeline


@pytest.fixture(scope="module")
def source(spec: CmMunicipioConceptPipeline) -> pd.DataFrame:
    return read_csv(NAMES, spec.csv)


def _known(spec: CmMunicipioConceptPipeline) -> set[str]:
    return set(spec.municipios.values())


def test_the_37_municipios_match_and_none_is_lost(
    spec: CmMunicipioConceptPipeline, source: pd.DataFrame, catalog: Catalog
) -> None:
    obs = normalize(source, spec)
    assert obs.quarantine.empty
    assert set(obs.frame["territory_code"]) == _known(spec)
    assert len(_known(spec)) == MUNICIPIOS
    assert set(obs.frame["admin_unit_id"]) == {f"ES.28.MUN.{c}" for c in _known(spec)}
    report = run_metric_quality(obs, spec, catalog.metrics, _known(spec))
    assert report.passed, [c for c in report.checks if not c.passed]


def test_every_spelling_the_source_writes_is_mapped(
    spec: CmMunicipioConceptPipeline, source: pd.DataFrame
) -> None:
    """The concept repeats the name, with errata («San Fernado de Henares», «Mejorada»,
    «Colmenar  Viejo» with two spaces): each one, and each name of the municipio column, has
    its INE code."""
    mapped = {clean_name(name): code for name, code in spec.municipios.items()}
    column = {clean_name(name) for name in source[spec.municipio_column]}
    in_concept = {clean_name(c.rsplit(" en ", 1)[1]) for c in source[spec.concept_column]}
    assert "San Fernado de Henares" in in_concept
    assert any("  " in concept for concept in source[spec.concept_column])
    assert column | in_concept <= set(mapped)
    assert mapped["San Fernado de Henares"] == mapped["San Fernando de Henares"] == "28130"
    assert mapped["Mejorada"] == mapped["Mejorada del Campo"] == "28084"
    assert mapped["Colmenar Viejo"] == "28045"
    assert mapped["Rozas de Madrid"] == "28127"  # Las Rozas de Madrid, not Rozas de Puerto Real


def test_only_the_total_of_the_definitive_years_is_read(
    spec: CmMunicipioConceptPipeline, source: pd.DataFrame
) -> None:
    obs = normalize(source, spec)
    frame = obs.frame
    assert set(frame["metric_id"]) == {"infracciones_penales_conocidas"}
    assert max(frame["period_start"]) == date(2024, 1, 1)  # 2025 is provisional
    assert obs.excluded_status == MUNICIPIOS
    assert obs.out_of_window == len(source) - len(frame) - MUNICIPIOS  # rows of other concepts
    assert metric_counts(obs)["excluded_status"] == MUNICIPIOS
    madrid = frame[
        (frame["territory_code"] == "28079") & (frame["period_start"] == date(2024, 1, 1))
    ]
    assert madrid["value"].tolist() == [237020.0]
    latest = frame[frame["period_start"] == date(2024, 1, 1)]
    assert set(latest["territory_code"]) == _known(spec)  # all 37 in the year that is shown


def test_a_name_that_is_not_mapped_fails_the_run_never_dropped(
    spec: CmMunicipioConceptPipeline, source: pd.DataFrame, catalog: Catalog
) -> None:
    renamed = source.copy()
    renamed.loc[renamed[spec.municipio_column] == "Getafe", spec.municipio_column] = "Xetafe"
    obs = normalize(renamed, spec)
    assert set(obs.quarantine["reason"]) == {
        "municipio 'Xetafe' is not in the pipeline's `municipios`"
    }
    report = run_metric_quality(obs, spec, catalog.metrics, _known(spec))
    failed = {c.name for c in report.checks if c.critical and not c.passed}
    assert failed == {"quarantine_ratio", "expected_municipios"}


def test_names_are_compared_with_their_whitespace_collapsed(
    spec: CmMunicipioConceptPipeline, source: pd.DataFrame
) -> None:
    spaced = source.copy()
    is_colmenar = spaced[spec.municipio_column] == "Colmenar Viejo"
    spaced.loc[is_colmenar, spec.municipio_column] = "Colmenar  Viejo"
    obs = normalize(spaced, spec)
    assert obs.quarantine.empty
    assert "28045" in set(obs.frame["territory_code"])


def test_the_declared_names_must_cover_the_expected_municipios(
    spec: CmMunicipioConceptPipeline,
) -> None:
    fewer = {name: code for name, code in spec.municipios.items() if code != "28065"}
    with pytest.raises(ValidationError, match="expected_municipios"):
        CmMunicipioConceptPipeline.model_validate(spec.model_dump() | {"municipios": fewer})
    with pytest.raises(ValidationError, match="status_column"):
        CmMunicipioConceptPipeline.model_validate(spec.model_dump() | {"status_column": None})
