"""Car parks as places (D-237): the kind from the start of the name, closed and repeated ones
left out, and nothing that scores (no database)."""

from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from pydantic import ValidationError

from hi_contracts.catalog.pipeline import PointsPipeline
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.pipelines.common import read_csv
from hi_ingestion.pipelines.places.normalize import Places, normalize_places
from hi_ingestion.pipelines.places.quality import run_quality

FIXTURES = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "golden" / "places_sample"
PARKING = [
    "ayto_aparcamientos_publicos",
    "ayto_aparcamientos_residentes",
    "crtm_aparcamientos_disuasion",
]
PUBLIC_KINDS = {"Aparcamiento público", "Aparcamiento mixto", "Aparcamiento disuasorio"}


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return load_catalog()


def _run(catalog: Catalog, dataset_id: str) -> tuple[PointsPipeline, Places]:
    spec = catalog.pipelines[dataset_id]
    assert isinstance(spec, PointsPipeline)
    return spec, normalize_places(read_csv(FIXTURES / f"{dataset_id}.csv", spec.csv), spec)


def _by_name(places: Places) -> dict[str, dict[str, Any]]:
    return {str(r["canonical_name"]): r for r in places.frame.to_dict("records")}  # pyright: ignore[reportUnknownVariableType]


@pytest.mark.parametrize("dataset_id", PARKING)
def test_fixture_passes_quality(catalog: Catalog, dataset_id: str) -> None:
    spec, places = _run(catalog, dataset_id)
    report = run_quality(places, spec)
    assert report.passed, [c for c in report.checks if not c.passed]
    assert places.quarantine.empty
    assert set(places.frame["category"]) == {"other"}


def test_the_kind_of_car_park_is_the_start_of_its_name(catalog: Catalog) -> None:
    _, public = _run(catalog, "ayto_aparcamientos_publicos")
    _, residents = _run(catalog, "ayto_aparcamientos_residentes")
    assert set(public.frame["subcategory"]) == {"Aparcamiento disuasorio", "Aparcamiento público"}
    names = _by_name(residents)
    assert names["Aparcamiento mixto. Alcántara"]["subcategory"] == "Aparcamiento mixto"
    assert names["Aparcamiento público. Plaza de España"]["subcategory"] == "Aparcamiento público"
    barcelo = "Aparcamiento para residentes del Centro Polivalente Barceló"
    assert names[barcelo]["subcategory"] == "Aparcamiento para residentes"


def test_a_mixed_car_park_is_published_once(catalog: Catalog) -> None:
    """The public file lists the mixed ones too, typed as residents': only one register keeps
    them, so no car park is counted twice."""
    _, public = _run(catalog, "ayto_aparcamientos_publicos")
    _, residents = _run(catalog, "ayto_aparcamientos_residentes")
    assert public.filtered_out["TIPO_not_allowed"] >= 1
    assert not set(public.frame["external_id"]) & set(residents.frame["external_id"])


def test_a_closed_car_park_is_not_a_place(catalog: Catalog) -> None:
    _, residents = _run(catalog, "ayto_aparcamientos_residentes")
    assert residents.filtered_out["NOMBRE_excluded"] == 1
    assert not any("cerrado" in name for name in _by_name(residents))


def test_coordinates_come_from_the_projected_columns(catalog: Catalog) -> None:
    """The source writes a longitude as «--3.65» in one row: X/Y in EPSG:25830 are read."""
    spec, public = _run(catalog, "ayto_aparcamientos_publicos")
    source = read_csv(FIXTURES / "ayto_aparcamientos_publicos.csv", spec.csv)
    assert source["LONGITUD"].str.startswith("--").any()  # the fixture keeps the bad row
    assert public.frame["lon"].between(-3.9, -3.5).all()
    assert public.frame["lat"].between(40.3, 40.6).all()


def test_a_car_park_both_publish_keeps_the_crtm_row_with_its_spaces(catalog: Catalog) -> None:
    """R-10 of PR #65: Aviación Española and Estadio Metropolitano come once, from the CRTM,
    which says their spaces and fee; the Ayuntamiento's rows of them are left out."""
    _, crtm = _run(catalog, "crtm_aparcamientos_disuasion")
    _, public = _run(catalog, "ayto_aparcamientos_publicos")
    names = _by_name(crtm)
    assert names["Aparcamiento disuasorio Aviación Española"]["attributes"]["plazas"] == "380"
    assert "Aparcamiento disuasorio Estadio Metropolitano" in names
    assert public.filtered_out["NOMBRE_excluded"] == 2
    municipal = _by_name(public)
    assert not any("Aviación Española" in n or "Estadio Metropolitano" in n for n in municipal)


