"""D-241 pipelines on synthetic rows: municipio names, VEDA planning areas and Plan Vive."""

from datetime import date
from typing import Any

import pandas as pd
import pytest
import yaml
from pydantic import ValidationError

from hi_contracts.catalog.manual import ZoneItemsTable, spanish_count
from hi_contracts.catalog.pipeline import (
    CmMunicipioNameTablePipeline,
    CuratedZoneItemsPipeline,
    MadridDevelopmentAreasPipeline,
)
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.stat_tables.normalize import RowError
from hi_ingestion.pipelines.zone_context.normalize import (
    municipio_names,
    normalize_development_areas,
    normalize_municipio_names,
    normalize_zone_items,
    quarter_period,
)
from hi_ingestion.pipelines.zone_context.run import (
    MANUAL_DIR,
    every_municipio_published,
    load_table,
)

NAMES = municipio_names({"28004": "Álamo (El)", "28079": "MADRID", "28127": "ROZAS DE MADRID, LAS"})
SALES = CmMunicipioNameTablePipeline(
    kind="cm_municipio_name_table",
    dataset_id="cm_transacciones_nueva_usada",
    metric_id="compraventas_vivienda",
    quarter_column="Periodo",
    period_min=2025,
    row_filters={"Indicador": ["Serie"]},
    dimension_columns={"Tipo": "tipo"},
    status_dimension="estado",
)


def _sale(name: str, year: str = "2026", quarter: str = "T2", **extra: str) -> dict[str, str]:
    row = {
        "Año": year,
        "Periodo": quarter,
        "Territorio": name,
        "Tipo": "Vivienda nueva",
        "Indicador": "Serie",
        "Valor": "7.0",
        "Unidad": "Número",
        "Estado dato": "",
    }
    return row | extra


def test_quarters_are_calendar_quarters() -> None:
    assert quarter_period("2026", "T2") == (date(2026, 4, 1), date(2026, 6, 30))
    assert quarter_period("2025", "T4") == (date(2025, 10, 1), date(2025, 12, 31))
    with pytest.raises(RowError):
        quarter_period("2025", "T5")


def test_names_resolve_without_case_accents_or_article_order() -> None:
    """The source writes «Alamo (El)» and «Rozas de Madrid (Las)»; the geography differs."""
    assert NAMES.resolve("Alamo (El)") == "28004"
    assert NAMES.resolve("Rozas de Madrid (Las)") == "28127"
    with pytest.raises(RowError):
        NAMES.resolve("Villa Inventada")


def test_two_municipios_with_one_key_are_a_geography_error() -> None:
    with pytest.raises(ValueError, match="share the name key"):
        municipio_names({"28001": "Acebeda (La)", "28999": "ACEBEDA, LA"})


def test_sales_keep_quarter_type_and_provisional_status() -> None:
    frame = pd.DataFrame(
        [
            _sale("Madrid", **{"Estado dato": "Provisional"}),
            _sale("Alamo (El)", quarter="T1", Tipo="Segunda mano"),
            _sale("Madrid", Indicador="Tasa de variación sobre el periodo anterior"),
            _sale("Madrid", year="2024"),
            _sale("Villa Inventada"),
        ]
    )
    obs = normalize_municipio_names(frame, SALES, NAMES)
    rows = obs.frame.to_dict("records")
    assert [(r["territory_code"], r["dims"]) for r in rows] == [
        ("28079", {"tipo": "vivienda_nueva", "estado": "provisional"}),
        ("28004", {"tipo": "segunda_mano"}),
    ]
    assert rows[0]["period_start"] == date(2026, 4, 1)
    assert obs.out_of_window == 1  # 2024, before period_min; the rate is out of scope
    assert obs.quarantine["reason"].str.contains("Villa Inventada").tolist() == [True]


def test_a_municipio_missing_from_the_table_blocks() -> None:
    frame = pd.DataFrame({"territory_level": ["municipio"], "territory_code": ["28079"]})
    assert not every_municipio_published(frame, {"28079", "28004"}).passed
    assert every_municipio_published(frame, {"28079"}).passed


AREAS = MadridDevelopmentAreasPipeline(
    kind="madrid_development_areas",
    dataset_id="ayto_pgoum_desarrollo_ambitos",
    metric_id="ambitos_desarrollo_residencial",
    municipio_ine="28079",
    phase_columns=["P", "G", "PU", "O"],
    uses=["Residencial"],
    states={
        "Finalizado": "done",
        "PGOUM-97": "done",
        "En Ejecución": "in_progress",
        "Sin Iniciar": "not_started",
    },
    keep_upper=["UVA"],
    expected_districts=21,
    min_rows=1,
    max_rows=10,
)


def _area(code: str, use: str, states: list[str], district: str = "19") -> dict[str, Any]:
    return {
        "Codigo_Distrito": district,
        "Distrito": "VICÁLVARO",
        "Ámbito": code,
        "Nombre": f"DESARROLLO DEL ESTE - {code}",
        "Uso Característico": use,
        "Superficie (m²)": "5507172",
        "Estado del desarrollo a fecha": "2026-07-01 00:00:00",
        **dict(zip(["P", "G", "PU", "O"], states, strict=True)),
    }


