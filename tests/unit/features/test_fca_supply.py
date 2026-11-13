"""Capacity per facility and people per street for the 2SFCA rows (D-217)."""

import numpy as np
import pytest

from hi_features.fca import census_by_zone, demand_keys, people_by_key, rows_for, supply_of

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


def test_a_zone_where_nobody_of_the_age_lives_is_not_applicable() -> None:
    """Fase de mejora: with 0 children of 0 to 4 in the census (La Acebeda) the row is
    NOT_APPLICABLE, not «the source does not publish it»; a zone with people but no street to
    place them on stays SOURCE_NO_COVERAGE."""
    f = {"per": 1000, "confidence": 1.0}
    rows = rows_for(
        ["28001", "28002", "28003"],
        np.array([0.0, 0.0, 2.0]),
        np.array([0.0, 0.0, 400.0]),
        None,
        f,
        1.0,
        census={"28001": 0.0, "28002": 25.0, "28003": 400.0},
    )
    reasons = {r["territory_code"]: r["null_reason"] for r in rows}
    assert reasons == {"28001": "NOT_APPLICABLE", "28002": "SOURCE_NO_COVERAGE", "28003": None}


def test_census_by_zone_adds_madrid_districts_into_the_municipio() -> None:
    people = {"28001": 0.0, "2807901": 10.0, "2807902": 5.0}
    assert census_by_zone(people, "municipio") == {"28001": 0.0, "28079": 15.0}
    assert census_by_zone(people, "distrito") == {"2807901": 10.0, "2807902": 5.0}
