"""Investor version (D-248): the pilot barrios, a barrio's sheet for whoever builds and the
viability v0 of a development. Shared with the web (TypeScript generated from the JSON Schemas).

Every figure carries where it comes from (`source`, per field, as Sitescope does) and whether it
is data («dato»), our assumption («supuesto») or the person's («usuario»). A missing figure is
null with its reason, never 0. Nothing here changes `/search` or `/gaps`.
"""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_contracts.public.common import DatasetRef, ZoneRef
from hi_contracts.public.gaps import GapRow

__all__ = [
    "AssumptionPart",
    "DemandBlock",
    "DemandOutcome",
    "DemandRequest",
    "FieldSource",
    "GapCount",
    "InvestorGaps",
    "InvestorZone",
    "InvestorZoneList",
    "InvestorZoneSummary",
    "LandBlock",
    "LandItem",
    "PricesBlock",
    "ScenarioOutcome",
    "SourcedValue",
    "ValueMark",
    "Verdict",
    "ViabilityDefaults",
    "ViabilityRequest",
    "ViabilityResult",
]


class ValueMark(StrEnum):
    DATO = "dato"
    SUPUESTO = "supuesto"
    USUARIO = "usuario"


class Verdict(StrEnum):
    SALE = "sale"
    AJUSTAR = "ajustar"
    NO_SALE = "no_sale"


