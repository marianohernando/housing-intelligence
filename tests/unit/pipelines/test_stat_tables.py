"""Stat-table normalisation and QA on real fixtures (no database)."""

from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st

from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_contracts.catalog.pipeline import CmPostcodeConceptPipeline, CmStatTablePipeline
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.pipelines.common import read_csv
from hi_ingestion.pipelines.stat_tables.normalize import (
    RowError,
    normalize,
    parse_period,
    parse_value,
    resolve_territory,
)
from hi_ingestion.pipelines.stat_tables.quality import run_quality

FIXTURES = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "golden" / "stat_sample"
KNOWN = {"28079", "28001", "28002"}
MISSING = ["-", ".", "..", "...", ""]


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return load_catalog()


def _obs(catalog: Catalog, dataset_id: str):
    spec = catalog.pipelines[dataset_id]
    assert isinstance(spec, CmStatTablePipeline | CmPostcodeConceptPipeline)
    return spec, normalize(read_csv(FIXTURES / f"{dataset_id}.csv", spec.csv), spec)


def test_missing_markers_are_unknown_never_zero() -> None:
    assert parse_value("-", MISSING, ".") == (None, NullReason.SOURCE_MISSING.value)
    assert parse_value("abc", MISSING, ".") == (None, NullReason.PARSE_ERROR.value)
    assert parse_value("0", MISSING, ".") == (0.0, None)
    assert parse_value("12,7", MISSING, ",") == (12.7, None)


@given(st.integers(min_value=1900, max_value=2100))
def test_years_become_full_calendar_periods(year: int) -> None:
    assert parse_period(str(year)) == (date(year, 1, 1), date(year, 12, 31))


def test_territory_resolution() -> None:
    assert resolve_territory(TerritoryLevel.MUNICIPIO, "0796", "Madrid") == (
        "28079",
        "ES.28.MUN.28079",
    )
    assert resolve_territory(TerritoryLevel.CCAA, "", "Comunidad de Madrid") == ("28", None)
    with pytest.raises(RowError):
        resolve_territory(TerritoryLevel.MUNICIPIO, "79", "x")
    with pytest.raises(RowError):
        resolve_territory(TerritoryLevel.CODIGO_POSTAL, "08001", "")


def test_population_fixture_is_clean_and_additive(catalog: Catalog) -> None:
    spec, obs = _obs(catalog, "cm_poblacion_edad_nacionalidad_sexo")
    assert len(obs.quarantine) == 0
    assert set(obs.frame["territory_level"]) == {"ccaa", "municipio", "zona_estadistica"}
    report = run_quality(obs, {m: catalog.metrics[m] for m in spec.metric_ids()}, KNOWN)
    checks = {c.name: c for c in report.checks}
    assert report.passed
    assert checks["totals_are_additive"].details["groups_checked"] > 0
    assert checks["totals_are_additive"].passed


def test_income_split_into_three_metrics(catalog: Catalog) -> None:
    _, obs = _obs(catalog, "cm_renta_disponible_municipal")
    assert set(obs.frame["metric_id"]) == {
        "renta_disponible_bruta_total",
        "renta_disponible_bruta_per_capita",
        "renta_disponible_bruta_indice_media",
    }


def test_postcode_is_extracted_from_concept(catalog: Catalog) -> None:
    _, obs = _obs(catalog, "cm_alquiler_m2_codigo_postal_madrid")
    assert set(obs.frame["territory_level"]) == {"codigo_postal"}
    assert set(obs.frame["territory_code"]) <= {"28013", "28026", "28046"}
    assert bool(obs.frame["territory_name"].notna().all())


def test_unknown_municipio_blocks_publication(catalog: Catalog) -> None:
    spec, obs = _obs(catalog, "cm_hogares_tamano_censo_2021")
    report = run_quality(obs, {m: catalog.metrics[m] for m in spec.metric_ids()}, {"28079"})
    failed = {c.name for c in report.checks if c.critical and not c.passed}
    assert "municipios_resolve_to_geography" in failed
    assert not report.passed


def test_broken_totals_are_detected(catalog: Catalog) -> None:
    spec, obs = _obs(catalog, "cm_hogares_tamano_censo_2021")
    frame = obs.frame.copy()
    is_member = frame["dims_key"] != "tamano=total"
    frame.loc[is_member, "value"] = frame.loc[is_member, "value"] * 2
    broken = type(obs)(frame, obs.quarantine, obs.source_rows)
    report = run_quality(broken, {m: catalog.metrics[m] for m in spec.metric_ids()}, KNOWN)
    additivity = next(c for c in report.checks if c.name == "totals_are_additive")
    assert not additivity.passed
    assert additivity.details["failures"] > 0


def test_unknown_territory_type_is_quarantined(catalog: Catalog) -> None:
    spec, _ = _obs(catalog, "cm_hogares_tamano_censo_2021")
    assert isinstance(spec, CmStatTablePipeline)
    frame = read_csv(FIXTURES / "cm_hogares_tamano_censo_2021.csv", spec.csv)
    frame.loc[frame.index[0], spec.territory_type_column] = "Planetas"
    obs = normalize(pd.DataFrame(frame), spec)
    assert len(obs.quarantine) == 1
    assert "unknown territory type" in obs.quarantine.iloc[0]["reason"]
