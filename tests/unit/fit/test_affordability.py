"""CORE-006 budget condition: PASS / FAIL / UNKNOWN, never PASS without a known rent (D-214)
or, to buy, without a published appraised value (DATA-021, D-227)."""

from itertools import pairwise

import pytest
from hypothesis import given
from hypothesis import strategies as st

from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_contracts.public import IndicatorValue
from hi_contracts.public.scenario import Budget, BudgetKind, Household, ScenarioState
from hi_contracts.public.search import ConstraintStatus
from hi_domain.affordability import (
    MEDIAN_FLOOR_AREA_M2,
    assumed_floor_area,
    budget_check,
    monthly_rent,
    purchase_cost,
)


def _rent(value: float | None, confidence: float = 1.0) -> IndicatorValue:
    return IndicatorValue(
        feature_id="alquiler_m2_mensual",
        label="Alquiler medio por metro cuadrado",
        value=value,
        unit="EUR/m2/mes",
        confidence=confidence if value is not None else 0.0,
        null_reason=None if value is not None else NullReason.SOURCE_MISSING,
        level=TerritoryLevel.MUNICIPIO,
        datasets=["cm_alquiler_m2_municipios"],
    )


def _price(value: float | None, confidence: float = 0.8) -> IndicatorValue:
    return IndicatorValue(
        feature_id="valor_tasado_vivienda_m2",
        label="Valor tasado medio de la vivienda libre por metro cuadrado",
        value=value,
        unit="EUR/m2",
        confidence=confidence if value is not None else 0.0,
        null_reason=None if value is not None else NullReason.SOURCE_MISSING,
        level=TerritoryLevel.MUNICIPIO,
        datasets=["cm_valor_tasado_vivienda_municipios"],
    )


def _buy(amount: int) -> Budget:
    return Budget(kind=BudgetKind.BUY, amount_eur=amount)


def _scenario(adults: int = 2, minors: int = 2, area: int | None = None) -> ScenarioState:
    return ScenarioState(
        budget=Budget(kind=BudgetKind.RENT, amount_eur=1500),
        household=Household(adults=adults, minors=minors),
        min_floor_area_m2=area,
    )


def test_floor_area_follows_the_census_median_of_the_household_size() -> None:
    assert assumed_floor_area(_scenario(1, 0)).m2 == 61
    assert assumed_floor_area(_scenario(2, 2)).m2 == 77
    assert assumed_floor_area(_scenario(4, 4)).m2 == MEDIAN_FLOOR_AREA_M2[5]
    assert assumed_floor_area(_scenario(2, 2)).from_household


def test_floor_area_chosen_by_the_person_wins() -> None:
    area = assumed_floor_area(_scenario(2, 2, area=95))
    assert area.m2 == 95
    assert not area.from_household


def test_floor_area_never_shrinks_with_more_people() -> None:
    sizes = sorted(MEDIAN_FLOOR_AREA_M2)
    assert all(MEDIAN_FLOOR_AREA_M2[a] <= MEDIAN_FLOOR_AREA_M2[b] for a, b in pairwise(sizes))


def test_rent_within_budget_passes_and_explains_the_cost() -> None:
    area = assumed_floor_area(_scenario())
    check = budget_check(Budget(kind=BudgetKind.RENT, amount_eur=1500), _rent(15.1), area)
    assert check.status is ConstraintStatus.PASS
    assert check.value == pytest.approx(round(15.1 * 77))
    assert check.threshold == 1500
    assert "77 m²" in check.label
    assert "1.163 €/mes" in check.explanation


def test_rent_over_budget_fails() -> None:
    area = assumed_floor_area(_scenario())
    check = budget_check(Budget(kind=BudgetKind.RENT, amount_eur=900), _rent(15.1), area)
    assert check.status is ConstraintStatus.FAIL


def test_unknown_rent_is_unknown_never_pass() -> None:
    area = assumed_floor_area(_scenario())
    for rent in (_rent(None), None):
        check = budget_check(Budget(kind=BudgetKind.RENT, amount_eur=20_000), rent, area)
        assert check.status is ConstraintStatus.UNKNOWN
        assert check.value is None
        assert check.confidence == 0.0


@pytest.mark.parametrize("price", [None, _price(None)])
def test_purchase_without_a_published_price_is_unknown(price: IndicatorValue | None) -> None:
    area = assumed_floor_area(_scenario())
    check = budget_check(_buy(300_000), _rent(15.1), area, price)
    assert check.status is ConstraintStatus.UNKNOWN
    assert check.unit == "€"
    assert check.confidence == 0.0
    assert "Sin precio de compra publicado" in check.explanation


