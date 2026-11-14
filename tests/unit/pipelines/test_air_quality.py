"""Air quality networks (D-237): the annual mean of NO2 per station from the hourly values
flagged valid, and each municipio of the region in its air quality zone."""

from typing import Any

import pandas as pd
import pytest

from hi_contracts.catalog.pipeline import AirQualityHourlyPipeline, AirQualityZonesPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.air_quality.means import (
    hours_in_year,
    run_means_quality,
    station_means,
)
from hi_ingestion.pipelines.air_quality.zones import run_zones_quality, zone_table


def _spec(**overrides: Any) -> AirQualityHourlyPipeline:
    data: dict[str, Any] = {
        "kind": "air_quality_hourly",
        "dataset_id": "cm_calidad_aire_horario_2025",
        "csv": {"decimal": ","},
        "magnitude": 8,
        "year": 2025,
        "min_stations": 2,
        "max_mean": 100.0,
    }
    return AirQualityHourlyPipeline.model_validate(data | overrides)


def _day(
    station: str, magnitude: str, year: str, hours: list[tuple[str, str]], *, upper: bool
) -> dict[str, str]:
    """FIXTURE: one made-up row of the hourly layout (24 values and 24 flags)."""
    row = {
        "provincia": "28",
        "municipio": "065",
        "estacion": station,
        "magnitud": magnitude,
        "punto_muestreo": f"28065{station}_{magnitude}_8",
        "ano": year,
        "mes": "01",
        "dia": "01",
    }
    for h in range(1, 25):
        value, flag = hours[h - 1] if h <= len(hours) else ("", "N")
        row[f"h{h:02d}"], row[f"v{h:02d}"] = value, flag
    return {k.upper(): v for k, v in row.items()} if upper else row


def _frame(*, upper: bool = False) -> pd.DataFrame:
    rows = [
        # Station 014: 10 and 20,5 valid; 99 not validated; NO2 of 2024 and CO (6) left out
        _day("014", "8", "2025", [("10", "V"), ("20,5", "V"), ("99", "N")], upper=upper),
        _day("014", "8", "2024", [("500", "V")], upper=upper),
        _day("014", "6", "2025", [("0,4", "V")], upper=upper),
        # Station 007: one valid hour of 30, and an hour flagged valid without a number
        _day("007", "8", "2025", [("30", "V"), ("", "V")], upper=upper),
    ]
    return pd.DataFrame(rows)


def test_the_annual_mean_counts_only_valid_hours_of_the_year_and_pollutant() -> None:
    result = station_means(_frame(), _spec())
    means = result.means.set_index("station_code")
    assert means.loc["28065014", "mean"] == pytest.approx(15.25)
    assert means.loc["28065014", "valid_hours"] == 2
    assert means.loc["28065014", "capture"] == pytest.approx(2 / 8760)
    assert means.loc["28065007", "mean"] == pytest.approx(30.0)
    assert result.rows_of_year == 3
    assert len(result.problems) == 1  # the valid hour without a number does not count


def test_the_ayuntamiento_layout_in_capitals_reads_the_same() -> None:
    upper = station_means(_frame(upper=True), _spec(csv={"decimal": "."}))
    assert upper.means.set_index("station_code").loc["28065007", "mean"] == pytest.approx(30.0)


def test_a_year_or_a_layout_that_is_not_there_fails_the_gate() -> None:
    assert run_means_quality(station_means(_frame(), _spec()), _spec()).passed
    for spec in (_spec(year=2026), _spec(min_stations=3), _spec(max_mean=20.0)):
        assert not run_means_quality(station_means(_frame(), spec), spec).passed
    broken = station_means(_frame().drop(columns=["v24"]), _spec())
    assert broken.missing_columns == ["v24"] and not run_means_quality(broken, _spec()).passed


def test_a_leap_year_has_more_hours() -> None:
    assert (hours_in_year(2025), hours_in_year(2024)) == (8760, 8784)


ZONES = AirQualityZonesPipeline.model_validate(
    {
        "kind": "air_quality_zones",
        "dataset_id": "cm_calidad_aire_zonas",
        "zone_code_column": "zona_calidad_aire_codigo",
        "zone_name_column": "zona_calidad_aire_descripcion",
        "municipio_name_column": "zona_calidad_aire_municipio",
    }
)
MUNICIPIOS = {  # FIXTURE: official names as the geography writes them
    "28004": "Álamo (El)",
    "28001": "Acebeda (La)",
    "28070": "Horcajo de la Sierra-Aoslos",
    "28079": "Madrid",
}


def _zones(names: list[str]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "zona_calidad_aire_codigo": ["3", "5", "5", "1"][: len(names)],
            "zona_calidad_aire_descripcion": [
                "AGLOMERACIÓN URBANA SUR",
                "RURAL SIERRA NORTE",
                "RURAL SIERRA NORTE",
                "MADRID",
            ][: len(names)],
            "zona_calidad_aire_municipio": names,
        }
    )


def test_each_municipio_is_found_by_its_name_with_or_without_the_article() -> None:
    names = ["EL ÁLAMO", "ACEBEDA", "HORCAJO DE LA SIERRA", "MADRID"]
    result = zone_table(_zones(names), ZONES, MUNICIPIOS)
    zones = dict(zip(result.zones["municipio_ine"], result.zones["zone_code"], strict=True))
    assert zones == {"28004": "3", "28001": "5", "28070": "5", "28079": "1"}
    assert (
        result.zones.set_index("municipio_ine").loc["28004", "zone_name"]
        == "Aglomeración Urbana Sur"
    )
    assert run_zones_quality(result).passed


def test_a_name_not_found_or_a_municipio_left_out_fails_the_gate() -> None:
    unknown = zone_table(
        _zones(["EL ÁLAMO", "ACEBEDA", "VILLA INVENTADA", "MADRID"]), ZONES, MUNICIPIOS
    )
    assert unknown.problems["municipio_name"].tolist() == ["VILLA INVENTADA"]
    assert not run_zones_quality(unknown).passed
    short = zone_table(_zones(["EL ÁLAMO", "ACEBEDA", "MADRID"]), ZONES, MUNICIPIOS)
    assert not run_zones_quality(short).passed


def test_the_catalog_reads_no2_of_2025_from_both_networks() -> None:
    catalog = load_catalog()
    for dataset_id in ("cm_calidad_aire_horario_2025", "ayto_calidad_aire_horario"):
        spec = catalog.pipelines[dataset_id]
        assert isinstance(spec, AirQualityHourlyPipeline)
        assert (spec.magnitude, spec.year, spec.valid_flag) == (8, 2025, "V")
    cm = catalog.pipelines["cm_calidad_aire_horario_2025"]
    assert isinstance(cm, AirQualityHourlyPipeline) and cm.csv.decimal == ","
