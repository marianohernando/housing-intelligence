"""indicators_by_zone: each known fit role lands in its place, an unknown is ignored (D-233)."""

import logging
from typing import Any

import pytest

from hi_api.services.search import indicators_by_zone
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
    ]
    with caplog.at_level(logging.WARNING):
        result = indicators_by_zone(rows)
    assert set(result.walk[KEY]) == {NeedKey.COLEGIO}
    assert not result.priority_walk
    assert not result.transit
    assert "something_new" in caplog.text
