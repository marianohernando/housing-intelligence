"""Postcodes read from place addresses (CORE-006): five digits, first declared key wins."""

from hi_features.loaders import postcode_from_address as _postcode

KEYS = ["cdpostal", "direccion_codigo_postal"]


def test_postcode_is_padded_to_five_digits() -> None:
    assert _postcode({"cdpostal": "8001"}, KEYS) == "08001"
    assert _postcode({"cdpostal": " 28013 "}, KEYS) == "28013"


def test_first_declared_key_wins() -> None:
    attributes = {"cdpostal": "28013", "direccion_codigo_postal": "28046"}
    assert _postcode(attributes, KEYS) == "28013"
    assert _postcode({"direccion_codigo_postal": "28046"}, KEYS) == "28046"


def test_malformed_postcodes_are_ignored_not_guessed() -> None:
    assert _postcode({"cdpostal": "280 13"}, KEYS) is None
    assert _postcode({"cdpostal": "280130"}, KEYS) is None
    assert _postcode({"cdpostal": None, "direccion_codigo_postal": ""}, KEYS) is None
    assert _postcode({}, KEYS) is None
