"""Viability v0 (D-248): the residual method on cases worked out by hand, one that works
(«sale»), one to adjust («ajustar») and one that does not («no sale»), with and without a land
price, the three scenarios and the demand check."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from hi_domain.viability import (
    ADJUST_FLOOR,
    APPRAISAL_MIN_MARGIN,
    COST_COEFFICIENT,
    COST_PARTS,
    ICIO_RATE,
    SALES_COSTS_SHARE,
    SCENARIOS,
    TARGET_MARGIN,
    DemandInputs,
    ScenarioResult,
    Verdict,
    ViabilityInputs,
    YieldLand,
    break_even,
    demand_check,
    monthly_payment,
    rough_money,
    viability,
)
from hi_domain.viability_data import (
    CRG_BLOQUE_ABIERTO_HIGH,
    CRG_BLOQUE_ABIERTO_LOW,
    CRG_YEAR,
    PEM_EUR_M2,
    PEM_PREVIOUS_EUR_M2,
    PEM_YEAR,
    REFERENCE_PEM_EUR_M2,
    ST_EUR_M2,
)

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
    "adjust_floor": 0.15,
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
    # Pessimistic (D-252: +15 % cost): 3.600.000 − (1.035.000 + 360.000 + 1.800.000) = 405.000,
    # 11,25 %: under the 15 % floor
    assert worst.margin == pytest.approx(0.1125)
    assert worst.verdict is Verdict.NO_SALE
    # The most the land can cost for 20 %: 3.200.000 − 900.000 − 400.000
    assert base.residual_land_value == pytest.approx(1_900_000)
    assert base.residual_land_value_m2 == pytest.approx(1900)


def test_ajustar_with_land() -> None:
    """Land 2.000.000: 4.000.000 − 3.300.000 = 700.000, 17,5 %: between the 15 % and the 20 %."""
    base = _run(land_eur=2_000_000)["base"]
    assert base.margin == pytest.approx(0.175)
    assert base.verdict is Verdict.AJUSTAR
    assert base.headline == "Ajustar: margen del 17,5 %, por debajo del 20 % objetivo."
    # D-252: 12,5 % is no longer «ajustar»: under the 15 % (the appraisal asks 18 %)
    low = _run(land_eur=2_200_000)["base"]
    assert low.margin == pytest.approx(0.125)
    assert low.verdict is Verdict.NO_SALE
    assert low.headline == "No sale: margen del 12,5 %, por debajo del 15 %."


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
        "Lo máximo que se puede pagar por el suelo, antes de financiación, impuestos de compra "
        "del suelo, urbanización y derribo: unos 1,9 millones de € (unos 1.900 € por m² "
        "edificable), para un margen del 20 %."
    )
    # Optimistic: 4.400.000 × 0,8 − 855.000 − 440.000
    # Pessimistic: 3.600.000 × 0,8 − 1.035.000 − 360.000
    assert runs["optimista"].residual_land_value == pytest.approx(2_225_000)
    assert runs["pesimista"].residual_land_value == pytest.approx(1_485_000)
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


def test_verdict_edges_at_exactly_20_and_15_percent() -> None:
    at_target = _edges(1_800_000)  # 800.000 / 4.000.000 = 20 %
    assert at_target.margin == 0.2
    assert at_target.verdict is Verdict.SALE
    at_floor = _edges(2_000_000)  # 600.000 / 4.000.000 = 15 % (D-252)
    assert at_floor.margin == 0.15
    assert at_floor.verdict is Verdict.AJUSTAR


def test_no_sale_with_a_small_positive_margin() -> None:
    small = _edges(2_400_000)  # 200.000 / 4.000.000 = 5 %
    assert small.margin == pytest.approx(0.05)
    assert small.verdict is Verdict.NO_SALE
    assert small.headline == "No sale: margen del 5,0 %, por debajo del 15 %."


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
    # D-252: the ICIO of Madrid is 3,75 % since 2024, so k = 1 + 0,19 + 0,08 + 0,0475 + 0,04
    assert pytest.approx(1.3575) == COST_COEFFICIENT
    assert sum(p.share for p in COST_PARTS) == pytest.approx(COST_COEFFICIENT - 1)
    assert pytest.approx(ICIO_RATE + 0.01) == COST_PARTS[2].share
    assert (
        "3,75 %" in COST_PARTS[2].source
        and "ordenanza fiscal del ICIO, art. 25" in COST_PARTS[2].source
    )
    assert "Libro de Ordenanzas Fiscales 2024, p. 154)" in COST_PARTS[2].source
    assert "vigente" not in COST_PARTS[2].source  # only what was verified (2024)
    assert pytest.approx(0.08) == SALES_COSTS_SHARE
    # D-252 (D8): «ajustar» from 15 %, under the 18 % the appraisal asks (ECO/805/2003, DA 6.ª)
    assert (TARGET_MARGIN, ADJUST_FLOOR, APPRAISAL_MIN_MARGIN) == (0.20, 0.15, 0.18)
    assert ADJUST_FLOOR < APPRAISAL_MIN_MARGIN < TARGET_MARGIN
    assert [(s.key, s.price_factor, s.cost_factor) for s in SCENARIOS] == [
        ("base", 1.0, 1.0),
        ("optimista", 1.10, 0.95),
        ("pesimista", 0.90, 1.15),
    ]
    assert all(p.source for p in COST_PARTS)


@pytest.mark.parametrize(
    ("amount", "words"),
    [
        (66_958_000, "unos 67 millones de €"),
        (140_490_000, "unos 140 millones de €"),
        (1_234_567, "unos 1,23 millones de €"),
        (12_345_678, "unos 12,3 millones de €"),
        (900_091, "unos 900.000 €"),
        (4_297.4, "unos 4.300 €"),
        (1_002_000, "alrededor de 1 millón de €"),  # review of #109, R-10
    ],
)
def test_the_residual_is_said_with_three_figures(amount: float, words: str) -> None:
    assert rough_money(amount) == words


def test_the_reference_pem_is_the_midpoint_of_the_crg() -> None:
    """costes_referencia_construccion.yaml: bloque abierto, área 1, 871–1.064 €/m² (2022)."""
    assert (CRG_YEAR, CRG_BLOQUE_ABIERTO_LOW, CRG_BLOQUE_ABIERTO_HIGH) == (2022, 871, 1064)
    assert REFERENCE_PEM_EUR_M2 == 968
    assert PEM_EUR_M2 < REFERENCE_PEM_EUR_M2 < ST_EUR_M2


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


# --- D-252: how much the construction can cost for the target margin ---


def test_break_even_with_free_land_is_the_most_the_construction_can_cost() -> None:
    # 4.000.000 × 0,8 − 400.000 = 2.800.000 for the construction: 2.800 €/m² built
    even = break_even(_inputs())
    assert even.construction_m2 == pytest.approx(2800)
    assert even.pem_m2 == pytest.approx(2800 / 1.5)
    assert even.coefficient == pytest.approx(2800 / 600)
    assert even.current_construction_m2 == pytest.approx(900)
    assert not even.land_counted and even.reachable


def test_break_even_with_a_land_price() -> None:
    # The same less 2.200.000 of land: 600 €/m², under the 900 of the inputs (the 12,5 % margin)
    even = break_even(_inputs(land_eur=2_200_000))
    assert even.construction_m2 == pytest.approx(600)
    assert even.pem_m2 == pytest.approx(400)
    assert even.coefficient == pytest.approx(1.0)
    assert even.land_counted and even.reachable


def test_break_even_by_scenario_is_in_the_inputs_cost_terms() -> None:
    # Optimistic: 4.400.000 × 0,8 − 440.000 − 2.200.000 = 880.000, over 1.000 m² × 0,95
    runs = _run(land_eur=2_200_000)
    even = runs["optimista"].break_even
    assert even is not None and even.construction_m2 == pytest.approx(880_000 / 950)
    assert runs["base"].break_even == break_even(_inputs(land_eur=2_200_000))


def test_break_even_not_reachable_when_the_land_alone_eats_the_room() -> None:
    even = break_even(_inputs(land_eur=5_000_000))
    assert even.construction_m2 < 0 and not even.reachable


@given(
    price=st.floats(min_value=1500, max_value=12_000),
    land=st.one_of(st.none(), st.floats(min_value=0, max_value=3_000_000)),
)
def test_at_the_break_even_cost_the_margin_is_the_target(price: float, land: float | None) -> None:
    even = break_even(_inputs(sale_price_m2=price, land_eur=land))
    if not even.reachable:
        return
    at = _run(sale_price_m2=price, land_eur=0.0 if land is None else land, pem_m2=even.pem_m2)
    margin = at["base"].margin
    assert margin is not None and margin == pytest.approx(CASE["target_margin"], abs=1e-9)
