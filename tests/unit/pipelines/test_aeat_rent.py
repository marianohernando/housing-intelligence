"""Agencia Tributaria rent comparison tables -> observations (D-228)."""

from pathlib import Path

import pytest

from hi_contracts.catalog.pipeline import AeatRentComparisonPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.aeat_rent.normalize import normalize, parse_html, parse_number
from hi_ingestion.pipelines.stat_tables.normalize import RowError

SAMPLE = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "golden" / "aeat_sample"
MUNICIPIOS = "aeat_alquiler_nuevos_contratos_municipios"
POSTCODES = "aeat_alquiler_nuevos_contratos_codigo_postal"


def _spec(dataset_id: str) -> AeatRentComparisonPipeline:
    spec = load_catalog().pipelines[dataset_id]
    assert isinstance(spec, AeatRentComparisonPipeline)
    return spec


def _values(dataset_id: str) -> dict[tuple[str, str, str, str], float]:
    obs = normalize(parse_html(SAMPLE / f"{dataset_id}.html"), _spec(dataset_id))
    return {
        (r["metric_id"], r["territory_level"], r["territory_code"], r["dims"]["contratos"]): r[
            "value"
        ]
        for r in obs.frame.to_dict("records")
    }


def test_municipio_table_keeps_the_province_and_the_region() -> None:
    obs = normalize(parse_html(SAMPLE / f"{MUNICIPIOS}.html"), _spec(MUNICIPIOS))
    assert obs.quarantine.empty
    assert obs.out_of_window == 3  # Total, Almería and the province row are out of scope
    values = _values(MUNICIPIOS)
    assert values["alquiler_mensual_irpf_municipio", "municipio", "28079", "todos"] == 1012
    assert values["alquiler_mensual_irpf_municipio", "municipio", "28079", "nuevos"] == 1167
    assert values["m2_alquiler_irpf_municipio", "municipio", "28079", "nuevos"] == 68
    assert values["alquiler_mensual_irpf_municipio", "ccaa", "28", "nuevos"] == 1101
    assert len(values) == 8
    madrid = obs.frame[obs.frame["territory_code"] == "28079"].iloc[0]
    assert madrid["admin_unit_id"] == "ES.28.MUN.28079"
    assert str(madrid["period_start"]) == "2024-01-01"


def test_postcode_table_keeps_only_postcodes() -> None:
    """The postcode table's «Madrid, Comunidad de» adds up Madrid alone: not the region."""
    values = _values(POSTCODES)
    assert {k[2] for k in values} == {"28013", "28029", "28036"}
    assert {k[1] for k in values} == {"codigo_postal"}
    assert values["alquiler_mensual_irpf_codigo_postal", "codigo_postal", "28013", "nuevos"] == 1515


def test_a_changed_header_stops_the_pipeline(tmp_path: Path) -> None:
    html = (SAMPLE / f"{MUNICIPIOS}.html").read_text(encoding="utf-8")
    broken = tmp_path / "broken.html"
    broken.write_text(html.replace("m2 medios", "superficie", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="unexpected header"):
        parse_html(broken)
    no_year = tmp_path / "no_year.html"
    no_year.write_text(html.replace("Ejercicio", "Año", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="Ejercicio"):
        parse_html(no_year)


@pytest.mark.parametrize(("raw", "value"), [("1.167", 1167.0), ("6,7", 6.7), ("729", 729.0)])
def test_spanish_numbers(raw: str, value: float) -> None:
    assert parse_number(raw) == value


def test_a_missing_cell_is_unknown_and_garbage_goes_to_quarantine() -> None:
    frame = parse_html(SAMPLE / f"{MUNICIPIOS}.html")
    frame.loc[frame["label"] == "Madrid-28079", "rent_new"] = "-"
    obs = normalize(frame, _spec(MUNICIPIOS))
    assert obs.quarantine.empty
    missing = obs.frame[obs.frame["value"].isna()]
    assert missing["null_reason"].tolist() == ["SOURCE_MISSING"]  # never 0
    frame.loc[frame["label"] == "Madrid-28079", "rent_new"] = "n/d"
    assert len(normalize(frame, _spec(MUNICIPIOS)).quarantine) == 1
    with pytest.raises(RowError):
        parse_number("n/d")


def test_a_page_with_two_years_is_rejected(tmp_path: Path) -> None:
    html = (SAMPLE / f"{MUNICIPIOS}.html").read_text(encoding="utf-8")
    two = tmp_path / "two.html"
    two.write_text(html.replace("</h1>", "</h1><p>Ejercicio 2023</p>", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="one «Ejercicio YYYY»"):
        parse_html(two)
