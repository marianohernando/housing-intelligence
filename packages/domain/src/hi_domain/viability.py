"""Viability v0 of a housing development (D-248): the residual method, pure and without I/O.

Every area is a built m² (m² construidos): the buildable area of a public parcel or of a planning
area, the area the building permits declare (PEM per m² built), the estimated price (the city's
appraised value shared out by the cadastral value per built m², D-234) and the reference rent
(Catastro m², D-242). So price × area and PEM × area use the same m².

    revenue        I = A × P × (1 + premium) × fp
    construction   C = A × PEM × k × fc
    sales costs    G = g × I
    land           S, given by the person (total or per m² buildable), or unknown
    margin         m = (I − C − G − S) / I                         (on sales, before financing)
    residual land  V = I × (1 − m*) − C − G                        (the most land can cost)
    rent           R = A × r × 12 × fp;  gross yield = R / (S + C)
                   (without a land price, S = V: paying for the land the most the target allows;
                    no yield when V ≤ 0)

`fp` and `fc` are the scenario's price and cost factors: base (1, 1), optimistic (1,10, 0,95),
pessimistic (0,90, 1,05), as Nestra's sensitivity. The verdict compares the margin with the
target margin m* and the floor below which the operation does not work, and only exists with a
land price: without it there is no verdict, and the headline is the residual land value (what
the land can cost at most). Financing (interest, fees) is out of v0.

Defaults that are not data carry the mark «supuesto» and where they come from; the API fills
the data (price, rent, premium, PEM, buildable m², income) with their datasets.
"""

from dataclasses import dataclass, replace
from enum import StrEnum

from hi_domain.gaps import es_number

VIABILITY_VERSION = "viability-0.1"


class Mark(StrEnum):
    """Where an input comes from: a dataset, an assumption of ours, or the person."""

    DATO = "dato"
    SUPUESTO = "supuesto"
    USUARIO = "usuario"


class YieldLand(StrEnum):
    PRECIO = "precio"  # the land price the person gave
    VALOR_RESIDUAL = "valor_residual"  # without one, the most the target margin allows


class Verdict(StrEnum):
    SALE = "sale"
    AJUSTAR = "ajustar"
    NO_SALE = "no_sale"


@dataclass(frozen=True)
class Part:
    """One piece of an assumed percentage, with where its figure comes from."""

    key: str
    label: str
    share: float
    source: str


# PEM → total construction cost: k = 1 + the parts, all on the PEM. «Supuesto»: no open data
# gives them by zone; the person edits k.
COST_PARTS: tuple[Part, ...] = (
    Part(
        "gastos_generales_beneficio",
        "Gastos generales y beneficio industrial del constructor (de PEM a PEC)",
        0.19,
        "13 % y 6 %, los de los contratos de obra pública (Reglamento general de la Ley de "
        "Contratos de las Administraciones Públicas, RD 1098/2001, art. 131); en obra privada "
        "se negocian",
    ),
    Part(
        "honorarios",
        "Honorarios técnicos: proyecto, dirección de obra y seguridad y salud",
        0.08,
        "supuesto: suelen ir del 6 % al 10 % del PEM",
    ),
    Part(
        "licencias_icio",
        "Licencia, ICIO y tasas",
        0.05,
        "ICIO de Madrid, 4 % del presupuesto (Ordenanza fiscal del impuesto), y la tasa de la "
        "licencia y otros tributos, alrededor de un 1 % (supuesto)",
    ),
    Part(
        "otros",
        "Otros: seguro decenal, organismo de control, ensayos y acometidas",
        0.04,
        "supuesto",
    ),
)
COST_COEFFICIENT = round(1 + sum(p.share for p in COST_PARTS), 4)

# Costs that follow the sales, as a share of revenue. «Supuesto».
SALES_COST_PARTS: tuple[Part, ...] = (
    Part("comercializacion", "Comercialización y publicidad", 0.03, "supuesto"),
    Part("gestion", "Gestión de la promoción y administración", 0.03, "supuesto"),
    Part(
        "notaria_registro_impuestos",
        "Notaría, registro e impuestos de la obra nueva y la división horizontal",
        0.02,
        "supuesto",
    ),
)
SALES_COSTS_SHARE = round(sum(p.share for p in SALES_COST_PARTS), 4)

# Margin on sales before financing. «Supuesto»: promoters usually ask 15-20 % or more; with
# financing out of v0, the target sits at the top. Below the floor the operation does not work.
TARGET_MARGIN = 0.20
ADJUST_FLOOR = 0.10
MARGIN_SOURCE = (
    "supuesto: un promotor suele pedir entre el 15 % y el 20 % sobre ventas, o más; como la "
    "financiación no entra, se toma el 20 %. Por debajo del 10 %, no sale"
)


