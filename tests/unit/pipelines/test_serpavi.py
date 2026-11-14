"""SERPAVI rent reference workbook -> observations (D-242)."""

from pathlib import Path

import pandas as pd
import pytest
from openpyxl import load_workbook

from hi_contracts.catalog.pipeline import SerpaviRentPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.serpavi.normalize import (
    cell_value,
    normalize,
    parse_workbook,
    territory_code,
)
from hi_ingestion.pipelines.serpavi.run import quartiles_ordered_check
from hi_ingestion.pipelines.stat_tables.normalize import RowError

SAMPLE = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "fixtures"
    / "golden"
    / "serpavi_sample"
    / "mivau_serpavi_alquiler.xlsx"
)
DATASET = "mivau_serpavi_alquiler"
SOL_SECTION = "2807901117"


def _spec() -> SerpaviRentPipeline:
    spec = load_catalog().pipelines[DATASET]
    assert isinstance(spec, SerpaviRentPipeline)
    return spec


def _units(*codes: tuple[str, str]) -> set[str]:
    prefix = {"municipio": "MUN", "distrito": "DIS", "seccion_censal": "SEC"}
    return {f"ES.28.{prefix[level]}.{code}" for level, code in codes}


def _values(spec: SerpaviRentPipeline) -> dict[tuple[str, str, str, str, str], float | None]:
    obs = normalize(parse_workbook(SAMPLE, spec), spec, set())
    return {
        (
            r["metric_id"],
            r["territory_level"],
            r["territory_code"],
            r["dims"]["tipologia"],
            r["dims"].get("estadistico", "n"),
        ): r["value"]
        for r in obs.frame.to_dict("records")
    }


def test_keeps_the_province_and_the_years_from_period_min() -> None:
    spec = _spec()
    frame = parse_workbook(SAMPLE, spec)
    assert not any(c.endswith("_23") for c in frame.columns)  # 2023 is before period_min
    obs = normalize(frame, spec, set())
    assert obs.quarantine.empty
    assert obs.out_of_window == 3  # the other province's row on each of the three sheets
    assert set(obs.frame["territory_code"].str[:2]) == {"28"}
    assert {str(p) for p in obs.frame["period_start"]} == {"2024-01-01"}
    assert set(obs.frame["territory_level"]) == {"municipio", "distrito", "seccion_censal"}


def test_one_observation_per_cell_with_typology_and_statistic() -> None:
    values = _values(_spec())
    rent, count = "alquiler_m2_mensual_serpavi", "contratos_alquiler_serpavi"
    assert values[count, "municipio", "28079", "colectiva", "n"] == 300447
    assert values[count, "municipio", "28079", "unifamiliar", "n"] == 3248
    assert values[rent, "municipio", "28079", "colectiva", "mediana"] == pytest.approx(13.968, 1e-3)
    assert values[rent, "municipio", "28079", "colectiva", "p25"] == pytest.approx(11.029, 1e-3)
    assert values[rent, "municipio", "28079", "colectiva", "p75"] == pytest.approx(17.925, 1e-3)
    assert values[rent, "distrito", "2807901", "colectiva", "mediana"] == pytest.approx(17.70, 1e-3)
    assert values[rent, "seccion_censal", SOL_SECTION, "colectiva", "mediana"] is not None
    # 8 per territory and year: 2 counts and 2 x 3 rent statistics
    assert len(values) == 8 * (3 + 5 + 19)


def test_a_rent_not_published_is_unknown_never_zero() -> None:
    """La Acebeda: 0 flats and 2 houses rented, below the 10 the source publishes."""
    spec = _spec()
    obs = normalize(parse_workbook(SAMPLE, spec), spec, set())
    acebeda = obs.frame[obs.frame["territory_code"] == "28001"]
    counts = acebeda[acebeda["metric_id"] == "contratos_alquiler_serpavi"]
    assert sorted(counts["value"].tolist()) == [0.0, 2.0]  # a published 0 stays 0
    rents = acebeda[acebeda["metric_id"] == "alquiler_m2_mensual_serpavi"]
    assert rents["value"].isna().all()
    assert set(rents["null_reason"]) == {"SOURCE_MISSING"}


def test_admin_unit_only_for_units_of_the_geography() -> None:
    spec = _spec()
    known = _units(("municipio", "28079"), ("seccion_censal", SOL_SECTION))
    obs = normalize(parse_workbook(SAMPLE, spec), spec, known)
    linked = obs.frame.loc[obs.frame["admin_unit_id"].notna(), "territory_code"]
    assert set(linked) == {"28079", SOL_SECTION}


def test_madrid_has_its_name_and_districts_none() -> None:
    spec = _spec()
    obs = normalize(parse_workbook(SAMPLE, spec), spec, set())
    names = dict(zip(obs.frame["territory_code"], obs.frame["territory_name"], strict=True))
    assert names["28079"] == "Madrid"
    assert pd.isna(names["2807901"])  # the district sheet has no name column


def test_a_missing_column_stops_the_pipeline(tmp_path: Path) -> None:
    book = load_workbook(SAMPLE)
    sheet = book["Distritos"]
    for cell in sheet[1]:
        if cell.value == "ALQM2_LV_75_VU_24":
            cell.value = "ALQM2_LV_75_VU_XX"
    broken = tmp_path / "broken.xlsx"
    book.save(broken)
    with pytest.raises(ValueError, match="missing columns"):
        parse_workbook(broken, _spec())


def test_no_year_from_period_min_stops_the_pipeline() -> None:
    later = _spec().model_copy(update={"period_min": 2030})
    with pytest.raises(ValueError, match="no year from 2030"):
        parse_workbook(SAMPLE, later)


@pytest.mark.parametrize(
    ("raw", "level", "code"),
    [
        ("28079", "municipio", "28079"),
        (2807901, "distrito", "2807901"),
        (1001, "municipio", "01001"),
    ],
)
def test_codes_keep_their_leading_zeros(raw: object, level: str, code: str) -> None:
    assert territory_code(raw, level) == code


def test_empty_cells_are_missing_and_garbage_goes_to_quarantine() -> None:
    assert cell_value(None) == (None, "SOURCE_MISSING")
    assert cell_value("") == (None, "SOURCE_MISSING")
    assert cell_value(float("nan")) == (None, "SOURCE_MISSING")
    assert cell_value(0) == (0.0, None)
    assert cell_value(12.5) == (12.5, None)
    with pytest.raises(RowError):
        cell_value("n/d")
    with pytest.raises(RowError):
        territory_code("28A79", "municipio")


def test_quartiles_out_of_order_fail_the_quality_check() -> None:
    spec = _spec()
    obs = normalize(parse_workbook(SAMPLE, spec), spec, set())
    assert quartiles_ordered_check(obs.frame, spec).passed
    frame = obs.frame.copy()
    p25 = frame["dims"].map(lambda d: d.get("estadistico") == "p25") & (
        frame["territory_code"] == "28079"
    )
    frame.loc[p25 & frame["dims"].map(lambda d: d["tipologia"] == "colectiva"), "value"] = 99.0
    check = quartiles_ordered_check(frame, spec)
    assert not check.passed and check.critical
