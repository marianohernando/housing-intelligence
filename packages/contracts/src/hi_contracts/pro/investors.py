"""Investor version (D-248): the pilot barrios, a barrio's sheet for whoever builds and the
viability v0 of a development. Shared with the web (TypeScript generated from the JSON Schemas).

Every figure carries where it comes from (`source`, per field, as Sitescope does) and whether it
is data («dato»), our assumption («supuesto») or the person's («usuario»). A missing figure is
null with its reason, never 0. Nothing here changes `/search` or `/gaps`.
"""

from datetime import date
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from hi_contracts.catalog.enums import NullReason, TerritoryLevel
from hi_contracts.public.common import DatasetRef, ZoneRef
from hi_contracts.public.gaps import GapRow

__all__ = [
    "AmbitPhase",
    "AmbitStatus",
    "AssumptionPart",
    "BreakEven",
    "Buildability",
    "BuildabilityKind",
    "DegradedPart",
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
    "NearbyParcel",
    "NormaZonal",
    "ParcelBlock",
    "ParcelCandidate",
    "ParcelCandidates",
    "ParcelCaution",
    "ParcelCautionKey",
    "ParcelContext",
    "ParcelInput",
    "ParcelSheet",
    "ParcelSource",
    "ParcelUnits",
    "PlanUseFigure",
    "PlanningBlock",
    "PlanningInstrument",
    "PlanningKind",
    "PricesBlock",
    "ScenarioOutcome",
    "SourcedValue",
    "UnitUse",
    "UseClass",
    "UseFigure",
    "UseOwnership",
    "ValueMark",
    "Verdict",
    "ViabilityDefaults",
    "ViabilityRequest",
    "ViabilityResult",
]

