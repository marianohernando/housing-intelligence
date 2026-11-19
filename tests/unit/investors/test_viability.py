"""Viability v0 (D-248): the residual method on cases worked out by hand, one that works
(«sale»), one to adjust («ajustar») and one that does not («no sale»), with and without a land
price, the three scenarios and the demand check."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from hi_domain.viability import (
    ADJUST_FLOOR,
    COST_COEFFICIENT,
    COST_PARTS,
    SALES_COSTS_SHARE,
    SCENARIOS,
    TARGET_MARGIN,
    DemandInputs,
    ScenarioResult,
    Verdict,
    ViabilityInputs,
    YieldLand,
    demand_check,
    monthly_payment,
    viability,
)
from hi_domain.viability_data import PEM_EUR_M2, PEM_PREVIOUS_EUR_M2, PEM_YEAR

# 1.000 m² at 4.000 €/m², PEM 600 × 1,5 and 10 % of sales costs:
# revenue 4.000.000, construction 900.000, sales costs 400.000 (base scenario)
CASE: dict[str, float | None] = {
    "buildable_m2": 1000.0,
    "sale_price_m2": 4000.0,
    "new_build_premium": 0.0,
    "rent_m2_month": 15.0,
    "pem_m2": 600.0,
    "cost_coefficient": 1.5,
    "sales_costs_share": 0.10,
    "target_margin": 0.20,
    "adjust_floor": 0.10,
}


def _inputs(**changes: float | None) -> ViabilityInputs:
    values = CASE | changes
    return ViabilityInputs(
        buildable_m2=values["buildable_m2"] or 0.0,
        sale_price_m2=values["sale_price_m2"] or 0.0,
        new_build_premium=values["new_build_premium"] or 0.0,
        rent_m2_month=values["rent_m2_month"],
        pem_m2=values["pem_m2"] or 0.0,
        cost_coefficient=values["cost_coefficient"] or 0.0,
        land_eur=values.get("land_eur"),
        sales_costs_share=values["sales_costs_share"] or 0.0,
        target_margin=values["target_margin"] or 0.0,
        adjust_floor=values["adjust_floor"] or 0.0,
    )


def _run(**changes: float | None) -> dict[str, ScenarioResult]:
    return {s.scenario.key: s for s in viability(_inputs(**changes)).scenarios}


def test_sale_with_land_and_its_three_scenarios() -> None:
    """Land 1.800.000: base 4.000.000 − (900.000 + 400.000 + 1.800.000) = 900.000, 22,5 %."""
    runs = _run(land_eur=1_800_000)
    base, best, worst = runs["base"], runs["optimista"], runs["pesimista"]
    assert base.revenue == pytest.approx(4_000_000)
    assert base.construction == pytest.approx(900_000)
    assert base.sales_costs == pytest.approx(400_000)
    assert base.total_cost == pytest.approx(3_100_000)
    assert base.profit == pytest.approx(900_000)
    assert base.margin == pytest.approx(0.225)
    assert base.verdict is Verdict.SALE
    assert base.headline == "Sale: margen del 22,5 % sobre ventas (objetivo, 20 %)."
    # Optimistic: 4.400.000 − (855.000 + 440.000 + 1.800.000) = 1.305.000
    assert best.margin == pytest.approx(1_305_000 / 4_400_000)
    assert best.verdict is Verdict.SALE
    # Pessimistic: 3.600.000 − (945.000 + 360.000 + 1.800.000) = 495.000, 13,75 %
    assert worst.margin == pytest.approx(0.1375)
    assert worst.verdict is Verdict.AJUSTAR
    # The most the land can cost for 20 %: 3.200.000 − 900.000 − 400.000
    assert base.residual_land_value == pytest.approx(1_900_000)
    assert base.residual_land_value_m2 == pytest.approx(1900)


def test_ajustar_with_land() -> None:
    """Land 2.200.000: 4.000.000 − 3.500.000 = 500.000, 12,5 %: between the 10 % and the 20 %."""
    base = _run(land_eur=2_200_000)["base"]
    assert base.margin == pytest.approx(0.125)
    assert base.verdict is Verdict.AJUSTAR
    assert base.headline == "Ajustar: margen del 12,5 %, por debajo del 20 % objetivo."


def test_no_sale_with_land() -> None:
    """Land 2.800.000: 4.000.000 − 4.100.000 = −100.000, a loss."""
    base = _run(land_eur=2_800_000)["base"]
    assert base.profit == pytest.approx(-100_000)
    assert base.margin == pytest.approx(-0.025)
    assert base.verdict is Verdict.NO_SALE
    assert base.headline == "No sale: pierde el 2,5 % de lo que vende."


def test_without_land_there_is_no_verdict_but_the_residual_land_value() -> None:
    runs = _run(land_eur=None)
    for result in runs.values():
        assert result.verdict is None
        assert result.total_cost is None and result.margin is None and result.profit is None
    assert runs["base"].headline == (
        "Lo máximo que se puede pagar por el suelo: 1,90 millones de € (1.900 € por m² "
        "edificable), para un margen del 20 %."
    )
    # Optimistic: 4.400.000 × 0,8 − 855.000 − 440.000
    # Pessimistic: 3.600.000 × 0,8 − 945.000 − 360.000
    assert runs["optimista"].residual_land_value == pytest.approx(2_225_000)
    assert runs["pesimista"].residual_land_value == pytest.approx(1_575_000)
    # PEM 2.000: construction 3.000.000; free land leaves 600.000, 15 %: under the 20 %
    short = _run(land_eur=None, pem_m2=2000.0)["base"]
    assert short.residual_land_value == pytest.approx(-200_000)
    assert short.verdict is None
    assert short.headline == (
        "Ni con el suelo gratis se llega al margen objetivo del 20 %: se queda en el 15,0 %."
    )


def test_rental_yield_never_leaves_out_the_land() -> None:
    """With a price, rent over construction and land; without one, the land at its residual
    value (the most the target margin allows); never over construction alone."""
    with_land = _run(land_eur=1_800_000)["base"]
    assert with_land.annual_rent == pytest.approx(180_000)  # 1.000 m² × 15 € × 12
    assert with_land.rental_yield == pytest.approx(180_000 / 2_700_000)
    assert with_land.yield_land is YieldLand.PRECIO
    without = _run(land_eur=None)["base"]
    # Residual land value 1.900.000: 180.000 / (900.000 + 1.900.000)
    assert without.rental_yield == pytest.approx(180_000 / 2_800_000)
    assert without.yield_land is YieldLand.VALOR_RESIDUAL
    # Not even free land reaches the target: no land value to count, no yield
    short = _run(land_eur=None, pem_m2=2000.0)["base"]
    assert short.rental_yield is None and short.yield_land is None
    assert _run(rent_m2_month=None)["base"].rental_yield is None


def _edges(land: float, **changes: float) -> ScenarioResult:
    """Exact figures: 1.000 m² at 4.000 €/m², construction 900.000 and sales costs 12,5 %
    (500.000), so revenue minus both is 2.600.000 and the margins are exact."""
    return _run(land_eur=land, sales_costs_share=0.125, **changes)["base"]


def test_verdict_edges_at_exactly_20_and_10_percent() -> None:
    at_target = _edges(1_800_000)  # 800.000 / 4.000.000 = 20 %
    assert at_target.margin == 0.2
    assert at_target.verdict is Verdict.SALE
    at_floor = _edges(2_200_000)  # 400.000 / 4.000.000 = 10 %
    assert at_floor.margin == 0.1
    assert at_floor.verdict is Verdict.AJUSTAR


def test_no_sale_with_a_small_positive_margin() -> None:
    small = _edges(2_400_000)  # 200.000 / 4.000.000 = 5 %
    assert small.margin == pytest.approx(0.05)
    assert small.verdict is Verdict.NO_SALE
    assert small.headline == "No sale: margen del 5,0 %, por debajo del 10 %."


def test_the_ajustar_floor_never_rises_above_the_target() -> None:
    """A target of 5 % leaves no «ajustar» band: 6 % works, 4 % does not (never a 422)."""
    assert _edges(2_360_000, target_margin=0.05).verdict is Verdict.SALE  # 6 %
    low = _edges(2_440_000, target_margin=0.05)  # 4 %
    assert low.verdict is Verdict.NO_SALE
    assert low.headline == "No sale: margen del 4,0 %, por debajo del 5 %."


def test_the_new_build_premium_raises_the_revenue() -> None:
    base = _run(new_build_premium=0.10, land_eur=None)["base"]
    assert base.revenue == pytest.approx(4_400_000)


def test_defaults_are_documented_assumptions() -> None:
    assert pytest.approx(1.36) == COST_COEFFICIENT
    assert sum(p.share for p in COST_PARTS) == pytest.approx(COST_COEFFICIENT - 1)
    assert pytest.approx(0.08) == SALES_COSTS_SHARE
    assert (TARGET_MARGIN, ADJUST_FLOOR) == (0.20, 0.10)
    assert [s.key for s in SCENARIOS] == ["base", "optimista", "pesimista"]
    assert all(p.source for p in COST_PARTS)


def test_pem_is_the_one_recomputed_from_the_permits() -> None:
    """data/catalog/manual/pem_visados_cm.yaml: 644 €/m² in 2025, 634 in 2024 (homes in blocks)."""
    assert (PEM_YEAR, PEM_EUR_M2, PEM_PREVIOUS_EUR_M2) == (2025, 644, 634)


@pytest.mark.parametrize(
    "change",
    [{"buildable_m2": 0.0}, {"sale_price_m2": -1.0}, {"cost_coefficient": 0.9}],
)
def test_impossible_inputs_are_refused(change: dict[str, float]) -> None:
    with pytest.raises(ValueError, match=r"positive|coefficient"):
        viability(_inputs(**change))


@given(
    land=st.floats(min_value=0, max_value=1e7),
    price=st.floats(min_value=1000, max_value=12000),
)
def test_scenarios_keep_their_order(land: float, price: float) -> None:
    """The optimistic margin is never below the base, nor the base below the pessimistic."""
    runs = _run(land_eur=land, sale_price_m2=price)
    best, base, worst = (runs[k].margin for k in ("optimista", "base", "pesimista"))
    assert best is not None and base is not None and worst is not None
    assert best >= base - 1e-12 >= worst - 2e-12


def test_monthly_payment_french_amortisation() -> None:
    """320.000 € at 3 % in 30 years: 1.349,13 € a month (any mortgage calculator)."""
    assert monthly_payment(320_000, 0.03, 30) == pytest.approx(1349.13, abs=0.01)
    assert monthly_payment(120_000, 0.0, 10) == pytest.approx(1000)


def test_demand_check_with_the_mean_income() -> None:
    """80 m² at 5.000 €/m²: 400.000 €, 320.000 of loan, 1.349 € a month; 40.000 € a year."""
    check = demand_check(
        DemandInputs(household_income_year=40_000, sale_price_m2=5000, rent_m2_month=15)
    )
    assert check.home_price == pytest.approx(400_000)
    assert check.down_payment == pytest.approx(80_000)
    assert check.down_payment_years == pytest.approx(2.0)
    assert check.purchase_effort == pytest.approx(1349.13 * 12 / 40_000, rel=1e-4)
    assert not check.purchase_within
    assert check.monthly_rent == pytest.approx(1200)
    assert check.rent_effort == pytest.approx(0.36)
    assert check.rent_within is False
    assert check.threshold == 0.30
    assert check.lines[1] == (
        "La cuota de la hipoteca (1.349 € al mes) sería el 40 % de la renta media de los "
        "hogares del barrio: por encima del 30 %."
    )
    assert check.lines[-2] == (
        "Solo cuenta la cuota o el alquiler, sin gastos ni suministros: la cuenta es optimista."
    )
    assert check.lines[-1].startswith("Es la renta media")


def test_demand_check_without_rent() -> None:
    check = demand_check(
        DemandInputs(household_income_year=90_000, sale_price_m2=3000, rent_m2_month=None)
    )
    assert check.purchase_within
    assert check.rent_effort is None and check.rent_within is None
    assert not any(line.startswith("El alquiler") for line in check.lines)
