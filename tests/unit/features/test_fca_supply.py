"""Capacity per facility and people per street for the 2SFCA rows (D-217)."""

import numpy as np
import pytest

from hi_features.fca import demand_keys, people_by_key, supply_of

SPEC = {
    "kind": "municipal_share",
    "by_attribute": "titularidad",
    "mapping": {
        "PÚBLICO": "publico",
        "PÚBLICO-TITULARIDAD PRIVADA": "publico",
        "PRIVADO CONCERTADO": "privado_concertado",
    },
}


def school(municipio: str, ownership: str) -> dict[str, object]:
    return {"municipio_ine": municipio, "attributes": {"titularidad": ownership}}


def test_classrooms_are_shared_equally_within_municipio_and_ownership() -> None:
    schools = [
        school("28001", "PÚBLICO"),
        school("28001", "PÚBLICO-TITULARIDAD PRIVADA"),  # public units too
        school("28001", "PRIVADO CONCERTADO"),
        school("28002", "PÚBLICO"),
    ]
    shares = {("28001", "publico"): 30.0, ("28001", "privado_concertado"): 12.0}
    supply = supply_of(schools, SPEC, shares)
    assert supply.tolist() == pytest.approx([15.0, 15.0, 12.0, 0.0])


def test_published_attribute_or_unknown_never_zero() -> None:
    centres = [
        {"attributes": {"plazas": "40"}},
        {"attributes": {}},
        {"attributes": {"plazas": "x"}},
    ]
    supply = supply_of(centres, {"kind": "attribute", "attribute": "plazas"}, {})
    assert supply[0] == 40.0
    assert np.isnan(supply[1]) and np.isnan(supply[2])


def test_madrid_districts_are_scaled_to_the_census_total() -> None:
    people = people_by_key(
        {"28079": 100.0, "28001": 7.0}, {"2807901": 30.0, "2807902": 20.0, "2804501": 9.0}
    )
    assert people == pytest.approx({"28001": 7.0, "2807901": 60.0, "2807902": 40.0})


def test_madrid_without_district_population_is_an_error() -> None:
    with pytest.raises(ValueError, match="district"):
        people_by_key({"28079": 100.0}, {})


def test_each_street_takes_its_district_in_madrid_and_its_municipio_elsewhere() -> None:
    assert demand_keys(["2807905001", "2800101001", ""]) == ["2807905", "28001", ""]