@dataclass(frozen=True)
class Scenario:
    key: str
    label: str
    price_factor: float
    cost_factor: float


SCENARIOS: tuple[Scenario, ...] = (
    Scenario("base", "Base", 1.0, 1.0),
    Scenario("optimista", "Optimista (+10 % precio, −5 % coste)", 1.10, 0.95),
    Scenario("pesimista", "Pesimista (−10 % precio, +5 % coste)", 0.90, 1.05),
)

# Demand check. «Supuesto» except the threshold, which is the one the housing law uses.
HOME_M2 = 80.0
HOME_M2_SOURCE = (
    "supuesto: un piso de 2 o 3 dormitorios; unos 68 m² útiles, la superficie mediana de los "
    "hogares de 2 personas en la Comunidad (Censo 2021, D-214), más su parte de zonas comunes"
)
LOAN_TO_VALUE = 0.80
LOAN_YEARS = 30
LOAN_RATE = 0.03
LOAN_SOURCE = (
    "supuesto: lo que suele financiar un banco (80 % del precio, 30 años) a un tipo fijo del 3 %"
)
EFFORT_THRESHOLD = 0.30
EFFORT_SOURCE = (
    "Ley 12/2023 por el derecho a la vivienda, art. 18.2 a): una zona está tensionada si la "
    "hipoteca o el alquiler, con los gastos y suministros básicos, superan el 30 % de la renta "
    "media de los hogares. Aquí solo se cuenta la cuota o el alquiler, sin gastos ni "
    "suministros: la cuenta es optimista"
)
EFFORT_CAVEAT = (
    "Solo cuenta la cuota o el alquiler, sin gastos ni suministros: la cuenta es optimista."
)

NOTICES: tuple[str, ...] = (
    "No es una tasación ni un informe vinculante ni una garantía de rentabilidad.",
    "Contexto urbanístico, no qué se puede construir: los m² edificables son los que publica "
    "la fuente; la normativa de cada parcela manda.",
    "Sin dato no es 0: lo que no sabemos se dice, nunca se rellena.",
    "La financiación (intereses y comisiones del préstamo) no entra en esta versión: el margen "
    "es antes de financiación e impuestos.",
    "El PEM de los visados suele declararse a la baja: el coste real de la obra puede ser mayor. "
    "Ajusta el coeficiente si tienes un presupuesto.",
)


@dataclass(frozen=True)
class ViabilityInputs:
    """Per built m² and in euros; shares as fractions (0.2 = 20 %)."""

    buildable_m2: float
    sale_price_m2: float  # €/m², before the new-build premium
    new_build_premium: float
    rent_m2_month: float | None
    pem_m2: float
    cost_coefficient: float = COST_COEFFICIENT
    land_eur: float | None = None
    sales_costs_share: float = SALES_COSTS_SHARE
    target_margin: float = TARGET_MARGIN
    adjust_floor: float = ADJUST_FLOOR


@dataclass(frozen=True)
class BreakEven:
    """D-252: the most the construction can cost per built m² (the PEM times the coefficient,
    before the scenario's cost factor) for the operation to keep the target margin, everything
    else as given; and the same as a PEM with the coefficient given, or as a coefficient on the
    PEM given. Without a land price it is the construction cost with free land: each euro under
    it is a euro the land can cost."""

    construction_m2: float
    pem_m2: float
    coefficient: float
    current_construction_m2: float
    land_counted: bool

    @property
    def reachable(self) -> bool:
        return self.construction_m2 > 0


@dataclass(frozen=True)
class ScenarioResult:
    scenario: Scenario
    revenue: float
    construction: float
    sales_costs: float
    land: float | None
    total_cost: float | None  # None without a land price
    profit: float | None
    margin: float | None
    residual_land_value: float
    residual_land_value_m2: float
    annual_rent: float | None
    rental_yield: float | None
    # What the yield counts as land: the person's price, or the residual land value without
    # one (paying the most the target margin allows); None when there is no yield
    yield_land: YieldLand | None
    verdict: Verdict | None  # only with a land price
    headline: str  # the verdict in words, or without land the residual land value
    break_even: BreakEven | None = None
    # Only with a land price: the same as if the land were free
    break_even_free_land: BreakEven | None = None


@dataclass(frozen=True)
class ViabilityResult:
    inputs: ViabilityInputs
    land_known: bool
    scenarios: tuple[ScenarioResult, ...]


def money(amount: float) -> str:
    """«1,25 millones de €» from a million up, else «850.000 €»."""
    if abs(amount) >= 1_000_000:
        return f"{es_number(amount / 1_000_000, 2)} millones de €"
    return f"{es_number(round(amount), 0)} €"


def pct(share: float, decimals: int = 0) -> str:
    return f"{es_number(share * 100, decimals)} %"


