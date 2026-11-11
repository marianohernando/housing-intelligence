"""Places normalisation and QA on real fixtures (no database)."""

from pathlib import Path

import pytest

from hi_contracts.catalog.pipeline import PointsPipeline
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.pipelines.common import read_csv
from hi_ingestion.pipelines.places.normalize import Places, canonical_place_id, normalize_places
from hi_ingestion.pipelines.places.quality import run_quality

FIXTURES = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "golden" / "places_sample"


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return load_catalog()


def _run(catalog: Catalog, dataset_id: str) -> tuple[PointsPipeline, Places]:
    spec = catalog.pipelines[dataset_id]
    assert isinstance(spec, PointsPipeline)
    return spec, normalize_places(read_csv(FIXTURES / f"{dataset_id}.csv", spec.csv), spec)


@pytest.mark.parametrize(
    "dataset_id",
    [
        "cm_centros_educativos",
        "cm_centros_sanitarios",
        "cm_centros_atencion_social",
        "cm_oficinas_farmacia",
    ],
)
def test_fixture_passes_quality(catalog: Catalog, dataset_id: str) -> None:
    spec, places = _run(catalog, dataset_id)
    report = run_quality(places, spec)
    assert report.passed, [c for c in report.checks if not c.passed]
    assert places.frame["lon"].between(-4.6, -3.0).all()
    assert places.frame["h3_r9"].str.len().eq(15).all()


def test_missing_coordinates_go_to_quarantine(catalog: Catalog) -> None:
    _, places = _run(catalog, "cm_centros_educativos")
    assert (places.quarantine["reason"] == "missing or unparseable coordinates").any()


def test_closed_schools_are_not_places(catalog: Catalog) -> None:
    _, places = _run(catalog, "cm_centros_educativos")
    assert places.filtered_out["SITUACIÓN_not_active"] >= 1


def test_protected_housing_is_never_mapped(catalog: Catalog) -> None:
    spec, places = _run(catalog, "cm_centros_atencion_social")
    source = read_csv(FIXTURES / "cm_centros_atencion_social.csv", spec.csv)
    assert (source["subtipo"] == "PISOS TUTELADOS").any()  # the fixture does contain one
    assert "PISOS TUTELADOS" not in set(places.frame["subcategory"])
    assert set(places.frame["subcategory"]) <= set(spec.row_filters["subtipo"])


def test_health_centres_are_grouped_with_their_services(catalog: Catalog) -> None:
    _, places = _run(catalog, "cm_centros_sanitarios")
    assert places.frame["external_id"].is_unique
    services = [a.get("oferta_asistecial") for a in places.frame["attributes"]]
    assert all(isinstance(s, list) for s in services if s is not None)


def test_no_contact_data_in_attributes(catalog: Catalog) -> None:
    for dataset_id in [
        "cm_centros_educativos",
        "cm_centros_sanitarios",
        "cm_centros_atencion_social",
    ]:
        _, places = _run(catalog, dataset_id)
        keys = {k for attrs in places.frame["attributes"] for k in attrs}
        assert not {
            k for k in keys if any(t in k for t in ("telefono", "correo", "mail", "nif", "web"))
        }


def test_pharmacies_are_named_by_address_never_by_holder(catalog: Catalog) -> None:
    _, places = _run(catalog, "cm_oficinas_farmacia")
    assert set(places.frame["subcategory"]) == {"Farmacia"}
    assert places.frame["canonical_name"].str.startswith("Farmacia · CALLE").any()
    assert not places.frame["canonical_name"].str.contains("redactado").any()
    keys = {k for attrs in places.frame["attributes"] for k in attrs}
    assert not any("titular" in k for k in keys)
    assert (places.quarantine["reason"] == "missing or unparseable coordinates").any()


def test_canonical_ids_are_stable() -> None:
    assert canonical_place_id("cm_x", "123") == canonical_place_id("cm_x", "123")
    assert canonical_place_id("cm_x", "123") != canonical_place_id("cm_y", "123")
