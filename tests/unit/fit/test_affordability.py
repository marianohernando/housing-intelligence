"""CORE-006 budget condition: PASS / FAIL / UNKNOWN, never PASS without a known rent (D-214)."""

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


def test_purchase_is_declared_without_data() -> None:
    area = assumed_floor_area(_scenario())
    check = budget_check(Budget(kind=BudgetKind.BUY, amount_eur=300_000), _rent(15.1), area)
    assert check.status is ConstraintStatus.UNKNOWN
    assert check.unit == "€"
    assert "Sin datos" in check.explanation


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