RC14_PATTERN = r"^[0-9A-Z]{14}$"


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
        "until loaded. An area that also covers other barrios counts whole here"
    )
    remaining_shared_areas: int | None = Field(
        default=None, description="How many of those areas also cover other barrios"
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
    use: str | None = Field(
        default=None, description="Line A's planning areas: their use, as the source writes it"
    )
    note: str | None = Field(
        default=None,
        description="A caveat that travels with the item: an area that also covers other "
        "barrios says which share of it is here (it counts whole in this barrio)",
    )
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
    pem_m2: SourcedValue = Field(
        description="D-252: the calculator's PEM, an assumption (midpoint of the CRG of the "
        "Comunidad de Madrid, bloque abierto, área 1)"
    )
    pem_permits_m2: SourcedValue | None = Field(
        default=None,
        description="D-252: the PEM the building permits declare (CM dataset "
        "cm_visados_presupuesto_obra, from the Feature Store): the low reference",
    )
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

    buildable_m2: float = Field(ge=50, le=500_000, description="m² built; 50 at least")
    sale_price_m2: float = Field(ge=500, le=30_000, description="€/m², before the premium")
    new_build_premium_pct: float = Field(default=0, ge=-20, le=50)
    rent_m2_month: float | None = Field(default=None, ge=1, le=100)
    pem_m2: float = Field(ge=200, le=5_000)
    cost_coefficient: float = Field(default=1.3575, ge=1, le=3)
    land_eur: float | None = Field(default=None, ge=0, le=1_000_000_000)
    land_eur_m2: float | None = Field(
        default=None, ge=0, le=30_000, description="€ per m² buildable"
    )
    sales_costs_pct: float = Field(default=8, ge=0, le=30)
    target_margin_pct: float = Field(default=20, ge=1, le=50)
    adjust_floor_pct: float = Field(
        default=15, ge=0, le=50, description="Lowered to the target margin when above it"
    )
    demand: DemandRequest | None = None

    @model_validator(mode="after")
    def _one_land_price(self) -> Self:
        if self.land_eur is not None and self.land_eur_m2 is not None:
            raise ValueError("land as a total or per m² buildable, not both")
        return self


class BreakEven(BaseModel):
    """D-252: the most the construction can cost for the operation to reach the target margin,
    the other inputs as they are: per built m² (the PEM times the coefficient), and the same said
    as a PEM with the coefficient given or as a coefficient on the PEM given."""

    model_config = ConfigDict(extra="forbid")

    construction_m2: float = Field(description="€ per built m², PEM × coefficient")
    pem_m2: float = Field(description="The same, as a PEM with the coefficient given")
    coefficient: float = Field(description="The same, as a coefficient on the PEM given")
    current_construction_m2: float = Field(description="The inputs' PEM × coefficient")
    land_counted: bool = Field(description="With the land price given; without one, free land")
    reachable: bool = Field(description="False when not even free construction reaches it")


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
    rental_yield_pct: float | None = Field(
        description="Annual rent over construction plus land; null without rent or when not "
        "even free land reaches the target margin"
    )
    yield_land: Literal["precio", "valor_residual"] | None = Field(
        description="The land the yield counts: the price given, or without one the residual "
        "land value (paying the most the target margin allows); never no land"
    )
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
    break_even: BreakEven | None = Field(
        default=None, description="The most the construction can cost for the target margin"
    )
    break_even_free_land: BreakEven | None = Field(
        default=None, description="Only with a land price: the same as if the land were free"
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


# --- Search by parcel (D-250) ---


class ParcelInput(StrEnum):
    """How the parcel was asked for: its cadastral reference, a point on the map or an address."""

    RC = "rc"
    POINT = "point"
    ADDRESS = "address"


class UnitUse(BaseModel):
    """How many units of one use a building has, and their built area: never floor and door."""

    model_config = ConfigDict(extra="forbid")

    use: str = Field(examples=["Residencial", "Comercial"])
    count: int = Field(ge=1)
    built_m2: float | None = Field(ge=0)


class ParcelUnits(BaseModel):
    """A building in horizontal division, summarised: units by use (no list of units)."""

    model_config = ConfigDict(extra="forbid")

    total: int = Field(ge=1)
    by_use: list[UnitUse]


class ParcelBlock(BaseModel):
    """«Datos de la parcela»: our fields, worked out from the Catastro's public data. Never its
    raw answer, never the units with their floor and door."""

    model_config = ConfigDict(extra="forbid")

    rc14: str = Field(pattern=RC14_PATTERN, examples=["2122202VK4722A"])
    address: str | None = Field(examples=["Calle Méndez Álvaro 47, 28045 Madrid"])
    postal_code: str | None = Field(default=None, pattern=r"^\d{5}$")
    lat: float | None = Field(default=None, ge=40.2, le=40.7)
    lon: float | None = Field(default=None, ge=-3.95, le=-3.45)
    area_m2: float | None = Field(ge=0, description="Surface of the parcel (land)")
    rustic: bool | None = Field(description="Rustic land: a reduced sheet, no buildability")
    is_vacant: bool | None = Field(
        description="Parcela sin edificar según su uso en el Catastro; no implica solar (a legal "
        "condition with services). null unknown"
    )
    horizontal_division: bool
    units: ParcelUnits | None = Field(description="Only in horizontal division")
    built_m2: float | None = Field(ge=0, description="Built today: context, not buildability")
    year_built: int | None = Field(default=None, ge=1000, le=2100)
    current_use: str | None
    official_url: HttpUrl | None = Field(
        description="The parcel in the Sede Electrónica del Catastro, as its service returns it"
    )
    observed_at: date = Field(description="When the Catastro was asked")


class PlanningKind(StrEnum):
    """What the planning code is: a norma zonal or a planning area (ámbito) of the PGOUM."""

    NORMA_ZONAL = "norma_zonal"
    API = "API"
    APE = "APE"
    APR = "APR"
    APD = "APD"
    UZI = "UZI"
    UZP = "UZP"
    UNP = "UNP"
    NUP = "NUP"
    AOE = "AOE"
    OTRO = "otro"


class NormaZonal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nz: int = Field(ge=1, le=11)
    grado: int | None = Field(default=None, ge=1, le=9)
    nivel: str | None = Field(default=None, pattern=r"^[a-z]$")
    name: str | None = Field(
        default=None,
        description="The zone's name in the Normas Urbanísticas (art. 8.0.5)",
        examples=["Edificación en manzana cerrada"],
    )


class PlanningInstrument(BaseModel):
    """The planning instrument in force at the point, with its official record."""

    model_config = ConfigDict(extra="forbid")

    figure: str | None = Field(examples=["MPR.02.391"])
    name: str | None
    file_number: str | None = Field(examples=["711/2014/11518"])
    url: HttpUrl | None


class UseClass(StrEnum):
    """D-252: a use as the person reads it, from the planning's or a source's words."""

    RESIDENCIAL = "residencial"
    TERCIARIO = "terciario"
    INDUSTRIAL = "industrial"
    DOTACIONAL = "dotacional"  # equipamientos and services
    ZONA_VERDE = "zona_verde"
    INFRAESTRUCTURA = "infraestructura"  # vía pública, transport, utilities
    SIN_USO = "sin_uso"  # «sin uso pormenorizado»
    OTRO = "otro"


class UseOwnership(StrEnum):
    PUBLICO = "publico"
    PRIVADO = "privado"


class UseFigure(BaseModel):
    """One source's buildable m² for a parcel, with the use that source gives it. A source that
    gives one figure is never split by use."""

    model_config = ConfigDict(extra="forbid")

    use_class: UseClass
    use: str = Field(description="As the source writes it", examples=["INDUSTRIAL"])
    value_m2: float = Field(ge=0)
    source: str
    dataset_id: str
    residential: bool = Field(description="Whether the calculator can use it (housing only)")


class PlanUseFigure(BaseModel):
    """D-252: what the plan allows of one use on the urban parcel (USOS_SUELO, table 4 for the
    principal use and table 5 for the others). The total the plan allows, not what is left; the
    urban parcel may not be the cadastral one."""

    model_config = ConfigDict(extra="forbid")

    use: str = Field(examples=["RESIDENCIAL VIVIENDA COLECTIVA"])
    use_class: UseClass
    use_ownership: UseOwnership | None = None
    principal: bool = Field(description="Table 4, «uso cualificado principal»; else table 5")
    value_m2: float | None = Field(
        default=None, description="m²; with a coefficient, coefficient × urban parcel area"
    )
    coefficient: float | None = Field(default=None, description="m²/m² when the plan gives it so")
    assumed: bool = Field(default=False, description="value_m2 computed from the coefficient")


class AmbitPhase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(examples=["Obras de urbanización"])
    state: str = Field(examples=["Sin Iniciar", "Finalizado", "No Necesita", "PGOUM-85"])


class AmbitStatus(BaseModel):
    """D-252: the state of the planning area, as the Ayuntamiento publishes it."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(description="The code in the Ayuntamiento's list")
    tracked: bool = Field(description="False: the Ayuntamiento does not publish its state")
    pending: bool = Field(description="Planning, management or urbanization not finished")
    phases: list[AmbitPhase] = Field(default_factory=list[AmbitPhase])
    veda_stage: (
        Literal[
            "pendiente_sectorizacion",
            "pendiente_planeamiento",
            "gestion_urbanizacion",
            "edificacion",
        ]
        | None
    ) = None
    as_of: date
    url: HttpUrl


class PlanningBlock(BaseModel):
    """«Planeamiento»: the Ayuntamiento's planning at the parcel's reference point."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(examples=["8.3.a", "APR.02.06"])
    name: str | None = Field(examples=["ZONA 8 GRADO 3º - NIVEL a", "MÉNDEZ ÁLVARO NORTE I"])
    kind: PlanningKind
    norma_zonal: NormaZonal | None
    use: str | None = Field(examples=["RESIDENCIAL VIVIENDA COLECTIVA"])
    use_class: UseClass | None = Field(default=None, description="D-252: the use, classified")
    use_ownership: UseOwnership | None = Field(
        default=None, description="D-252: dotacional público or privado, when the plan says it"
    )
    urban_parcel: str | None = Field(examples=["MANZANA B"])
    urban_parcel_area_m2: float | None = Field(
        default=None, description="D-252: the area of the urban parcel's polygon in the plan"
    )
    plan_uses: list[PlanUseFigure] | None = Field(
        default=None,
        description="D-252: what the plan allows by use on the urban parcel; [] when it publishes "
        "nothing, null when it could not be read",
    )
    plan_uses_as_of: date | None = Field(
        default=None, description="D-252c: the date of the snapshot of tables 4 and 5"
    )
    plan_principal_without_figure: bool = Field(
        default=False,
        description="D-252c: the plan sets the urban parcel's principal use without a figure",
    )
    ambit: AmbitStatus | None = Field(
        default=None, description="D-252: the state of the planning area; null for a norma zonal"
    )
    instrument: PlanningInstrument | None
    sheet_url: HttpUrl | None = Field(
        description="The official record: the instrument's, or the article of the Normas "
        "Urbanísticas for a norma zonal"
    )
    sheet_label: str | None
    viewer_url: HttpUrl = Field(description="The Geoportal viewer, centred on the parcel")
    notice: str
    observed_at: date


class BuildabilityKind(StrEnum):
    OFICIAL = "oficial"
    SUPUESTO = "supuesto"
    SIN_DATO = "sin_dato"


class Buildability(BaseModel):
    """The buildable m² the calculator starts from: official, assumed or unknown. Always
    editable."""

    model_config = ConfigDict(extra="forbid")

    value_m2: float | None = Field(ge=0)
    kind: BuildabilityKind
    source: str = Field(description="In words, with its date or its article")
    article: str | None = Field(default=None, examples=["8.8.9"])
    article_url: HttpUrl | None = None
    coefficient: float | None = Field(default=None, ge=0, description="m² per m² of parcel")
    formula: str | None = Field(default=None, examples=["0,7 m²/m² × 502 m² de parcela"])
    note: str | None = Field(default=None, description="What to keep in mind about the figure")
    assumed_m2: float | None = Field(
        default=None, ge=0, description="The norm's assumption when an official figure wins"
    )
    dataset_ids: list[str] = Field(default_factory=list[str])
    by_use: list[UseFigure] = Field(
        default_factory=list[UseFigure],
        description="D-252: every official figure of the parcel with its use and source",
    )
    editable: Literal[True] = True


class ParcelSource(BaseModel):
    """Who the sheet's data comes from, its licence and how it asks to be cited."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    name: str
    publisher: str
    license: str
    license_url: HttpUrl | None = None
    attribution: str
    url: HttpUrl | None = None
    accessed_at: date | None = None


class ParcelContext(BaseModel):
    """The barrio around the parcel: the whole investor sheet in a pilot barrio (D-248); outside
    the pilot, its district's figures, and it says so."""

    model_config = ConfigDict(extra="forbid")

    level: TerritoryLevel
    in_pilot: bool
    note: str | None
    sheet: InvestorZone


# planning: the Ayuntamiento or its layer of instruments did not answer; buildability: the Z of
# norma zonal 1 could not be read; context: the barrio (the database)
DegradedPart = Literal["catastro", "planning", "buildability", "context", "plan_uses"]


class ParcelCautionKey(StrEnum):
    """D-252: what keeps the sheet's figures from passing for free housing ready to build."""

    OTRO_USO = "otro_uso"
    AMBITO_PENDIENTE = "ambito_pendiente"
    VIVIENDA_PROTEGIDA = "vivienda_protegida"
    UNIFAMILIAR = "unifamiliar"
    AMBITO_SIN_ESTADO = "ambito_sin_estado"


class ParcelCaution(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: ParcelCautionKey
    text: str


class ParcelSheet(BaseModel):
    """GET /api/v1/investors/parcels: one parcel of Madrid capital for whoever builds."""

    model_config = ConfigDict(extra="forbid")

    input: ParcelInput
    parcel: ParcelBlock
    planning: PlanningBlock | None = Field(description="null when the Ayuntamiento fails")
    buildability: Buildability
    barrio: ZoneRef | None
    district: ZoneRef | None
    context: ParcelContext | None = Field(description="null when the barrio is unknown")
    defaults: ViabilityDefaults
    sources: list[ParcelSource]
    notices: list[str]
    degraded: list[DegradedPart] = Field(
        default_factory=list[DegradedPart], description="The parts that could not be read now"
    )
    cautions: list[ParcelCaution] = Field(
        default_factory=list[ParcelCaution], description="D-252: shown before the figures"
    )
    public_land: LandItem | None = Field(
        default=None,
        description="D-252: the parcel as public land of the Portal del Suelo in its barrio "
        "(owner, regime, urbanization), when the barrio's sheet lists it",
    )
    fallback: Literal["demo_snapshot"] | None = Field(
        default=None, description="Served from the saved demo sheet because a source failed"
    )


class ParcelCandidate(BaseModel):
    """An address that matches what was typed, with its parcel. Shown for the person to pick:
    never picked for them."""

    model_config = ConfigDict(extra="forbid")

    address: str
    postal_code: str | None = Field(default=None, pattern=r"^\d{5}$")
    rc14: str = Field(pattern=RC14_PATTERN)
    lat: float | None = None
    lon: float | None = None


class ParcelCandidates(BaseModel):
    """GET /api/v1/investors/parcels/candidates: portals of Madrid capital with their parcel."""

    model_config = ConfigDict(extra="forbid")

    candidates: list[ParcelCandidate]
    needs_number: bool = Field(description="The text matches streets but no portal: add the number")
    sources: list[ParcelSource]


class NearbyParcel(BaseModel):
    """A parcel near a point that falls on the street (in a 404's `details.nearest`)."""

    model_config = ConfigDict(extra="forbid")

    rc14: str = Field(pattern=RC14_PATTERN)
    address: str | None
    distance_m: float | None = Field(ge=0)
