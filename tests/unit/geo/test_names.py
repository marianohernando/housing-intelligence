"""Readable municipio names and the characters a published place name may carry."""

import pytest

from hi_domain.geo.names import display_name, invalid_name_chars, match_rank, name_key


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


@pytest.mark.parametrize(
    ("typed", "key"),
    [
        ("Chamartín", "chamartin"),
        ("  FUENCARRAL-el   Pardo ", "fuencarral el pardo"),
        ("Villanueva de la Cañada", "villanueva de la canada"),
        ("San Martín de la Vega.", "san martin de la vega"),
        ("¿?", ""),
    ],
)
def test_name_key_ignores_case_accents_and_punctuation(typed: str, key: str) -> None:
    assert name_key(typed) == key


@pytest.mark.parametrize(
    ("query", "name", "rank"),
    [
        ("chamartin", "Chamartín", 0),
        ("Alcalá", "Alcalá de Henares", 1),
        ("rozas", "Las Rozas de Madrid", 2),
        ("pardo", "Fuencarral-El Pardo", 2),
        ("ozas", "Las Rozas de Madrid", 3),
        ("Getafe", "Leganés", None),
        ("", "Madrid", None),
    ],
)
def test_match_rank_orders_exact_prefix_word_and_inside(
    query: str, name: str, rank: int | None
) -> None:
    assert match_rank(query, name) == rank
