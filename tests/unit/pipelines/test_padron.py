"""Padrón (Ayuntamiento de Madrid) -> population by district in the CM's 5-year age bands."""

from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

from hi_contracts.catalog.pipeline import CmStatTablePipeline, MadridPadronPipeline
from hi_domain.population import TOTAL_AGE, five_year_age_band, five_year_age_bands
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.pipelines.common import read_csv
from hi_ingestion.pipelines.padron.normalize import normalize, parse_age
from hi_ingestion.pipelines.padron.quality import run_padron_quality
from hi_ingestion.pipelines.stat_tables.normalize import RowError
from hi_ingestion.pipelines.stat_tables.normalize import normalize as normalize_stat

GOLDEN = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "golden"
FIXTURE = GOLDEN / "padron_sample" / "ayto_padron_municipal.csv"
DATASET = "ayto_padron_municipal"
SAMPLE_DISTRICTS = {"2807901", "2807905", "2807906"}


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return load_catalog()


@pytest.fixture(scope="module")
def spec(catalog: Catalog) -> MadridPadronPipeline:
    pipeline = catalog.pipelines[DATASET]
    assert isinstance(pipeline, MadridPadronPipeline)
    return pipeline


@pytest.fixture(scope="module")
def source(spec: MadridPadronPipeline) -> pd.DataFrame:
    return read_csv(FIXTURE, spec.csv)


@given(st.integers(min_value=0, max_value=130))
def test_every_age_falls_in_exactly_one_band(age: int) -> None:
    band = five_year_age_band(age)
    assert band in five_year_age_bands()
    assert five_year_age_bands().count(band) == 1


def test_band_edges() -> None:
    assert five_year_age_band(0) == "de_0_4_anos"
    assert five_year_age_band(4) == "de_0_4_anos"
    assert five_year_age_band(5) == "de_5_9_anos"
    assert five_year_age_band(99) == "de_95_99_anos"
    assert five_year_age_band(100) == "de_100_y_mas_anos"
    assert five_year_age_band(117) == "de_100_y_mas_anos"
    with pytest.raises(ValueError, match="negative"):
        five_year_age_band(-1)


def test_bands_are_the_cm_census_bands(catalog: Catalog) -> None:
    """Same keys as poblacion_censada, so feature dims filters work on both metrics."""
    cm = catalog.pipelines["cm_poblacion_edad_nacionalidad_sexo"]
    assert isinstance(cm, CmStatTablePipeline)
    stat = normalize_stat(read_csv(GOLDEN / "stat_sample" / f"{cm.dataset_id}.csv", cm.csv), cm)
    cm_bands = {dims["edad"] for dims in stat.frame["dims"]} - {TOTAL_AGE}
    assert set(five_year_age_bands()) == cm_bands


def test_open_age_and_padding_parse() -> None:
    assert parse_age("100 o +") == 100
    assert parse_age("71") == 71
    for bad in ("", "abc", "-3"):
        with pytest.raises(RowError):
            parse_age(bad)


def test_districts_get_bands_and_total(spec: MadridPadronPipeline, source: pd.DataFrame) -> None:
    obs = normalize(source, spec)
    frame = obs.frame
    assert obs.quarantine.empty
    assert set(frame["territory_code"]) == SAMPLE_DISTRICTS
    assert set(frame["territory_level"]) == {"distrito"}
    assert set(frame["admin_unit_id"]) == {f"ES.28.DIS.{code}" for code in SAMPLE_DISTRICTS}
    assert set(frame["period_start"]) == {date(2026, 10, 1)}
    assert all(set(dims) == {"edad"} for dims in frame["dims"])  # never nationality or sex
    for _, rows in frame.groupby("territory_code"):
        total = rows.loc[[d["edad"] == TOTAL_AGE for d in rows["dims"]], "value"]
        bands = rows.loc[[d["edad"] != TOTAL_AGE for d in rows["dims"]], "value"]
        assert len(total) == 1
        assert bands.sum() == total.iloc[0]


