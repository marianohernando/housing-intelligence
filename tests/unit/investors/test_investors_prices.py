"""The barrio's sale price is an estimate (D-234: the city's appraised value shared out by the
cadastral value), so the sheet and the calculator mark it «estimación», never «dato». No
database."""

from datetime import date
from typing import Any

from hi_api.services.investors import (
    BARRIO,
    PRICE,
    Place,
    Sources,
    defaults_block,
    pem_value,
    prices_block,
    sourced,
)
from hi_contracts.pro.investors import ValueMark

PLACE = Place("28079164", "2807916")


def _price(value: float | None) -> dict[str, Any]:
    return {
        "feature_id": PRICE,
        "territory_level": BARRIO.value,
        "territory_code": PLACE.code,
        "value": value,
        "null_reason": None if value is not None else "SOURCE_NO_COVERAGE",
        "confidence": 0.5,
        "period_start": date(2025, 1, 1),
        "inputs": {"dataset_versions": {}},
        "unit": "EUR/m2",
    }


def test_the_estimated_sale_price_is_marked_as_an_estimate() -> None:
    values = {(PRICE, BARRIO.value, PLACE.code): _price(5123.0)}
    prices = prices_block(values, PLACE, Sources({}))
    assert prices.sale_m2.value == 5123.0
    assert prices.sale_m2.confidence == 0.5
    assert prices.sale_m2.mark is ValueMark.ESTIMACION
    assert prices.new_build_sale_m2.mark is ValueMark.ESTIMACION  # the same estimate, plus
    none = sourced(None, Sources({}), "€/hogar/año")
    defaults = defaults_block(prices, none, pem_value({}, Sources({})))
    assert defaults.sale_price_m2.mark is ValueMark.ESTIMACION
    assert defaults.pem_permits_m2 is not None
    assert defaults.pem_permits_m2.mark is ValueMark.DATO  # a published figure stays «dato»


def test_a_missing_price_is_still_an_estimate_with_its_reason() -> None:
    prices = prices_block({}, PLACE, Sources({}))
    assert prices.sale_m2.value is None and prices.sale_m2.null_reason is not None
    assert prices.sale_m2.mark is ValueMark.ESTIMACION
