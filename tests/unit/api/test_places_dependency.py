"""GET /api/v1/places says whether each health place is public or private and who runs each
hospital (D-239), without a database: the value the load wrote from the CM register goes out on
the place itself, beds or not, and a network hospital a private company runs is public."""

from typing import Any

import pytest

from hi_api.services.places import _feature  # pyright: ignore[reportPrivateUsage]
from hi_contracts.public.places import PlaceFeature
from hi_domain.facilities import PRIVATE_MANAGEMENT, PRIVATE_MANAGEMENT_DIRECTORY


def _row(attributes: dict[str, Any], subcategory: str = "Hospital general") -> dict[str, Any]:
    """FIXTURE: a made-up row of place_master, never shown in the demo."""
    return {
        "id": "00000000-0000-0000-0000-000000000001",
        "canonical_name": "Hospital de prueba",
        "category": "health",
        "subcategory": subcategory,
        "municipio_ine": "28079",
        "seccion_admin_unit_id": "ES.28.SEC.2807905001",
        "attributes": attributes,
        "confidence": 1.0,
        "official_dataset_id": "cm_centros_sanitarios",
        "lon": -3.7,
        "lat": 40.4,
    }


@pytest.mark.parametrize("dependency", ["publica", "privada"])
def test_a_hospital_without_beds_still_says_public_or_private(dependency: str) -> None:
    feature = PlaceFeature.model_validate(_feature(_row({"dependency": dependency}), []))
    assert feature.properties.dependency == dependency
    assert feature.properties.capacity is None


def test_a_matched_hospital_says_it_on_the_place_and_with_its_beds() -> None:
    directory = {"capacity": 651, "dataset_id": "ms_catalogo_nacional_hospitales"}
    attributes = {"dependency": "privada", "directory": directory}
    feature = PlaceFeature.model_validate(_feature(_row(attributes), []))
    assert feature.properties.dependency == "privada"
    assert feature.properties.capacity is not None
    assert feature.properties.capacity.dependency == "privada"  # as before D-239


@pytest.mark.parametrize("attributes", [{}, {"dependency": None}, {"dependency": "concertada"}])
def test_an_unknown_dependency_is_left_out_never_guessed(attributes: dict[str, Any]) -> None:
    """Data synced before the code: a value this contract does not know must not break /places."""
    feature = PlaceFeature.model_validate(_feature(_row(attributes), []))
    assert feature.properties.dependency is None


def _matched(code: str, dataset_id: str = PRIVATE_MANAGEMENT_DIRECTORY) -> dict[str, Any]:
    return {"capacity": 300, "dataset_id": dataset_id, "external_id": code}


def test_a_network_hospital_a_private_company_runs_is_public_with_private_management() -> None:
    """The Fundación Jiménez Díaz: «Privado No Benéfico» in the register, in the network of the
    Servicio Madrileño de Salud by concierto singular. Public, «gestión privada», beds too."""
    attributes = {"dependency": "privada", "directory": _matched("280421")}
    properties = PlaceFeature.model_validate(_feature(_row(attributes), [])).properties
    assert (properties.dependency, properties.management) == ("publica", "privada")
    assert properties.capacity is not None and properties.capacity.dependency == "publica"


@pytest.mark.parametrize("code", sorted(PRIVATE_MANAGEMENT))
def test_every_hospital_of_the_list_says_private_management(code: str) -> None:
    attributes = {"dependency": "publica", "directory": _matched(code)}
    properties = PlaceFeature.model_validate(_feature(_row(attributes), [])).properties
    assert (properties.dependency, properties.management) == ("publica", "privada")


@pytest.mark.parametrize(
    ("dependency", "directory", "expected"),
    [
        ("publica", _matched("280029"), ("publica", "publica")),  # run by the SERMAS
        ("privada", _matched("280000"), ("privada", "privada")),
        ("publica", None, ("publica", "publica")),  # no beds: still a public hospital
        # The same number in another directory is not the catalogue's code: never guessed
        ("privada", _matched("280421", "cm_otro_directorio"), ("privada", "privada")),
    ],
)
def test_the_rest_keep_the_register_and_say_who_runs_them(
    dependency: str, directory: dict[str, Any] | None, expected: tuple[str, str]
) -> None:
    attributes = {"dependency": dependency, "directory": directory}
    properties = PlaceFeature.model_validate(_feature(_row(attributes), [])).properties
    assert (properties.dependency, properties.management) == expected


def test_only_hospitals_say_who_runs_them() -> None:
    row = _row({"dependency": "publica"}, subcategory="Centro de salud")
    properties = PlaceFeature.model_validate(_feature(row, [])).properties
    assert (properties.dependency, properties.management) == ("publica", None)
    unknown = PlaceFeature.model_validate(_feature(_row({}), [])).properties
    assert unknown.management is None
