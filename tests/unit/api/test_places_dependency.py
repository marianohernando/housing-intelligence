"""GET /api/v1/places says who runs each health place (D-239), without a database: the value
the load wrote from the CM register goes out on the place itself, beds or not."""

from typing import Any

import pytest

from hi_api.services.places import _feature  # pyright: ignore[reportPrivateUsage]
from hi_contracts.public.places import PlaceFeature


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
