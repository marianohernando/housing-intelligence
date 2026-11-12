"""Affordability (CORE-006, D-214): what a home for the household costs in a zone, and the
budget condition PASS / FAIL / UNKNOWN. UNKNOWN never counts as PASS (CLAUDE.md §14).

Rent: the zone's published rent per m² (feature `alquiler_m2_mensual`) times the floor area
the household needs. Unless the person sets it, that area is the median useful floor area of
the homes of households of the same size in the Comunidad de Madrid (Censo de Población y
Viviendas 2021, INE table 59524). Purchase (DATA-021, D-227): the zone's mean appraised value
per m² of free-market housing (feature `valor_tasado_vivienda_m2`, Ministerio de Vivienda via
the CM portal) times the same area; only municipios of more than 25.000 inhabitants have it,
so everywhere else the condition is UNKNOWN and says so.
"""

from typing import NamedTuple

from hi_contracts.public import (
    Budget,
    BudgetKind,
    ConstraintCheck,
    ConstraintStatus,
    IndicatorValue,
    ScenarioState,
)
from hi_domain.gaps import es_number

# Median useful floor area (m²) of the main dwellings of households of each size in the
# Comunidad de Madrid, interpolated inside the INE size bands; 5 means 5 or more people.
# Censo 2021, INE table 59524 (2.532.510 households with known area). D-214.
MEDIAN_FLOOR_AREA_M2: dict[int, int] = {1: 61, 2: 68, 3: 71, 4: 77, 5: 77}
FLOOR_AREA_SOURCE = (
    "superficie útil mediana de las viviendas de los hogares de ese tamaño en la Comunidad "
    "de Madrid (Censo 2021, INE)"
)
# What the rent figure is when the data does not say (its feature's `fit.note`, D-228): the
# mean of the leases in force, as in the rent feature before version 3.
RENT_NOTE = "media de los contratos vigentes; uno nuevo suele costar más"
PURCHASE_NOTE = "valor tasado medio de la vivienda libre, no el precio de un anuncio"
PURCHASE_ROUND_EUR = 1000  # an appraised mean is no more precise than this
BUDGET_ID = "budget"


class FloorArea(NamedTuple):
    m2: int
    from_household: bool  # False when the person chose it


def assumed_floor_area(scenario: ScenarioState) -> FloorArea:
    if scenario.min_floor_area_m2 is not None:
        return FloorArea(scenario.min_floor_area_m2, from_household=False)
    people = min(max(scenario.household.people, 1), max(MEDIAN_FLOOR_AREA_M2))
    return FloorArea(MEDIAN_FLOOR_AREA_M2[people], from_household=True)


def monthly_rent(rent_m2: float, area_m2: int) -> float:
    return rent_m2 * area_m2


def euros(value: float) -> str:
    return f"{es_number(round(value), 0)} €"


def budget_label(budget: Budget, area: FloorArea) -> str:
    if budget.kind is BudgetKind.BUY:
        return f"Compra hasta {euros(budget.amount_eur)}"
    return f"Alquiler hasta {euros(budget.amount_eur)}/mes para {area.m2} m²"


def rent_explanation(rent_m2: float, area: FloorArea, note: str | None = None) -> str:
    """«Alquiler ≈ 1.270 €/mes por 77 m² (16,5 €/m², contratos firmados en 2024; …)»; without a
    note from the data, the old mean of the leases in force."""
    cost = monthly_rent(rent_m2, area.m2)
    head = "Alquiler medio" if note is None else "Alquiler"
    return (
        f"{head} ≈ {euros(cost)}/mes por {area.m2} m² "
        f"({es_number(rent_m2, 1)} €/m², {note or RENT_NOTE})"
    )


def purchase_cost(price_m2: float, area_m2: int) -> int:
    """Appraised value per m² times the area, rounded to thousands: the state, the value and
    the text use this one number."""
    return round(price_m2 * area_m2 / PURCHASE_ROUND_EUR) * PURCHASE_ROUND_EUR


def purchase_explanation(price_m2: float, area: FloorArea) -> str:
    cost = purchase_cost(price_m2, area.m2)
    return (
        f"Comprar ≈ {euros(cost)} por {area.m2} m² ({es_number(price_m2, 0)} €/m², {PURCHASE_NOTE})"
    )


def _purchase_check(
    budget: Budget, price: IndicatorValue | None, area: FloorArea
) -> ConstraintCheck:
    base = {
        "constraint_id": BUDGET_ID,
        "label": budget_label(budget, area),
        "threshold": float(budget.amount_eur),
        "unit": "€",
    }
    if price is None or price.value is None:
        return ConstraintCheck(
            **base,
            status=ConstraintStatus.UNKNOWN,
            confidence=0.0,
            explanation=(
                "Sin precio de compra publicado para esta zona: el valor tasado del Ministerio de "
                "Vivienda solo llega a los municipios de más de 25.000 habitantes con tasaciones "
                "suficientes, no a los distritos ni a los pueblos"
            ),
        )
    cost = purchase_cost(price.value, area.m2)
    return ConstraintCheck(
        **base,
        status=ConstraintStatus.PASS if cost <= budget.amount_eur else ConstraintStatus.FAIL,
        value=float(cost),
        confidence=price.confidence,
        explanation=purchase_explanation(price.value, area),
    )


def budget_check(
    budget: Budget,
    rent: IndicatorValue | None,
    area: FloorArea,
    price: IndicatorValue | None = None,
    rent_note: str | None = None,
) -> ConstraintCheck:
    if budget.kind is BudgetKind.BUY:
        return _purchase_check(budget, price, area)
    if rent is None or rent.value is None:
        return ConstraintCheck(
            constraint_id=BUDGET_ID,
            label=budget_label(budget, area),
            status=ConstraintStatus.UNKNOWN,
            threshold=float(budget.amount_eur),
            unit="€/mes",
            confidence=0.0,
            explanation=(
                "Sin datos de alquiler para esta zona: la fuente solo publica las zonas con "
                "contratos suficientes"
            ),
        )
    cost = round(monthly_rent(rent.value, area.m2))  # the state, value and text use one number
    return ConstraintCheck(
        constraint_id=BUDGET_ID,
        label=budget_label(budget, area),
        status=ConstraintStatus.PASS if cost <= budget.amount_eur else ConstraintStatus.FAIL,
        value=float(cost),
        threshold=float(budget.amount_eur),
        unit="€/mes",
        confidence=rent.confidence,
        explanation=rent_explanation(rent.value, area, rent_note),
    )
