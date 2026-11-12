"""Which zones a census section counts for in the commute matrix (CORE-009, D-220, D-232)."""

from hi_features.commute import origin_zones

ZONES = {
    "28079": "ES.28.MUN.28079",
    "2807920": "ES.28.DIS.2807920",
    "28001": "ES.28.MUN.28001",
}
BARRIOS = {"ES.28.BAR.28079201"}


def test_a_madrid_section_counts_for_its_district_madrid_and_its_barrio() -> None:
    zones = origin_zones("2807920001", "ES.28.BAR.28079201", ZONES, BARRIOS)
    assert zones == ["ES.28.DIS.2807920", "ES.28.MUN.28079", "ES.28.BAR.28079201"]


def test_a_section_elsewhere_counts_for_its_municipio_only() -> None:
    assert origin_zones("2800101001", "ES.28.DIS.2800101", ZONES, BARRIOS) == ["ES.28.MUN.28001"]


def test_a_parent_that_is_not_a_barrio_adds_nothing() -> None:
    zones = origin_zones("2807920001", "ES.28.DIS.2807920", ZONES, BARRIOS)
    assert zones == ["ES.28.DIS.2807920", "ES.28.MUN.28079"]
