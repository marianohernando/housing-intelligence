"""Affordability (CORE-006, D-214): what a home for the household costs in a zone, and the
budget condition PASS / FAIL / UNKNOWN. UNKNOWN never counts as PASS (CLAUDE.md §14).

Rent: the zone's published rent per m² (feature `alquiler_m2_mensual`) times the floor area
the household needs. Unless the person sets it, that area is the median useful floor area of
the homes of households of the same size in the Comunidad de Madrid (Censo de Población y
Viviendas 2021, INE table 59524). Purchase: no open official source of prices by zone yet
(DATA-021), so its condition is UNKNOWN and says so (D-203).
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
RENT_NOTE = "media de los contratos vigentes; uno nuevo suele costar más"
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


def rent_explanation(rent_m2: float, area: FloorArea) -> str:
    cost = monthly_rent(rent_m2, area.m2)
    return (
        f"Alquiler medio ≈ {euros(cost)}/mes por {area.m2} m² "
        f"({es_number(rent_m2, 1)} €/m², {RENT_NOTE})"
    )


def _purchase_unknown(budget: Budget, area: FloorArea) -> ConstraintCheck:
    return ConstraintCheck(
        constraint_id=BUDGET_ID,
        label=budget_label(budget, area),
        status=ConstraintStatus.UNKNOWN,
        threshold=float(budget.amount_eur),
        unit="€",
        confidence=0.0,
        explanation=(
            "Sin datos: aún no hay una fuente oficial abierta y fiable de precios de compra por "
            "zona, así que no podemos decir si te llega"
        ),
    )


def budget_check(budget: Budget, rent: IndicatorValue | None, area: FloorArea) -> ConstraintCheck:
    if budget.kind is BudgetKind.BUY:
        return _purchase_unknown(budget, area)
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
    cost = monthly_rent(rent.value, area.m2)
    return ConstraintCheck(
        constraint_id=BUDGET_ID,
        label=budget_label(budget, area),
        status=ConstraintStatus.PASS if cost <= budget.amount_eur else ConstraintStatus.FAIL,
        value=float(round(cost)),
        threshold=float(budget.amount_eur),
        unit="€/mes",
        confidence=rent.confidence,
        explanation=rent_explanation(rent.value, area),
    )