class FieldSource(BaseModel):
    """Where one figure comes from, to show next to it."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        description="In words, with its date",
        examples=["Valor tasado de Madrid (Ministerio de Vivienda, 2025) repartido por barrios"],
    )
    level: TerritoryLevel | None = Field(
        default=None,
        description="The zone the figure is of: the barrio, its district or the whole city",
    )
    period: str | None = Field(default=None, examples=["2025"])
    dataset_ids: list[str] = Field(default_factory=list[str])
    url: HttpUrl | None = Field(default=None, description="Where to open the source")


class SourcedValue(BaseModel):
    """A figure with its unit, mark and source; `low` and `high` when the source gives a range."""

    model_config = ConfigDict(extra="forbid")

    feature_id: str | None = Field(
        default=None, description="The Feature Store figure behind it, when it is data"
    )
    value: float | None
    unit: str
    mark: ValueMark
    source: FieldSource
    null_reason: NullReason | None = Field(
        default=None, description="Why value is missing; never 0 for unknown"
    )
    confidence: float | None = Field(default=None, ge=0, le=1)
    low: float | None = None
    high: float | None = None


class AssumptionPart(BaseModel):
    """One piece of an assumed percentage (the cost coefficient, the sales costs)."""

    model_config = ConfigDict(extra="forbid")

    key: str
    label: str
    pct: float = Field(ge=0, le=100)
    source: str


class GapCount(BaseModel):
    model_config = ConfigDict(extra="forbid")

    falta: int = Field(ge=0)
    justo: int = Field(ge=0)
    rows: list[str] = Field(description="Labels of the FALTA rows, then the JUSTO ones")


class InvestorZoneSummary(BaseModel):
    """A pilot barrio in the list: what it lacks (its district's rows), its land and prices."""

    model_config = ConfigDict(extra="forbid")

    zone: ZoneRef
    district: ZoneRef
    gaps: GapCount | None = Field(description="Its district's «Qué falta»; null if not computed")
    parcels: int | None = Field(description="Public parcels for housing; null if unknown")
    parcels_m2: float | None
    remaining_m2: float | None = Field(
        description="Residential buildable area left in its planning areas (line A); null "
        "until loaded"
    )
    commerce_per_1000: float | None = Field(
        description="Open local shops per 1.000 inhabitants (line A); null until loaded"
    )
    sale_price_m2: float | None
    rent_m2_month: float | None


class InvestorZoneList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pilot: str = Field(examples=["Madrid capital dentro de la M-40"])
    zones: list[InvestorZoneSummary]
    datasets: list[DatasetRef]


class DemandBlock(BaseModel):
    """Who lives there. Each figure at the finest level published (its `source.level`)."""

    model_config = ConfigDict(extra="forbid")

    population: SourcedValue
    household_size: SourcedValue
    one_person_pct: SourcedValue
    five_plus_pct: SourcedValue
    over_65_pct: SourcedValue
    under_15_pct: SourcedValue
    income: SourcedValue


class PricesBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sale_m2: SourcedValue
    new_build_premium_pct: SourcedValue
    new_build_sale_m2: SourcedValue
    rent_m2_month: SourcedValue


class InvestorGaps(BaseModel):
    """«Qué falta»: the district's rows (the list is not computed by barrio) and the commerce of
    the barrio (line A)."""

    model_config = ConfigDict(extra="forbid")

    level: TerritoryLevel
    zone_name: str
    rows: list[GapRow]
    commerce: list[SourcedValue]
    warnings: list[str] = Field(default_factory=list[str])


class LandItem(BaseModel):
    """A public parcel (D-246) or a planning area with buildable area left (line A)."""

    model_config = ConfigDict(extra="forbid")

    kind: str = Field(description="parcela | ambito")
    code: str | None
    name: str | None
    parcel: str | None = None
    buildable_m2: float | None = Field(description="null when the source does not publish it")
    regime: str | None = Field(default=None, description="venta | concesion")
    manager: str | None = None
    stage: str | None = None
    url: str | None = Field(default=None, description="The official viewer or record")


class LandBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parcels: list[LandItem]
    parcels_m2: SourcedValue
    remaining: list[LandItem]
    remaining_m2: SourcedValue
    vacant_units: SourcedValue


class ViabilityDefaults(BaseModel):
    """What the calculator starts from, every value with its mark and source."""

    model_config = ConfigDict(extra="forbid")

    sale_price_m2: SourcedValue
    new_build_premium_pct: SourcedValue
    rent_m2_month: SourcedValue
    pem_m2: SourcedValue
    cost_coefficient: SourcedValue
    cost_parts: list[AssumptionPart]
    sales_costs_pct: SourcedValue
    sales_cost_parts: list[AssumptionPart]
    target_margin_pct: SourcedValue
    adjust_floor_pct: SourcedValue
    household_income: SourcedValue
    home_m2: SourcedValue
    ltv_pct: SourcedValue
    loan_years: SourcedValue
    loan_rate_pct: SourcedValue
    effort_threshold_pct: SourcedValue


class InvestorZone(BaseModel):
    """GET /api/v1/investors/zones/{admin_unit_id}: the sheet of one pilot barrio."""

    model_config = ConfigDict(extra="forbid")

    zone: ZoneRef
    district: ZoneRef
    demand: DemandBlock
    prices: PricesBlock
    gaps: InvestorGaps | None
    land: LandBlock
    defaults: ViabilityDefaults
    notices: list[str]
    datasets: list[DatasetRef]


class DemandRequest(BaseModel):
    """The demand check: a typical new home against the barrio's mean household income."""

    model_config = ConfigDict(extra="forbid")

    household_income: float = Field(ge=5_000, le=500_000, description="€ net a year")
    home_m2: float = Field(default=80, ge=20, le=300)
    ltv_pct: float = Field(default=80, ge=0, le=100)
    loan_years: int = Field(default=30, ge=5, le=40)
    loan_rate_pct: float = Field(default=3, ge=0, le=15)
    effort_threshold_pct: float = Field(default=30, ge=5, le=100)


class ViabilityRequest(BaseModel):
    """POST /api/v1/investors/viability. Per built m² and in euros; percentages as 20 = 20 %.
    Land as a total or per m² buildable, not both; without it, the result is the residual land
    value (the most the land can cost)."""

    model_config = ConfigDict(extra="forbid")

    buildable_m2: float = Field(gt=0, le=500_000)
    sale_price_m2: float = Field(ge=500, le=30_000, description="€/m², before the premium")
    new_build_premium_pct: float = Field(default=0, ge=-20, le=50)
    rent_m2_month: float | None = Field(default=None, ge=1, le=100)
    pem_m2: float = Field(ge=200, le=5_000)
    cost_coefficient: float = Field(default=1.36, ge=1, le=3)
    land_eur: float | None = Field(default=None, ge=0, le=1_000_000_000)
    land_eur_m2: float | None = Field(
        default=None, ge=0, le=30_000, description="€ per m² buildable"
    )
    sales_costs_pct: float = Field(default=8, ge=0, le=30)
    target_margin_pct: float = Field(default=20, ge=1, le=50)
    adjust_floor_pct: float = Field(default=10, ge=0, le=50)
    demand: DemandRequest | None = None

    @model_validator(mode="after")
    def _one_land_price(self) -> Self:
        if self.land_eur is not None and self.land_eur_m2 is not None:
            raise ValueError("land as a total or per m² buildable, not both")
        if self.adjust_floor_pct > self.target_margin_pct:
            raise ValueError("the floor of «ajustar» is at most the target margin")
        return self


class ScenarioOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(examples=["base", "optimista", "pesimista"])
    label: str
    price_factor: float
    cost_factor: float
    revenue: float
    construction: float
    sales_costs: float
    land: float | None
    total_cost: float | None = Field(description="null without a land price")
    profit: float | None
    margin_pct: float | None
    residual_land_value: float
    residual_land_value_m2: float
    annual_rent: float | None
    rental_yield_pct: float | None
    yield_includes_land: bool
    verdict: Verdict | None = Field(
        description="Only with a land price; without it, null: the headline is the residual "
        "land value"
    )
    headline: str = Field(
        examples=[
            "Sale: margen del 22,5 % sobre ventas (objetivo, 20 %).",
            "Lo máximo que se puede pagar por el suelo: 1,90 millones de € (1.900 € por m² "
            "edificable), para un margen del 20 %.",
        ]
    )


class DemandOutcome(BaseModel):
    model_config = ConfigDict(extra="forbid")

    home_price: float
    loan: float
    down_payment: float
    down_payment_years: float
    monthly_payment: float
    purchase_effort_pct: float
    monthly_rent: float | None
    rent_effort_pct: float | None
    threshold_pct: float
    purchase_within: bool
    rent_within: bool | None
    lines: list[str]


class ViabilityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(examples=["viability-0.1"])
    land_known: bool
    sale_price_m2_new: float = Field(description="The sale price with the new-build premium")
    scenarios: list[ScenarioOutcome]
    demand: DemandOutcome | None
    notices: list[str]