def test_total_is_the_sum_of_every_count_column(
    spec: MadridPadronPipeline, source: pd.DataFrame
) -> None:
    """A row without a census section still belongs to its district."""
    expected: dict[str, int] = {}
    for record in source.to_dict("records"):
        code = f"28079{int(record['COD_DISTRITO']):02d}"
        expected[code] = expected.get(code, 0) + sum(int(record[c]) for c in spec.count_columns)
    frame = normalize(source, spec).frame
    totals = frame.loc[[d["edad"] == TOTAL_AGE for d in frame["dims"]]]
    assert dict(zip(totals["territory_code"], totals["value"], strict=True)) == expected


def _people(row: pd.Series, spec: MadridPadronPipeline) -> int:
    return sum(int(str(row[column])) for column in spec.count_columns)


def test_bad_rows_go_to_quarantine_never_to_zero(
    spec: MadridPadronPipeline, source: pd.DataFrame
) -> None:
    rows = source.loc[source["COD_DISTRITO"] == "6"].head(3).copy()
    good = _people(rows.iloc[2], spec)
    rows.loc[rows.index[0], spec.count_columns[0]] = ""
    rows.loc[rows.index[1], spec.age_column] = "n/a"
    obs = normalize(rows, spec)
    assert len(obs.quarantine) == 2
    assert obs.source_rows == 3
    totals = obs.frame.loc[[d["edad"] == TOTAL_AGE for d in obs.frame["dims"]], "value"].tolist()
    assert totals == [good]  # the broken rows add nothing, not even a 0


def test_an_age_without_rows_is_published_as_zero(
    spec: MadridPadronPipeline, source: pd.DataFrame
) -> None:
    """D-209: the padrón is exhaustive, so a band with nobody in it is 0, not missing."""
    row = source.loc[source["COD_DISTRITO"] == "1"].head(1)
    band = five_year_age_band(parse_age(str(row[spec.age_column].iloc[0])))
    frame = normalize(row, spec).frame
    assert len(frame) == len(five_year_age_bands()) + 1
    values = {d["edad"]: v for d, v in zip(frame["dims"], frame["value"], strict=True)}
    people = _people(row.iloc[0], spec)
    assert values[band] == values[TOTAL_AGE] == people
    assert all(v == 0.0 for b, v in values.items() if b not in {band, TOTAL_AGE})


def test_quality_requires_every_district(spec: MadridPadronPipeline, source: pd.DataFrame) -> None:
    obs = normalize(source, spec)
    metrics = load_catalog().metrics
    sample = spec.model_copy(update={"expected_districts": 3})
    ok = run_padron_quality(obs, sample, metrics, SAMPLE_DISTRICTS, census_total=None)
    assert ok.passed
    missing = run_padron_quality(obs, spec, metrics, SAMPLE_DISTRICTS, census_total=None)
    assert not missing.passed  # 3 of 21 districts
    unknown = run_padron_quality(obs, sample, metrics, {"2807901"}, census_total=None)
    assert not unknown.passed


def test_a_district_that_shrinks_suddenly_blocks_publication(
    spec: MadridPadronPipeline, source: pd.DataFrame
) -> None:
    """A truncated file would publish missing ages as 0; the last valid totals catch it."""
    obs = normalize(source, spec)
    sample = spec.model_copy(update={"expected_districts": 3})
    metrics = load_catalog().metrics
    totals = obs.frame.loc[[d["edad"] == TOTAL_AGE for d in obs.frame["dims"]]]
    previous = dict(zip(totals["territory_code"], totals["value"], strict=True))
    same = run_padron_quality(obs, sample, metrics, SAMPLE_DISTRICTS, None, previous)
    assert same.passed
    previous["2807905"] *= 2  # Chamartín had twice the people in the last valid version
    halved = run_padron_quality(obs, sample, metrics, SAMPLE_DISTRICTS, None, previous)
    check = next(c for c in halved.checks if c.name == "district_totals_stable")
    assert check.critical
    assert not check.passed
    assert check.details["changed"] == ["2807905"]


def test_census_comparison_is_reported_not_blocking(
    spec: MadridPadronPipeline, source: pd.DataFrame
) -> None:
    obs = normalize(source, spec)
    sample = spec.model_copy(update={"expected_districts": 3})
    metrics = load_catalog().metrics
    report = run_padron_quality(obs, sample, metrics, SAMPLE_DISTRICTS, census_total=1.0)
    check = next(c for c in report.checks if c.name == "total_vs_cm_census")
    assert not check.critical
    assert not check.passed
    assert report.passed
