"""Readable municipio names from the official uppercase spelling."""

import pytest

from hi_domain.geo.names import display_name


@pytest.mark.parametrize(
    ("official", "readable"),
    [
        ("MADRID", "Madrid"),
        ("ROZAS DE MADRID, LAS", "Las Rozas de Madrid"),
        ("ALAMO, EL", "El Alamo"),
        ("SAN SEBASTIAN DE LOS REYES", "San Sebastian de los Reyes"),
        ("VILLANUEVA DE LA CAÑADA", "Villanueva de la Cañada"),
        ("  TORREJON   DE ARDOZ ", "Torrejon de Ardoz"),
    ],
)
def test_display_name(official: str, readable: str) -> None:
    assert display_name(official) == readable