def sale_price_with_premium(inputs: ViabilityInputs) -> float:
    return inputs.sale_price_m2 * (1 + inputs.new_build_premium)


def adjust_floor(inputs: ViabilityInputs) -> float:
    """The floor of «ajustar» never above the target: a target of 8 % leaves no «ajustar» band."""
    return min(inputs.adjust_floor, inputs.target_margin)


def gross_yield(
    rent: float | None, construction: float, land: float | None, residual: float
) -> tuple[float | None, YieldLand | None]:
    """Annual rent over what is invested to build. Never without land: without a price, the land
    is the residual value (the most the target margin allows); if even free land misses the
    target, there is no land value to count and no yield."""
    if rent is None:
        return None, None
    if land is not None:
        return rent / (construction + land), YieldLand.PRECIO
    if residual <= 0:
        return None, None
    return rent / (construction + residual), YieldLand.VALOR_RESIDUAL


def residual_land_value(revenue: float, construction: float, sales: float, margin: float) -> float:
    """What the land can cost for the operation to keep `margin` on its sales."""
    return revenue * (1 - margin) - construction - sales


def margin_verdict(margin: float, target: float, floor: float) -> tuple[Verdict, str]:
    """A margin is said with one decimal (12,5 %), the thresholds without."""
    shown = pct(margin, 1)
    if margin >= target:
        return Verdict.SALE, f"Sale: margen del {shown} sobre ventas (objetivo, {pct(target)})."
    if margin >= floor:
        return (
            Verdict.AJUSTAR,
            f"Ajustar: margen del {shown}, por debajo del {pct(target)} objetivo.",
        )
    if margin < 0:
        return Verdict.NO_SALE, f"No sale: pierde el {pct(-margin, 1)} de lo que vende."
    return Verdict.NO_SALE, f"No sale: margen del {shown}, por debajo del {pct(floor)}."


def residual_headline(
    revenue: float, construction: float, sales: float, inputs: ViabilityInputs
) -> str:
    """Without a land price there is no verdict: what the land can cost at most for the target
    margin, or, if not even free land reaches it, the margin free land would leave."""
    at_target = residual_land_value(revenue, construction, sales, inputs.target_margin)
    if at_target > 0:
        per_m2 = at_target / inputs.buildable_m2
        return (
            f"Lo máximo que se puede pagar por el suelo: {money(at_target)} "
            f"({es_number(round(per_m2), 0)} € por m² edificable), para un margen del "
            f"{pct(inputs.target_margin)}."
        )
    free_land_margin = (revenue - construction - sales) / revenue
    return (
        f"Ni con el suelo gratis se llega al margen objetivo del {pct(inputs.target_margin)}: "
        f"se queda en el {pct(free_land_margin, 1)}."
    )


def break_even(inputs: ViabilityInputs, scenario: Scenario = SCENARIOS[0]) -> BreakEven:
    """How much the construction may cost for the operation to keep the target margin:

        I (1 − m*) − g·I − S ≥ A · c · fc   ⇔   c ≤ (I (1 − m*) − g·I − S) / (A · fc)

    with I the scenario's revenue, S the land price (0 without one) and c the construction per
    built m² as the person gives it (PEM × coefficient). Same model as run_scenario."""
    area = inputs.buildable_m2
    revenue = area * sale_price_with_premium(inputs) * scenario.price_factor
    sales = inputs.sales_costs_share * revenue
    land = inputs.land_eur or 0.0
    room = revenue * (1 - inputs.target_margin) - sales - land
    construction_m2 = room / (area * scenario.cost_factor)
    return BreakEven(
        construction_m2=construction_m2,
        pem_m2=construction_m2 / inputs.cost_coefficient,
        coefficient=construction_m2 / inputs.pem_m2,
        current_construction_m2=inputs.pem_m2 * inputs.cost_coefficient,
        land_counted=inputs.land_eur is not None,
    )


def run_scenario(inputs: ViabilityInputs, scenario: Scenario) -> ScenarioResult:
    area = inputs.buildable_m2
    revenue = area * sale_price_with_premium(inputs) * scenario.price_factor
    construction = area * inputs.pem_m2 * inputs.cost_coefficient * scenario.cost_factor
    sales = inputs.sales_costs_share * revenue
    residual = residual_land_value(revenue, construction, sales, inputs.target_margin)
    land = inputs.land_eur
    if land is None:
        total = profit = margin = None
        verdict, text = None, residual_headline(revenue, construction, sales, inputs)
    else:
        total = construction + sales + land
        profit = revenue - total
        margin = profit / revenue
        verdict, text = margin_verdict(margin, inputs.target_margin, adjust_floor(inputs))
    rent = None
    if inputs.rent_m2_month is not None:
        rent = area * inputs.rent_m2_month * 12 * scenario.price_factor
    rental_yield, yield_land = gross_yield(rent, construction, land, residual)
    return ScenarioResult(
        scenario=scenario,
        revenue=revenue,
        construction=construction,
        sales_costs=sales,
        land=land,
        total_cost=total,
        profit=profit,
        margin=margin,
        residual_land_value=residual,
        residual_land_value_m2=residual / area,
        annual_rent=rent,
        rental_yield=rental_yield,
        yield_land=yield_land,
        verdict=verdict,
        headline=text,
        break_even=break_even(inputs, scenario),
        break_even_free_land=None
        if land is None
        else break_even(replace(inputs, land_eur=None), scenario),
    )