def test_purchase_within_budget_passes_with_the_appraised_value() -> None:
    area = assumed_floor_area(_scenario())  # 4 people: 77 m²
    check = budget_check(_buy(300_000), None, area, _price(3000.0))
    assert check.status is ConstraintStatus.PASS
    assert check.value == 231_000
    assert check.unit == "€"
    assert check.confidence == 0.8
    assert "valor tasado" in check.explanation
    assert "3.000 €/m²" in check.explanation


def test_purchase_over_budget_fails() -> None:
    area = assumed_floor_area(_scenario())
    check = budget_check(_buy(300_000), _rent(10.0), area, _price(4993.3))
    assert check.status is ConstraintStatus.FAIL
    assert check.value == 384_000  # 4.993,3 €/m² × 77 m², rounded to thousands


@given(
    st.floats(min_value=1500, max_value=9000),
    st.integers(min_value=10_000, max_value=5_000_000),
    st.integers(min_value=0, max_value=500_000),
)
def test_more_purchase_budget_never_turns_pass_into_fail(
    price_m2: float, budget: int, extra: int
) -> None:
    area = assumed_floor_area(_scenario())
    low = budget_check(_buy(budget), None, area, _price(price_m2))
    high = budget_check(_buy(min(budget + extra, 5_000_000)), None, area, _price(price_m2))
    if low.status is ConstraintStatus.PASS:
        assert high.status is ConstraintStatus.PASS


def test_purchase_state_value_and_text_agree_at_the_edge() -> None:
    """300.400 € reads as 300.000 € everywhere, so it fits a 300.000 € budget."""
    area = assumed_floor_area(_scenario())
    check = budget_check(_buy(300_000), None, area, _price(300_400 / 77))
    assert check.value == purchase_cost(300_400 / 77, 77) == 300_000
    assert check.status is ConstraintStatus.PASS
    assert "300.000 €" in check.explanation


@given(
    st.floats(min_value=5, max_value=30),
    st.integers(min_value=100, max_value=20_000),
    st.integers(min_value=0, max_value=2_000),
)
def test_more_budget_never_turns_pass_into_fail(rent_m2: float, budget: int, extra: int) -> None:
    area = assumed_floor_area(_scenario())
    low = budget_check(Budget(kind=BudgetKind.RENT, amount_eur=budget), _rent(rent_m2), area)
    high_amount = min(budget + extra, 20_000)
    high = budget_check(Budget(kind=BudgetKind.RENT, amount_eur=high_amount), _rent(rent_m2), area)
    if low.status is ConstraintStatus.PASS:
        assert high.status is ConstraintStatus.PASS


@given(st.floats(min_value=5, max_value=30), st.integers(min_value=15, max_value=400))
def test_monthly_rent_is_price_times_area(rent_m2: float, m2: int) -> None:
    assert monthly_rent(rent_m2, m2) == pytest.approx(rent_m2 * m2)


def test_state_value_and_text_agree_at_the_edge() -> None:
    """1.500,4 €/mes reads as 1.500 € everywhere, so it fits a 1.500 € budget."""
    area = assumed_floor_area(_scenario())
    check = budget_check(Budget(kind=BudgetKind.RENT, amount_eur=1500), _rent(1500.4 / 77), area)
    assert check.value == 1500
    assert check.status is ConstraintStatus.PASS
    assert "1.500 €/mes" in check.explanation


ESTIMATE_NOTE = "precio estimado: valor tasado de Madrid repartido según el valor catastral"


def test_an_estimated_purchase_price_decides_with_low_confidence_and_says_so() -> None:
    """D-234: a district's estimate gives PASS or FAIL like a published value, with its own
    confidence and the words «precio estimado» instead of the appraised-value note."""
    area = assumed_floor_area(_scenario(adults=2, minors=0))  # a couple: 68 m²
    note = f"{ESTIMATE_NOTE} del distrito; Ministerio de Vivienda y Catastro vía Ayuntamiento"
    estimate = _price(6051.0, confidence=0.5)
    fits = budget_check(_buy(450_000), None, area, estimate, price_note=note)
    assert fits.status is ConstraintStatus.PASS
    assert fits.value == 411_000
    assert fits.confidence == 0.5
    assert fits.explanation == (
        "Comprar ≈ 411.000 € por 68 m² (6.051 €/m², precio estimado: valor tasado de Madrid "
        "repartido según el valor catastral del distrito; Ministerio de Vivienda y Catastro vía "
        "Ayuntamiento)"
    )
    assert "valor tasado medio de la vivienda libre" not in fits.explanation
    too_low = budget_check(_buy(400_000), None, area, estimate, price_note=note)
    assert too_low.status is ConstraintStatus.FAIL


def test_the_unknown_purchase_text_no_longer_blames_districts_and_barrios() -> None:
    area = assumed_floor_area(_scenario())
    check = budget_check(_buy(300_000), None, area, None)
    assert check.status is ConstraintStatus.UNKNOWN
    assert "distritos" not in check.explanation
    assert "25.000 habitantes" in check.explanation