def test_only_unfinished_residential_areas_are_kept_with_their_stage() -> None:
    frame = pd.DataFrame(
        [
            _area("A1", "Residencial", ["Finalizado", "Finalizado", "Finalizado", "En Ejecución"]),
            _area("A2", "Residencial", ["Finalizado"] * 4),
            _area("A3", "Dotacional", ["Sin Iniciar"] * 4),
            _area(
                "A4", "Residencial", ["PGOUM-97", "Sin Iniciar", "Sin Iniciar", "Sin Iniciar"], "1"
            ),
            _area("A5", "Industrial", ["Nuevo estado"] * 4),  # out of scope: never read
        ]
    )
    result = normalize_development_areas(frame, AREAS)
    rows = result.obs.frame.to_dict("records")
    assert [(r["territory_code"], r["dims"]["item"], r["dims"]["stage"]) for r in rows] == [
        ("2807919", "A1", "obras"),
        ("2807901", "A4", "sin_empezar"),
    ]
    assert rows[0]["dims"]["name"] == "Desarrollo del Este - A1"
    assert rows[0]["value"] == 5507172.0
    assert rows[0]["period_start"] == date(2026, 7, 1)
    assert result.areas == 5
    assert result.districts == frozenset({"2807919", "2807901"})
    assert result.obs.quarantine.empty


def test_a_state_nobody_declared_is_quarantined() -> None:
    frame = pd.DataFrame(
        [_area("A1", "Residencial", ["Finalizado", "Suspendido", "Sin Iniciar", "Sin Iniciar"])]
    )
    result = normalize_development_areas(frame, AREAS)
    assert result.obs.frame.empty
    assert "Suspendido" in result.obs.quarantine["reason"].iloc[0]


def _entry(**changes: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "municipio_ine": "28006",
        "municipio": "Alcobendas",
        "item": "alcobendas",
        "name": "avda. Olímpica y avda. Camilo José Cela",
        "value": 756,
        "stage": "Construcción",
        "says": "Alcobendas · Nº viviendas: 756 · En fase de: Construcción · Promociones: 2 · "
        "Ubicación: avda. Olímpica y avda. Camilo José Cela",
    }
    return entry | changes


def _table(*entries: dict[str, Any]) -> ZoneItemsTable:
    return ZoneItemsTable.model_validate(
        {
            "title": "Plan Vive",
            "publisher": "Comunidad de Madrid",
            "url": "https://www.comunidad.madrid/plan-vive",
            "consulted": "2026-11-14",
            "unit": "viviendas",
            "items": list(entries),
        }
    )


def test_spanish_counts_use_a_dot_for_thousands() -> None:
    assert spanish_count(1616) == "1.616"
    assert spanish_count(756) == "756"


@pytest.mark.parametrize(
    "changes",
    [{"value": 765}, {"stage": "Entrega"}, {"name": "c/ Inventada"}, {"municipio": "Getafe"}],
)
def test_an_entry_its_quote_does_not_say_is_rejected(changes: dict[str, Any]) -> None:
    """Nothing typed from memory: the figure, stage, place and municipio are the page's."""
    with pytest.raises(ValidationError, match="does not say"):
        _table(_entry(**changes))


def test_districts_are_madrids_and_cite_where_they_come_from() -> None:
    placed = {"districts": [{"code": "2807916", "says": "16 · HORTALEZA · VALDEBEBAS"}]}
    with pytest.raises(ValidationError, match="district_source"):
        _table(_entry(**placed))


def test_an_entry_is_in_its_municipio_and_in_each_district_it_names() -> None:
    madrid = _entry(
        municipio_ine="28079",
        municipio="Madrid",
        item="madrid",
        name="Valdebebas y Los Ahijones",
        value=1616,
        stage="Entrega y construcción",
        says="Madrid · Nº viviendas: 1.616 · En fase de: Entrega y construcción · Promociones: 5"
        " · Ubicación: Valdebebas y Los Ahijones",
        districts=[
            {"code": "2807916", "says": "16 · HORTALEZA · VALDEBEBAS"},
            {"code": "2807919", "says": "19 · VICÁLVARO · LOS AHIJONES"},
        ],
        district_source={
            "publisher": "Ayuntamiento de Madrid",
            "url": "https://datos.madrid.es/dataset/203200-0-desarrollo-ambitos",
            "consulted": "2026-11-14",
        },
        note="La Comunidad no publica cuántas hay en cada sitio.",
    )
    obs = normalize_zone_items(_table(_entry(), madrid), "plan_vive_viviendas")
    rows = obs.frame.to_dict("records")
    assert [(r["territory_level"], r["territory_code"], r["value"]) for r in rows] == [
        ("municipio", "28006", 756.0),
        ("municipio", "28079", 1616.0),
        ("distrito", "2807916", 1616.0),
        ("distrito", "2807919", 1616.0),
    ]
    assert rows[1]["dims"]["note"].startswith("La Comunidad")
    assert "note" not in rows[0]["dims"]
    assert {r["period_start"] for r in rows} == {date(2026, 11, 14)}
    assert obs.quarantine.empty


def test_the_versioned_plan_vive_table_is_the_pages() -> None:
    """The real table: 26 entries, Madrid's in Hortaleza and Vicálvaro, every quote checked."""
    catalog = load_catalog()
    spec = catalog.pipelines["cm_plan_vive_promociones"]
    assert isinstance(spec, CuratedZoneItemsPipeline)
    table = load_table(spec)
    assert len(table.items) == 26
    assert sum(i.value for i in table.items) == 11845
    madrid = next(i for i in table.items if i.municipio_ine == "28079")
    assert [d.code for d in madrid.districts] == ["2807916", "2807919"]
    raw = yaml.safe_load((MANUAL_DIR / spec.table).read_text(encoding="utf-8"))
    assert raw["url"] == "https://www.comunidad.madrid/plan-vive"