def viability(inputs: ViabilityInputs) -> ViabilityResult:
    """The three scenarios. Raises ValueError on inputs no development can have."""
    if inputs.buildable_m2 <= 0 or inputs.sale_price_m2 <= 0 or inputs.pem_m2 <= 0:
        raise ValueError("buildable area, sale price and PEM must be positive")
    if inputs.cost_coefficient < 1:
        raise ValueError("the cost coefficient starts at 1 (the PEM alone)")
    if not 0 <= inputs.sales_costs_share < 1 or not 0 <= inputs.target_margin < 1:
        raise ValueError("shares go from 0 to 1")
    return ViabilityResult(
        inputs=inputs,
        land_known=inputs.land_eur is not None,
        scenarios=tuple(run_scenario(inputs, s) for s in SCENARIOS),
    )


# --- Demand check: what the home would take from the barrio's mean household income ---


@dataclass(frozen=True)
class DemandInputs:
    household_income_year: float  # net mean income of the barrio's households
    sale_price_m2: float  # €/m² of the new home (with the premium)
    rent_m2_month: float | None
    home_m2: float = HOME_M2
    loan_to_value: float = LOAN_TO_VALUE
    loan_years: int = LOAN_YEARS
    loan_rate: float = LOAN_RATE
    effort_threshold: float = EFFORT_THRESHOLD


@dataclass(frozen=True)
class DemandCheck:
    home_price: float
    loan: float
    down_payment: float
    down_payment_years: float  # the down payment in years of the mean income
    monthly_payment: float
    purchase_effort: float
    monthly_rent: float | None
    rent_effort: float | None
    threshold: float
    purchase_within: bool
    rent_within: bool | None
    lines: tuple[str, ...]


def monthly_payment(loan: float, annual_rate: float, years: int) -> float:
    """French amortisation: the fixed monthly payment of a loan."""
    months = years * 12
    if annual_rate == 0:
        return loan / months
    rate = annual_rate / 12
    return loan * rate / (1 - (1 + rate) ** -months)


def effort_line(what: str, effort: float, threshold: float) -> str:
    side = "por encima" if effort > threshold else "dentro"
    return (
        f"{what} sería el {pct(effort)} de la renta media de los hogares del barrio: "
        f"{side} del {pct(threshold)}."
    )


def demand_check(inputs: DemandInputs) -> DemandCheck:
    if inputs.household_income_year <= 0 or inputs.home_m2 <= 0:
        raise ValueError("income and home area must be positive")
    price = inputs.home_m2 * inputs.sale_price_m2
    loan = price * inputs.loan_to_value
    payment = monthly_payment(loan, inputs.loan_rate, inputs.loan_years)
    purchase_effort = payment * 12 / inputs.household_income_year
    rent = None if inputs.rent_m2_month is None else inputs.home_m2 * inputs.rent_m2_month
    rent_effort = None if rent is None else rent * 12 / inputs.household_income_year
    down = price - loan
    lines = [
        f"Una vivienda nueva de {es_number(inputs.home_m2, 0)} m² costaría unos {money(price)}.",
        effort_line(
            f"La cuota de la hipoteca ({money(payment)} al mes)",
            purchase_effort,
            inputs.effort_threshold,
        ),
        f"La entrada ({money(down)}) son {es_number(down / inputs.household_income_year, 1)} "
        "años de esa renta, sin contar los gastos de la compra.",
    ]
    if rent is not None and rent_effort is not None:
        lines.append(
            effort_line(f"El alquiler ({money(rent)} al mes)", rent_effort, inputs.effort_threshold)
        )
    lines.append(EFFORT_CAVEAT)
    lines.append("Es la renta media: no dice cuántos hogares ganan más o menos que ella.")
    return DemandCheck(
        home_price=price,
        loan=loan,
        down_payment=down,
        down_payment_years=down / inputs.household_income_year,
        monthly_payment=payment,
        purchase_effort=purchase_effort,
        monthly_rent=rent,
        rent_effort=rent_effort,
        threshold=inputs.effort_threshold,
        purchase_within=purchase_effort <= inputs.effort_threshold,
        rent_within=None if rent_effort is None else rent_effort <= inputs.effort_threshold,
        lines=tuple(lines),
    )
