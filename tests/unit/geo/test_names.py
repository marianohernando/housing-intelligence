"""Readable municipio names and the characters a published place name may carry."""

import pytest

from hi_domain.geo.names import display_name, invalid_name_chars


@pytest.mark.parametrize(
    ("official", "readable"),
    [
        ("MADRID", "Madrid"),
        ("ROZAS DE MADRID, LAS", "Las Rozas de Madrid"),
        ("ALAMO, EL", "El Alamo"),
        ("SAN SEBASTIAN DE LOS REYES", "San Sebastian de los Reyes"),
        ("VILLANUEVA DE LA CAÑADA", "Villanueva de la Cañada"),
        ("  TORREJON   DE ARDOZ ", "Torrejon de Ardoz"),
        ("Fuencarral-El Pardo", "Fuencarral-El Pardo"),  # districts come in mixed case
        ("Chamartín", "Chamartín"),
        # Spelling of the CM statistical tables (DATA-022): the article goes to the front.
        ("Álamo (El)", "El Álamo"),
        ("Rozas de Madrid (Las)", "Las Rozas de Madrid"),
        ("Santos de la Humosa (Los)", "Los Santos de la Humosa"),
        ("Acebeda (La) — distrito censal 01", "La Acebeda — distrito censal 01"),
        ("Griñón", "Griñón"),
        ("Piñuécar-Gandullas", "Piñuécar-Gandullas"),
    ],
)
def test_display_name(official: str, readable: str) -> None:
    assert display_name(official) == readable


@pytest.mark.parametrize(
    ("name", "bad"),
    [
        ("REDUE/A", ["/"]),
        ("GRIÐON", ["Ð"]),
        ("PI/UECAR-GANDULLAS", ["/"]),
        ("FUENTIDUEÐA DE TAJO — distrito censal 01", ["Ð"]),
        ("Tetu�n", ["�"]),  # undecoded byte
    ],
)
def test_broken_source_spellings_are_rejected(name: str, bad: list[str]) -> None:
    assert invalid_name_chars(name) == bad


@pytest.mark.parametrize(
    "name",
    [
        "Redueña",
        "Villanueva de la Cañada",
        "Álamo (El)",
        "San Blas-Canillejas",
        "Vicálvaro",
        "Argüelles",
        "Madrid — distrito censal 22",
        "Navalcarnero",
    ],
)
def test_official_spellings_are_accepted(name: str) -> None:
    assert invalid_name_chars(name) == []
