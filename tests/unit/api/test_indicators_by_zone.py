"""indicators_by_zone: each known fit role lands in its place, an unknown is ignored (D-233)."""

import logging
from typing import Any

import pytest

from hi_api.services.search import indicators_by_zone, scenario_warnings, zone_price, zone_rent
from hi_contracts.public import NearbyNeed, NeedKey, PriorityKey, ScenarioState

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


def test_the_leisure_groups_land_as_walking_needs_and_ocio_has_no_feature_of_its_own(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """D-236: each group of «Ocio» is a need measured on foot, read like the colegio; the
    priority «ocio» scores those needs, so a feature bound to it would be a mistake: ignored
    with the warning of any unknown binding, never a park-like priority walk."""
    rows = [
        _row("min_a_pie_bar", {"role": "walk_minutes", "need": "bares"}),
        _row("min_a_pie_restaurante", {"role": "walk_minutes", "need": "restaurantes"}),
        _row("min_a_pie_gimnasio", {"role": "walk_minutes", "need": "gimnasios"}),
        _row("min_a_pie_cultura", {"role": "walk_minutes", "need": "cultura"}),
        _row("ocio", {"role": "walk_minutes", "priority": "ocio"}),
    ]
    with caplog.at_level(logging.WARNING):
        result = indicators_by_zone(rows)
    assert {need: v.feature_id for need, v in result.walk[KEY].items()} == {
        NeedKey.BARES: "min_a_pie_bar",
        NeedKey.RESTAURANTES: "min_a_pie_restaurante",
        NeedKey.GIMNASIOS: "min_a_pie_gimnasio",
        NeedKey.CULTURA: "min_a_pie_cultura",
    }
    assert not result.priority_walk
    assert "walk_minutes:priority=ocio" in caplog.text


def test_an_unknown_role_is_ignored_with_a_warning(caplog: pytest.LogCaptureFixture) -> None:
    rows = [
        _row("min_a_pie_colegio", {"role": "walk_minutes", "need": "colegio"}),
        _row("futuro", {"role": "something_new", "need": None, "priority": None, "mode": None}),
        _row("futuro_2", {"role": "something_new"}),
        _row("piscinas", {"role": "walk_minutes", "need": "piscinas"}),
        _row("mascotas", {"role": "walk_minutes", "priority": "mascotas"}),
        _row("tranvia", {"role": "transit_mode", "mode": "tram"}),
    ]
    with caplog.at_level(logging.WARNING):
        result = indicators_by_zone(rows)
    assert set(result.walk[KEY]) == {NeedKey.COLEGIO}
    assert not result.priority_walk
    assert not result.transit
    assert "something_new" in caplog.text
    for ignored in (
        "walk_minutes:need=piscinas",
        "walk_minutes:priority=mascotas",
        "transit_mode:mode=tram",
    ):
        assert ignored in caplog.text


ESTIMATE = {"role": "price_m2_estimate"}


def test_an_estimated_price_is_kept_apart_from_the_published_one() -> None:
    """D-234: the estimate has its own role (`price_m2_estimate`) and never overwrites the
    published row, whatever the order the rows arrive in."""
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


def test_leisure_in_nearby_without_ocio_comes_back_as_a_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """D-236: the API or the MCP may send a leisure group without the priority «ocio»; the search
    ignores it (hi_domain.fit.ignored_leisure) and the answer says so."""
    plain = ScenarioState(nearby=[NearbyNeed(need=NeedKey.COLEGIO)])
    loose = ScenarioState(nearby=[NearbyNeed(need=NeedKey.BARES), NearbyNeed(need=NeedKey.CULTURA)])
    marked = loose.model_copy(update={"priorities": [PriorityKey.OCIO]})
    assert scenario_warnings(plain) == []
    assert scenario_warnings(marked) == []
    with caplog.at_level(logging.WARNING):
        (warning,) = scenario_warnings(loose)
    assert warning.startswith("INVALID_PROFILE: nearby bares, cultura ignored")
    assert "bares, cultura" in caplog.text


FILL = {
    "role": "rent_m2_fill",
    "note": "referencia del Ministerio de Vivienda para contratos firmados en 2024",
    "source": "Ministerio de Vivienda (SERPAVI), 2024",
}
REFERENCE = {"reference_rent": {"typology": "colectiva", "quartiles": {"p25": 7.3, "p75": 10.6}}}


def _fill(value: float | None = 9.0, typology: str = "colectiva") -> dict[str, Any]:
    inputs = {"dataset_versions": {}, "reference_rent": {**REFERENCE["reference_rent"]}}
    inputs["reference_rent"]["typology"] = typology
    row = _row("alquiler_m2_mensual_referencia", FILL) | {"value": value, "inputs": inputs}
    if value is None:
        row |= {"null_reason": "SOURCE_MISSING", "confidence": 0.0}
    return row


def _cm(value: float | None) -> dict[str, Any]:
    row = _row("alquiler_m2_mensual", {"role": "rent_m2", "note": "contratos firmados en 2024"})
    if value is None:
        return row | {"value": None, "null_reason": "SOURCE_NO_COVERAGE", "confidence": 0.0}
    return row | {"value": value}


def test_the_cm_rent_wins_whatever_the_order() -> None:
    """D-242: where the CM publishes the rent it stays, as it was: no range, its own note."""
    for rows in ([_fill(), _cm(14.3)], [_cm(14.3), _fill()]):
        chosen = zone_rent(indicators_by_zone(rows), KEY)
        assert chosen.rent is not None and chosen.rent.feature_id == "alquiler_m2_mensual"
        assert chosen.note == "contratos firmados en 2024"
        assert chosen.range_m2 is None and chosen.source is None


def test_without_the_cm_rent_the_reference_fills_with_its_range_and_source() -> None:
    chosen = zone_rent(indicators_by_zone([_cm(None), _fill()]), KEY)
    assert chosen.rent is not None and chosen.rent.feature_id == "alquiler_m2_mensual_referencia"
    assert chosen.rent.value == 9.0
    assert chosen.note == FILL["note"]
    assert chosen.range_m2 == (7.3, 10.6)
    assert chosen.source == "Ministerio de Vivienda (SERPAVI), 2024"


def test_houses_say_so_in_the_note() -> None:
    chosen = zone_rent(indicators_by_zone([_fill(typology="unifamiliar")]), KEY)
    assert chosen.note is not None and chosen.note.startswith("precio de casas unifamiliares")


def test_with_neither_the_cm_row_says_why() -> None:
    """The CM row's reason stays (a barrio without postcodes, D-232); no CM row at all: the
    reference's own null row; nothing: None."""
    chosen = zone_rent(indicators_by_zone([_cm(None), _fill(None)]), KEY)
    assert chosen.rent is not None and chosen.rent.feature_id == "alquiler_m2_mensual"
    assert chosen.rent.null_reason == "SOURCE_NO_COVERAGE" and chosen.range_m2 is None
    only_fill = zone_rent(indicators_by_zone([_fill(None)]), KEY)
    assert only_fill.rent is not None and only_fill.rent.value is None
    assert zone_rent(indicators_by_zone([]), KEY).rent is None


def test_the_reference_is_read_apart_and_never_as_the_cm_rent() -> None:
    """Its own role (rollback-safe, like D-234): code that does not know `rent_m2_fill` leaves
    it out with a warning; this code keeps it apart from the CM rent."""
    result = indicators_by_zone([_fill()])
    assert not result.rent
    assert result.rent_fill[KEY].feature_id == "alquiler_m2_mensual_referencia"
