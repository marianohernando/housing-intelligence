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
def barrio_spec(catalog: Catalog) -> MadridPadronPipeline:
    pipeline = catalog.pipelines[DATASET]
    assert isinstance(pipeline, MadridPadronPipeline)
    return pipeline


@pytest.fixture(scope="module")
def spec(barrio_spec: MadridPadronPipeline) -> MadridPadronPipeline:
    """The districts alone, as before D-247 (the barrio totals are tested below)."""
    off = {"barrio_column": None, "barrio_metric_id": None, "expected_barrios": None}
    return barrio_spec.model_copy(update=off)


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


def _barrio_rows(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.loc[frame["territory_level"] == "barrio"]


def test_barrios_get_their_total_and_add_up_to_their_district(
    barrio_spec: MadridPadronPipeline, spec: MadridPadronPipeline, source: pd.DataFrame
) -> None:
    """D-247: each barrio's total, as its own metric; the district rows do not change."""
    frame = normalize(source, barrio_spec).frame
    barrios = _barrio_rows(frame)
    assert set(barrios["metric_id"]) == {"poblacion_padron_barrio"}
    assert all(d == {"edad": TOTAL_AGE} for d in barrios["dims"])
    assert set(barrios["admin_unit_id"]) == {f"ES.28.BAR.{c}" for c in barrios["territory_code"]}
    districts = frame.loc[frame["territory_level"] == "distrito"].reset_index(drop=True)
    assert districts.equals(normalize(source, spec).frame.reset_index(drop=True))
    added: dict[str, float] = {}
    for code, value in zip(barrios["territory_code"], barrios["value"], strict=True):
        added[code[:7]] = added.get(code[:7], 0.0) + value
    totals = districts.loc[[d["edad"] == TOTAL_AGE for d in districts["dims"]]]
    assert added == dict(zip(totals["territory_code"], totals["value"], strict=True))
    tetuan = {
        str(r["COD_DIST_BARRIO"]) for r in source.to_dict("records") if r["COD_DISTRITO"] == "6"
    }
    assert {c for c in barrios["territory_code"] if c.startswith("2807906")} == {
        f"2807906{int(b) % 100}" for b in tetuan
    }


def test_a_row_without_barrio_counts_in_its_district_only(
    barrio_spec: MadridPadronPipeline, source: pd.DataFrame
) -> None:
    rows = source.loc[source["COD_DISTRITO"] == "6"].head(2).copy()
    rows.loc[rows.index[0], "COD_DIST_BARRIO"] = ""
    obs = normalize(rows, barrio_spec)
    assert obs.quarantine.empty
    total = obs.frame.loc[
        [
            d["edad"] == TOTAL_AGE and lvl == "distrito"
            for d, lvl in zip(obs.frame["dims"], obs.frame["territory_level"], strict=True)
        ],
        "value",
    ]
    assert total.tolist() == [
        _people(rows.iloc[0], barrio_spec) + _people(rows.iloc[1], barrio_spec)
    ]
    assert _barrio_rows(obs.frame)["value"].tolist() == [_people(rows.iloc[1], barrio_spec)]


def test_a_barrio_of_another_district_is_listed_and_still_counts_in_its_district(
    barrio_spec: MadridPadronPipeline, spec: MadridPadronPipeline, source: pd.DataFrame
) -> None:
    """The district population never depends on the barrio column (review R-01 of #93)."""
    rows = source.loc[source["COD_DISTRITO"] == "6"].head(1).copy()
    rows.loc[rows.index[0], "COD_DIST_BARRIO"] = "501"
    obs = normalize(rows, barrio_spec)
    assert len(obs.quarantine) == 1
    assert "district only" in obs.quarantine["reason"].iloc[0]
    assert _barrio_rows(obs.frame).empty
    districts = obs.frame.loc[obs.frame["territory_level"] == "distrito"].reset_index(drop=True)
    assert districts.equals(normalize(rows, spec).frame.reset_index(drop=True))


def test_barrios_that_do_not_add_up_block_publication(
    barrio_spec: MadridPadronPipeline, source: pd.DataFrame
) -> None:
    """A broken barrio column would leave the barrios short: beyond 0.1 % it blocks."""
    metrics = load_catalog().metrics
    sample = barrio_spec.model_copy(update={"expected_districts": 3, "expected_barrios": None})
    obs = normalize(source, sample)
    known = set(_barrio_rows(obs.frame)["territory_code"])
    ok = run_padron_quality(obs, sample, metrics, SAMPLE_DISTRICTS, None, None, known)
    assert ok.passed
    broken = source.copy()
    broken.loc[broken["COD_DISTRITO"] == "1", "COD_DIST_BARRIO"] = ""
    report = run_padron_quality(
        normalize(broken, sample), sample, metrics, SAMPLE_DISTRICTS, None, None, known
    )
    check = next(c for c in report.checks if c.name == "barrios_add_up_to_districts")
    assert check.critical and not check.passed
    assert check.details["broken"] == ["2807901"]
