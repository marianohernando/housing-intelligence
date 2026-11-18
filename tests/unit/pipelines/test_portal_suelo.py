"""D-246 on synthetic rows: public parcels for housing of the Portal del Suelo, by zone."""

from datetime import date
from typing import Any

import pandas as pd
import pytest
from pydantic import ValidationError

from hi_contracts.catalog.manual import ParcelPointsTable
from hi_contracts.catalog.pipeline import PublicLandParcelsPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.zone_context.parcels import Placement, normalize_parcels
from hi_ingestion.pipelines.zone_context.run import load_points, parcels_quality

SPEC = PublicLandParcelsPipeline(
    kind="public_land_parcels",
    dataset_id="cm_parcelas_portal_suelo",
    metric_id="suelo_publico_parcela_m2_edificable",
    uses=["R"],
    split_municipio_ine="28079",
    points="portal_suelo_madrid_puntos.yaml",
    regimes={"V": "venta", "C": "concesion"},
    undocumented_regimes=["D"],
    urbanization={"U": "urbanizado", "P": "sin_urbanizar"},
    undocumented_urbanization=["p"],
    min_rows=1,
    max_rows=100,
)
NAMES = {"28079": "Madrid", "28086": "Molar (El)", "28080": "Majadahonda"}
VICALVARO = Placement("2807919", "28079191")
DAY = date(2026, 11, 18)


def _parcel(
    ref: str, municipio: str = "080", name: str = "Majadahonda", **extra: str
) -> dict[str, str]:
    row = {
        "referencia_codigo": ref,
        "municipio_codigo": municipio,
        "municipio_descripcion": name,
        "uso_principal_codigo": "R",
        "regimen_codigo": "V",
        "urbanizacion_codigo": "U",
        "localizacion_descripcion": "C/  EL VELLÓN 5",
        "parcela_descripcion": "API 08.12",
        "gestor_descripcion": "Consorcio Urbanístico\nÁrea Sur ",
        "superficie_edificable": "13475,8",
        "url_visor": "https://idem.comunidad.madrid/visor/?v=suelo",
    }
    return row | extra


def _run(*rows: dict[str, str], placed: dict[str, Placement] | None = None) -> Any:
    return normalize_parcels(pd.DataFrame(list(rows)), SPEC, NAMES, placed or {}, DAY)


def _dims(result: Any, ref: str) -> dict[str, str]:
    frame = result.obs.frame
    return frame.loc[frame["dims"].map(lambda d: d["item"]) == ref, "dims"].iloc[0]


def test_only_residential_parcels_are_kept_and_the_rest_counted() -> None:
    result = _run(_parcel("1"), _parcel("2", uso_principal_codigo="T"))
    assert result.parcels == 2 and result.out_of_scope == 1
    assert list(result.obs.frame["territory_code"]) == ["28080"]
    assert result.obs.frame["value"].iloc[0] == pytest.approx(13475.8)  # decimal comma
    assert result.obs.quarantine.empty


def test_texts_are_one_line_and_codes_are_labelled_only_when_the_cm_says_what_they_mean() -> None:
    result = _run(
        _parcel("1"),
        _parcel("2", regimen_codigo="C", urbanizacion_codigo="P"),
        _parcel("3", regimen_codigo="D", urbanizacion_codigo="p"),
    )
    assert _dims(result, "1") == {
        "item": "1",
        "name": "C/ EL VELLÓN 5",
        "parcel": "API 08.12",
        "regime": "venta",
        "manager": "Consorcio Urbanístico Área Sur",
        "url": "https://idem.comunidad.madrid/visor/?v=suelo",
        "stage": "urbanizado",
    }
    assert (_dims(result, "2")["regime"], _dims(result, "2")["stage"]) == (
        "concesion",
        "sin_urbanizar",
    )
    assert "regime" not in _dims(result, "3") and "stage" not in _dims(result, "3")


def test_a_code_nobody_declared_is_quarantined() -> None:
    result = _run(_parcel("1", regimen_codigo="X"))
    assert result.obs.frame.empty
    assert "regime code 'X'" in result.obs.quarantine["reason"].iloc[0]


def test_the_municipio_is_the_geographys_by_code_and_name() -> None:
    """«Molar, El» is «Molar (El)»; a code whose name is another municipio's is quarantined."""
    result = _run(
        _parcel("1", municipio="086", name="Molar, El"),
        _parcel("2", municipio="086", name="Majadahonda"),
        _parcel("3", municipio="999", name="Nowhere"),
    )
    assert list(result.obs.frame["territory_code"]) == ["28086"]
    assert result.obs.frame["territory_name"].iloc[0] == "Molar (El)"
    assert len(result.obs.quarantine) == 2


