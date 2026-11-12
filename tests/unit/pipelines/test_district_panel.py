"""District panel (Ayuntamiento de Madrid) -> households by district (DATA-012 Fase 3) and the
residents' perception of safety in their barrio, with the city value (DATA-020, D-226)."""

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from hi_contracts.catalog.enums import NullReason
from hi_contracts.catalog.pipeline import MadridDistrictPanelPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import read_csv
from hi_ingestion.pipelines.district_panel.normalize import normalize
from hi_ingestion.pipelines.district_panel.run import run_panel_quality

GOLDEN = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "golden"
DATASET = "ayto_panel_indicadores_distritos_barrios"
FIXTURE = GOLDEN / "panel_sample" / f"{DATASET}.csv"
SAMPLE_DISTRICTS = {"2807901", "2807905", "2807906"}
PERCEPTION = {"percepcion_seguridad_barrio_noche", "percepcion_seguridad_barrio_dia"}
MADRID = "28079"


@pytest.fixture(scope="module")
def spec() -> MadridDistrictPanelPipeline:
    pipeline = load_catalog().pipelines[DATASET]
    assert isinstance(pipeline, MadridDistrictPanelPipeline)
    return pipeline


@pytest.fixture(scope="module")
def source(spec: MadridDistrictPanelPipeline) -> pd.DataFrame:
    return read_csv(FIXTURE, spec.csv)


def _value(frame: pd.DataFrame, metric: str, code: str, day: date) -> float:
    mask = (
        (frame["metric_id"] == metric)
        & (frame["territory_code"] == code)
        & (frame["period_start"] == day)
    )
    values: list[float] = frame.loc[mask, "value"].tolist()
    assert len(values) == 1
    return float(values[0])


def test_only_declared_indicators_at_district_level(
    spec: MadridDistrictPanelPipeline, source: pd.DataFrame
) -> None:
    obs = normalize(source, spec)
    frame = obs.frame
    assert obs.quarantine.empty
    assert set(frame["metric_id"]) == {"hogares_padron", "tamano_medio_hogar_padron", *PERCEPTION}
    districts = frame.loc[frame["territory_level"] == "distrito"]
    assert set(districts["territory_code"]) == SAMPLE_DISTRICTS
    assert set(districts["admin_unit_id"]) == {f"ES.28.DIS.{c}" for c in SAMPLE_DISTRICTS}
    assert obs.out_of_window > 0  # city, barrio and other indicators are left out, not lost
    key = ["metric_id", "territory_level", "territory_code", "period_start"]
    assert not frame.duplicated(key).any()


def test_the_city_row_is_kept_only_for_the_city_indicators(
    spec: MadridDistrictPanelPipeline, source: pd.DataFrame
) -> None:
    """D-226: the residents' perception comes with the Madrid value to compare with."""
    frame = normalize(source, spec).frame
    city = frame.loc[frame["territory_level"] == "municipio"]
    assert set(city["metric_id"]) == PERCEPTION
    assert set(city["territory_code"]) == {MADRID}
    assert set(city["admin_unit_id"]) == {f"ES.28.MUN.{MADRID}"}
    assert _value(city, "percepcion_seguridad_barrio_noche", MADRID, date(2025, 1, 1)) == 6.4
    assert _value(city, "percepcion_seguridad_barrio_dia", MADRID, date(2025, 1, 1)) == 7.8
    night = frame.loc[frame["territory_level"] == "distrito"]
    assert _value(night, "percepcion_seguridad_barrio_noche", "2807906", date(2025, 1, 1)) == 6.1


def test_a_date_repeated_in_two_panel_editions_is_one_observation(
    spec: MadridDistrictPanelPipeline, source: pd.DataFrame
) -> None:
    """The 2020 and 2021 panels both carry the 2019 survey: one observation, never two."""
    frame = normalize(source, spec).frame
    centro = frame.loc[frame["territory_level"] == "distrito"]
    assert _value(centro, "percepcion_seguridad_barrio_noche", "2807901", date(2019, 1, 1)) == 6.98


def test_a_revised_value_takes_the_latest_panel_edition(
    spec: MadridDistrictPanelPipeline, source: pd.DataFrame
) -> None:
    revised = source.copy()
    later = (
        (revised["Periodo panel"] == "2021")
        & (revised["cod_distrito"] == "1")
        & (revised["indicador_completo"] == "Percepción de seguridad en el barrio por la noche")
    )
    assert int(later.sum()) == 1
    revised.loc[later, "valor_indicador"] = "7,1"
    frame = normalize(revised.iloc[::-1].reset_index(drop=True), spec).frame
    centro = frame.loc[frame["territory_level"] == "distrito"]
    assert _value(centro, "percepcion_seguridad_barrio_noche", "2807901", date(2019, 1, 1)) == 7.1


def test_city_indicators_must_be_declared_indicators(spec: MadridDistrictPanelPipeline) -> None:
    data = spec.model_dump() | {"city_indicators": ["Indicador que no se lee"]}
    with pytest.raises(ValueError, match="city_indicators"):
        MadridDistrictPanelPipeline.model_validate(data)


def test_values_dates_and_decimal_comma(
    spec: MadridDistrictPanelPipeline, source: pd.DataFrame
) -> None:
    frame = normalize(source, spec).frame
    assert _value(frame, "hogares_padron", "2807901", date(2025, 1, 1)) == 75159
    assert _value(frame, "tamano_medio_hogar_padron", "2807901", date(2025, 1, 1)) == 1.95
    assert date(2019, 1, 1) in set(frame["period_start"])  # every panel year is kept


def test_unreadable_values_stay_unknown_and_bad_dates_go_to_quarantine(
    spec: MadridDistrictPanelPipeline, source: pd.DataFrame
) -> None:
    district_rows = (
        (source["indicador_completo"] == "Total hogares")
        & (source["cod_distrito"] != "")
        & (source["cod_barrio"] == "")
    )
    rows = source.loc[district_rows].head(2).copy()
    rows.loc[rows.index[0], "valor_indicador"] = "n.d."
    rows.loc[rows.index[1], "fecha_indicador"] = "2025"
    obs = normalize(rows, spec)
    assert len(obs.quarantine) == 1
    assert bool(obs.frame["value"].isna().all())
    assert obs.frame["null_reason"].tolist() == [NullReason.PARSE_ERROR.value]


def test_quality_requires_every_district(
    spec: MadridDistrictPanelPipeline, source: pd.DataFrame
) -> None:
    obs = normalize(source, spec)
    metrics = load_catalog().metrics
    sample = spec.model_copy(update={"expected_districts": 3})
    assert run_panel_quality(obs, sample, metrics, SAMPLE_DISTRICTS).passed
    assert not run_panel_quality(obs, spec, metrics, SAMPLE_DISTRICTS).passed


def test_quarantine_points_at_the_source_row_and_lost_district_codes_are_not_hidden(
    spec: MadridDistrictPanelPipeline, source: pd.DataFrame
) -> None:
    rows = source.loc[
        (source["indicador_completo"] == "Total hogares") & (source["cod_barrio"] == "")
    ].copy()
    district = rows.loc[rows["cod_distrito"] != ""].index[0]
    rows.loc[district, "cod_distrito"] = ""  # a district row that lost its code, name kept
    obs = normalize(rows.reset_index(drop=True), spec)
    position = rows.index.get_loc(district)
    assert obs.quarantine["source_row"].tolist() == [position]
    city = int((rows["cod_distrito"] == "").sum()) - 1
    assert obs.out_of_window == city  # only the real city rows are outside the scope
