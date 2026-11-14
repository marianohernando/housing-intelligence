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
# Every row the pipeline reads (the totals and the cybercrime, 2016-2025) plus the rows with a
# misspelt name.
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


def test_only_the_total_and_the_cybercrime_of_the_definitive_years_are_read(
    spec: CmMunicipioConceptPipeline, source: pd.DataFrame
) -> None:
    """D-224 §3: the feature leaves the cybercrime out, so it is read beside the total, each
    row with its `tipologia`; the other rows by type are not read."""
    obs = normalize(source, spec)
    frame = obs.frame
    assert set(frame["metric_id"]) == {"infracciones_penales_conocidas"}
    assert set(frame["dims_key"]) == {"tipologia=total", "tipologia=cibercriminalidad"}
    assert max(frame["period_start"]) == date(2024, 1, 1)  # 2025 is provisional
    provisional = 2 * MUNICIPIOS  # the total and the cybercrime of each municipio
    assert obs.excluded_status == provisional
    assert obs.out_of_scope == len(source) - len(frame) - provisional  # rows of other concepts
    counts = metric_counts(obs)
    assert counts["excluded_status"] == provisional
    assert counts["out_of_scope"] == obs.out_of_scope
    assert "out_of_window" not in counts  # no period window here, as in the panel
    madrid = frame[
        (frame["territory_code"] == "28079") & (frame["period_start"] == date(2024, 1, 1))
    ]
    assert dict(zip(madrid["dims_key"], madrid["value"], strict=True)) == {
        "tipologia=total": 237020.0,
        "tipologia=cibercriminalidad": 36591.0,
    }
    latest = frame[frame["period_start"] == date(2024, 1, 1)]
    for kind in ("total", "cibercriminalidad"):  # all 37 in the year that is shown
        rows = latest[latest["dims_key"] == f"tipologia={kind}"]
        assert set(rows["territory_code"]) == _known(spec)


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
    assert failed == {
        "quarantine_ratio",
        "expected_municipios",
        "quarantine_empty",
        "latest_year_complete",
    }


def _getafe_total_2024(source: pd.DataFrame, spec: CmMunicipioConceptPipeline) -> pd.Series:
    rows = (
        (source[spec.municipio_column] == "Getafe")
        & (source[spec.period_column].astype(str) == "2024")
        & source[spec.concept_column].str.startswith("Total hechos conocidos")
    )
    assert int(rows.sum()) == 1
    return rows


@pytest.mark.parametrize("renamed", ["municipio", "concept"])
def test_a_single_total_row_lost_in_the_year_shown_fails_the_run(
    spec: CmMunicipioConceptPipeline, source: pd.DataFrame, catalog: Catalog, renamed: str
) -> None:
    """Review R-01: one row of 2024 renamed by the source (Getafe's total) is a figure lost
    in the year the zone view shows. Its name goes to quarantine, below the quarantine ratio
    that the other tables tolerate; its concept takes it out of the rows read. Both fail."""
    changed = source.copy()
    rows = _getafe_total_2024(changed, spec)
    if renamed == "municipio":
        changed.loc[rows, spec.municipio_column] = "Xetafe"
    else:
        changed.loc[rows, spec.concept_column] = "Totales de hechos conocidos en Getafe"
    obs = normalize(changed, spec)
    report = run_metric_quality(obs, spec, catalog.metrics, _known(spec))
    assert not report.passed
    failed = {c.name for c in report.checks if c.critical and not c.passed}
    lost = {"latest_year_complete"} | ({"quarantine_empty"} if renamed == "municipio" else set())
    assert failed == lost  # the ratio and the 37 municipios of other years let it through
    complete = next(c for c in report.checks if c.name == "latest_year_complete")
    assert complete.details["missing"] == {"total": ["28065"]}


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
    nested = spec.concepts | {"Total hechos": "otro"}  # it would also take the totals
    with pytest.raises(ValidationError, match="starts another"):
        CmMunicipioConceptPipeline.model_validate(spec.model_dump() | {"concepts": nested})