def test_park_and_ride_keeps_its_spaces(catalog: Catalog) -> None:
    _, crtm = _run(catalog, "crtm_aparcamientos_disuasion")
    names = _by_name(crtm)
    alcala = names["Aparcamiento disuasorio Alcalá de Henares"]
    assert alcala["subcategory"] == "Aparcamiento disuasorio"
    assert alcala["attributes"]["plazas"] == "495"
    assert alcala["municipio_ine"] is None  # CMUN3 is not the INE code: the geography assigns it


def test_park_and_ride_sharing_an_id_are_two_car_parks(catalog: Catalog) -> None:
    """IDFEMPLAZAMIENTO repeats across different car parks (28_005_8 is Alcalá de Henares and
    Vicálvaro): keyed by the layer's FID, none is lost."""
    _, crtm = _run(catalog, "crtm_aparcamientos_disuasion")
    names = _by_name(crtm)
    assert (
        names["Aparcamiento disuasorio Vicálvaro - Puerta de Arganda"]["attributes"]["plazas"]
        == "129"
    )
    assert "Aparcamiento disuasorio Alcalá de Henares" in names


def test_no_car_park_keeps_a_postcode_the_rent_would_read(catalog: Catalog) -> None:
    """The district rent weighs postcodes by the places that carry them (CORE-006): a car park
    must never move it."""
    rent = (catalog.features["alquiler_m2_mensual"].formula.model_extra or {})["levels"]
    keys = {k for level in rent.values() for k in level.get("postcode_attributes", [])}
    assert keys
    for dataset_id in PARKING:
        _, places = _run(catalog, dataset_id)
        for attributes in places.frame["attributes"]:
            assert not keys & set(attributes), dataset_id


def test_car_parks_are_context_and_never_score(catalog: Catalog) -> None:
    spec = catalog.features["min_a_pie_aparcamiento_publico"]
    formula = spec.formula.model_extra or {}
    assert spec.fit is None and spec.gap_row is None
    assert set(formula["subcategories"]) == PUBLIC_KINDS  # never the residents-only ones
    assert formula["destination_category"] == "other"
    scoring = [f for f in catalog.features.values() if f.fit or f.gap_row]
    for feature in scoring:
        other = (feature.formula.model_extra or {}).get("destination_category")
        assert other != "other", feature.feature_id


def _spec(**overrides: Any) -> dict[str, Any]:
    return {
        "kind": "points_csv",
        "dataset_id": "ayto_aparcamientos_publicos",
        "category": "other",
        "id_column": "PK",
        "name_column": "NOMBRE",
        "x_column": "X",
        "y_column": "Y",
        "attribute_columns": ["DISTRITO"],
    } | overrides


def test_a_register_declares_one_way_to_name_its_kinds() -> None:
    prefixes = {"column": "NOMBRE", "prefixes": {"Aparcamiento mixto": "Aparcamiento mixto"}}
    PointsPipeline.model_validate(_spec(subcategory_prefixes=prefixes))
    with pytest.raises(ValidationError, match="exactly one"):
        PointsPipeline.model_validate(_spec())
    with pytest.raises(ValidationError, match="exactly one"):
        PointsPipeline.model_validate(_spec(subcategory_prefixes=prefixes, subcategory_value="x"))
    with pytest.raises(ValidationError, match="invalid exclude pattern"):
        PointsPipeline.model_validate(
            _spec(subcategory_value="x", exclude_patterns={"NOMBRE": ["("]})
        )


def test_a_name_without_a_known_start_is_left_out_and_counted() -> None:
    spec = PointsPipeline.model_validate(
        _spec(
            subcategory_prefixes={
                "column": "NOMBRE",
                "prefixes": {"aparcamiento MIXTO": "Aparcamiento mixto"},
            },
            crs="EPSG:25830",
        )
    )
    frame = pd.DataFrame(
        {
            "PK": ["1", "2"],
            "NOMBRE": ["Aparcamiento mixto. Uno", "Garaje privado"],
            "X": ["440000", "440100"],
            "Y": ["4474000", "4474100"],
            "DISTRITO": ["CENTRO", "CENTRO"],
        }
    )
    places = normalize_places(frame, spec)
    assert list(places.frame["subcategory"]) == ["Aparcamiento mixto"]  # the case is ignored
    assert places.filtered_out["NOMBRE_without_subcategory"] == 1
