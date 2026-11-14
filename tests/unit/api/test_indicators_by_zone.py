"""indicators_by_zone: each known fit role lands in its place, an unknown is ignored (D-233)."""

import logging
from typing import Any

import pytest

from hi_api.services.search import indicators_by_zone, zone_price
from hi_contracts.public import NeedKey, PriorityKey

KEY = ("distrito", "2807910")


def _row(feature_id: str, fit: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "feature_id": feature_id,
        "territory_level": "distrito",
        "territory_code": "2807910",
        "value": 4.0,
        "null_reason": None,
        "confidence": 0.9,
        "inputs": {"dataset_versions": {}},
        "human_name": feature_id,
        "unit": "min",
        "fit": fit,
    }


def test_every_known_role_lands_in_its_place() -> None:
    result = indicators_by_zone(
        [
            _row("alquiler_m2_mensual", {"role": "rent_m2", "note": "contratos de 2024"}),
            _row("valor_tasado_vivienda_m2", {"role": "price_m2"}),
            _row("min_a_pie_colegio", {"role": "walk_minutes", "need": "colegio"}),
            _row("min_a_pie_parque", {"role": "walk_minutes", "priority": "zonas_verdes"}),
            _row("min_a_pie_bus", {"role": "transit_mode", "mode": "bus", "need": None}),
            _row("min_a_pie_metro", {"role": "transit_mode", "mode": "metro"}),
        ]
    )
    assert result.rent[KEY].feature_id == "alquiler_m2_mensual"
    assert result.rent_note == "contratos de 2024"
    assert result.price[KEY].feature_id == "valor_tasado_vivienda_m2"
    assert result.walk[KEY][NeedKey.COLEGIO].feature_id == "min_a_pie_colegio"
    assert result.priority_walk[KEY][PriorityKey.ZONAS_VERDES].feature_id == "min_a_pie_parque"
    assert {m: v.feature_id for m, v in result.transit[KEY].items()} == {
        "bus": "min_a_pie_bus",
        "metro": "min_a_pie_metro",
    }
    assert NeedKey.TRANSPORTE not in result.walk.get(KEY, {})


def test_an_unknown_role_is_ignored_with_a_warning(caplog: pytest.LogCaptureFixture) -> None:
    rows = [
        _row("min_a_pie_colegio", {"role": "walk_minutes", "need": "colegio"}),
        _row("futuro", {"role": "something_new", "need": None, "priority": None, "mode": None}),
        _row("futuro_2", {"role": "something_new"}),
        _row("bares", {"role": "walk_minutes", "need": "bares"}),
        _row("ocio", {"role": "walk_minutes", "priority": "ocio"}),
        _row("tranvia", {"role": "transit_mode", "mode": "tram"}),
    ]
    with caplog.at_level(logging.WARNING):
        result = indicators_by_zone(rows)
    assert set(result.walk[KEY]) == {NeedKey.COLEGIO}
    assert not result.priority_walk
    assert not result.transit
    assert "something_new" in caplog.text
    for ignored in (
        "walk_minutes:need=bares",
        "walk_minutes:priority=ocio",
        "transit_mode:mode=tram",
    ):
        assert ignored in caplog.text


ESTIMATE = {"role": "price_m2", "estimate": True}


def test_an_estimated_price_is_kept_apart_from_the_published_one() -> None:
    """D-234: both features bind `price_m2`; the estimate never overwrites the published row,
    whatever the order the rows arrive in."""
    published = _row("valor_tasado_vivienda_m2", {"role": "price_m2"})
    estimate = _row("precio_compra_estimado_m2", ESTIMATE)
    for rows in ([estimate, published], [published, estimate]):
        result = indicators_by_zone(rows)
        assert result.price[KEY].feature_id == "valor_tasado_vivienda_m2"
        assert result.price_estimate[KEY].feature_id == "precio_compra_estimado_m2"


def test_a_zone_takes_the_published_price_and_only_then_the_estimate() -> None:
    missing = _row("valor_tasado_vivienda_m2", {"role": "price_m2"}) | {
        "value": None,
        "null_reason": "SOURCE_MISSING",
        "confidence": 0.0,
    }
    estimate = _row("precio_compra_estimado_m2", ESTIMATE) | {"value": 6051.0, "confidence": 0.5}
    price, estimated = zone_price(indicators_by_zone([missing, estimate]), KEY)
    assert price is not None and price.value == 6051.0 and estimated
    assert price.feature_id == "precio_compra_estimado_m2"

    published = _row("valor_tasado_vivienda_m2", {"role": "price_m2"}) | {"value": 4993.0}
    price, estimated = zone_price(indicators_by_zone([published, estimate]), KEY)
    assert price is not None and price.value == 4993.0 and not estimated


def test_without_the_estimate_in_the_data_a_district_is_unknown_as_before() -> None:
    """New code on old data: only the SOURCE_MISSING row of the published feature."""
    missing = _row("valor_tasado_vivienda_m2", {"role": "price_m2"}) | {
        "value": None,
        "null_reason": "SOURCE_MISSING",
        "confidence": 0.0,
    }
    price, estimated = zone_price(indicators_by_zone([missing]), KEY)
    assert price is not None and price.value is None and not estimated
    assert zone_price(indicators_by_zone([]), KEY) == (None, False)