def test_madrid_parcels_are_also_in_their_district_and_barrio() -> None:
    result = _run(_parcel("M1", municipio="079", name="Madrid"), placed={"M1": VICALVARO})
    frame = result.obs.frame
    assert set(zip(frame["territory_level"], frame["territory_code"], strict=True)) == {
        ("municipio", "28079"),
        ("distrito", "2807919"),
        ("barrio", "28079191"),
    }
    assert set(frame["admin_unit_id"]) >= {"ES.28.DIS.2807919"}
    assert set(frame["period_start"]) == {DAY}


@pytest.mark.parametrize("placed", [{}, {"M1": Placement(None, None)}])
def test_a_madrid_parcel_without_a_district_blocks(placed: dict[str, Placement]) -> None:
    """Without its point (a parcel added after the points were read) or with a point in no
    district, the parcel is quarantined and the run stops: never left out of its district."""
    result = _run(_parcel("M1", municipio="079", name="Madrid"), placed=placed)
    assert result.obs.frame.empty and len(result.obs.quarantine) == 1
    metrics = {m: load_catalog().metrics[m] for m in SPEC.metric_ids()}
    report = parcels_quality(result, SPEC, metrics, set(NAMES), {"2807919", "28079191"})
    failed = [c.name for c in report.checks if c.critical and not c.passed]
    assert "nothing_quarantined" in failed


def test_a_missing_buildable_surface_is_unknown_never_zero() -> None:
    result = _run(_parcel("1", superficie_edificable=""))
    row = result.obs.frame.iloc[0]
    assert pd.isna(row["value"]) and row["null_reason"] == "SOURCE_MISSING"


def test_a_repeated_reference_is_quarantined() -> None:
    result = _run(_parcel("1"), _parcel("1"))
    assert len(result.obs.frame) == 1 and len(result.obs.quarantine) == 1


def test_a_cut_file_blocks() -> None:
    result = _run(_parcel("1"))
    metrics = {m: load_catalog().metrics[m] for m in SPEC.metric_ids()}
    spec = SPEC.model_copy(update={"min_rows": 2})
    report = parcels_quality(result, spec, metrics, set(NAMES), set())
    assert [c.name for c in report.checks if c.critical and not c.passed] == ["file_size"]


def test_a_code_is_documented_or_not() -> None:
    with pytest.raises(ValidationError):
        PublicLandParcelsPipeline.model_validate(
            SPEC.model_dump() | {"undocumented_regimes": ["V"]}
        )


def _points(**changes: Any) -> dict[str, Any]:
    table = {
        "title": "Puntos",
        "publisher": "Comunidad de Madrid",
        "url": "https://idem.comunidad.madrid/geoidem/UsoDelSuelo/ows",
        "layer": "UsoDelSuelo:IDEM_V_SUELO_PARCELA",
        "crs": "EPSG:25830",
        "consulted": "2026-11-18",
        "method": "Punto interior del polígono",
        "municipio_ine": "28079",
        "points": [{"ref": "07900151Y", "x": 438356, "y": 4481322}],
    }
    return table | changes


@pytest.mark.parametrize(
    "changes",
    [
        {"points": [{"ref": "07900151Y", "x": -3.7, "y": 40.4}]},  # degrees, not metres
        {"points": [{"ref": "A", "x": 438356, "y": 4481322}] * 2},
        {"crs": "EPSG:4326"},
    ],
)
def test_points_are_metres_inside_the_region_one_per_parcel(changes: dict[str, Any]) -> None:
    ParcelPointsTable.model_validate(_points())
    with pytest.raises(ValidationError):
        ParcelPointsTable.model_validate(_points(**changes))


def test_the_versioned_points_are_madrids_from_the_cm_layer() -> None:
    """The real file: Madrid's parcels of the IDEM layer, read from the URL the dataset
    declares, with the date it was read."""
    catalog = load_catalog()
    spec = catalog.pipelines["cm_parcelas_portal_suelo"]
    assert isinstance(spec, PublicLandParcelsPipeline)
    table = load_points(spec)
    assert table.municipio_ine == spec.split_municipio_ine
    layer = next(r for r in catalog.datasets[spec.dataset_id].resources if r.role == "points")
    assert str(table.url) == str(layer.url)
    assert len(table.points) >= 38  # the 38 residential parcels of Madrid on 18 Nov 2026
